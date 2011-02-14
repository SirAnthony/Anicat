
from time import time, strftime, gmtime 
from anime.models import *

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
        self.cursor =self.__db.cursor(cursorclass = self.MySQLdb.cursors.DictCursor)

    
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

def moveAnumeItems():
    sql = Sql(db='tempcat', user='catman', passwd='catpass')
    res = sql.executeQuery('SELECT * FROM `catalog` ORDER BY id')
    for element in res:
        record = AnimeItem(id=element['id'], title=element['name'], genre=getGenreId(element['genre'].split(',')), releaseType=getTypeId(element['type']), episodesCount=element['numberofep'], duration=element['duration'], releasedAt=timedecode(element['translation']), endedAt=timedecode(element['enddate']), air=bool(element['air']))
        record.save()

        
        
    