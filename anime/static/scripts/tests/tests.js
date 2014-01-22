/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Javascript tests
 *
 */

define(['base/events', 'base/ajax', 'base/request_processor'],
function(events, ajax, RequestProcessor){

    ajax_calls = new Array()
    break_after = true // false
    avaliable_tests = ['add', 'card', 'cnt', 'filter', 'main',
                       'search', 'statistics', 'user']

    return {
        init: function(){
            var self = this
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
            }

            this.tests = {}
            avaliable_tests.forEach(function(testname){
                if (self.tests[testname])
                    console.log('Multiple tests with name ' + testname + 'loaded')
                require(['tests/units/' + testname], function(module){
                    self.tests[testname] = module })
            })
        },

        from_url: function(){
            var testre = document.location.hash.match(/^#test\/(\w+)(\/(\w+))?/)
            if(!testre)
                return
            this.start(testre[1], testre[3])
        },

        start: function(testname, subtest) {
            if(!testname)
                return

            // Redefine ajax.load to setup status to running when called
            ajax.prototype.load = function(url, qry, processor){
                ajax_calls.push([this, url, qry, processor])
                StatusManager.take()
                ajax.loadXMLDoc.call(ajax, url, qry, processor)
            }

            // Define postprocessor for requests
            RequestProcessor.prototype._parsed = function(){
                StatusManager.put()
                if(!ajax_calls.pop())
                    StatusManager.take() // Parser was called without server call
            }

            var callback = {
                'condition': break_after && this.continue_bt,
                'target': [this.continue_bt, 'click']
            }

            var test = this.tests[testname]
            if(test && test.run){
                if (test.setup(testname, callback))
                    test.run(subtest)
                test.teaddown()
            }
        }
    }
})