# -*- coding: utf-8 -*-
import os, re
from time import time, strftime, gmtime
import json

class Out:
    
    def __init__(self, cgi, sql, user, version='3.0.0'):
        self.cgi = cgi
        self.sql = sql
        self.user = user
        self.version = version
        self.defstats = {'0': 'none', '1': 'want', '2': 'now', '3': 'ok', '4': 'dropped', '5':'partially watched'}
        self.color = {'0': "white", '1': "DeepSkyBlue", '2': "cyan", '3': "#ccffcc", '4': "red", '5': "#F0F0F0",
         '1on': "#FF69B4", '2on': "#FFD700", '4on': "#ffb300", '0on': "yellow", '3on': "#f2f696", '5on': "FFFFCC"}
        self.display = { 'catalog': ['id', 'name', 'numberofep', 'translation', 'enddate', 'type', 'air'],
                    'organisation': ['production'], 
                    'people': ['director', 'scenario']}
        self.excludekeys = ['id','enddate', 'air']
    
    def main(self):
    	include = self.cgi.include
        color = self.color        
        limit = 100         
        try: page = int(self.cgi.getVal('page', 1))
        except ValueError: page = 1
        if page < 1: page = 1
        start = (page-1)*limit
        stats = self.user.getStats()
        sort = self.cgi.getVal('sort', 'name')        
        show = self.cgi.getVal('show')
        for i in self.defstats:
            if self.defstats[i] == show:
                show = i
                break
        shw = []
        if show:
            for i in stats:            
                if int(stats[i]['job']) == int(show):
                    shw.append(i)
        show = {}
        if shw: show['id'] = shw
        data, header, count = self.sql.getAll(self.display, exclude = self.excludekeys, ordertag = sort, showdict=show,
                                  orderdesc = self.cgi.checkVal('desc'), limit = limit, limstart = start)
        if data[0] == 'ok': data = data[1]
        else:
            print data
            return
        prms = {}
        out = ''
        for i in range(0, len(data)):
            num = start+1+i
            td = ''
            rid = data[i]['id']
            td += '<td class="link" id="link'+str(rid)+'''">
                <a href="/card/'''+str(rid)+'''/" class="cardurl" target="_blank">
                    <img src="/templates/arrow.gif" alt="Go" />
                </a>
            </td>'''
            td += '<td class="id" id="id'+str(rid)+'" onclick="cnt('+"'id', '"+str(rid)+"'"+');">'+str(num)+'</td>'
            bgcolor, jsfunct, watched, clr = '', '', None, '0';            
            if stats and stats.has_key(rid):
                clr = str(stats[rid]['job'])
                if stats[rid]['job'] == 2 or stats[rid]['job'] == 4:
                    watched = stats[rid]['comm']
            if data[i]['air'] == 1: clr += 'on' #bycicle            
            for j in range(0, len(header)):                 
                hdr = header[j]['name']
                if hdr != 'link':
                    jsfunc = 'onclick="cnt('+"'"+hdr+"', '"+str(rid)+"'"+');"'
                if hdr == 'translation':
                    translation = self.cgi.timedecode(data[i]['translation'])
                    if data[i]['air']:
                        translation += ' - ?'
                    if data[i].has_key('enddate') and data[i]['enddate']:
                        translation += ' - ' + self.cgi.timedecode(data[i]['enddate'])
                    td += '<td class="translation" id="translation'+str(rid)+'"' + jsfunc + '>'+translation+'</td>'
                else:
                    content = ''
                    if data[i][hdr]:                        
                        content = data[i][hdr]
                    if hdr == 'numberofep' and watched:
                        content = str(watched) + '/' + str(content)
                    td += '<td class="'+hdr+'" id="' + hdr + str(rid) + '"' + jsfunc + '>'+str(content)+'</td>'
            out += '<tr class="r' + clr + '">' + td + '</tr>'
        pager = ''
        curpage = re.sub(r"&page=\d+", r"", os.environ["REQUEST_URI"])
        for i in range(1, (count/limit)+2):
            if i == page:
                pager += '<span id="spanl">[' + str(i) + ']&nbsp;</span>'
            else:
                pager += '<a href="'+curpage+'&amp;page='+str(i)+'">' + str(i) + '</a>&nbsp;'
        print include('main', 'table', 0, hd = self.tblHeader(header, sort), body = out, pg = pager)

    def tblHeader(self, keys, sort='name'):
    	include = self.cgi.include
    	hd = ''
    	hd += include('main', 'tblhdr', 0, cls = 'link')
    	hd += include('main', 'tblhdr', 0, cls = 'id', key = '№', url="/")
    	wosort = re.sub(r"(&sort=\w+)|(&desc)", r"", os.environ["REQUEST_URI"])    	    	    	
        for i in range(0, len(keys)):
            desc = ''
            if str(keys[i]['name']) == sort and not self.cgi.checkVal('desc'): desc = '&desc'  
            hd += include('main', 'tblhdr', 0, key = str(keys[i]['value']).capitalize(),
                         cls = str(keys[i]['name']), url = wosort + '&sort=' + str(keys[i]['name']), desc = desc)
        return hd
        
    
    def xmlHeader(fn):
        def new(*args):
            print "Content-Type: text/xml; charset=UTF-8\n"
            return fn(*args)
        return new
    
    def json(self, obj):
        print "Content-type: text/javascript; charset=UTF-8"
        print self.cgi.cookies
        print json.dumps(obj)
    
    def out(self):
        user = self.user
        print "Content-Type: text/html; charset=UTF-8"        
        print self.cgi.cookies
        include = self.cgi.include
        include('main', 'head', 1)
        include('main', 'header',  1);
        include('main', 'forms', 1);
        include('usr', 'add', 1)
        if user.session and user.session['data'].has_key('userid'):
            include('usr', 'logged', 1, username=user.session['data']['user'])
            include('usr', 'show', 1)
        else:
            include("usr", "logform", 1)
        include("main", "hdend", 1)
        include("all", "search", 1)
        #include("main", "tempnote", 1)
        #if os.environ["REMOTE_ADDR"] == '192.168.1.2':
        if self.user.session:
            self.main()
        include('main', 'end', 1)
        include('other', 'div', 1, classname='footer', 
            cont='v. <a style="font-size: 10pt; color: #000081" href="/changes.list">'+self.cgi.version+'</a>.<br/>Time: '+self.cgi.processTime()+'s.'); 
