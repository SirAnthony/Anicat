//##############################################################################
//###############################   Аякс    ####################################
//##############################################################################

var ajax = new (function(){

    var cookie = cookies;

    var defaultProcessor = new RequestProcessor(function(resp){
        throw new Error('Bad request processor');
    })

    //################# Вызов аяксового обьекта.
    this.loadXMLDoc = function(url, qry, processor){
        if(!isHash(qry)){
            alert('Input is old');
            return;
        }

        if(!isHash(processor) || !isFunction(processor.process))
            processor = defaultProcessor;

        var xmlHttp = null;
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
        processor.setRequest();

        var data = makeRequest(url, qry);

        if(data.request){
            if (xmlHttp){
                xmlHttp.open("POST", url, true);
                xmlHttp.onreadystatechange = processor.process;
                xmlHttp.setRequestHeader("Content-type", "multipart/form-data; boundary=" + data.boundary);
                xmlHttp.send(data.request);
            }
        }
    }

    var makeRequest = function(url, qry){
        var request = '';

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

        return {'request': request, 'boundary': boundary};
    }

})();


//################# Request processor
function RequestProcessor(parser, response){

    this.parser = parser;
    this.response = response;

    this.setRequest = function(){
        message.create('Processing Request');
        message.addTree(element.create('img', {src: '/static/loader.gif'}));
        message.show();
        message.lock();
    }


    // Process closure
    this.process = (function(processor){
        return function(){ processor._process.call(this, processor); }
    })(this);


    // This calls as xmlHttp.onreadystatechange, 'this' variable is xmlHttp object
    this._process = function(processor){
        try{
            if(this.readyState == 4) {
                if(this.status == 200){
                    var resp = this.responseText.replace(/\n/gi,'');
                    if( /^\{.*\}$/.test(resp)){
                        resp = eval("("+resp+")");
                        processor.parse(resp);
                    }else if(this.responseXML){ //Опера не отличает жсон от xml. лол.
                        //ajxedt(this.responseXML.documentElement);
                    }
                    message.unlock();
                }else{
                    message.create('Status: ' + this.status);
                    message.add('Data receiving failed: \u000A' + this.statusText);
                    message.addHTML(this.responseText);
                    message.show();
                }
            }
        }catch(e){
            message.create('Caught Exception: ' + e);
            message.show();
        }
    }


    // Error catcher in parser call
    this.parse = function(resp){
        try{
            if(resp.response == 'error'){
                if(resp.text)
                    throw new Error(resp.text); // FIXME: doubling
                else
                    throw new Error('Unknown error.');
            }else if(response && resp.response != response){
                throw new Error('Unexpected response type: ' + resp.response);
            }else
                this.parser(resp);
        }catch(e){
            message.create(e);
            if(resp.text){
                message.add('Server response:');
                message.add(resp.text);
            }
            message.show();
        }
    }

};
