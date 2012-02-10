
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from anime.edit.default import EditError, EditableDefault
from anime.models import AnimeItem, AnimeLink



class EditableAnimeBased(EditableDefault):

    def setObject(self):
        try:
            self.obj = AnimeItem.objects.get(id=self.item_id)
        except AnimeItem.DoesNotExist:
            raise EditError(_('Bad id passed.'))
        self.retid = self.item_id


class Name(EditableAnimeBased):
    extra_error_messages = {
        'not_exists': _('{0} does not exists.'),
        'no_names': _('Cannot delete all names. One name must be left.'),
    }

    def save(self, form, obj):
        if not obj or not obj.id:
            raise ValueError(self.error_messages['not_exists'].format(type(obj).__name__))
        names = obj.animenames.all()
        cleaned = form.cleaned_data.values()
        newNames = filter(lambda x: x and x not in names, cleaned)
        oldNames = filter(lambda x: x and x not in cleaned, names)
        if not newNames and len(oldNames) == len(names):
            raise Exception(self.error_messages['no_names'])
        for name in oldNames:
            try:
                newname = newNames.pop()
            except IndexError:
                name.delete()
                if obj.title == name.title:
                    newname = obj.animenames.all()[0]
                    obj.title = newname.title
                    #Does not check again
                    super(AnimeItem, obj).save()
            else:
                if obj.title == name.title:
                    obj.title = newname.title
                    #Does not check again
                    super(AnimeItem, obj).save()
                name.title = newname.title
                name.save()
        for name in newNames:
            name.save()


class Links(EditableAnimeBased):

    def save(self, form, obj):
        if not obj or not obj.id:
            raise ValueError('%s does not exists.' % type(obj).__name__)
        links = list(obj.links.all())
        cleaned = form.cleaned_data
        cleanlinks = [0] * (len(form.cleaned_data) / 2)
        cleantypes = [0] * (len(form.cleaned_data) / 2)
        oldLinks = []
        for name, value in cleaned.items():
            s = name.rsplit(None, 1)[-1]
            if name.find('type') >= 0:
                cleantypes[int(s)] = int(value)
            else:
                cleanlinks[int(s)] = value
        for link in links[:]:
            if link.link in cleanlinks:
                i = cleanlinks.index(link.link)
                if cleantypes[i] and link.linkType != cleantypes[i]:
                    link.linkType = cleantypes[i]
                else:
                    links.remove(link)
                cleanlinks.pop(i)
                cleantypes.pop(i)
            else:
                oldLinks.append(links.pop(links.index(link)))
        # Now in links only modified links,
        # in cleanlinks - links that must be added to db,
        # in oldlinks - links that must be removed
        for link in cleanlinks[:]:
            i = cleanlinks.index(link)
            if not link:
                cleanlinks.pop(i)
                cleantypes.pop(i)
                continue
            if len(oldLinks):
                l = oldLinks.pop()
                l.link = cleanlinks.pop(i)
                l.linkType = cleantypes.pop(i)
                links.append(l)
            else:
                links.append(AnimeLink(anime=obj, link=cleanlinks.pop(i), linkType=cleantypes.pop(i)))
        for link in oldLinks:
            link.delete()
        for l in links:
            try:
                l.save()
            except IntegrityError:
                pass
