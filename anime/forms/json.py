# -*- coding: utf-8 -*-
import datetime

from anime.models import DATE_FORMATS
from anime.utils.misc import is_iterator

from django import forms
from django.forms import formsets

from django.utils.encoding import smart_unicode, force_unicode
from django.utils.functional import Promise


def prepare_data(data, depth=None):

    #Not works with 0
    depth = depth or 7

    if depth <= 0:
        return smart_unicode(data)

    if isinstance(data, basestring):
        return smart_unicode(data)

    elif isinstance(data, (bool, int, long, float, complex)):
        return data

    elif data is None:
        return data

    elif isinstance(data, datetime.datetime) or \
         isinstance(data, datetime.date):
        return data.strftime(DATE_FORMATS[0])

    elif isinstance(data, Promise):
        return force_unicode(data)

    elif isinstance(data, dict):
        return dict((key, prepare_data(value, depth - 1))
                            for key, value in data.iteritems())

    elif is_iterator(data):
        return [prepare_data(value, depth - 1) for value in data]

    return smart_unicode(data)


class FormSerializer(object):

    _instance = None

    def __new__(cls, form):
        if not cls._instance:
            cls._instance = super(FormSerializer, cls).__new__(cls)
        return cls._instance.serialize(form)

    def get_field_tag(self, field):
        types = {
            'selectmultiple': 'select',
            'select': 'select',
            'textarea': 'textarea',
        }
        ftype = self.get_field_type(field)
        return types[ftype] if ftype in types else 'input'

    def get_field_type(self, field):
        widget = field.widget

        if isinstance(widget, forms.SelectMultiple):
            return 'selectmultiple'
        if isinstance(widget, forms.RadioSelect):
            return 'radio'
        if isinstance(widget, forms.Select):
            return 'select'
        elif isinstance(widget, forms.CheckboxInput):
            return 'checkbox'
        elif isinstance(widget, forms.Textarea):
            return 'textarea'
        elif isinstance(widget, forms.HiddenInput):
            return 'hidden'
        return 'text'

    def field_to_dict(self, bound_field):
        field_dict = {}
        field = bound_field.field
        field_tag = self.get_field_tag(field)
        field_type = self.get_field_type(field)

        for attr_name in ['required', 'label', 'choices']:
            attr = getattr(field, attr_name, None)
            if attr is not None:
                field_dict[attr_name] = attr

        if 'choices' in field_dict:
            #TODO: move it to form generation.
            if type(field_dict['choices']) is list and \
               field_dict['choices'][0][1] == '---------':
                del field_dict['choices'][:1]
            #FIXME: no additional tests
            try:
                for elem in field_dict['choices']:
                    if int(elem[0]) != int(elem[1]):
                        raise ValueError
                if field_dict['choices'][0][0]:
                    s = field_dict['choices'][0][0]
                else:
                    s = field_dict['choices'][1][0]
                field_dict['choices'] = 'range(%s, %s)' % (
                    s, field_dict['choices'][-1][0])
            except (TypeError, ValueError):
                pass

        field_dict['id'] = bound_field.auto_id
        field_dict['name'] = bound_field.html_name
        field_dict['value'] = bound_field.value()

        if bound_field.help_text:
            field_dict['title'] = bound_field.help_text

        if field_tag == 'input':
            field_dict['type'] = field_type
        elif field_tag == 'select':
            if field_type == 'selectmultiple':
                field_dict['multiple'] = 'multiple'

        for name, attr in field.widget.attrs.items():
            if name == 'class':
                name = 'className'
            field_dict[name] = attr

        try:
            field_dict['className'] += bound_field.css_classes()
        except:
            pass

        for key in field_dict.keys():
            if not field_dict[key]:
                del field_dict[key]

        return {field_tag: field_dict}

    def form_to_data(self, form_instance):
        fields, hidden_fields = [], []
        top_errors = form_instance.non_field_errors()
        output = []

        for name in form_instance.fields.iterkeys():
            field = form_instance[name]
            field = self.field_to_dict(field)
            if 'type' in field and field['type'] == 'hidden':
                if form_instance.errors:
                    top_errors.extend([
                        u'(Hidden field %s) %s' % (
                            name, force_unicode(e)
                        ) for e in form_instance.errors
                    ])
                hidden_fields.append(field)
            else:
                if form_instance.errors:
                    field['errors'] = form_instance.errors
                fields.append(field)

        if top_errors:
            output.extend(top_errors)
        output.extend(fields)
        if hidden_fields: # Insert any hidden fields in the last row.
            output.extend(hidden_fields)

        return prepare_data(output)

    def formset_to_dict(self, formset):
        formset_data = []
        formset_data.append(self.form_to_data(formset.management_form))
        for form in formset.forms:
            formset_data.append(self.form_to_data(form))
        return formset_data

    def serialize(self, form_instance):
        if isinstance(form_instance, forms.Form) or  \
           isinstance(form_instance, forms.ModelForm):
            return self.form_to_data(form_instance)
        if isinstance(form_instance, formsets.BaseFormSet):
            return self.formset_to_dict(form_instance)
        raise TypeError('Form instance has bad type.')
