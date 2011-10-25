//##############################################################################
//###############################   Аякс    ####################################
//##############################################################################

var ajax = new (function(){

    var xmlHttp = null;
    var cookie = cookies;

    //################# Вызов аяксового обьекта.
    this.loadXMLDoc = function(url, qry){
        var request = '';
        if(!isHash(qry)){
            alert('Input is old');
            return;
        }

        setRequest();

        if(!(/^http:.*/.test(url) || /^https:.*/.test(url)))
            qry['csrfmiddlewaretoken'] = cookie.get('csrftoken');

        for(item in qry){
            if(!qry[item]) continue;
            if(request)
                request += '&';
            if(isArray(qry[item])){
                var e = new Array();
                for(var i in qry[item])
                    e.push(item + '=' + qry[item][i]);
                request += e.join('&');
            }else{
                request += item + '=' + qry[item];
            }
        }

        xmlHttp = null;
        if(window.XMLHttpRequest){
            try{
                xmlHttp = new XMLHttpRequest();
            }catch(e){}
        }else if(window.ActiveXObject){
            try{
                xmlHttp = new ActiveXObject('Msxml2.XMLHTTP');
            }catch(e){
                try{
                    xmlHttp = new ActiveXObject('Microsoft.XMLHTTP');
                }catch(e){}
            }
        }

        if (request){
            if (xmlHttp){
                xmlHttp.open("POST", url, true);
                xmlHttp.onreadystatechange = handleRequestStateChange;
                xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xmlHttp.send(request);
            }
        }
    }

    this.processGetRequest = function(opts){
        setRequest();
        processingResult({'response': 'get', "status": true, 'text': opts});
        message.unlock()
    }

    this.processSetRequest = function(opts){
        setRequest();
        opts.response = 'edit';
        processingResult(opts);
        message.unlock()
    }

    var setRequest = function(){
        message.create('Processing Request');
        message.addTree(element.create('img', {src: '/static/loader.gif'}));
        message.show();
        message.lock();
    }

    //################# обработка результатов
    var handleRequestStateChange = function(){
        try{
            //if (!app.appajax){
                /*if (xmlHttp.readyState == 1) { //Мозила
                    setRequest();
                }
                if (xmlHttp.readyState == 2) { //А это специально для эстета оперы, которая статус 1 признавать не хочет.
                    setRequest();
                }*/
            //}
            //if (xmlHttp.readyState == 3){}
            if (xmlHttp.readyState == 4) {
                //app.appajax = null;
                if (xmlHttp.status == 200){
                    var resp = xmlHttp.responseText.replace(/\n/gi,'');
                    if( /^\{.*\}$/.test(resp)){
                        resp = eval("("+resp+")");
                        processingResult(resp);
                    }else if(xmlHttp.responseXML){ //Опера не отличает жсон от xml. лол.
                        //ajxedt(xmlHttp.responseXML.documentElement);
                    }
                    message.unlock();
                }else{
                    message.create('Status: '+xmlHttp.status);
                    message.add('Не удалось получить данные: \u000A'+xmlHttp.statusText);
                    message.addHTML(xmlHttp.responseText);
                    message.show();
                }
            }
        }catch(e){
            alert('Caught Exception: ' + e);
        }
    }

    var processingResult = function(resp){
        var mspn = document.getElementById('mspan');
        try{
            switch(resp['response']){

                /*case 'app':
                    app.retfunct(resp['text']);
                break;*/

                case 'add':
                    add.processResponse(resp);
                break;

                case 'edit':
                    if(resp.model == 'state'){
                        if(!resp.status){
                            if(resp.returned && typeof user_storage != "undefined" && user_storage.enabled){
                                resp.text = {'state': resp.returned};
                                user_storage.addItem('list.'+resp.id, resp.returned);
                            }else{
                                throw new Error(resp.text);
                                break;
                            }
                        }
                        message.hide();
                        var statusdiv = document.getElementById('card_userstatus');
                        if(statusdiv){
                            var statusname = ({"0": "None", "1": "Want", "2": "Now", "3": "Ok",
                                 "4": "Dropped", "5": "Partially watched"})[resp.text.state]
                            element.remove((function(x){
                                var a = new Array();
                                for(var i in x)
                                    if(x[i] && (x[i].tagName == "SPAN" || x[i].tagName == "FORM"
                                        || x[i].tagName == "INPUT")) a.push(x[i]);
                                return a;
                            })(statusdiv.childNodes));
                            element.appendChild(statusdiv, [{'span': {innerText: statusname}},
                                {'input': {type: 'hidden', name: 'card_userstatus_input', value: resp.text.state}}]);
                            if(resp.text.count){
                                element.appendChild(statusdiv, [{'span':
                                    {innerText: resp.text.count + '/' + (function(){
                                        var n = document.getElementsByName('episodesCount');
                                        for(var i in n)
                                            if(n[i].tagName == "SPAN") return n[i].innerText;
                                        })(),
                                    className: 'right'}}, {'input': {type: 'hidden',
                                             name: 'card_usercount_input', value: resp.text.count}}]);
                            }
                        }

                        var rs = getStylesheetRule('.rs'+resp.text.state, 'background-color');
                        rs = rs ? rs : '#FFF';
                        var as = getStylesheetRule('.as'+resp.text.state, 'background-color');
                        as = as ? as : '#FFF';
                        var sl = getStylesheetRule('.sl'+resp.text.state, 'color');
                        sl = sl ? sl : '#000';
                        var rules = [['.r'+resp.id, ['background-color', rs]],
                                    ['.a'+resp.id, ['background-color', as]],
                                    ['.s'+resp.id, ['color', sl, true]]];
                        addStylesheetRules(rules);
                    }
                break;

                case 'error':
                    if(resp.text){
                        throw new Error(resp.text);
                    }else{
                        throw new Error('Unknown error.');
                    }
                break;

                case 'get':
                    element.removeAllChilds(mspn);
                    for(var i in resp.text.order){
                        var curname = resp.text.order[i];
                        if(!curname) continue;
                        if(!resp.text[curname]) continue;
                        var current = resp.text[curname];
                        var capCurname = curname.substr(0,1).toUpperCase() + curname.substr(1)
                        var label = element.create('label', { 'for': curname + resp.text.id,
                                            innerText: capCurname + ':', name: resp.text.id});
                        var sp = element.create('p', {'id': curname+resp.text.id, 'name': curname});
                        var cld = new Array();
                        if(curname == 'state'){
                            //Ненадежно это все
                            if(isString(current)){
                                if(typeof user_storage != "undefined" && user_storage.loaded){
                                    if(!user_storage.enabled) user_storage.enable();
                                    var list = user_storage.getItem('list.'+resp.text.id);
                                    current = {"selected": ((list) ? list : 0), "select": {
                                        "0": "none", "1": "want", "2": "now", "3": "ok",
                                        "4": "dropped", "5": "partially watched"}};
                                }else{
                                    sp.innerText = current;
                                    element.appendChild(mspn, [label, sp,{'p': {
                                            innerText: 'Enable local storage to use catalog anonymously.'}}]);
                                    continue;
                                }
                            }else{
                                if(typeof user_storage != "undefined" && user_storage.loaded)
                                    if(user_storage.enabled) user_storage.disable();
                            }
                            sp = createStatusForm(resp.text.id, current.selected,
                                                    current.select, current.all, current.completed);
                        }else if(isString(current)){
                            sp.innerText = current;
                        }else{
                            var hid = ((current.model) ? current.model : "anime");
                            hid = element.create('input', {type: 'hidden', name: 'table', value: hid});
                            //var edt = createElem('span',{className: 'edtl', 'name': i});
                            /*if(!resp.text.edt && !resp.text[i][0]){continue;}
                            if(resp.text.edt && !resp.text[i][0]){}else{}*/
                            var num = numHash(current);
                            for(var g=0; g<=num; g++){
                                var cur = current[g];
                                if(cur && isHash(cur)){
                                    var p = (curname == 'bundle') ? element.create('p',{name: cur.elemid}) :
                                                                        element.create('p',{'name': g});
                                    var s = (curname == 'bundle') ? element.create('span',{name: 'name'}, [
                                            {'a': {href: '/card/'+cur.elemid+'/', innerText: encd(cur.name),
                                            className: 's s' + cur.elemid}}]) : element.create('span',{name: 'name',
                                                               innerText: encd(cur.title ? cur.title : cur.name)});
                                    cld.push(p, [s]);
                                    if(cur.role){
                                        element.appendChild(p, [
                                            {'span': {name: 'role', innerText: ' as '+encd(cur.role)}}]);
                                    }
                                    if(cur.comm){
                                        element.appendChild(p, [
                                            {'span': {name: 'comm', innerText: '('+encd(cur.comm)+')'}}]);
                                    }
                                }else{
                                    if(curname == 'links'){
                                        var s = new Array();
                                        for(var link in current){
                                            if(!current[link]) continue;
                                            var l;
                                            switch(link){
                                                case 'AniDB':
                                                    l = "http://anidb.net/perl-bin/animedb.pl?show=anime&aid=";
                                                break;
                                                case 'ANN':
                                                    l = "http://www.animenewsnetwork.com/encyclopedia/anime.php?id=";
                                                break;
                                                case 'MAL':
                                                    l = "http://myanimelist.net/anime/";
                                                break;
                                            }
                                            s.push(element.create('a', {className: 's0', href: l+current[link],
                                                                        innerText: link}));
                                            s.push(element.create('', {innerText: '\240'}));
                                        }
                                        cld.push(element.create('p'), s);
                                    }else{
                                        if(curname == 'duration') current += ' min.';
                                        var s = element.create('span', {name: 'name', innerText: encd(current)});
                                        cld.push(element.create('p'), [s]);
                                    }
                                }
                            }
                        }
                        element.appendChild(mspn, [label, /*edt,*/ sp, cld]);
                    }
                break;

                case 'card':
                    message.hide();
                    var card = document.getElementById("card");
                    var res = resp.text;
                    var data = new Array();
                    var fields = ['name', 'type', 'genre', 'episodesCount',
                                'duration', 'release', 'links', 'state']
                    for(var i in fields){
                        var field = res[fields[i]];
                        var n;
                        switch(i){
                            case 3: n = 'episodes:'; break;
                            case 5: n = 'released:'; break;
                            default: n = fields[i] + ':'; break;
                        }
                        var d = element.create('div', null, {'h4': {innerText: capitalise(n)}});
                        data.push(d);
                        if(fields[i] == 'name'){
                            var names = new Array();
                            for(var name in field){
                                names.push(element.create('', {innerText: field[name].title}));
                                names.push(element.create('br', {}));
                            }
                            element.appendChild(d, names)
                        }else if(fields[i] == 'state'){
                            element.appendChild(d, [{'span': {innerText: capitalise(field.select[field.selected])}},
                                {'input': {'type': 'hidden', 'name': 'card_userstatus_input', 'value': field.selected}}]);
                            if(field.completed && field.all){
                                element.appendChild(d, [{'span': {className: 'right',
                                    innerText: field.completed + '/' + field.all}},
                                {'input': {'type': 'hidden', 'name': 'card_usercount_input', 'value': field.completed}}]);
                            }
                        }else if(fields[i] == 'links'){
                            if(!field) continue;
                            if(field.AniDB)
                                element.appendChild(d, [{'a': {'target': '_blank', innerText: 'AniDB',
                                    'href': 'http://www.animenewsnetwork.com/encyclopedia/anime.php?id=' + field.AniDB}},
                                    {'': {innerText: ' '}}]);
                            if(field.ANN)
                                element.appendChild(d, [{'a': {'target': '_blank', innerText: 'ANN',
                                    'href': 'http://anidb.net/perl-bin/animedb.pl?show=anime&aid=' + field.ANN}},
                                    {'': {innerText: ' '}}]);
                            if(field.MAL)
                                element.appendChild(d, {'a': {'target': '_blank', innerText: 'MAL',
                                    'href': 'http://myanimelist.net/anime/' + field.ANN}});
                        }else{
                            element.appendChild(d, {'': {innerText: field ? field : 'None'}});
                        }
                    }
                    element.appendChild(card, [
                        {'div': {'id': 'imagebun', 'className': 'cardcol'}}, [
                            {'div': {'id': 'cimg'}}, [
                                {'img': {'src': 'http://anicat.net/images/' + res.id + '/'}}],
                            'div', [
                                {'h4': {innerText: 'Bundled with:'}},
                                'table', (function(bn){
                                    if(!bn) return;
                                    var b = new Array();
                                    var num = numHash(bn);
                                    for(var i=0; i<=num; i++){
                                        var cur = bn[i]
                                        b.push(element.create('tr', {}, [
                                            {'td': {innerText: (cur.elemid == res.id) ? '►' : ''}},
                                            {'td': {'text-align': 'right', innerText: i+1}},
                                            'td', [{'a': {'target': '_blank',
                                                href: '/card/'+cur.elemid+'/',
                                                innerText: encd(cur.name),
                                                className: 's s' + cur.elemid,
                                                onclick: (function(id){
                                                    return function(){return getCard(id);};
                                                })(cur.elemid)}}]
                                        ]));
                                    }
                                    return b;
                                })(res.bundle)
                            ]
                        ],
                        {'div': {'id': 'main', 'className': 'cardcol'}}, data

                    ]);
                    var soffsety = (document.documentElement.scrollTop || document.body.scrollTop) - document.documentElement.clientTop;
                    card.style.top = soffsety + ((soffsety > card.parentNode.offsetTop) ? 5 : 40) + 'px';
                    var imgbun;
                    if(card.clientWidth < 750){
                        imgbun = (card.clientWidth < 600) ? 200 : 300;
                        card.firstChild.style.maxWidth = imgbun + 'px';
                        card.firstChild.firstChild.firstChild.style.maxWidth = imgbun + 'px';
                        imgbun += 40;
                    }else{
                        imgbun = card.firstChild.clientWidth + 40;
                    }
                    card.lastChild.style.maxWidth = card.clientWidth - imgbun + 'px';
                break;

                case 'login':
                    message.hide();
                    if(resp.status){
                        user.loginSuccess(resp.text);
                        updateStylesheets('/css/');
                    }else{
                        user.loginFail(resp.text);
                    }
                break;

                case 'regfail':
                    user.registerFail(resp.text);
                break;

                case 'search':
                    searcher.putResult(resp.text);
                break;
            }
        }catch(e){
            message.create(e);
            if(resp.text.text != 'notext'){
                message.add('Server response:');
                message.add(resp.text);
            }
            message.show();
        }
    }

})();
