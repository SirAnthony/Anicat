
class Stat:
    
    def __init__(self, cgi, sql, user):
        self.cgi = cgi
        self.sql = sql
        self.usr = user
    
    def out(self, id):
        user = self.usr
        include = self.cgi.include
        if id == '0' and user.session and user.session['data'].has_key('userid'):
            include('other', 'redirect', 1, location = 'stat/' + str(user.session['data']['userid']))
            return
        print "Content-Type: text/html; charset=UTF-8"
        print self.cgi.cookies
        include('main', 'head', 1, add = include('main', 'jshdr', 0, name = 'stat'))
        include('main', 'header',  1);
        include('main', 'nmforms', 1);        
        if user.session and user.session['data'].has_key('userid'):
            include('usr', 'logged', 1, username = user.session['data']['user'])
            include('usr', 'nmshow', 1)
        else:
            include("usr", "logform", 1)
        include("main", "hdend", 1)
        self.main(id);
        include('main', 'end', 1)
        include('other', 'div', 1, classname='footer', 
            cont='v. <a style="font-size: 10pt; color: #000081" href="/changes.list">'+self.cgi.version+'</a>.<br/>Time: '+self.cgi.processTime()+'s.');
        
    def main(self, id):
        include = self.cgi.include
        user = self.usr
        defstats = ['None', 'Want', 'Now', 'Ok', 'Dropped','Partially watched']
        try: id = int(id)
        except: return
        uname = None
        if not id or id == 0:
            if not user.session or not user.session['data'].has_key('userid'):
                include('other', 'nostat', 1)
                return
            else:
                id = user.session['data']['userid']
        if user.session and user.session['data'].has_key('userid') and user.session['data']['userid'] == id:
            uname = user.session['data']['user']
        else:
            uname = user.getUsername(id)
        include("other", "stuser", 1, user = uname)
        st = ''
        total = {'eps': 0, 'full': 0, 'custom': 0}
        for job in range(1,6):
            fields = ['COUNT(*) as count', 'SUM(catalog.numberofep*catalog.duration) as full']
            if job == 2 or job == 4: fields.append('SUM(catalog.duration*statsbun.comm) AS custom')
            d = self.sql.getRecords('catalog', fields, job = job,  elemid = id,
                    limit = None, QueryJoins = 'JOIN statsbun ON(catalog.id = statsbun.mainid)')            
            if d[0] == 'ok':
                d = d[1][0]
                if not d['full']: d['full'] = 0
                if job == 3: d['custom'] = d['full']                
                elif not d.has_key('custom') or not d['custom']: d['custom'] = 0
                if job != 5:
                    total['eps'] += d['count']
                    total['full'] += d['full']
                    total['custom'] += d['custom']
                st += include('other', 'sttr', 0, key = defstats[job], dur = d['full'],
                                eps = d['count'], tot = d['custom'])
        st += include('other', 'sttr', 0, key = 'Total', dur = total['full'], eps = total['eps'],
                            tot = total['custom'])
        include('other', 'stmain', 1, st = st)
			
                
            