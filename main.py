import functions
from sql import Sql
from user import User
from cgi import FieldStorage
from out import Out
from ajax import Ajax
from card import Card
from statistics import Stat

class Main:
    
    def __init__(self):
        self.version = '3.0.0'        
        self.cgi = functions.CgiHelper(FieldStorage(keep_blank_values=True), self.version)
        self.sql = Sql(self.cgi, db='tempcat', user='catman', passwd='catpass')
        self.usr = User(self.sql, self.cgi)
        self.outobj = Out(self.cgi, self.sql, self.usr, version=self.version)
        self.parseParams()
        
    def ajax(self):
        return Ajax(self.cgi, self.sql, self.usr, self.outobj)
    
    def card(self):
        return Card(self.cgi, self.sql, self.usr)
    
    def stat(self):
        return Stat(self.cgi, self.sql, self.usr)

    def out(self):
        self.outobj.out()

    def parseParams(self):        
        getVal = self.cgi.getVal
        if getVal('card'):
            self.card().out(getVal('card'))
        elif getVal('stat'):
            self.stat().out(getVal('stat'))
        elif getVal('search'):
            self.ajax().search()
        elif getVal('get'):
            self.ajax().get()
        elif getVal('edit'):
            self.ajax().edit()
        elif getVal('add'):
            self.ajax().add()
        elif getVal('login'):
            self.ajax().login()
        elif getVal('register'):
            self.ajax().register()        
        else:
            self.out()
