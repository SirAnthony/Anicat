
from django.core.exceptions import ValidationError
from django.forms import ModelForm, ChoiceField
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
            raise ValidationError(_('This form is readonly for you.'))
        return super(ReadOnlyModelForm, self).clean()

class ErrorModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        #FUUUU
        kwargs.pop('user', None)
        super(ErrorModelForm, self).__init__(*args, **kwargs)

    def addError(self, text):
        self.errors['__all__'] = self.error_class([text])

    def as_json(self):
        #TODO: no checkboxes, radiobuttons or textareas
        top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
        output, hidden_fields = [], []

        for name, field in self.fields.items():
            bf = BoundField(self, field, name)
            bf_errors = self.error_class([conditional_escape(error) for error in bf.errors])
            tag = 'input'
            children = []
            fieldobj = {
                'id': bf.auto_id,
                'name': force_unicode(bf.name),
                'value': bf.value(),
            }
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
                fieldobj['type'] = 'hidden'
                if fieldobj.has_key('value'):
                    fieldobj['value'] = force_unicode(fieldobj['value'])
                hidden_fields.append({tag: fieldobj})
            else:
                if hasattr(field.widget, 'choices'):
                    tag = 'select'
                    values = []
                    if isinstance(field.widget, Select):
                        values = fieldobj.pop('value')
                        if isinstance(field.widget, SelectMultiple):
                            fieldobj['multiple'] = 'multiple'
                    for c in field.widget.choices:
                        prop = {'value': force_unicode(c[0]), 'innerText': force_unicode(c[1])}
                        if c[0] == values or (type(values) is list and c[0] in values):
                            prop['selected'] = 'selected'
                        children.append({'option': prop})
                else:
                    try:
                        fieldobj['type'] = field.widget.input_type
                    except AttributeError:
                        pass

                try:
                    fieldobj['className'] = bf.css_classes()
                except:
                    pass
                else:
                    if not fieldobj['className']:
                        del fieldobj['className']

                if field.help_text:
                    fieldobj['title'] = force_unicode(field.help_text)

                if fieldobj.has_key('value'):
                    if fieldobj['value']:
                        fieldobj['value'] = force_unicode(fieldobj['value'])
                    else:
                        del fieldobj['value']

                o = {tag: fieldobj}
                if bf_errors:
                    o['errors'] = bf_errors
                output.append(o)
                if children:
                    output.append(children)

        if top_errors:
            output.extend(0, top_errors)
        if hidden_fields: # Insert any hidden fields in the last row.
            output.extend(hidden_fields)
        return output

    class Meta:
        pass

class AnimeForm(ErrorModelForm):
    releasedAt = UnknownDateField(label='Released')
    endedAt = UnknownDateField(label='Ended', required=False)

    def __init__(self, *args, **kwargs):
        super(AnimeForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            for field in ['released', 'ended']:
                try:
                    self.fields[field + 'At'].widget._known = getattr(self.instance, field + 'Known')
                except:
                    continue

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
                (i, str(i)) for i in range(1, self.instance.anime.episodesCount+1)))

    class Meta:
        model = UserStatusBundle
        exclude = ('anime', 'user')

