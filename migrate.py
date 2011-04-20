# -*- coding: utf-8 -*-

from time import time, strftime, gmtime 
from anime.models import *
import re

def getGenreId(genres):
    genrelist = []
    for genre in genres:
        try:
            a = [i[0] for i in ANIME_GENRE if i[-1] == genre][0]
            genrelist.append(a)
        except Exception:
            raise NameError, genre
    return genrelist

def getTypeId(tp):
    try:
        itp = [i[0] for i in ANIME_TYPES if i[-1] == tp][0]
    except Exception:
        raise NameError, tp
    return itp

def timedecode(tstr):
    try: tstr = int(tstr)
    except Exception:
        return tstr
    return strftime('%Y-%m-%d', gmtime(tstr))

def encd(string):
    "Convert codes into characters"
    string = string.strip()
    string = re.sub(r"&quot;", r"\"", string)
    string = re.sub(r"&#37;", r"%", string)
    string = re.sub(r"&#39;", r"'", string)
    string = re.sub(r"&#92;", r"\\", string)
    string = re.sub(r"&#47;", r"/", string)
    string = re.sub(r"&#43;", r"+", string)
    string = re.sub(r"&#61;", r"=", string)
    string = re.sub(r"&lt;", r"<", string)
    string = re.sub(r"&rt;", r">", string)
    string = re.sub(r"&#171;", r"«", string)
    string = re.sub(r"&#176;", r"°", string)
    string = re.sub(r"&#187;", r"»", string)
    string = re.sub(r"&#189;", r"½", string)
    string = re.sub(r"&#212;", r"Ô", string)
    string = re.sub(r"&#215;", r"×", string)
    string = re.sub(r"&#216;", r"Ø", string)
    string = re.sub(r"&#227;", r"ã", string)
    string = re.sub(r"&#232;", r"è", string)
    string = re.sub(r"&#233;", r"é", string)
    string = re.sub(r"&#244;", r"ô", string)
    string = re.sub(r"&#251;", r"û", string)
    string = re.sub(r"&#8211;", r"–", string)
    string = re.sub(r"&#8212;", r"—", string)
    string = re.sub(r"&#8217;", r"’", string)
    string = re.sub(r"&#8220;", r"“", string)
    string = re.sub(r"&#8221;", r"”", string)
    string = re.sub(r"&#8224;", r"†", string)
    string = re.sub(r"&#8230;", r"…", string)
    string = re.sub(r"&#35;", r"#", string)
    string = re.sub(r"&amp;", r"&", string)
    return str(string)

class Sql:
    "mysql module"
    import MySQLdb

    def __init__(self, **vars):
        if not vars.has_key("db"):
            print "Database not specified"
        elif not vars.has_key("user"):
            print "Database user name not specified"
        elif not vars.has_key("passwd"):
            print "Database user password not specified"
        else:
            self.connect(vars["db"], vars["user"], vars["passwd"])

    def connect(self, db, user, passwd):
        self.__db = self.MySQLdb.connect(db=db, user=user, passwd=passwd)
        self.__db.set_character_set('utf8')
        self.cursor =self.__db.cursor(cursorclass = self.MySQLdb.cursors.DictCursor)
        self.cursor.execute('SET NAMES utf8;')
        self.cursor.execute('SET CHARACTER SET utf8;')
        self.cursor.execute('SET character_set_connection=utf8;')

    def executeQuery(self, query, action="select"):
        ##Add more debugging information
        c = self.cursor
        try:
            c.execute(query)
        except Exception, e:
            return str(e)
        self.__db.commit()
        if action == "select":
            fetch = c.fetchall()
            return fetch
        if action == "insert":
            return c.lastrowid

def moveAll():
    moveGenres()
    moveAnumeItems()
    moveAnimeName()
    moveBundles()
    moveCredit()
    movePeople()
    movePeopleBundles()
    moveOrganisation()    
    moveOrganisationBundles()
    moveUserStatus()

def moveGenres():
    sql = Sql(db='tempcat', user='catman', passwd='catpass')
    genres = sql.executeQuery('DESC `catalog` genre')[0]['Type'].decode('utf-8')[5:-2].split("','")
    for genre in genres:
        try:
            ng = Genre(name=genre)
            ng.save()
        except Exception, e:
            print genre
            raise Exception, e

