#!/usr/bin/env python
from random import choice, randint
from anime.models import Genre, AnimeItem, AnimeName, AnimeBundle, ANIME_TYPES
from datetime import date

charlist = [u'bcdfgklmnprstxz', u'aejioqvuwy']


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

    for i in range(0, 10000):
        a = AnimeItem(title=randname(),
                  releaseType=ANIME_TYPES[randint(0, 6)][0],
                  episodesCount=randint(1, 400),
                  duration=randint(1, 220),
                  releasedAt=date.fromordinal(randint(startdate, enddate)),
                  endedAt=date.fromordinal(randint(startdate, enddate)))
        a.save()
        for g in range(0, 4):
            a.genre.add(genres[randint(0, genrecount - 1)])
        for h in range(3, 6):
            n = AnimeName(title=randname(), anime=a)
            try:
                n.save()
            except:
                pass
    #make bundles
    acount = AnimeItem.objects.count()
    for i in range(0, 5000):
        one = AnimeItem.objects.get(id=randint(0, acount))
        two = AnimeItem.objects.get(id=randint(0, acount))
        while two == one:
            two = AnimeItem.objects.get(id=randint(0, 10000))
        AnimeBundle.tie(one, two)


def FillWithTrash():
    CreateGenres()
    CreateRecords()
