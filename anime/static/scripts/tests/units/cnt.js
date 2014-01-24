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
        'link': function(){
            var l = getElementsByClassName('link', document, 'td')[0]
            l.firstChild.click()
        },
        'id': function(){
            getElementsByClassName('id', document, 'td')[0].click()
        },
        'title': function(){
            getElementsByClassName('title', document, 'td')[0].click()
        },
        'episodes': function(){
            getElementsByClassName('episodes', document, 'td')[0].click()
        },
        'release': function(){
            getElementsByClassName('release', document, 'td')[0].click()
        },
        'type': function(){
            getElementsByClassName('type', document, 'td')[0].click()
        },
        'id_send': function(){
            var state = document.getElementById('id_state')
            var selected = element.getSelected(state)
            var new_sel = selected
            while(new_sel == selected)
                new_sel = Math.floor((Math.random() * state.options.length) + 1);
            state.options[new_sel].selected = true
            state.onchange()
        },
    }, {'id_send': ['id'],
        'all': ['type', 'release', 3000, 'episodes', 'title', 'id', 'link', 'id_send']})
})