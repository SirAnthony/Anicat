
from django.core import paginator
from django.core.cache import cache
from django.db.models.query import QuerySet

class Paginator(paginator.Paginator):

    def _get_name_length(self):
        return getattr(self, '_name_length', 4)
    name_length = property(_get_name_length)

    def set_order(self, order):
        if order.startswith('-'):
            self.order = order[1:]
            self.reverse = ''
        else:
            self.order = order
            self.reverse = '-'

    def set_cachekey(self, key):
        self.cachekey = key

    def get_names(self):
        names = None
        cachekey = getattr(self, 'cachekey', None)
        if getattr(self, 'names', None) is None:
            if cachekey is not None:
                names = cache.get('Pages:%s' % cachekey)
            if not names:
                names = list(self.iternames())
                if cachekey is not None:
                    cache.set('Pages:%s' % cachekey, names)
            self.names = names
        return self.names

    def iternames(self):
        length = self.name_length
        order = self.order
        qs = self.object_list
        zero = None
        if type(qs) is not QuerySet:
            raise TypeError('iternames only works with QuerySets as item list.')
        for i in range(0, self.count, self.per_page):
            if not i:
                zero = unicode(getattr(qs.only(order)[i], order)).strip()[:length]
            else:
                (second, first) = qs.only(order)[i - 1:i + 1]
                yield u'{0} - {1}'.format(zero,
                    unicode(getattr(second, order)).strip()[:length])
                zero = unicode(getattr(first, order)).strip()[:length]
        yield u'{0} - {1}'.format(zero, unicode(getattr(
            qs.order_by(self.reverse + order).only(order)[0], order
            )).strip()[:length])

