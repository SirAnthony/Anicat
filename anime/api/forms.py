
from anime.api.fields import guess_type, guess_by_widget
from anime.api.types import WidgetFieldType


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
