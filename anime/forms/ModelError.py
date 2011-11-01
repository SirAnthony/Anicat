
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.forms.forms import BoundField
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.translation import ugettext_lazy as _
from anime.forms.fields import  UnknownDateField
from anime.models import AnimeItem, UserStatusBundle

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
            html_class_attr = None
            bf = BoundField(self, field, name)
            bf_errors = self.error_class([conditional_escape(error) for error in bf.errors])
            tag = 'input'
            children = []
            fieldobj = {
                'id': bf.auto_id,
                'name': force_unicode(bf.name),
                'value': force_unicode(bf.value()),
            }
            if bf.is_hidden:
                if bf_errors:
                    top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
                fieldobj['type'] = 'hidden'
                fieldobj = {tag: fileobj}
            else:
                if hasattr(field.widget, 'choices'):
                    tag = 'select'
                    for c in field.widget.choices:
                        prop = {'value': force_unicode(c[0]), 'innerText': force_unicode(c[1])}
                        children.append({'option': prop})
                else:
                    try:
                        fieldobj['type'] = field.widget.input_type
                    except AttributeError:
                        pass
                try:
                    html_class_attr = bf.css_classes().split()
                except:
                    pass

                if field.help_text:
                    help_text = force_unicode(field.help_text)
                else:
                    help_text = None

                o = {tag: fieldobj}
                if bf_errors:
                    o['errors'] = bf_errors
                if help_text:
                    o['help_text'] = help_text
                if html_class_attr:
                    o['html_class_attr'] = html_class_attr
                output.append(o)
                if children:
                    output.append(children)

        if top_errors:
            output.extend(0, top_errors)
        if hidden_fields: # Insert any hidden fields in the last row.
            for field in hidden_fields:
                output.append(field)
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

    class Meta():
        model = AnimeItem
        exclude = ('bundle', 'locked', 'releasedKnown', 'endedKnown')


class UserStatusForm(ErrorModelForm):
    class Meta:
        model = UserStatusBundle
        exclude = ('anime', 'user')

