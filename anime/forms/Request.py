import os
from hashlib import sha1

from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import Textarea, CharField
from django.utils.translation import ugettext_lazy as _

from anime.forms.ModelError import ReadOnlyModelForm, ErrorModelForm
from anime.forms.fields import CardImageField
from anime.models import AnimeItem, AnimeImageRequest

class RequestForm(ErrorModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        instance = kwargs.get('instance', None)
        super(RequestForm, self).__init__(*args, **kwargs)
        if instance and user:
            try:
                instance.user
            except:
                instance.user = user

    class Meta:
        exclude = ('user', 'anime', 'status')

class PureRequestForm(ReadOnlyModelForm, RequestForm):
    error_messages = {
        'notchangable': _('You cannot change it anymore.'),
    }

    def __init__(self, *args, **kwargs):
        user = kwargs.get('user', None)
        super(PureRequestForm, self).__init__(*args, **kwargs)
        if not user or not user.is_staff:
            self.readonly()

    def clean_status(self):
        if self.instance.requestType == 1 and self.instance.status > 0:
            if 'status' in self._get_changed_data():
                raise ValidationError(self.error_messages['notchangable'])
        return self.cleaned_data['status']

    class Meta:
        exclude = ('user', 'anime', 'text', 'requestType',)

class AnimeItemRequestForm(RequestForm):
    text = CharField(label="Request anime", widget=Textarea)
    class Meta:
        exclude = ('user', 'anime', 'requestType', 'reason', 'status')

class ImageRequestForm(RequestForm):
    error_messages = {
        'notexists': _('Record not exist.'),
        'notanime': _('{0} is not AnimeItem instance.'),
        'required': _('This field is required.'),
        'loaded': _('This file already loaded.')
    }
    text = CardImageField(max_length=150, label='File')
    def __init__(self, *args, **kwargs):
        anime = kwargs.pop('instance', None)
        if not anime or not anime.id:
            raise ValueError(unicode(self.error_messages['notexists']))
        if not isinstance(anime, AnimeItem):
            raise TypeError(self.error_messages['notanime'].format(type(anime.__class__).__name__))
        instance = AnimeImageRequest(anime=anime)
        super(ImageRequestForm, self).__init__(*args, instance=instance, **kwargs)
        self.files = kwargs.get('files', None)

    #FIXME: It will be better in clean()
    def _clean_fields(self):
        name = 'text'
        super(ImageRequestForm, self)._clean_fields()
        if name in self.errors:
            return
        image = self.files.get(name)
        try:
            fname, ext = image.name.rsplit('.', 1)
            image.name = sha1(fname.encode('utf-8')).hexdigest()
            filename = u'%s%s.%s' % (image.size, image.name, ext.lower())
            fullfilename = os.path.join(settings.MEDIA_ROOT, filename)
            if os.path.exists(fullfilename):
                raise ValidationError(self.error_messages['loaded'])
            try:
                fileobj = open(fullfilename, 'wb+')
                for chunk in image.chunks():
                    fileobj.write(chunk)
                fileobj.close()
            except Exception, e:
                raise ValidationError(e)
            self.cleaned_data[name] = filename
        except ValidationError, e:
            self._errors[name] = self.error_class(e.messages)
            if name in self.cleaned_data:
                del self.cleaned_data[name]

    class Meta:
        exclude = ('user', 'anime', 'requestType', 'reason', 'status')

class FeedbackForm(RequestForm):
    text = CharField(label=_('Please tell about your suffering'), widget=Textarea)
    class Meta:
        exclude = ('user', 'anime', 'requestType', 'reason', 'status')
