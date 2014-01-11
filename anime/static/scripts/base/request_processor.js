/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * AJAX module; request processor
 *
 */

define(['base/message'], function(message) {

    function RequestProcessor(parsers, caller){

        this.parsers = parsers;
        this.caller = caller;
        if(!this.caller) this.caller = this;

        this.setRequest = function(){
            message.create('Processing Request');
            message.addTree(element.create('img', {src: '/static/loader.gif'}));
            message.show();
            message.lock();
        };

        // Process closure
        this.process = (function(processor){
            return function(){ processor._process.call(this, processor); };
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
                            processor.parse.call(processor, resp);
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
                throw e;
                message.create('Caught Exception: ' + e);
                message.show();
            }
        };


        // Error catcher in parser call
        this.parse = function(resp){
            try{
                if(resp.response == 'error'){
                    throw new Error(resp.text || 'Unknown error.');
                }else{
                    var parser = this.parsers[resp.response];
                    if(!parser)
                        throw new Error('Unexpected response type: ' + resp.response);
                    parser.call(caller, resp);
                }
            }catch(e){
                this._сatch(e);
                message.create(e);
                if(resp.text){
                    message.add('Server response:');
                    message.add(resp.text);
                }
                message.show();
            }
            this._parsed();
        };

    }

    RequestProcessor.prototype._parsed = function(){};
    RequestProcessor.prototype._сatch = function(err){ throw err; };


    return RequestProcessor;
});