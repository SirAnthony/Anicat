/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Javascript tests
 *
 */

define(['base/events', 'base/ajax', 'base/request_processor', 'tests/status'],
function(events, ajax, RequestProcessor, StatusManager){

    var ajax_calls = new Array()
    var break_after = false // true
    var avaliable_tests = ['add', 'card', 'cnt', 'filter', 'main',
                       'search', 'statistics', 'user']
    var test_re = new RegExp('^#test/(\\w+)/(?:(\\w+)/?)?')
    var tests_fullpath = map(function(name) {
                        return 'tests/units/' + name }, avaliable_tests)

    return {
        init: function(){
            var self = this
            this.tests = {}
            avaliable_tests.forEach(function(testname){
                if(this.tests[testname])
                    console.log('Multiple tests with name ' + testname + 'loaded')
                require(tests_fullpath, function(){
                    for(var i = 0; i < arguments.length; ++i)
                        self.tests[avaliable_tests[i]] = arguments[i] })
            }, this)

            if(break_after){
                this.continue_bt = document.getElementById('test_c_bt')
                if(!this.continue_bt){
                    this.continue_bt = element.create('input', {'value': 'Next test',
                        'id': 'test_c_bt', 'style': {'position': 'fixed',
                        'right': '500px', 'bottom': '0px'},  'type': 'button'})
                    element.appendChild(document.body, this.continue_bt)
                }
                events.add(this.continue_bt, 'click', function(e) {
                    self.from_url()
                    events.remove(this, 'click', arguments.callee)
                })
            } else {
                events.onload(self.from_url, self)
            }
        },

        from_url: function(){
            var testre = document.location.hash.match(test_re)
            if(!testre)
                return
            this.start(testre[1], testre[2])
        },

        start: function(testname, subtest) {
            if(!testname)
                return

            // Redefine ajax.load to setup status to running when called
            ajax.constructor.prototype.load = function(url, qry, processor){
                ajax_calls.push([this, url, qry, processor])
                StatusManager.take()
                ajax.loadXMLDoc.call(ajax, url, qry, processor)
            }

            // Define postprocessor for requests
            RequestProcessor.prototype._parsed = function(){
                var call = ajax_calls.pop()
                if(call){ // Parser was called with server call
                    console.log(call)
                    StatusManager.put()
                }

            }

            var callback = {
                'condition': this.continue_bt && break_after,
                'target': [this.continue_bt, 'click']
            }

            var test = this.tests[testname]
            if(test && test.run){
                if (test.setup(testname, callback))
                    test.run(subtest)
                test.teardown()
            }
        }
    }
})