def moveAnumeItems():
    sql = Sql(db='tempcat', user='catman', passwd='catpass')
    res = sql.executeQuery('SELECT * FROM `catalog` ORDER BY id')
    for element in res:
        try:
            if element['enddate'] == 0:
                element['enddate'] = None
            record = AnimeItem(id=element['id'], title=unicode(encd(element['name']), 'utf-8'),
                releaseType=getTypeId(element['type']), episodesCount=element['numberofep'],
                duration=element['duration'], releasedAt=timedecode(element['translation']),
                endedAt=timedecode(element['enddate']), air=bool(element['air'])
            )
            record.save()
            for genre in element['genre'].split(','):
                g = Genre.objects.get(name=genre)
                record.genre.add(g)
        except Exception, e:
            print element
            raise Exception, e

def moveBundles():
    sql = Sql(db='tempcat', user='catman', passwd='catpass')
    res = sql.executeQuery('SELECT * FROM `bundlebun` ORDER BY id')
    for element in res:
        try:
            main = AnimeItem.objects.get(id=element['mainid'])
            bound = AnimeItem.objects.get(id=element['elemid'])
            if main != bound:
                AnimeBundle.tie(main, bound)
        except Exception, e:
            print element
            raise Exception, e

def moveAnimeName():
    sql = Sql(db='tempcat', user='catman', passwd='catpass')
    res = sql.executeQuery('SELECT * FROM `namebun` ORDER BY id')
    for element in res:
        item = AnimeItem.objects.get(id=element['mainid'])
        if not item:
            raise NameError, element['mainid']
        try:
            record = AnimeName(title=unicode(encd(element['name']), 'utf-8'), anime=item)
            record.save()
        except Exception, e:
            print element
            raise Exception, e

def moveCredit():
    sql = Sql(db='tempcat', user='catman', passwd='catpass')
    res = sql.executeQuery('SELECT * FROM `credit` ORDER BY id')
    for element in res:
        try:
            record = Credit(id=element['id'], title=unicode(encd(element['name']), 'utf-8'))
            record.save()
        except Exception, e:
            print element
            raise Exception, e

def movePeople():
    sql = Sql(db='tempcat', user='catman', passwd='catpass')
    res = sql.executeQuery('SELECT * FROM `people` ORDER BY id')
    for element in res:
        try:
            record = People(id=element['id'], name=unicode(encd(element['name']), 'utf-8'))
            record.save()
        except Exception, e:
            print element
            raise Exception, e

def movePeopleBundles():
    sql = Sql(db='tempcat', user='catman', passwd='catpass')
    res = sql.executeQuery('SELECT * FROM `peoplebun` ORDER BY id')
    for element in res:
        try:
            anime = AnimeItem.objects.get(id=element['mainid'])
            man = People.objects.get(id=element['elemid'])
            job = Credit.objects.get(id=element['job'])
            record = PeopleBundle(anime=anime, person=man, job=job,
                        role=unicode(encd(element['role']), 'utf-8'),
                        comment=unicode(encd(element['comm']), 'utf-8'))
            record.save()
        except Exception, e:
            print element
            raise Exception, e

def moveOrganisation():
    sql = Sql(db='tempcat', user='catman', passwd='catpass')
    res = sql.executeQuery('SELECT * FROM `organisation` ORDER BY id')
    for element in res:
        try: 
            record = Organisation(id=element['id'], name=unicode(encd(element['name']), 'utf-8'))
            record.save()
        except Exception, e:
            print element
            raise Exception, e

def moveOrganisationBundles():
    sql = Sql(db='tempcat', user='catman', passwd='catpass')
    res = sql.executeQuery('SELECT * FROM `organisationbun` ORDER BY id')
    for element in res:
        try:
            anime = AnimeItem.objects.get(id=element['mainid'])
            corp = Organisation.objects.get(id=element['elemid'])
            job = Credit.objects.get(id=element['job'])
            record = OrganisationBundle(anime=anime, organisation=corp, job=job,
                        role=unicode(encd(element['role']), 'utf-8'),
                        comment=unicode(encd(element['comm']), 'utf-8'))
            record.save()
        except Exception, e:
            print element
            raise Exception, e

def moveUserStatus():
    sql = Sql(db='tempcat', user='catman', passwd='catpass')
    res = sql.executeQuery('SELECT * FROM `statsbun` ORDER BY id')
    for element in res:
        try:
            anime = AnimeItem.objects.get(id=element['mainid'])
            user = User.objects.get(id=element['elemid'])
            record = UserStatusBundle(anime=anime, user=user, status=element['job'],
                        count=element['comm'], changed=element['changed'])
            record.save()
        except Exception, e:
            print element
            raise Exception, e