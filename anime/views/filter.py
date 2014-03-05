# -*- coding: utf-8 -*-
from hashlib import sha1


class AnimeListFilter(object):
    def __init__(self, data, user):
        self.user = user
        if type(data) == dict:
            self.data = data
        else:
            self.data = {}

    def get_cachestring(self, cachestr):
        return sha1(cachestr + str(self.data)).hexdigest()

    def get_queryset(self, queryset):
        for key, value in self.data.items():
            field = getattr(self, key, None)
            if callable(field):
                queryset = field(queryset, value)
            else:
                filtercase = key + self.get_relation(*value[1:])
                queryset = queryset.filter(**{filtercase: value[0]})
        return queryset

    def get_relation(self, relation, equal):
        if relation in ['__lt', '__gt']:
            return relation + 'e' * bool(equal)
        elif equal:
            return '__exact'
        return ''

    def releaseType(self, queryset, value):
        return queryset.filter(releaseType__in=value)

    def genre(self, queryset, value):
        return queryset.filter(genre__in=value)

    def state(self, queryset, value):
        return queryset.filter(statusbundles__user=self.user,
                               statusbundles__state__in=value)
