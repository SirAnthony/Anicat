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
		'_init': function() {
			this.form = document.getElementById('addform')
			if(!this.form)
				throw new Error('Form not found')
		},

        'show': function(){
            var h = getElementsByClassName('leftmenu')[0]
            if(h.lastChild.href == '/add/')
                h.lastChild.click()
        },
        'fill_type': function(){ // Not works
            toggle(this.form, 1)
            var type = document.getElementById('id_releaseType')
            add.typeChange.call(type)
            type.options[0].selected = false
            type.options[1].selected = true
            add.typeChange.call(type)
            type.options[1].selected = false
            type.options[2].selected = true
            add.typeChange.call(type)
            type.options[2].selected = false
            type.options[3].selected = true
            add.typeChange.call(type)
        },
        'fill_genre': function(){
            toggle(this.form, 1)
            var link = document.getElementById('ImportAddLink')
            link.click()
            link.click()
            var genre = document.getElementById('id_genre')
            genre.options[2].selected = true
            genre.options[3].selected = true
        },
        'fill_date': function(){
            toggle(this.form, 1)
            var date = document.getElementById('id_releasedAt')
            date.value = '25.09.2012'
        },
        'fill_title': function(){
            toggle(this.form, 1)
            var title = document.getElementById('id_title')
            title.value = Date().replace(/[\D-]/gi, '')
        },
        'send_blank': function(){
            toggle(this.form, 1)
            this.form.lastChild.onclick({})
        },
        'calendar': function(){
            toggle(this.form, 1)
            var cal = getElementsByClassName('datetimeshortcuts', this.form, 'span').pop()
            if(!cal || !cal.firstChild)
                throw Error('Calendar not found')
            cal.firstChild.click()
            cal.firstChild.click()
            var box = getElementsByClassName('calendarbox').pop()
            box.getElementsByTagName('a').forEach(function(el){
            		el.click && el.click()	})
        },
        'submit': function(){
            toggle(this.form, 1)
            this.form.lastChild.click()
        }
    }, {'all': ['show', 'send_blank', 'fill_type', 'calendar', 'submit', 5000, 'show'],
    'submit': ['fill_type', 'calendar', 'fill_genre', 'fill_date', 'fill_title']})
})