//##############################################################################
//###############################    Аякс   ####################################
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
            request += item + '=' + qry[item];
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
        
        //var cookies = cookie.get('SESSION');
        if (qry){
            if (xmlHttp){
                xmlHttp.open("POST", url, true);
                xmlHttp.onreadystatechange = handleRequestStateChange;
                xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                /*xmlHttp.setRequestHeader("Connection", "close");                
                if (cookie){
                    cookies = 'SESSION=' + cookies+ ';';
                    xmlHttp.setRequestHeader("Cookie", cookies);
                }*/
                xmlHttp.send(request);
            }    
        }
    }
    
    var setRequest = function(){
        message.new('Processing Request');
        message.addTree(element.create('img', {src: '/static/loader.gif'}));
        message.show();
        /*var mspan = document.getElementById('mspan');
        var menu = document.getElementById('menu');
        element.removeAllChilds(mspan)
        element.appendChild(mspan, [element.create('p', {innerText: 'Processing Request'}),
                                element.create('img', {src: '/templates/loader.gif'})]);
        menu.style.display = 'block';
        */
    }
    
    //################# обработка результатов
    var handleRequestStateChange = function(){
        try{
            if (!app.appajax){
                /*if (xmlHttp.readyState == 1) { //Мозила
                    setRequest();
                }
                if (xmlHttp.readyState == 2) { //А это специально для эстета оперы, которая статус 1 признавать не хочет.
                    setRequest();
                }*/
            }
            //if (xmlHttp.readyState == 3){}
            if (xmlHttp.readyState == 4) {
                app.appajax = null;                        
                if (xmlHttp.status == 200){
                    //alert(xmlHttp.responseText);
                    //    document.getElementById('mspan').innerHTML = xmlHttp.responseText;
                    var resp = xmlHttp.responseText.replace(/\n/gi,'');
                    if( /^\{.*\}$/.test(resp)){
                        resp = eval("("+resp+")");
                        //if( /^\[.*\]$/.test(xmlHttp.responseText)){
                        processingResult(resp);
                        /*}else{
                            var resp = xmlHttp.responseText;
                            document.getElementById('mspan').innerHTML = resp;
                        */
                    }else if(xmlHttp.responseXML){ //Опера не отличает жсон от xml. лол.
                        ajxedt(xmlHttp.responseXML.documentElement);                 
                    }
                    mfl = 1; //Сыграем на том, что это возьмет немного времени;                 
                }else{
                    message.new('Status: '+xmlHttp.status);
                    message.add('Не удалось получить данные: \u000A'+xmlHttp.statusText);
                    message.addHTML(xmlHttp.responseText);
                    message.show();
                    /*alert(xmlHttp.status);
                    alert("Не удалось получить данные: \u000A"+xmlHttp.statusText);
                    */
                }
            }
        }catch(e){
            alert('Caught Exception: ' + e);        
            mfl = 1;
        }        
    }
    
    var processingResult = function(response){    
        var mspn = document.getElementById('mspan');
        var resp = response;
        try{      
            switch(resp['response']){
            
                case 'app':                
                    app.retfunct(resp['text']);
                break;
                
                case 'edtok':
                /*
                    document.getElementById('menu').style.display='none';
                    mspn.innerHTML = 'none';
                    edit.processResult(resp['text']);
                */                
                break;
                
                case 'editok':
                /*
                    mspn.innerHTML = 'База успешно обновлена';            
                    if (!resp.text){
                        elm.innerHTML = "";
                    }else{                                    
                        if(resp.text != 'notext' && elm)
                            elm.innerHTML = resp.text;                    
                    }
                    timer = setTimeout("document.getElementById('menu').style.display='none';", 1500);
                */
                break;
                
                case 'error':
                    //if(elm && elm.firstChild.defaultValue){elm.innerHTML = elm.firstChild.defaultValue;}
                    if(resp.text){
                        throw new Error(resp.text);
                    }else{
                        throw new Error('Unknown error.');
                    }
                break;
                
                case 'nmform':                
                    var inn = element.create('form',{ id: 'frm'});
                    var label = element.create('label',{ htmlFor: 'state', 
                        innerText: resp.text.val });
                    var sel = element.create('select',{id: 'stid', name: 'state',
                        onchange: function(){sndstat(resp.text.id, resp.text.name);}
                    });
                    resp.text.select = (function(obj){
                        var ret = {};
                        for(var i = 0; i<(function(o){var n=0; for(e in o) n++; return n;})(obj); i++) ret[i] = obj[i];
                        return ret;
                    })(resp.text.select);
                    element.addOption(sel, resp.text.select);                                
                    if(resp.text.selected){                        
                        for(var i in sel.childNodes){
                            if( sel.childNodes[i].value == resp.text.selected)
                                sel.childNodes[i].selected = true
                        }
                    }
                    element.appendChild(inn,[label,element.create('br'),sel])
                    if(resp.text.all){
                        var sel = element.create('select',{id: 'stnum',
                            onchange: function(){sndstat(resp.text.id, resp.text.name);}});
                        var arr = new Array();
                        for(var i=1; i<=resp.text.all; i++){arr[i] = i;}//Пиздец, а не способ!
                        element.addOption(sel, arr);
                        if(resp.text.cmp && sel.childNodes[resp.text.cmp]){
                            var el = resp.text.cmp;
                            sel.childNodes[el].selected = true;
                        }else{sel.childNodes[0].selected = true;}
                        sel.removeChild(sel.firstChild);                    
                        element.appendChild(inn,[sel]);
                    }
                    element.removeAllChilds(mspn);
                    element.appendChild(mspn, [inn]);
                    sel.focus();
                break;
                
                case 'frmedt':
                    var el = document.getElementById('id'+resp.text.id).parentNode;
                    el.style.backgroundColor = resp.text.color;                    
                    obj = document.getElementById('numberofep' + resp.text.id);
                    nof = obj.textContent.replace(/(\d+\/)?/, "")
                    element.removeAllChilds(obj);
                    if(resp.text.comm){
                        element.appendChild(obj, [element.create('TextNode', {innerText: resp.text.comm+'/'+nof})]);
                    }else{
                        element.appendChild(obj, [element.create('TextNode', {innerText: nof})]);
                    }
                    document.getElementById('menu').style.display = 'none';
                    element.removeAllChilds(mspn);
                break;
                
                case 'egetok':
                    if(resp.text.edt == 'yes'){
                        var name;
                        for(var i in resp.text){
                            if(i == 'edt' || i == 'id'){continue;}
                            name = i;                                         
                        }
                        edit.fillCont(resp.text[name], name, resp.text.id);
                    }
                break;
                
                case 'getok':                
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
                        if(isString(current)){
                            sp.innerText = current;
                        }else{
                            if(curname == 'state'){                            
                                var sel = element.create('select',{id: 'stid', name: 'state',
                                    onchange: function(){sndstat(resp.text.id, curname);}
                                });                            
                                /*
                                // Ох, лол, это какой-то безумный sort
                                // Я не представляю, зачем это писал, но оно мне нравится, поэтому оставлю
                                resp.text.select = (function(obj){  
                                    var ret = {};
                                    for(var i = 0; i<(function(o){var n=0; for(e in o) n++; return n;})(obj); i++)
                                        ret[i] = obj[i];
                                    return ret;
                                })(resp.text.select);*/
                                element.addOption(sel, current.select);
                                if(current.selected){                        
                                    for(var i in sel.childNodes){
                                        if( sel.childNodes[i].value == current.selected)
                                            sel.childNodes[i].selected = true
                                    }
                                }
                                cld.push(sel);
                                if(current.all){
                                    sel = element.create('select',{id: 'stnum',
                                        onchange: function(){sndstat(resp.text.id, curname);}});
                                    var arr = new Array();
                                    for(var i=1; i<=current.all; i++){arr[i] = i;}//Пиздец, а не способ!
                                    element.addOption(sel, arr);
                                    if(current.completed && sel.childNodes[current.completed]){
                                        var el = current.completed;
                                        sel.childNodes[el].selected = true;
                                    }else{sel.childNodes[0].selected = true;}
                                    sel.removeChild(sel.firstChild);
                                    cld.push(sel);
                                }
                                sel.focus();
                            }else{
                                var hid = ((current.tbl) ? current.tbl : "catalog");
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
                                        var s = (curname == 'bundle') ? element.create('span',{name: 'name'}) :
                                                    element.create('span',{name: 'name', innerText: encd(cur.name)});
                                        cld.push(p, [s]);
                                        if(curname == 'bundle'){
                                            var a = element.create('a',{href: '/card/'+cur.elemid+'/',
                                                     innerText: encd(cur.name), className: 'snone'});
                                            if(cur.job) pclass.add(a,"s"+cur.job);
                                            element.appendChild(s, [a])
                                        }
                                        if(cur.role){
                                            element.appendChild(p, [
                                                element.create('span', {name: 'role', innerText: ' as '+encd(cur.role)})]);
                                        }
                                        if(cur.comm){
                                            element.appendChild(p, [
                                                element.create('span', {name: 'comm', innerText: '('+encd(cur.comm)+')'})]);
                                        }
                                    }else{
                                        var s;
                                        if(curname == 'translation'){
                                            s = element.create('span', {name: 'name'});
                                            element.appendChild(s, [
                                                element.create('span', {name: 'trstart', innerText: encd(current[0][0])})]);
                                            if(current[0][1])
                                                element.appendChild(s, [
                                                    element.create('span', {innerText: ' - '}),
                                                    element.create('span', {name: 'trend', innerText: encd(current[0][1])})
                                                ]);
                                        }else{
                                            if(curname == 'duration') current += ' min.';
                                            s = element.create('span', {name: 'name', innerText: encd(current)});
                                        }
                                        cld.push(element.create('p'), [s]);
                                    }
                                }
                            }
                        }
                        element.appendChild(mspn, [label, [/*edt,*/ sp, cld]]);
                    }
                break;
                
                case 'logfail':
                    user.loginFail(resp.text);
                    throw new Error("Login error");
                break;
                
                case 'logok':
                    message.hide();
                    user.loginSuccess(resp.text);
                    window.location.reload();
                break;
                
                case 'regfail':
                    user.registerFail(resp.text);
                break;
                
                case 'search':
                    searcher.putResult(resp.text);
                break;
            }
        }catch(e){
            message.new(e);
            if(resp.text.text != 'notext'){
                message.add('Server response:');
                message.add(resp.text);
            }
            message.show();
        }
    }
    
})();