# -*- coding: utf-8 -*-
from anime.api.fields import guess_type, guess_by_widget
from anime.api.types import (Noneable, WidgetFieldType)

def from_form(form):
    if isinstance(form, basestring):
        (path, name) = form.rsplit('.', 1)
        form = getattr(__import__(path, globals(), {}, [name]), name)
    form = form()
    fields = {}
    for name, value in form.fields.items():
        val = guess_type(value)
        if val == WidgetFieldType:
            fields.update(guess_by_widget(name, value))
        else:
            fields[name] = val
    return fields


def from_view(view):
    if isinstance(view, basestring):
        (path, name) = view.rsplit('.', 1)
        view = getattr(__import__(path, globals(), {}, [name]), name)
    fields = {}
    for name, default, error in view.parameters:
        desc = view.parameters_api.get(name)
        t = desc[0] if desc else type(default)
        if name not in view.required_parameters:
            t = Noneable(t, desc[1] if desc else default)
        fields[name] = t
    return fields