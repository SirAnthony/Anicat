import gzip
import os
import xml.dom.minidom as xmlp
from anime.models import AnimeItem, AnimeName, UserStatusBundle
from django.conf import settings
import re

MAL_STATUS = [
    (0, ''),
    (1, u'watching'),
    (2, u'completed'),
    (3, u'onhold'),
    (4, u'dropped'),
    (5, ''),
    (6, u'plantowatch')
    ]

MAL_STATUS_CONVERT_LIST = [
    0, #none
    2, #watching => now
    3, #completed => ok
    2, #onhold => now
    4, #dropped => dropped
    0, #none
    1, #plantowatch => want
]

MAL_TYPE_CONVERT_LIST = [
    (0, u'TV'),
    (1, u'Movie'),
    (2, u'OVA'),
    (3, u'Special'),
    (4, u'SMovie'),
    (5, u'ONA'),
    (6, u'Music')
]

def getData(file):
    f = gzip.GzipFile(fileobj=file)
    file_content = f.read()
    f.close()
    return file_content

def process(user, filename, rewrite=True):
    file = open(filename, 'rb+')
    doc = xmlp.parseString(getData(file))
    file.close()
    os.remove(filename)
    animelist = doc.getElementsByTagName('myanimelist')[0].getElementsByTagName('anime')
    result = {'withMal': [], 'withNames': [], 'notFound': []}
    for anime in animelist:
        state, anime = searchAnime(anime)
        l = None
        if state > 0:
            l = result['withMal']
        elif state < 0:
            l = result['withNames']
        else:
            l = result['notFound']
        l.append(anime)
    addInBase(user, result, rewrite)
    addToCache(user, result)

def searchAnime(obj):
    anime = {}
    state = 0
    for node in obj.childNodes:
        if node.nodeType == 1:
            if not node.firstChild:
                continue
            val = node.firstChild.nodeValue
            if node.nodeName == 'my_status':
                try:
                    val = MAL_STATUS_CONVERT_LIST[val]
                except TypeError:
                    val = re.sub('[\s-]', '', val).lower()
                    val = MAL_STATUS_CONVERT_LIST[[i[0] for i in MAL_STATUS if i[-1] == val][0]]
            if node.nodeName == 'series_type':
                val = val.lower()
                val = [i[0] for i in MAL_TYPE_CONVERT_LIST if i[-1].lower() == val][0]
            anime[node.nodeName] = val
    if anime['my_status'] not in [2, 4]:
        anime['my_watched_episodes'] = None
    return (state, anime)

def addInBase(user, animeList, rewrite=True):
    for key in ['withMal', 'withNames']:
        for anime in animeList[key]:
            try:
                ub = UserStatusBundle.objects.get(anime=anime['object'], user=user)
                if rewrite and not anime['my_status'] == ub.status:
                    ub.status = anime['my_status']
                    ub.count = anime['my_watched_episodes']
                    #ub.save()
            except UserStatusBundle.DoesNotExist:
                ub = UserStatusBundle(anime=anime['object'], user=user, 
                                        status=anime['my_status'], count=anime['my_watched_episodes'])
                #ub.save()

def addToCache(user, animeList):
    pass
    

def passFile(file, user, rewrite=True):
    filename = os.path.join(settings.MEDIA_ROOT, file.name + str(file.size))
    if os.path.exists(filename):
        return False, 'File already loading.'
    try:
        fileobj = open(filename, 'wb+')
        for chunk in file.chunks():
            fileobj.write(chunk)
        fileobj.close()
    except Exception, e:
        return False, e
    
    process(user, filename, rewrite)
    return True, None

