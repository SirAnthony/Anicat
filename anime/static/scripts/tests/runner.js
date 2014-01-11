/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Javascript tests runner
 *
 */

 define(['base/request_processor', 'tests/status', 'tests/Tests'],
    function(RequestProcessor, StatusManager, Tests){

    function TestRunner(tests, prepare, wait){

        this.timer = null;
        this.timeout = 1000;
        this.stack = [];
        this.tests = tests;
        this.prepare = {};
        this.results = [];
        this.waitBefore = wait;

        var onclick_call = function(_this){
            return function(e){
                e.stopPropagation && e.stopPropagation();
                e.cancelBubble = true;
                _this.process.call(_this);
            };
        };


        this.ajax_call = function(){
            var _runner = this;
            return function(e){
                _runner.results.push(['Ajax', false, e.toString()]);
                RequestProcessor.prototype._catch = function(){ };
            };
        };

        for(var t in prepare){
            if(!isArray(prepare[t]))
                continue;
            this.prepare[t] = filter((function(tests){
                return function(el){
                    if(isNumber(el) || tests[el] || prepare[el])
                        return true;
                    else
                        throw Error('Test ' + e + 'not found in ' + tests + '.');
                };
            })(this.tests), prepare[t]);
        }


        this.run = function(name){
            var test = null;
            if(name)
                test = this.tests[name];
            else
                test = this.tests;
            var pn = this.prepare[name];
            if(pn){
                for(var pname in pn)
                    this.run(pn[pname]);
            }
            if(isFunction(test) || isNumber(test))
                this.stack.push([name, test]);
            if(this.waitBefore && Tests.break_after && Tests.continue_bt)
                Tests.continue_bt.onclick = onclick_call(this);
            else
                this.nextTimer();
        };

        this.nextTimer = function(timeout){
            var _this = this;
            this.timer = setTimeout(function(){ _this.process.call(_this); },
                (isNumber(timeout) ? timeout : this.timeout));
        };

        this.process = function(){
            clearTimeout(this.timer);
            this.timer = null;
            if(StatusManager.status > 0)
                return this.nextTimer(func);
            if(StatusManager.status < 0)
                return;
            var func = this.stack.shift();
            if(!func)
                return;
            if(isArray(func) && isFunction(func[1]))
                StatusManager.take();
                try{
                    RequestProcessor.prototype._catch = this.ajax_call();
                    func[1].call(this);
                    if(!Tests.ajax_calls.length){
                        // Return old prototype if not needed;
                        RequestProcessor.prototype._catch = function(){};
                    }
                    this.results.push([func[0], true]);
                }catch(e){
                    this.results.push([func[0], false, e.toString()]);
                }
                StatusManager.put();
            if(this.stack.length){
                if(Tests.break_after && Tests.continue_bt)
                    Tests.continue_bt.onclick = onclick_call(this);
                else
                    this.nextTimer(func);
            }else{
                this.printResults();
                StatusManager.put();
            }
        };

        this.printResults = function(){
            var resdiv = document.getElementById('TestResults');
            if(!resdiv){
                resdiv = element.create('div', {'id': 'TestResults',
                    'style': {'position': 'absolute', 'bottom': 0,
                    'right': 0, 'width': '400px', 'background': '#FFF',
                    'border': '2px solid #b0b0b0', 'borderRadius': '3px',
                    'padding': '2px 5px'}});
                element.appendChild(document.body, resdiv);
            }
            for(var i = 0; i < this.results.length; i++){
                var result = this.results[i];
                var resp = element.create('p', {'style': {'borderRadius': '5px',
                    'background': (result[1] ? '#CCFFCC' : '#FF0000'),
                    'padding': '0px 10px', 'margin': '2px 0px'}},
                    [{'span': {'innerText': result[0] + ':', 'style': {'marginRight': '10px'}}},
                     {'span': {'innerText': (result[1] ? 'Done' : 'Failed')}}]);
                if(!result[1])
                    element.appendChild(resp, {'span': {'innerText': result[2],
                    'style': {'display': 'block'}}});
                element.appendChild(resdiv, resp);
            }
        };

    }

    return TestRunner;
});
