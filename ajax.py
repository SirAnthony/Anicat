#ajax
import os,re

class Ajax:
    
    def __init__(self, cgi, sql, user, out):
        self.cgi = cgi
        self.sql = sql
        self.usr = user
        self.out = out
        self.ret = {}
        self.setResponse('error', 'Unknown error')
        
    def search(self):
        res = 'error'
        val = {'data': 'none'}
        ret = {}
        find = self.cgi.getVal('string')
        if find:
            try: srchres = int(self.cgi.getVal('results', 20)) #to user
            except Exception:
                srchres = 20
            if srchres > 30: srchres = 30 
            area = []
            data = self.sql.search(find, area)
            if len(data):
                if data[0] == 'error':
                    val = data[1]
                else:
                    ret['results'] = srchres
                    try: ret['page'] = int(self.cgi.getVal('page', 1))
                    except Exception: ret['page'] = 1
                    if ret['page'] < 1: ret['page'] = 1
                    ret['count'] = len(data)
                    if ret['page'] > ( ret['count'] / srchres + 1 ): ret['page'] = ret['count'] / srchres
                    limstart = srchres * (ret['page'] - 1)
                    sort = self.cgi.getVal('sort', 'name')
                    data, header, count = self.sql.getAll(self.out.display, exclude = self.out.excludekeys,
                                ordertag = sort, showdict={'id': data}, orderdesc = self.cgi.checkVal('desc'),
                                limit = srchres, limstart = limstart)
                    if data[0] == 'ok':
                        res = 'search'
                        ids = []                        
                        for elem in data[1]:
                            ids.append(elem['id'])
                        uid = None
                        if self.usr.session: uid = self.usr.session['data']['userid']
                        if uid: uid = self.usr.getStats(uid = uid, rid = ids)
                        for elem in data[1]:
                            elem['translation'] = self.cgi.timedecode(elem['translation'])
                            if elem['air']:
                                elem['translation'] += ' - ?'
                            if elem.has_key('enddate') and elem['enddate']:
                                elem['translation'] += ' - ' + self.cgi.timedecode(elem['enddate'])
                                del elem['enddate']
                            if uid:
                                if ret['count'] < 2:
                                    elem['job'] = uid['job']
                                elif uid.has_key(elem['id']):
                                    elem['job'] = uid[elem['id']]['job']
                        ret['data'] = data[1]
                        ret['header'] = header                        
                        val = ret
                        val['time'] = self.cgi.processTime()
                    else:
                        val = data[1]
            else:
                res = 'search'
                val['time'] = self.cgi.processTime()
        self.out.json({'response': str(res), 'text': val})
	
    
    def get(self):        
        res = 'error'
        #val = 'Unprocessed option ' + string + '. Did hackir done his homework?'
        val = 'Nothing to see here'
        try: get = int(self.cgi.getVal('get', 1))
        except Exception: 
            self.out.json({'response': str(res), 'text': val})
            return
        string = self.cgi.getVal('string')
        if string == 'state':
            if not self.usr.session:
                val = 'You must be logged for change status'
            else:
                defstats = self.out.defstats
                stats = self.usr.getStats(rid = [get])                
                val = stats
                if not stats: stats['job'] = 0
                res = 'nmform'
                val = {'id': str(get), 'val': 'State:', 'name': 'state', 'select': defstats, 'selected': str(stats['job'])}
                if stats['job'] == 2 or stats['job'] == 4:
                    all = self.sql.find('catalog', get, 'id', 'numberofep')
                    if all[0] == 'error':
                        val = all[1]
                    else:
                        val['cmp'] = stats['comm']
                        val['all'] = all[1]['numberofep']
        else:
            opt = string.split(',')
            val = {'order': [], 'id': get}
            for i in opt:
                col, table = None, None
                try: (col, table) = i.rsplit('_', 1)
                except ValueError: col = i
                if not table:
                    if col == 'name':
                        val[col] = []
                        nm = self.sql.getRecords('namebun', select = ['name'], mainid = get)
                        if nm[0] == 'error':
                            val[col] = nm[1]
                        else:
                            res = 'getok'
                            for j in nm[1]: val[col].append({"name": j['name']})
                    elif col == 'bundle':
                        uid = None
                        if self.usr.session: uid = self.usr.session['data']['userid']
                        ret = self.sql.selectBundle(col, bunid=get, uid=uid)
                        val[col] = ret[1]
                        if ret[0] != 'error':
                            res = 'getok'
                    elif col == 'translation':
                        val[col] = []
                        date = self.sql.getRecords('catalog', select = ['translation', 'enddate'], id = get)
                        if date[0] == 'error':
                            val[col] = date[1]
                        else:
                            res = 'getok'
                            val[col].append([self.cgi.timedecode(date[1][0]['translation'])]);
                            if date[1][0]['enddate']:
                                val[col][0].append(self.cgi.timedecode(date[1][0]['enddate']))
                    else:
                        val[col] = [[]]
                        ret = self.sql.find('catalog',  get, 'id', col)
                        res = 'getok'
                        if type(ret[1]).__name__ == 'dict':
                            val[col][0] = ret[1][col]
                        else: val[col][0] = ret[1]
                    val['order'].append(col)
                else:                    
                    get = self.sql.selectBundle(table, id = get, job = col)
                    if get[0] == 'error':
                        val = get[1] 
                    else:
                        val = {'table': table, 'col': col, col: get[1], 'order': [col]}
                        res = 'getok'
        self.out.json({'response': str(res), 'text': val})

    def edit(self):
        res = 'error'
        val = 'Nothing to see here. Move along.'
        edit = self.cgi.getVal('edit')
        rid = int(self.cgi.getVal('id'))
        string = self.cgi.getVal('string')
        if edit == 'id':
          val = 'This field is not editable.'
        elif not rid:
          val = 'Something wrong with id.'
        #elif os.environ["REMOTE_ADDR"] != '192.168.1.2':
          #val = 'You can not do this.'
        else:
            if edit == 'state':                
                if not self.usr.session or not self.usr.session['data'].has_key('userid'):
                    val = 'You must be logged for choose status'
                else:                    
                    try: string = int(string)
                    except Exception:
                        val = 'Unprocessed option ' + string + '. Did hackir done his homework?'
                    else:
                        now = None
                        if string == 2 or string ==4:
                            now = self.cgi.getVal('numnow', 1)
                        ret = self.usr.editStats(mainid = rid, elemid = self.usr.session['data']['userid'], 
                                                    job=string, comm=now)
                        if ret[0] == 'ok':
                            air = self.sql.find('catalog', rid, 'id', 'air')
                            if air[0] == 'error':
                                val = air[1]
                            else:
                                res = 'frmedt'
                                clr = str(string)
                                if air[1]['air'] == 1: clr += 'on' #bycicle
                                if not self.out.color.has_key(clr): clr = '0';                                 
                                val = {'id': rid, 'color': self.out.color[clr]}
                                if string == 2 or string == 4:
                                    val['comm'] = now
                        else:
                            val = ret[1] 
                    #$res = 'frmedt';                     
                    #my %air = $sql->find($opts{'id'}, 'id', 'air');
                    #use Catfunct qw/%color/;
                    #$air{'air'} = 'on' if $air{'air'};
                    #$val = '{"id": "'.$opts{'id'}.'", "color": "'.$air{'air'}.'", "retc": "'.$opts{'string'}.'"}';
                #}                                
            #}
            else:
                if edit == 'translation':
                    pass
                    #use Catfunct qw(dateconv);
                    #use POSIX qw(strftime);
                    #my $translation = dateconv($opts{'string'});
                    #$res = $sql->edit($opts{'id'}, $opts{'edit'}, $translation->[0]);                        
                    #$res = $sql->edit($opts{'id'}, 'enddate', $translation->[1]) if $res eq 'editok' && $translation->[1];
                elif edit == 'duration':
                    string = re.sub(r"/D+", r"", string)
                      
    #}else{        
        #}elsif($opts{'edit'} eq 'state' || $opts{'edit'} eq 'air'){
            #my $user = Users->new();
            #my $usr = $user->get_user();
            #if(!$usr->{'userid'}){
                #$res = 'error';
                #$val = '"text": "You must be logged for choose status"';
            #}else{
                #my $nnow = $opts{'numnow'}+1 if $opts{'string'} == 2 || $opts{'string'} == 4;
                #my $e;
                #if($opts{'edit'} eq 'state'){
                    #$e = $user->editst('mainid'=>$opts{'id'}, 'uid'=>$$usr{'userid'},  'stat'=>$opts{'string'}, 
                    #                                            'num'=> $nnow);                
                #}else{
                    #$e = $sql->edit($opts{'id'}, $opts{'edit'}, $opts{'string'});
                #}
                #if($e eq 'editok'){
                    #$res = 'frmedt';                     
                    #my %air = $sql->find($opts{'id'}, 'id', 'air');
                    #use Catfunct qw/%color/;
                    #$air{'air'} = 'on' if $air{'air'};
                    #$val = '{"id": "'.$opts{'id'}.'", "color": "'.$air{'air'}.'", "retc": "'.$opts{'string'}.'"}';
                #}                                
            #}
        #}else{
            #if($opts{'edit'} eq 'name' && !$opts{'string'}){
                #$res = 'error'; $val = 'Whole name';
            #}else{
                #if($opts{'edit'} =~ /[\d]/){
                    #my $edit = Catfunct::convert($opts{'string'});
                    #$res = $sql->add_elms($opts{'edit'}, $edit);                    
                    #$val = Catfunct::json($edit) if $res eq 'edtok';                    
                #}else{
                    #$res = $sql->edit($opts{'id'}, $opts{'edit'}, $opts{'string'});
                #}
            #}
        #}        
        #if($res eq 'editok'){
            #if($opts{'edit'} eq 'state'){$res = 'frmedt';}
            #my %all = $sql->find($opts{'id'}, 'id', $opts{'edit'});
            #$val = $all{$opts{'edit'}};
        #}
        #if($opts{'edit'} eq 'translation'){
            #my $translation = dateconv($opts{'string'});
            #$val = strftime("%d.%m.%Y", localtime($translation->[0]));
            #if($translation->[1] == '36000'){$val .= " - ?";}else{ 
                #$val .= ' - '.  strftime("%d.%m.%Y", localtime($translation->[1])) if $translation->[1];
            #}            
        #}elsif($opts{'edit'} eq 'numberofep'){
            #$val = '-' if $val < 0;            
        #}elsif($opts{'edit'} !~ /[\d]/){Catfunct::encd(\$val);}
    #}
        self.out.json({'response': str(res), 'text': val})
        
        
    def login(self):
        self.setResponse('logfail', 'Incorrect username or password')
        if self.usr.getUser():
            self.setResponse(t='Already logged. Try to clean cookies.')            
            return self.result()
        getVal = self.cgi.getVal
        name = getVal('name')
        passwd = getVal('pass')
        long = None
        if getVal('long'): long = True        
        self.setResponse(r=self.usr.login(name, passwd, long))
        if self.ret['response'] != 'logfail':
            self.setResponse(t={'name': name})
        return self.result()
    
    def register(self):
        getVal = self.cgi.getVal        
        self.setResponse(t='registration error')
        name = getVal('name')
        passwd = getVal('pass')
        mail =  getVal('mail')
        if not name or not passwd:
            self.setResponse(t='Bad login name or password.')
        for el in [name, passwd, mail]:
            el = "".join(el.split())
        resp = self.usr.register(name, passwd, mail)
        self.setResponse(*resp)
        return self.result()
        
    def result(self):
        self.out.json(self.ret)
    
    def setResponse(self, r=None, t=None):
        if r: self.ret['response'] = str(r)
        if t: self.ret['text'] = str(t)
