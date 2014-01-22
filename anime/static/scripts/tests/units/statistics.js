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
		'_init': function(){
			this.block = document.getElementById('statistic')
		},

        'show': function(){
            if(!this.block.childNodes.length || this.block.style.display != 'block'){
                var menu = document.getElementById('usermenu')
                if(menu.nextSibling)
                    menu = menu.nextSibling
                menu.firstChild.click()
            }
        },
        'open_link_want': function(){
            var el = getElementsByClassName('statwant', this.block, 'td')[0]
            el.parentNode.lastChild.click()
        },
        'open_link_now': function(){
            var el = getElementsByClassName('statnow', this.block, 'td')[0]
            el.parentNode.lastChild.click()
        },
        'open_link_done': function(){
            var el = getElementsByClassName('statdone', this.block, 'td')[0]
            el.parentNode.lastChild.click()
        },
        'open_link_drop': function(){
            var el = getElementsByClassName('statdropped', this.block, 'td')[0]
            el.parentNode.lastChild.click()
        },
        'open_link_part': function(){
            var el = getElementsByClassName('statpartially', this.block, 'td')[0]
            el.parentNode.lastChild.click()
        },
        'open_id': function(){
            getElementsByClassName('id', document, 'td')[0].click()
        },
        'id_send': function(){
            var state = document.getElementById('id_state')
            state.options[3].selected = true
            state.onchange()
        }
    }, {'change': ['show', 'open_id', 'id_send'], 'all': ['change', 'open_link'],
        'open_link': ['show', 'open_link_want', 'open_link_now', 'open_link_done',
        'open_link_drop', 'open_link_part'],
        'open_link_want': ['show'], 'open_link_now': ['show'], 'open_link_done': ['show'],
        'open_link_drop': ['show'], 'open_link_part': ['show'],})
})