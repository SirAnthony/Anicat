
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from anime.edit.objects import EditableDefault, EditError
from anime.edit.animebased import EditableAnimeBased



class Request(EditableDefault):

    def last(self):
        cache.delete('requests')


class Animerequest(Request):
    pass


class Feedback(Request):
    pass


class Image(Request, EditableAnimeBased):

    def save(self, form, obj):
        obj = self.obj = form.instance
        self.retid = obj.id
        super(Image, self).save(form, obj)



