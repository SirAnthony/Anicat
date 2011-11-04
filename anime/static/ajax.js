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

        for(var item in qry){
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
                    edit.processResponse(resp);
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
                                if(catalog_storage.enable()){
                                    current = catalog_storage.getStatus(resp.text.id);
                                }else{
                                    sp.innerText = current;
                                    element.appendChild(mspn, [label, sp,{'p': {
                                            innerText: 'Enable local storage to use catalog anonymously.'}}]);
                                    continue;
                                }
                            }else{
                                catalog_storage.disable();
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
                                            s.push(element.create('a', {className: 's0', href: current[link],
                                                                        innerText: link}));
                                            s.push(element.create('', {innerText: '\240'}));
                                        }
                                        if(!s.length)
                                            s.push(element.create('', {innerText: 'None'}));
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
                        if(edit)
                            element.insert(d.firstChild, {'a': {className: 'right',
                                'href': edit.getFieldLink(resp.text.id, fields[i]),
                                innerText: 'Edit', target: '_blank',
                                onclick: ((fields[i] == 'state') ? function(){
                                    cardstatus(resp.text.id);
                                    return false;} : undefined)}});
                        data.push(d);
                        element.appendChild(d, createFieldContent(fields[i], field, resp.text.id));
                        if(fields[i] == 'state')
                            d.id = 'card_userstatus'
                    }
                    element.appendChild(card, [
                        {'div': {'id': 'imagebun', 'className': 'cardcol'}}, [
                            {'div': {'id': 'cimg'}}, [
                                {'img': {'src': 'http://anicat.net/images/' + res.id + '/'}}],
                            'div', [
                                (edit ? {'a': {className: 'right',
                                'href': edit.getFieldLink(resp.text.id, 'bundle'),
                                innerText: 'Edit', target: '_blank'}} : undefined ),
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
                    if(typeof hideEdits == 'undefined')
                        element.appendChild(document.getElementsByTagName("head")[0],
                            {'script': {'type': 'text/javascript', 'src': '/static/card.js'}});
                    else
                        hideEdits();
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
