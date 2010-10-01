#!/usr/bin/python
# -*- coding: utf-8 -*-

class Sql:
    "mysql module"
    import MySQLdb    

    def __init__(self, cgi, **vars):
        self.hlp = cgi
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
        try: c.execute(query)
        except Exception, e: return ['error', str(e)]
        self.__db.commit()
        if action == "select":
            fetch = c.fetchall()
            return ['ok', fetch]
        if action == "insert":    
            return ['ok', c.lastrowid]

    def insertNew(self, tbl, upd=[], **vars):
        fields = []
        values = []
        update = ''
        for name in vars:
            if vars[name] != None:
                fields.append(name)
                values.append(str(vars[name]))
        if len(upd) > 0:
            up = []
            for i in upd:
                if vars.has_key(i) and vars[i] != None:
                    up.append(''.join([i, ' = ', "'", str(vars[i]), "'"]))
            if len(up) > 0:
                update = ' '.join(['ON DUPLICATE KEY UPDATE', ', '.join(up)])
        fields = ', '.join(fields)
        values = '", "'.join(values)
        qw = self.hlp.include("sql", 'insert', 0, tbl = tbl, fields = fields, values = values, update = update)
        id = self.executeQuery(qw, 'insert')
        return id


    def search(self, value, areas):
        #clause = self.createClause(WClauseOperator = 'LIKE', name = '%' + value + '%')
        #for area in areas:
            #pass
        tbl = 'namebun'
        ret = self.getRecords(tbl, select=['mainid'], And = False, WClauseOperator = 'LIKE', name = '%'+value+'%',
                            limit = None)
        if ret[0] == 'error':
            return ret
        else:
            ids = []
            for i in range(0, len(ret[1])):
                ids.append(ret[1][i]['mainid'])            
            return ids
            
            
    #for(my $i; $i<=$#{$area}; $i++){
        #$str .= " (";
        #for(my $g; $g<=$#{$value}; $g++){
            #$str .= " ".$area->[$i]." LIKE '%".$value->[$g]."%' ";
            #$str .= "AND" if $g < $#{$value};
        #}
        #$str .= ") ";
        #$str .= "OR" if $i < $#{$area};
    #}        
    #if(!$count){
        #$lim = "LIMIT ".$limst.", ".$lim if $lim || $limst;
        #$lim = '' if !$lim;
        #$qw = "SELECT id FROM `".$tbl."` WHERE ".$str." ORDER BY ".$area->[0]." ".$lim;
        #my $sth = $dbh->prepare($qw) or die "$DBI::errstr\n";
        #$sth->execute;
        #my @ret;    
        #while( my $href = $sth->fetchrow_arrayref ) {        
            #push(@ret, $href->[0]);                
        #}
        #$sth->finish();                
        #return @ret;
    #}else{
        #$qw = "SELECT COUNT(*) FROM `".$tbl."` WHERE ".$str;
        #my $sth = $dbh->prepare($qw) or die "$DBI::errstr\n";
        #$sth->execute;
        #my $col= \ $sth->fetchrow_array();
        #$sth->finish();                        
        #return ${$col};    
    #}
    
    def find(self, tbl, value, column, *fields):
        '''Usage: (table, find_value, find_column, return_columns). ID column added if not given'''
        fields = list(fields)
        try: fields.index('id')
        except: fields.append('id')
        var = {}
        var[column] = value
        res = self.getRecords(tbl, select=fields, limit=1, **var)
        if res[0] != 'error' and res[1]: res[1] = res[1][0]
        return res

    def getCount(self, tbl, clause = None, **vars):
        if not clause:
            clause = self.createClause(**vars)
        qw = self.hlp.include("sql", "count", 0, tbl = tbl, wclause = clause)
        ret = self.executeQuery(qw)
        try: return int(ret[1][0].values()[0]) #lol
        except: return 0;

    def getRecords(self, tbl, select = [], QueryJoins = '', limit = 20, limstart = 0, **vars):        
        if len(select):
            select = ','.join(select)
        else:
            select = '*'
        clause = self.createClause(**vars)
        if limit: limit = 'LIMIT ' + str(limstart) + ',' + str(limit)
        else: limit = ''
        qw = self.hlp.include("sql", "select", 0,  wclause = clause, tbl = tbl, joins = QueryJoins,
                                                    select = select, limit = limit)
        if vars.has_key('debug'): return ['error', qw]
        ret = self.executeQuery(qw)
        return ret

    def updateRecords(self, tbl, set={}, **vars):
        update = []
        for key in set.keys():
            update.append('='.join([key, "'"+str(set[key])+"'"]))
        update = ', '.join(update)
        clause = self.createClause(**vars)        
        qw = self.hlp.include("sql", "update", 0,  update=update, wclause = clause, tbl = tbl)
        rows = self.executeQuery(qw)
        return rows

    def createClause(self, And = True, WClauseOperator = '=', **vars):
        "In future this 'll be use > along with ="
        wclause = []        
        for i in vars.keys():
            if vars[i]:
                if type(vars[i]).__name__ == 'list':
                    v = vars[i]
                    cl = []
                    for j in v:
                        cl.append(str(i) + ' ' + WClauseOperator + " '" + str(j) + "'")
                    wclause.append('(' + ' OR '.join(cl) + ')')                                                
                else:
                    wclause.append(str(i) + ' ' + WClauseOperator + " '" + str(vars[i]) + "'")
        if len(wclause):
            if And:
                wclause = 'WHERE ' + ' AND '.join(wclause)
            else:
                wclause = 'WHERE ' + ' OR '.join(wclause)
        else:
            wclause = ''
        return wclause

    def addUser(self, name, passwd, email):
        ret = self.insertNew('users', login=name, passwd=passwd, mail=email)
        if ret[0] == 'error':
            return ret
        return ['editok', ret[1]]
    
    def getAll(self, columns, limstart=0, limit=100, ordertag='name', orderdesc=False, exclude = [], showdict={}):
        #TODO: more dynamics
        #TODO: very slow
        #TODO: It's very very bad function
        if orderdesc: orderdesc='DESC'
        else: orderdesc='ASC'
        select = []
        joinref = []        
        keynames = []
        for key in columns.keys():
            for element in range(0, len(columns[key])):
                elem = columns[key][element]
                if key != 'catalog':
                    keyname = '_'.join([elem, key])
                    select.append(' '.join(['.'.join([''.join([key[0:1], str(element)]), 'name']),
                                 'AS', ''.join(['"',keyname, '"'])]))
                    tnum = ''.join([key[0:1], str(element)])
                    joinref.append( self.hlp.include("sql", "join", 0, elm = key, job = elem, tnum = tnum ) )
                    if elem not in exclude:
                        keynames.append({"name":keyname, "value": elem})
                else:
                    select.append('.'.join([key, elem]))
                    if elem not in exclude:
                        keynames.append({"name":elem, "value": elem})
        clause = self.createClause(**showdict)
        order = ' '.join(['ORDER BY',  '`' + str(ordertag) + '`', orderdesc])
        if limit: limit = ''.join(['LIMIT ', str(limstart), ',', str(limit)])            
        qw = self.hlp.include("sql", "select", 0, tbl = 'catalog', select = ', '.join(select), joins = ' '.join(joinref),
                                 wclause = clause, order = order, limit = limit)
        ret = self.executeQuery(qw)        
        count = self.getCount(tbl = 'catalog', clause = clause)
        return ret, keynames, count

    def selectBundle(self, tbl, **param):
        if tbl == 'bundle':
            main = self.find('bundlebun', param['bunid'], 'elemid', 'mainid')
            if main[0] == 'error':
                return main
            if not main[1] or not main[1].has_key('mainid'):
                return ['ok', None]
            main = main[1]['mainid']
            if param.has_key('uid') and param['uid']:
                qw = self.hlp.include('sql', 'select', 0, tbl='bundlebun', 
                    select = ', '.join(['elemid', 'comm', 'name', 'job']),
                    joins='''LEFT JOIN `catalog` on catalog.id = bundlebun.elemid LEfT JOIN 
                    (SELECT mainid,job FROM `statsbun` WHERE  elemid = ''' + str(param['uid']) +''')
                    as s on (s.mainid = bundlebun.elemid)''', wclause = 'WHERE bundlebun.mainid='+str(main),
                    order="ORDER BY translation ASC")
            else:
                qw = self.hlp.include('sql', 'select', 0, tbl='bundlebun',
                    select = ', '.join(['elemid', 'comm', 'name']),
                    joins='LEFT JOIN `catalog` on catalog.id = bundlebun.elemid',
                     wclause=self.createClause(mainid=main),
                    order="ORDER BY translation ASC")
            bundle = self.executeQuery(qw)
            if bundle[0] != 'ok':
                return bundle
            return ['ok', bundle[1]]
        elif tbl == 'stats':            
            get = self.getRecords( tbl = tbl+'bun', select = ['mainid', 'job', 'comm'], #debug=True,
                                 limit = None,  **param )
            ret = {}
            if get[0] != 'error':
                get = get[1]
                for i in get:
                    ret[i['mainid']] = { 'job': i['job'], 'comm': i['comm']}
            else: ret = get
            return ret
        else:
            qw = self.hlp.include('sql', 'select', 0, tbl=tbl+'bun',
                    select = ', '.join(['elemid', 'comm', 'role', tbl+'.name as name', 'credit.name as job']),
                    joins = 'LEFT JOIN `credit` on credit.id = ' + tbl + 'bun.job LEFT JOIN `' + tbl + '''`
                    on ''' + tbl + '.id = ' + tbl + 'bun.elemid',
                    wclause = 'WHERE ' + tbl + 'bun.mainid=' + str(param['id']) + ' AND ' + "credit.name='" + str(param['job']) + "'",
                    order = "ORDER BY name ASC")
            get = self.executeQuery(qw)
            if get[0] != 'ok':
                return get
            return ['getok', get[1]]

    def editBundle(self, tag, **bun):
        res = self.insertNew(tag+'bun', upd = ['job', 'comm'], **bun)        
        return res
        #return ['editok']
        
        #if tag == 'stats':
    #my $self = shift;
    #my($tag, $id, %bun) = @_;
    #my($qw,%ret);
    #if($tag eq 'stats'){
        #$qw = $qw = Catfunct::include("sql","bun_edit", 0,'tbl' => $tag.'bun', 'mainid' => $id,'job'=> $bun{'job'},
                                                                #'elemid'=> $bun{'id'},  'comment'=> $bun{'comm'});
    #}
    #if(!$bun{'cast'}){
    #    if($bun{'job'} eq 'bundle'){
    #        $tag =$bun{'job'};
    #        $qw = Catfunct::include("sql", "bundlesel", 0, 'id' => $id.','.$bun{'id'}, 'area'=> 'mainid', 
    #                                                                    'tbl'=> $tag.'bun', 'c'=> 'elemid', 'ord'=> 'mainid');
    #        $sth = $dbh->prepare($qw) or die "$DBI::errstr\n";
    #        my $rv = $sth->execute;
    #        my $r = $sth->fetchrow_array();
    #        if(!$r){
    #            my $qw = Catfunct::include("sql", "bundles_edit", 0, 'elms' => 'mainid, elemid', 'upd_val'=> $id,
    #                                                                       'tbl'=> $tag.'bun', 'vals'=> "($id, $id)", 'upd'=> 'elemid');
    #            my $sth = $dbh->do($qw);
    #            $r = $id;         
    #        }
    #        $qw = Catfunct::include("sql", "bundles_edit", 0, 'elms' => 'mainid, elemid', 'upd_val'=> $r, 
    #                            'tbl'=> $tag.'bun', 'vals'=> "($r, $id)", 'upd'=> "mainid");            
    #        my $sth = $dbh->do($qw);
    #        $qw = Catfunct::include("sql", "bundles_edit", 0, 'elms' => 'mainid, elemid, comm', 'upd_val'=> $r, 
    #                            'tbl'=> $tag.'bun', 'vals'=> "($r,".$bun{'id'}.",'".$bun{'comm'}."')", 
    #                            'upd'=> "comm = '".$bun{'comm'}."', mainid");
    #    }else{
    #        $qw = Catfunct::include("sql","bun_edit", 0,'tbl' => $tag.'bun', 'mainid' => $id,'job'=> $bun{'job'},
    #                                                            'elemid'=> $bun{'id'},  'comment'=> $bun{'comm'});
    #    }
    #}else{
    #    $qw = Catfunct::include("sql", "buncast_edit", 0, 'tbl' => $tag.'bun', 'mainid' => $id, 
    #            'job'=> $bun{'job'}, 'elemid'=> $bun{'id'},  'comment'=> $bun{'comm'}, 'cast'=>$bun{'cast'});        
    #}
    #my $sth = $dbh->prepare($qw) or die "$DBI::errstr\n";#return \%ret if $ret{'error'};
    #my $rv = $sth->execute;        
    #$ret{'status'} = 'ok';
    #return \%ret;
    
            
                
        