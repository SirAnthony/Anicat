
from time import time
import random

class Card:
    
    def __init__(self, cgi, sql, user):
        self.cgi = cgi
        self.sql = sql
        self.usr = user
    
    def out(self, id):
        user = self.usr
        #print "Content-Type: text/html; charset=UTF-8"        
        print "Content-type: text/xml; charset=UTF-8"
        print self.cgi.cookies
        include = self.cgi.include
        #include('main', 'head', 1)
        include('xml', 'xhead', 1, name = 'card')
         #include('main', 'header',  1);
        username, userid = '', ''
        if user.session and user.session['data'].has_key('userid'):
            username = user.session['data']['user']
            userid = user.session['data']['userid']
        include('xml', 'parent', 1, tag = 'version', data = self.cgi.version)                
        include('xml', 'header', 1, name = username, id = userid)
        #include('main', 'forms', 1);        
        #if user.session and user.session['data'].has_key('userid'):
            #include('usr', 'logged', 1, username=user.session['data']['user'])
            #include('usr', 'show', 1, id=user.session['data']['userid'])
        #else:
            #include("usr", "logform", 1)
        #include("main", "hdend", 1)
        self.main(id);
        #include('main', 'end', 1)
        #include('other', 'div', 1, classname='footer', 
            #cont='v. <a style="font-size: 10pt; color: #000081" href="/changes.list">'+self.cgi.version+'</a>.<br/>Time: '+str(time() - self.cgi.starttime)+'s.');
        include('xml', 'parent', 1, tag = 'time', data = self.cgi.processTime())
        include('xml', 'bdend', 1)

    def main(self, id):
        try: id = int(id)
        except Exception: id = 0
        if id == int(0):
            id = random.randint(1, self.sql.getCount('catalog'))
        data = self.sql.find('catalog', id, 'id', '*')
        if data[0] != 'ok':
            print data[1]
        else:
            data = data[1]
        include = self.cgi.include 
        if not data:
            include('other', 'nocard', 1)
        nm = self.sql.getRecords('namebun', select = ['name'], mainid = id)
            
        data['translation'] = self.cgi.timedecode(data['translation'])
        if data['enddate']:
            data['translation'] += ' - ' + self.cgi.timedecode(data['enddate'])
                    
        del [ data['catalog.id'], data['air'], data['enddate'] ]
        
        uid = None
        if self.usr.session: uid = self.usr.session['data']['userid']
        bundle = self.sql.selectBundle('bundle', bunid=id, uid=uid)
            
        #imagebun = []
        #imagebun.append(include('other', 'cardimage', 0, id = id))        
        #imagebun.append('<b>Bundled with:</b><br/>')
        
        bundles = ''
        if bundle[0] != 'error' and bundle[1]:
            for i in range(0, len(bundle[1])):
                element = bundle[1][i]
                selected = ''
                if int(element['elemid']) == id:
                    selected = 1
                if not element.has_key('job') or not element['job']:
                    element['job'] = 0
                bundles += include('xml', 'cardbundle', 0, selected = selected, number = i+1,
                                id = element['elemid'], name = element['name'], comm = element['comm'],
                                color = element['job'])
                #arr = ''
                #clr = '0'
                #if int(element['elemid']) == id:
                    #arr = include('other', 'img', 0, name = 'arrowblack')
                #if element['comm']:
                    #element['comm'] = '(' + element['comm'] + ')'
                #if element.has_key('job') and element['job']:
                    #clr = str(element['job'])
                #bundles.append(include('other', 'cardbun', 0, href = str(element['elemid']), num = str(i+1),
                                #arr = arr, text = element['name'], comm = element['comm'],
                                #color = clr))
        #imagebun.append(include('other', 'tabletag', 0, cont = ''.join(bundles)))
                
        
        cont = ''
        for key in data.keys():
            if key == 'name':
                name = ''
                if nm[0] == 'error':
                    name += data['name']
                else:
                    for j in nm[1]:
                        name += include('xml', 'element', 0, data = j['name'])
                data[key] = name
            cont += include('xml', 'cardmain', 0, name = key, title = key.capitalize(), content = data[key])
            #include('other', 'cardinfo', 0, prop = key.capitalize(), val = data[key])
        
        include('xml', 'id', 1, id = id)
        include('xml', 'parent', 1, tag = 'bundles', data = bundles)
        include('xml', 'parent', 1, tag = 'main', data = cont )
        #include('other', 'div', 1, classname = 'cardcol', id = 'imagebun', cont = ''.join(imagebun) )
        #include('other', 'div', 1, classname = 'cardcol', id = 'main', cont = ''.join(cont))
        
        
                
        