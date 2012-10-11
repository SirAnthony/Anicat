/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * AJAX module
 *
 */

//################# Ajax worker

function AjaxClass(){

    var cookie = cookies;

    var defaultProcessor = new RequestProcessor({})

    this.url = '/ajax/'

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
                xmlHttp.open("POST", this.url + url + '/', true);
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
            s += 'Content-Disposition: form-data; name="' + name + '"';
            // isFile
            if(value != null && typeof value == "object" &&
                    'lastModifiedDate' in value && 'name' in value){
                throw Error('This is not supported yet. Use static uploading.');
                //~ s += '; filename="' + value.name + '"' + crlf;
                //~ s += 'Content-Type: application/octet-stream' + crlf;
                //~ var reader = new FileReader();
                //~ reader.readAsBinaryString(value);
                //~ s += crlf + reader.result + crlf;
            }else{
                s += crlf + crlf + (!isString(value) ? jsonToString(value) : value) + crlf;
            }
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


};

var ajax = new AjaxClass();

AjaxClass.prototype.load = ajax.loadXMLDoc


//################# Request processor

function RequestProcessor(parsers, caller){

    this.parsers = parsers;
    this.caller = caller;
    if(!this.caller) this.caller = this;

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
                    resp = resp.replace(/"\$(.+?)\$"/gi,'$1');
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
            }else{
                var parser = this.parsers[resp.response];
                if(!parser)
                    throw new Error('Unexpected response type: ' + resp.response);
                parser.call(caller, resp);
            }
        }catch(e){
            this._catch(e)
            message.create(e);
            if(resp.text){
                message.add('Server response:');
                message.add(resp.text);
            }
            message.show();
        }
        this._parsed();
    }

};

RequestProcessor.prototype._сatch = function(){}
RequestProcessor.prototype._parsed = function(){}
