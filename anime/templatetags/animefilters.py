# -*- coding: utf-8 -*-
from django import template
from anime.core.user import get_username

register = template.Library()

@register.filter
def hash(h, key):
    return h[key]


@register.filter
def animeitem(h, key):
    return getattr(h, key)


@register.filter
def username(user):
    return get_username(user)


#TODO: move anywhere
HEADER_FIELDS = {
    'action_id' : '№',
    'action_type': 'action type',
    'action_date': 'date',
    'action_user': 'user',
    'action_ip': 'IP',
    'release': 'released',
    'bundle_id': 'bundle',
    'linkType': 'link type'
}

@register.filter
def header_title(field):
    return HEADER_FIELDS.get(field, field).capitalize()
