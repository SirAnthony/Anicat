#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import re
from time import time, strftime, gmtime 

class CgiHelper:
    
    def __init__(self, form = None, version = '3.0.0'):
        self.starttime = time()
        self.__incfile = {}
        self.__incpath = os.path.join(os.path.abspath(os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))), "templates")
        self.cookies = ''
        self.form = form
        self.version = version
            
    def encd(self, string):
        "Convert codes into characters"
        string = re.sub(r"&quot;", r"\"", string)
        string = re.sub(r"&#37;", r"%", string)
        string = re.sub(r"&#39; ", r"'", string)        
        string = re.sub(r"&#92;", r"\\", string)
        string = re.sub(r"&#47;", r"/", string)
        string = re.sub(r"&#43;", r"\+", string)
        string = re.sub(r"&#61;", r"=", string)
        string = re.sub(r"&lt;", r"<", string)
        string = re.sub(r"&rt;", r">", string)        
        string = re.sub(r"&#35;", r"#", string)
        string = re.sub(r"&amp;", r"&", string)
        return str(string)
    
    def appcode(self, string):    
        "Convert characters into codes"
        string = re.sub(r"&", r"&amp;", string)
        string = re.sub(r"#", r"&#35;", string)
        string = re.sub(r"\"", r"&quot;", string)
        string = re.sub(r"%", r"&#37;", string)
        string = re.sub(r"'", r"&#39;", string)
        string = re.sub(r"\\", r"&#92;", string)
        string = re.sub(r"/", r"&#47;", string)
        string = re.sub(r"\+", r"&#43;", string)
        string = re.sub(r"=", r"&#61;", string)
        string = re.sub(r"<", r"&lt;", string)
        string = re.sub(r">", r"&rt;", string)                
        return str(string)
    
    def timedecode(self, tstr):
        try: tstr = int(tstr)
        except Exception:
            return tstr
        return strftime("%d.%m.%Y", gmtime(tstr))
    
    def processTime(self):
        return str(time() - self.starttime)
    
    def setCookie(self, name, value, path='/', expires=None, prnt = True):        
        if expires:
            #Wdy, DD-Mon-YYYY HH:MM:SS GMT
            expires = 'expires='+strftime("%a, %d-%b-%Y %H:%M:%S GMT; ", gmtime(time()+2629744))
        else: expires = ''
        cookie = 'Set-Cookie: '+name+'='+value+'; path='+path+'; '+expires+"\n"
        if prnt:
            self.cookies += cookie+"\n"
        else:
            return cookie	
    
    def getCookie(self):
        if 'HTTP_COOKIE' in os.environ:
            cookies = os.environ['HTTP_COOKIE']
            cookies = cookies.split('; ')
            handler = {}
            for cookie in cookies:
                cookie = cookie.split('=')
                handler[cookie[0]] = cookie[1]
            return handler
        
    def delCookie(self):
        pass
        #my @c = split(/; /, $ENV{'HTTP_COOKIE'});
        #my $ret;
        #foreach $_ (@c) {
        #		/(.+)=/;
        #		$ret .= $self->set_cookie("$1");
        #	}
        #	return $ret;
        #}
    
    def getVal(self, val, default = '', obj = None):
        if not obj:
            if not self.form:
                return default
            else:
                obj = self.form	
        if obj.has_key(val):
            if type(obj[val]).__name__ == 'list':                
                return obj[val][-1].value
            else:    
                return obj[val].value
        return default
    
    def checkVal(self, val, obj = None):
        if not obj:
            if not self.form:
                return default
            else:
                obj = self.form	
        if obj.has_key(val):
            return True
        return False
    
    def include(self, block, part, prnt = 0, **vars):
        "Include template. You can change path by changing this incpath variable"
        if not self.__incfile.has_key(block):
            f = open(os.path.join(self.__incpath, ''.join([block,'.tpl'])), 'r')
            curname = ''
            self.__incfile.update({block:{}})
            for line in f:                
                if not re.match(ur"(^#[^!].+)", line):
                    res = re.match(ur"(^#!(\w+)$)", line)
                    if res:                        
                        curname = res.group(2)
                        self.__incfile[block].update({curname: []})
                    elif curname:
                        self.__incfile[block][curname].append(line)
            f.close()
            for i in self.__incfile[block].keys():
                self.__incfile[block][i] = ''.join(self.__incfile[block][i])
        rstr = self.__incfile[block][part]
        m = re.findall(ur"\$(\w+)\.?", rstr, re.M)
        if len(m):
            for i in m:                
                r = re.compile(ur"\$%s\.?" % i)
                if vars.has_key(i):
                    rstr = re.sub(r, str(vars[i]), rstr)
                else:
                    rstr = re.sub(r, '', rstr)
        #rstr =~ re.sub(r"@#(.[^@]*)@", self.incfile[block][r"\1"], rstr) А надо ли?
        if prnt:
            print rstr
        else: 
            return str(rstr)    
