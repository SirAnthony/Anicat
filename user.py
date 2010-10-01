#User.py
import hashlib
import sessions

class User:
    
    def __init__(self, sql, cgi):
        self.sql = sql
        self.cgi = cgi
        self.session = None
        self.getUser()
    
    def checkUser(self, user, passwd):
        hash = hashlib.new('md5')
        hash.update(passwd)
        passwd = hash.hexdigest()
        user = self.sql.find('users', user, 'login', 'passwd', 'login')
        if user[1] and passwd == user[1]['passwd']: return user[1]
        return 0

    def login(self, user, passwd, long=None):
        user = self.checkUser(user, passwd)
        if user:            
            self.session = sessions.SQLSession('anicat', self.cgi, self.sql, login=True, long=long)
            self.session['userid'] = user['id']
            self.session['user'] = user['login']
            self.session['passwd'] = user['passwd']            
            if long: self.session['long'] = True
            self.session.save()
            return "logok"
        return 'logfail'

    def getUser(self):
        if not self.session:
            self.session = sessions.SQLSession('anicat', self.cgi, self.sql).get()
        if self.session:# and self.session.has_key('data'):
        	#return self.session['data']
        	return True
    
    def register(self, name, passwd, email):
        hash = hashlib.new('md5')
        hash.update(passwd)
        hpasswd = hash.hexdigest()
        res = self.sql.addUser(name, hpasswd, email)
        if res[0] != 'editok': return 'error', res[1]
        res = self.mail(email, name)
        return self.login(name, passwd), {'name': name}

    def getUsername(self, uid):	
        ret =  self.sql.find('users', uid, 'id', 'login', 'visible');
        if ret[0] == 'error':
            return ret[1]
        if ret[1] and ret[1]['visible']: ret[1]['login']
        else: return 'Anonymous'

    def getStats(self, uid=None, stat=None, rid=None):    	
    	if uid == None:
    	    if self.session != None:
    	        uid = self.session['data']['userid']
    	    else: return
        stats = self.sql.selectBundle(tbl='stats', mainid=rid, elemid=uid, job=stat)
        if stat: stats['keys'] = stats.keys()
        if rid and len(rid) == 1 and stats.has_key(long(rid[0])): stats = stats[long(rid[0])]        
        return stats

    def editStats(self, **stats):
        if not stats.has_key('elemid') or not stats.has_key('mainid'):
            return ['error', 'Bad user id, or record id.']
        ret = self.sql.editBundle('stats', **stats)
        return ret

    def getShow(self, show, uid):
        stat = self.getStats(uid, ('none', 'want', 'now', 'ok', 'droped')[show]);	
        return stat['keys']

    def getDisplay(self, uid):
        #TODO: add debug info
        disp = self.sql.find('users', 'id', uid, 'display');
        return disp[1]

    def mail(self, email, user):
        from smtplib import SMTP
        to = user+' <'+email+'>'
        msg = self.cgi.include("other", "regmessg", 0, user=user, to=to)
        s = SMTP('localhost', '25')
        s.sendmail('noreply@anicat.net', email, msg)
        s.quit()
        return 'send'