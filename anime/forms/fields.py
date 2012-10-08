import datetime
import re
import time
from anime.models import AnimeItem, AnimeName, DATE_FORMATS
from anime.utils.json import JSONFunctionCaller
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.forms import CharField, TextInput, URLField, DateField, ImageField
from django.forms.fields import IntegerField
from django.forms.widgets import CheckboxInput, RadioSelect, MultiWidget
# format_html in django trunk
# from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


#dirty but works
INPUT_FORMATS = (
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y',
    '%b %d %Y', '%b %d, %Y',
    '%d %b %Y', '%d %b, %Y',
    '%B %d %Y', '%B %d, %Y',
    '%d %B %Y', '%d %B, %Y',
)


LINKS_URLS = [
    (0, None, None),
    (1, re.compile(u'^(?:http|ftp)s?://anidb\.net/(?:perl-bin/animedb\.pl\?show=anime\&aid=|a)(\d+)'),
        u'http://anidb.net/a{0}'),
    (2, re.compile(u'^(?:http|ftp)s?://www\.animenewsnetwork\.com/encyclopedia/anime\.php\?id=(\d+)'),
        u'http://www.animenewsnetwork.com/encyclopedia/anime.php?id={0}'),
    (3, re.compile(u'^(?:http|ftp)s?://myanimelist\.net/anime/(\d+)'),
        u'http://myanimelist.net/anime/{0}'),
    (4, re.compile(u'^(?:http|ftp)s?://[a-z]{2}\.wikipedia\.org/wiki/(.+)#?'), None),
    (5, None, None),
    (6, None, None),
    (7, None, None),
    (8, None, None),
    (9, None, None),
    (10, None, None),
    (11, None, None),
    (12, None, None),
    (13, None, None),
    (14, None, None),
    (15, None, None)
]


class TextToAnimeItemField(CharField):
    extra_error_messages = {
        'multiple': _(u'Too many items with such title, try to use id instead title.'),
    }
    widget = TextInput(attrs={'onfocus': JSONFunctionCaller('add_auto',
                        'this', {'className': 'app bundle_app'},
                        ['title', 'type', 'release'], "'id'")})

    def __init__(self, *args, **kwargs):
        super(TextToAnimeItemField, self).__init__(*args, **kwargs)
        self.error_messages.update(self.extra_error_messages)

    def to_python(self, value):
        if not value:
            return None
        value = value.strip()
        try:
            ivalue = int(value)
            value = AnimeItem.objects.get(id=ivalue)
        except:
            try:
                value = AnimeItem.objects.get(title=value)
            except AnimeItem.DoesNotExist, e:
                raise ValidationError(e)
            except AnimeItem.MultipleObjectsReturned, e:
                raise ValidationError(self.error_messages['multiple'])
        return value


class TextToAnimeNameField(CharField):
    extra_error_messages = {
        'noname': _(u'AnimeItem not set.'),
    }
    _animeobject = None

    def __init__(self, *args, **kwargs):
        super(TextToAnimeNameField, self).__init__(*args, **kwargs)
        self.error_messages.update(self.extra_error_messages)

    def to_python(self, value):
        try:
            value = value.strip()
            if value in EMPTY_VALUES:
                raise ValueError
        except:
            return None
        if not self._animeobject:
            raise ValidationError(self.error_messages['noname'])
        try:
            try:
                value = AnimeName.objects.get(anime=self._animeobject, title=value)
            except AnimeName.DoesNotExist:
                value = AnimeName(anime=self._animeobject, title=value)
        except Exception, e:
            raise ValidationError(e)
        return value


class TextToAnimeLinkField(URLField):
    extra_error_messages = {
        'notype': _(u'Type for this field is not set.'),
        'badtype': _(u'Bad link type choosen.'),
        'badlink': _(u'Bad link passed.'),
    }
    _linktype = None

    def __init__(self, *args, **kwargs):
        super(TextToAnimeLinkField, self).__init__(*args, **kwargs)
        self.error_messages.update(self.extra_error_messages)

    def to_python(self, value):
        if self._linktype is None:
            raise ValidationError(self.error_messages['notype'])
        try:
            value = value.strip()
            if value in EMPTY_VALUES:
                raise ValueError
        except:
            return None
        regexp = None
        if self._linktype == 0:
            for t, r, l in LINKS_URLS[1:]:
                if r:
                    regexp = r.match(value)
                    if regexp:
                        self._linktype = t
                        break
            if not self._linktype:
                self._linktype = 15
        cregexp = LINKS_URLS[self._linktype][1]
        link = LINKS_URLS[self._linktype][2]
        if not regexp and cregexp:
            regexp = cregexp.match(value)
            if not regexp:
                raise ValidationError(self.error_messages['badlink'])
        try:
            if regexp and link:
                value = link.format(regexp.groups()[-1])
            elif value.isdecimal():
                value = link.format(value)
        except AttributeError:
            #Check value type first, str cannot into isdecimal
            raise ValidationError(self.error_messages['badtype'])
        return super(TextToAnimeLinkField, self).to_python(value)


