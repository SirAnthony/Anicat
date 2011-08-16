import datetime
import time
from anime.models import AnimeItem, AnimeName, DATE_FORMATS
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.forms import CharField, TextInput, DateField, ImageField

#dirty but works
INPUT_FORMATS = (
    '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y',
    '%b %d %Y', '%b %d, %Y',
    '%d %b %Y', '%d %b, %Y',
    '%B %d %Y', '%B %d, %Y',
    '%d %B %Y', '%d %B, %Y',
)

class TextToAnimeItemField(CharField):
    def to_python(self, value):
        if not value:
            return None
        try:
            ivalue = int(value)
            value = AnimeItem.objects.get(id=ivalue)
        except:
            try:
                value = AnimeItem.objects.get(title=value)
            except AnimeItem.DoesNotExist, e:
                raise ValidationError(e)
            except AnimeItem.MultipleObjectsReturned, e:
                raise ValidationError('Too many items with such title, try to use id instead title.')
        return value

class TextToAnimeNameField(CharField):
    def to_python(self, value):
        try:
            value = value.strip()
            if not value:
                raise ValueError
        except:
            return None
        if not self._animeobject:
            raise ValidationError('AnimeItem not set.')
        try:
            value, create = AnimeName.objects.get_or_create(anime=self._animeobject, title=value)
        except Exception, e:
            raise ValidationError(e)
        return value



class CalendarWidget(TextInput):
    class Media:
        js = ("calendar.js", "DateTimeShortcuts.js")

    def __init__(self, attrs={}):
        self._known = 0
        super(CalendarWidget, self).__init__(attrs={'class': 'vDateField', 'size': '10'})

    def render(self, name, value, attrs=None):
        if isinstance(value, datetime.date):
            try:
                value = value.strftime(DATE_FORMATS[self._known])
            except:
                value = 'Bad value'
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
        if value in EMPTY_VALUES:
            return None
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
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
                raise ValueError('Only PNG, JPEG and GIF formats are accepted.')
            if max(trial_image.size) >= 800:
                raise ValueError('Image too big.')
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
            raise ValidationError(self.error_messages['invalid_image'] + ' ' + str(e))
        if hasattr(f, 'seek') and callable(f.seek):
            f.seek(0)
        return f
