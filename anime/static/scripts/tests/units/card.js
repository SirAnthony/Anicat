/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Javascript tests
 *
 */

define(['base/request_processor'], function (RequestProcessor){

    function set_processor(done, func){
        RequestProcessor.prototype._parsed = function() {
            func && func()
            done()
        }
    }

    return describe('card', function() {

        afterEach(function() {
            RequestProcessor.prototype._parsed = function() {}
        })

        describe('open', function() {
            it('should pass', function(done) {
                set_processor(done)
                var l = getElementsByClassName('link', document, 'td')[0]
                l.firstChild.click()
            })
        })

        describe('edit', function() {
            it('should pass', function(done) {
                set_processor(done)
                var card = document.getElementById('card')
                var elements = getElementsByClassName('right', card, 'a')
                elements.forEach(function(elem){
                    if(elem.innerText != 'Submit new')
                        elem.click()
                })
            })
        })

        'send': function(){
            var card = document.getElementById('card')
            var elements = getElementsByClassName('right', card, 'a')
            elements.forEach(function(elem){
                if(elem.innerText != 'Save')
                    elem.click()
            })
        },
        'cancel': function(){
            var card = document.getElementById('card');
            var elements = getElementsByClassName('right', card, 'a');
            elements.forEach(function(elem){
                if(elem.innerText != 'Cancel')
                    elem.click()
            })
        },

    }, {'edit': ['open'], 'send': ['edit'], 'cancel': ['edit'],
        'all': ['edit', 5000, 'send', 5000, 'cancel']});
})