class CalendarWidget(TextInput):

    def __init__(self, attrs={}):
        self._known = 0
        attrs['class'] = 'vDateField'
        super(CalendarWidget, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        if isinstance(value, datetime.date):
            try:
                value = value.strftime(DATE_FORMATS[self._known])
            except:
                value = _('Bad value')
        return super(CalendarWidget, self).render(name, value, attrs)


class UnknownDateField(DateField):
    widget=CalendarWidget
    cleaned_data = {}

    def __init__(self, *args, **kwargs):
        super(UnknownDateField, self).__init__(*args, **kwargs)
        self.input_formats = DATE_FORMATS + INPUT_FORMATS

    #Not needed if changeset > 16137
    def to_python(self, value):
        """
        Validates that the input can be converted to a date. Returns a Python
        datetime.date object.
        """
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        try:
            value = value.strip()
            if value in EMPTY_VALUES:
                raise ValueError
        except:
            return None
        for format in self.input_formats:
            try:
                return self.strptime(value, format)
            except ValueError:
                continue
        raise ValidationError(self.error_messages['invalid'])

    def strptime(self, value, format):
        date = datetime.date(*time.strptime(value, format)[:3])
        #cs > 16137
        #date = super(UnknownDateField, self).strptime(self, value, format)
        label = self.label.lower()
        try:
            dindex = DATE_FORMATS.index(format)
            self.cleaned_data[label + 'Known'] = dindex
            if label == 'ended':
                date = self.get_last_date(date, dindex)
            for field in ('released', 'ended'):
                if field == label:
                    self.cleaned_data[u'air'] = True if date >= date.today() else False
        except ValueError:
            self.cleaned_data[label + 'Known'] = 0
        return date

    def get_last_date(self, date, format_index):
        if format_index & 4: # year
            date = date.replace(year=date.max.year)
        if format_index & 2: # month
            date = date.replace(month=date.max.month)
        if format_index & 1: #day
            date = date.replace(day=1, month=(date.month%12)+1) - datetime.timedelta(1)
        return date


class CardImageField(ImageField):
    extra_error_messages = {
        'bad_format': _(u'Only PNG, JPEG and GIF formats are accepted'),
        'big_image': _(u'Image too big'),
    }

    def __init__(self, *args, **kwargs):
        super(CardImageField, self).__init__(*args, **kwargs)
        self.error_messages.update(self.extra_error_messages)
        self.error_messages['invalid_image'] = u'{1}. {0}'.format(
                self.error_messages.get('invalid_image', ''), u'{0}')

    def to_python(self, data):
        """
        Checks that the file-upload field data contains a valid image (GIF, JPG,
        PNG). Resize image if it is biggest than allowed.
        """
        f = super(ImageField, self).to_python(data)
        if f is None:
            return None
        # Try to import PIL in either of the two ways it can end up installed.
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO
        try:
            from PIL import Image
        except ImportError:
            import Image
        # We need to get a file object for PIL. We might have a path or we might
        # have to read the data into memory.
        if hasattr(data, 'temporary_file_path'):
            file = data.temporary_file_path()
        else:
            if hasattr(data, 'read'):
                file = StringIO(data.read())
            else:
                file = StringIO(data['content'])
        try:
            # load() is the only method that can spot a truncated JPEG,
            #  but it cannot be called sanely after verify()
            trial_image = Image.open(file)
            trial_image.load()
            if trial_image.format not in ('PNG', 'JPEG', 'GIF'):
                raise ValueError(self.error_messages['bad_format'])
            if max(trial_image.size) >= 801:
                raise ValueError(self.error_messages['big_image'])
            # Since we're about to use the file again we have to reset the
            # file object if possible.
            if hasattr(file, 'reset'):
                file.reset()
            # verify() is the only method that can spot a corrupt PNG,
            #  but it must be called immediately after the constructor
            trial_image = Image.open(file)
            trial_image.verify()
        except ImportError:
            # Under PyPy, it is possible to import PIL. However, the underlying
            # _imaging C module isn't available, so an ImportError will be
            # raised. Catch and re-raise.
            raise
        except Exception, e: # Python Imaging Library doesn't recognize it as an image
            string = unicode(e)
            string = string[0].capitalize() + string[1:]
            raise ValidationError(self.error_messages['invalid_image'].format(string))
        if hasattr(f, 'seek') and callable(f.seek):
            f.seek(0)
        return f


class LabeledCheckboxInput(CheckboxInput):
    def render(self, name=None, value=None, attrs=None):
        if 'id' in self.attrs:
            label_for = format_html(' for="{0}_{1}"', self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = self.attrs['label']
        checkbox = super(LabeledCheckboxInput, self).render(name, value, attrs)
        # format_html in django trunk
        #return format_html('<label{0}>{1} {2}</label>', label_for, checkbox, choice_label)
        return mark_safe('<label{0}>{1} {2}</label>'.format(label_for, checkbox, choice_label))


def create_filter_widget(widget):

    class _FilterWidget(MultiWidget):
        def __init__(self, attrs={}):
            _widgets = (
                widget(attrs=attrs),
                RadioSelect(attrs={'onclick': 'hideRadio(this);'}, choices=(('__lt', 'less'), ('__gt', 'more'))),
                LabeledCheckboxInput(attrs={'label': 'equal'}),
            )
            super(_FilterWidget, self).__init__(_widgets, attrs)

        def decompress(self, value):
            return [getattr(value, 'value', None),
                    getattr(value, 'relation', None),
                    getattr(value, 'equal', None)]

        def value_from_datadict(self, data, files, name):
            value = [None, None, None]
            for d in filter(lambda x: x.startswith(name), data):
                try:
                    index = int(d[len(name)+1:])
                except:
                    continue
                value[index] = data[d]
            return value

    return _FilterWidget


FilterWidget = create_filter_widget(TextInput);


class FilterIntegerField(IntegerField):
    def clean(self, value):
        ret = [super(FilterIntegerField, self).clean(value[0]), value[1], value[2]]
        if ret[0]:
            return ret
        return None


class FilterUnknownDateField(UnknownDateField):
    widget = create_filter_widget(CalendarWidget)

    def clean(self, value):
        ret = [super(FilterUnknownDateField, self).clean(value[0]), value[1], value[2]]
        if ret[0]:
            return ret
        return None
