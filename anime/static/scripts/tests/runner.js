/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Javascript tests runner
 *
 */

 define(['base/events', 'base/request_processor', 'tests/status'],
    function(events, RequestProcessor, StatusManager){

    function TestRunner(tests, prepare, wait){

        this.timer = null
        this.timeout = 1000
        this.stack = []
        this.tests = tests
        this.prepare = {}
        this.results = []
        this.waitBefore = wait

        var onclick_call = function(_this){
            if(!_this.callback.condition)
                return false
            var params = _this.callback.target
            events.add(params[0], params[1], function(e){
                events.stop(e)
                _this.process.call(_this)
                events.remove(params[0], params[1], arguments.callee)
            })
            return true
        }

        var wraps = 0
        var old_proto = RequestProcessor.prototype._catch
        this.wrap_request = function(){
            wraps++
            var _runner = this
            RequestProcessor.prototype._catch = function(e){
                _runner.results.push(['Ajax', false, e.toString()])
                if (!(--wraps))
                    RequestProcessor.prototype._catch = old_proto
            }
        }

        if(tests._init){
            this._setup = tests._init
            tests._init = undefined
        }

        for(var t in prepare){
            if(!isArray(prepare[t]))
                continue
            this.prepare[t] = filter((function(tests){
                return function(el){
                    if(isNumber(el) || tests[el] || prepare[el])
                        return true
                    else
                        throw Error('Test ' + e + 'not found in ' + tests + '.')
                }
            })(this.tests), prepare[t])
        }

        this.setup = function(name, callback) {
            this._callback = callback
            try {
                if(this._setup)
                    this._setup()
                return true
            } catch(e) {
                this.results.push([name, false, 'Setup phase:' + e.toString()])
            }
            return false
        }

        this.teardown = function() { }

        this.run = function(name){
            var tests = {}
            if(name)
                tests[name] = this.tests[name]
            else
                tests = this.tests
            for (var testname in tests){
                var test = tests[testname]
                var prepare = this.prepare[testname] || []
                prepare.forEach(this.run, this)
                if(isFunction(test) || isNumber(test))
                    this.stack.push([name, test])
                if(!this.waitBefore || !onclick_call(this))
                    this.nextTimer()
            }
        }

        this.nextTimer = function(timeout){
            var _this = this
            this.timer = setTimeout(function(){ _this.process.call(_this) },
                (isNumber(timeout) ? timeout : this.timeout))
        }

        this.process = function(){
            clearTimeout(this.timer)
            this.timer = null
            if(StatusManager.status > 0)
                return this.nextTimer(func)
            if(StatusManager.status < 0)
                return
            var func = this.stack.shift()
            if(!func)
                return
            if(isArray(func) && isFunction(func[1]))
                StatusManager.take()
                try{
                    this.wrap_request()
                    func[1].call(this)
                    this.results.push([func[0], true])
                }catch(e){
                    this.results.push([func[0], false, e.toString()])
                }
                StatusManager.put()
            if(this.stack.length){
                if(!onclick_call(this))
                    this.nextTimer(func)
            }else{
                this.printResults()
                StatusManager.put()
            }
        }

        this.printResults = function(){
            var resdiv = document.getElementById('TestResults')
            if(!resdiv){
                resdiv = element.create('div', {'id': 'TestResults',
                    'style': {'position': 'absolute', 'bottom': 0,
                    'right': 0, 'width': '400px', 'background': '#FFF',
                    'border': '2px solid #b0b0b0', 'borderRadius': '3px',
                    'padding': '2px 5px'}})
                element.appendChild(document.body, resdiv)
            }
            this.resultss.forEach(function(result) {
                var resp = element.create('p', {'style': {'borderRadius': '5px',
                    'background': (result[1] ? '#CCFFCC' : '#FF0000'),
                    'padding': '0px 10px', 'margin': '2px 0px'}},
                    [{'span': {'innerText': result[0] + ':', 'style': {'marginRight': '10px'}}},
                     {'span': {'innerText': (result[1] ? 'Done' : 'Failed')}}])
                if(!result[1])
                    element.appendChild(resp, {'span': {'innerText': result[2],
                    'style': {'display': 'block'}}})
                element.appendChild(resdiv, resp)
            })
        }

    }

    return TestRunner
})
