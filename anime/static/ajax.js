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

        var boundary = '-----------' + parseInt(Math.random()*1000000000000)

        var makePostData = function(name, value){
            var crlf = '\r\n'
            var s = '--' + boundary + crlf;
            s += 'Content-Disposition: form-data; name="' + name + '"' + crlf;
            s += crlf + value + crlf;
            return s;
        }

        for(var item in qry){
            if(!item || !qry[item]) continue;
            if(isArray(qry[item])){
                for(var i=0; i<qry[item].length; i++)
                    request += makePostData(item, qry[item][i]);
            }else{
                request += makePostData(item, qry[item]);
            }
        }
        request += '--' + boundary + '--'

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
                xmlHttp.setRequestHeader("Content-type", "multipart/form-data; boundary=" + boundary);
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
                    message.create();
                    for(var i in resp.text.order){
                        var curname = resp.text.order[i];
                        if(!curname || !resp.text[curname]) continue;
                        var current = resp.text[curname];
                        var label = element.create('label', { 'for': curname + resp.id,
                                        innerText: capitalise(curname) + ':'});
                        var field = forms.getField(curname, resp.id, current);
                        message.addTree(label);
                        message.addTree(field);
                    }
                    message.show();
                break;

                case 'card':
                    message.hide();
                    Card.create(resp.id, resp.text);
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
            if(resp.text){
                message.add('Server response:');
                message.add(resp.text);
            }
            message.show();
        }
    }

})();
