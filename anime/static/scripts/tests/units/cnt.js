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

    return describe('cnt', function() {

        afterEach(function() {
            RequestProcessor.prototype._parsed = function() {}
        })

        describe('link', function() {
            it('should pass', function(done) {
                set_processor(done)
                var l = getElementsByClassName('link', document, 'td')[0]
                l.firstChild.click()
            })
        })
        describe('id', function() {
            it('should pass', function(done) {
                set_processor(done)
                getElementsByClassName('id', document, 'td')[0].click()
            })
        })
        describe('title', function() {
            it('should pass', function(done) {
                set_processor(done)
                getElementsByClassName('title', document, 'td')[0].click()
            })
        })
        describe('episodes', function() {
            it('should pass', function(done) {
                set_processor(done)
                getElementsByClassName('episodes', document, 'td')[0].click()
            })
        })
        describe('episodes', function() {
            it('should pass', function(done) {
               set_processor(done)
                getElementsByClassName('episodes', document, 'td')[0].click()
            })
        })
        describe('release', function() {
            it('should pass', function(done) {
                set_processor(done)
                getElementsByClassName('release', document, 'td')[0].click()
            })
        })
        describe('type', function() {
            it('should pass', function(done) {
                set_processor(done)
                getElementsByClassName('type', document, 'td')[0].click()
            })
        })
        describe('id_send', function() {
            it('should pass', function(done) {
                set_processor(done, function() {
                    var state = document.getElementById('id_state')
                    var selected = element.getSelected(state)
                    var new_sel = selected
                    while(new_sel == selected)
                        new_sel = Math.floor((Math.random() * state.options.length) + 1);
                    state.options[new_sel].selected = true
                    state.onchange()
                })
                getElementsByClassName('id', document, 'td')[0].click()
            })
        })
    })
})
