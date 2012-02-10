
from django.core.exceptions import ValidationError
from django.forms import ModelForm, ChoiceField, ModelChoiceField
from django.forms.forms import BoundField
from django.forms.widgets import Select, SelectMultiple
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.translation import ugettext_lazy as _
from anime.forms.fields import  UnknownDateField
from anime.models import AnimeItem, AnimeName, UserStatusBundle

class ReadOnlyModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.__readonly__ = False
        super(ReadOnlyModelForm, self).__init__(*args, **kwargs)

    def readonly(self):
        self.__readonly__ = True

    def writeable(self):
        self.__readonly__ = False

    def clean(self):
        if hasattr(self, '__readonly__') and self.__readonly__:
            raise ValidationError(_('This form is read-only for you.'))
        return super(ReadOnlyModelForm, self).clean()


class ErrorModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        #FUUUU
        kwargs.pop('user', None)
        super(ErrorModelForm, self).__init__(*args, **kwargs)

    def addError(self, text):
        self.errors['__all__'] = self.error_class([text])

    class Meta:
        pass


class AnimeForm(ErrorModelForm):
    releasedAt = UnknownDateField(label='Released')
    endedAt = UnknownDateField(label='Ended', required=False)

    def __init__(self, *args, **kwargs):
        super(AnimeForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            for field in ['released', 'ended']:
                if field + 'At' in self.fields:
                    self.fields[field + 'At'].widget._known = getattr(self.instance, field + 'Known')

    def _clean_form(self):
        super(AnimeForm, self)._clean_form()
        for name, field in self.fields.items():
            try:
                self.cleaned_data.update(getattr(field, 'cleaned_data'))
            except AttributeError:
                pass
        if not self.instance.id:
            title = self.cleaned_data.get('title')
            release = self.cleaned_data.get('releasedAt')
            names = AnimeName.objects.filter(title=title)
            for name in names:
                if name.anime.releasedAt.date() == release:
                    self.addError(
                        _('Anime record already exists: "%s" (%s).' % (
                            name.anime.title, name.anime.id)))
                    return


    class Meta():
        model = AnimeItem
        exclude = ('bundle', 'locked', 'releasedKnown', 'endedKnown')


class UserStatusForm(ErrorModelForm):

    def __init__(self, *args, **kwargs):
        super(UserStatusForm, self).__init__(*args, **kwargs)
        if self.instance.state != 3:
            del self.fields['rating']
        if self.instance.state not in (2, 4) or self.instance.anime.episodesCount == 1:
            del self.fields['count']
        else:
            self.fields['count'] = ChoiceField(choices=(
                (i, i) for i in range(1, self.instance.anime.episodesCount+1)))

    class Meta:
        model = UserStatusBundle
        exclude = ('anime', 'user')
