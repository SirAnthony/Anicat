
from anime.api.fields import guess_type


def from_form(form):
    if isinstance(form, basestring):
        (path, name) = form.rsplit('.', 1)
        form = getattr(__import__(path, globals(), {}, [name]), name)
    form = form()
    fields = {}
    for name, value in form.fields.items():
        fields[name] = guess_type(value)
    return fields
