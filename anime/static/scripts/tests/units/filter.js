/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Javascript tests
 *
 */

define(['tests/runner'], function (TestRunner){
	return new TestRunner({
        'show': function(){
            var h = document.getElementsByTagName('a')
            h = filter(function(el){
                return /^filter/gi.test(el.innerText) }, h, null, true)[0]
            h.click()
        },
        'apply': function(){
            var fl = document.getElementById('id_filter_container')
            toggle(fl, 1)
            var rt = document.getElementById('id_filter_releaseType')
            rt.options[0].selected = true
            fl.lastChild.previousSibling.click()
        },
        'clear_select': function(){
            var fl = document.getElementById('id_filter_container')
            toggle(fl, 1)
            var rt = document.getElementById('id_filter_releaseType')
            rt.options[0].selected = true
            rt.parentNode.parentNode.firstChild.click()
        },
        'clear': function(){
            var fl = document.getElementById('id_filter_container')
            toggle(fl, 1)
            var rt = document.getElementById('id_filter_releaseType')
            rt.options[0].selected = true
            fl.lastChild.previousSibling.previousSibling.click()
            fl.lastChild.previousSibling.click()
        },
        'error': function(){
            var fl = document.getElementById('id_filter_container')
            toggle(fl, 1)
            document.getElementById('id_releasedAt_0').value = "a"
            fl.lastChild.previousSibling.click()
        },
    }, {'all': ['show', 'apply', 'clear', 'clear_select',
                'error']})
})