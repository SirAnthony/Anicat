import time, hmac, random, os, hashlib
try:
    import cPickle as pickle
except ImportError:
    import pickle

class Session(dict):
    def _make_hash(self, sid, secret):
        """Create a hash for 'sid'        
        This function may be overridden by subclasses."""
        return hmac.new(secret, sid, hashlib.sha1).hexdigest()[:8]

    def _create(self, secret):
        """Create a new session ID and, optionally hash        
        This function must insert the new session ID (which must be 8 hexadecimal
        characters) into self["id"].
        It may optionally insert the hash into self["hash"]. If it doesn't, then
        _make_hash will automatically be called later.
        This function may be overridden by subclasses.
        """
        rnd = str(time.time()) + str(random.random())# + \
            #str(self._req.environ.get("UNIQUE_ID"))
        hash = hashlib.new('sha')
        hash.update(rnd)
        self["id"] = hash.hexdigest()[:8]

    def _load(self):
        """Load the session dictionary from somewhere        
        This function may be overridden by subclasses.
        It should return 1 if the load was successful, or 0 if the session could
        not be found. Any other type of error should raise an exception as usual."""
        return 1

    def save(self):
        """Save the session dictionary to somewhere        
        This function may be overridden by subclasses."""
        pass

    @staticmethod
    def tidy( ):
        pass

    def __init__(self, cgi, secret, sid=None, root="", login=None,
        shash=None, secure=0, domain=None, long=None):
        dict.__init__(self)
        self["id"] = None
        self.cgi = cgi        
        cookie = cgi.getCookie()
        # try and determine existing session id
        if sid is not None:
            self["id"] = sid
            if shash is None:
                self["hash"] = self._make_hash(self["id"], secret)
            else:
                self["hash"] = shash
                if self["hash"] != self._make_hash(self["id"], secret):
                    self["id"] = None
        if cookie and cookie.has_key('SESSION'):        
            self["id"] = cookie['SESSION'][:8]
            self["hash"] = cookie['SESSION'][8:]            
            if self["hash"] != self._make_hash(self["id"], secret):
                self["id"] = None        
        # try and load the session
        if self["id"] is not None:
            if not self._load(): self["id"] = None
        # if no session was available and loaded, create a new one
        if login:
            if self["id"] is None:
                if self.has_key("hash"): del self["hash"]
                self.created = time.time()
                self._create(secret)
                if not self.has_key("hash"):
                    self["hash"] = self._make_hash(self["id"], secret)
                cookie = cgi.setCookie('SESSION', self['id'] + self['hash'], expires=long)

    def __setattr__(self, name, value):
        self[name] = value

    def __getattr__(self, name):
        if self.has_key(name):
            return self[name]

    def get(self):
        if not self['id'] or not self['hash']:
            return
        var = self.copy()
        #remove this        
        del var['cgi']
        del var['table']
        del var['dbc']
        del var['sql']
        ########
        return var

class GenericSQLSession(Session):
    def _create(self, secret):
        while 1:
            Session._create(self, secret)
            self["hash"] = self._make_hash(self["id"], secret)
            try:
                self.dbc.execute("INSERT INTO %s (ID,hash,created,updated,data)"
                    " VALUES (%%s,%%s,%%s,%%s,%%s)" % (self.table,),
                    (self["id"], self["hash"], int(self.created), int(self.created),
                    pickle.dumps({}, 1)))
                self.dbc.execute("COMMIT")
            except self.dbc.IntegrityError:
                pass
            else:
                break

    def _load(self):
        #TODO: add debug
        ret = self.sql.find(self.table, self["id"], 'ID',  'created', 'data')        
        if ret[0] == 'error' or not ret[1]:
            return 0
        else:            
            self['created'] = ret[1]['created']
            self['data'] = pickle.loads(ret[1]['data'])
            return 1

    def save(self):
        self.dbc.execute("UPDATE %s SET updated=%%s,data=%%s"
            " WHERE ID=%%s" % (self.table,), (int(time.time()),
            pickle.dumps(self.get(), 1), self["id"]))
        self.dbc.execute("COMMIT")

    @staticmethod
    def tidy(dbc, table="catsessions", max_idle=0, max_age=0):
        now = time.time()
        if max_idle:
            dbc.execute("DELETE FROM %s WHERE updated < %%s" % (self.table,),
                (now - max_idle,))
        if max_age:
            dbc.execute("DELETE FROM %s WHERE created < %%s" % (self.table,),
                (now - max_age,))
        if max_idle or max_age:
            dbc.execute("COMMIT")
        
    def __init__(self, secret, cgi, sql, table="catsessions", **kwargs):
        self.sql = sql
        self.dbc = sql.cursor
        self.table = table
        Session.__init__(self, cgi, secret, **kwargs)

class MySQLSession(GenericSQLSession):
    
    def _create(self, secret):
        #TODO: add debug
        self.dbc.execute("LOCK TABLES %s WRITE" % (self.table,))
        while 1:
            Session._create(self, secret)
            ret = self.sql.find(self.table, self["id"], 'ID',  '1')
            if not ret[1]: break
        self["hash"] = self._make_hash(self["id"], secret)
        self.dbc.execute("INSERT INTO %s (ID,hash,created,updated,data) VALUES " \
            "(%%s,%%s,%%s,%%s,%%s)" % (self.table,),
            (self["id"], self["hash"], int(self.created),
            int(self.created), pickle.dumps({}, 1)))
        self.dbc.execute("UNLOCK TABLES")        

    def save(self):
        self.sql.updateRecords(self.table, set={'updated': int(time.time()), 'data': pickle.dumps(self.get(), 1)}, ID=self["id"])
        #self.dbc.execute("UPDATE "+  + " SET updated='"+  + "', data='" ++ "' WHERE ID=%s" % )

SQLSession = MySQLSession # backwards compatibility name