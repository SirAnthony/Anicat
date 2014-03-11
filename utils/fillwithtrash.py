#!/usr/bin/env python
from random import choice, randint
from anime.models import Genre, AnimeItem, AnimeName, AnimeBundle, AnimeLink, UserStatusBundle, ANIME_TYPES, USER_STATUS
from datetime import date
from django.contrib.auth.models import User

charlist = [u'bcdfgklmnprstxz', u'aejioqvuwy']
animecount = 2

def randname():
    return ' '.join(map(''.join, map(apply,
        [lambda: map(choice, (charlist * randint(1, 4)))] * randint(1, 3))))


def CreateGenres():
    for i in range(0, 30):
        g = Genre(name=randname())
        g.save()


def CreateRecords():
    startdate = date(1960, 1, 1).toordinal()
    enddate = date(2020, 1, 1).toordinal()
    genres = Genre.objects.all()
    genrecount = len(genres)

    for i in range(0, animecount):
        a = AnimeItem(title=randname(),
                  releaseType=ANIME_TYPES[randint(0, 6)][0],
                  episodesCount=randint(1, 400),
                  duration=randint(1, 220),
                  releasedAt=date.fromordinal(randint(startdate, enddate)),
                  endedAt=date.fromordinal(randint(startdate, enddate)))
        a.save()
        for l in range(0, randint(1, 3)):
            AnimeLink(anime=a, link="http://example.org/{0}".format(l), linkType=l).save()
        for g in range(0, 4):
            a.genre.add(genres[randint(0, genrecount-1)])
        for h in range(3, 6):
            n = AnimeName(title=randname(), anime=a)
            try:
                n.save()
            except:
                pass
    #make bundles
    acount = AnimeItem.objects.count()
    for i in range(0, animecount/2):
        one = AnimeItem.objects.get(id=randint(1, acount))
        two = AnimeItem.objects.get(id=randint(1, acount))
        while two == one:
            two = AnimeItem.objects.get(id=randint(1, animecount))
        AnimeBundle.tie(one, two)


def UsersStatus():
    for user in User.objects.all():
        for c in range(1, randint(1, animecount)):
            UserStatusBundle(anime=AnimeItem.objects.get(id=c), state=randint(2, len(USER_STATUS))-1, user=user).save()


def FillWithTrash():
    CreateGenres()
    CreateRecords()
    UsersStatus()
