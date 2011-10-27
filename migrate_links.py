
# This script helps to migrate links from 3.0.99.8xx to 3.0.99.9xx

from anime.models import AnimeLink, AnimeLinks, LINKS_TYPES

def migrate():
    for link in AnimeLinks.objects.all():
        if link.AniDB:
            a = AnimeLink(anime=link.anime, linkType=LINKS_TYPES[1][0],
                link="http://anidb.net/a%s" % link.AniDB)
            a.save()
        if link.ANN:
            a = AnimeLink(anime=link.anime, linkType=LINKS_TYPES[2][0],
                link="http://www.animenewsnetwork.com/encyclopedia/anime.php?id=%s" % link.ANN)
            a.save()
        if link.MAL:
            a = AnimeLink(anime=link.anime, linkType=LINKS_TYPES[3][0],
                link="http://myanimelist.net/anime/%s" % link.MAL)
            a.save()
