import os
import re
import gzip
import threading
import xml.dom.minidom as xmlp
from django.core.cache import cache
from django.conf import settings
from anime.models import AnimeLinks, AnimeName, UserStatusBundle
from datetime import datetime

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
    try:
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
    except Exception, e:
        result = {'error': e}
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
    try:
        anime['object'] = AnimeLinks.objects.get(mal=int(anime['series_animedb_id']))
        state = 1
    except AnimeLinks.DoesNotExist:
        matchedTitles = []
        unmatchedTitles = []
        names = AnimeName.objects.filter(title__iexact=anime['series_title'])
        if not anime['series_title'].find('The '):
            names = list(names)
            names.extend(AnimeName.objects.filter(title__iexact=re.sub('^The\s+', '', anime['series_title'])))
        for name in names:
            title = name.anime
            if title not in matchedTitles and title not in unmatchedTitles:
                if title.releaseType == anime['series_type'] or ( 
                    anime['series_type'] == 1 and title.releaseType == 4):
                    matchedTitles.append(title)
                else:
                    unmatchedTitles.append(title)
        if len(matchedTitles) > 0:
            anime['object'] = matchedTitles[:1][0]
            unmatchedTitles = matchedTitles[1:] #Report about
            state = -1
        else: #Nothing found but we try to found similar
            names = AnimeName.objects.filter(title__icontains=anime['series_title'])
            for name in names:
                title = name.anime
                if title not in unmatchedTitles:
                    unmatchedTitles.append(title)
        anime['unmatched'] = map(lambda x: {'name': x.title, 'id': x.id}, unmatchedTitles) #Report about
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
            anime['object'] = {'name': anime['object'].title, 'id': anime['object'].id}

def addToCache(user, animeList):
    lastload = {'list': animeList, 'date': datetime.now()}
    cache.set('MalList:%s' % user.id, lastload)

def passFile(file, user, rewrite=True):
    cache.set('MalList:%s' % user.id, {'list': {'updated': 1}, 'date': datetime.now()})
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
    t = threading.Thread(target=process, args=[user, filename, rewrite], kwargs={})
    t.setDaemon(True)
    t.start()
    return True, None

