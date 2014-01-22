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
            var lf = document.getElementById('loginform')
            if(!lf)
                throw Error('Must be in non-logined mode.')
            toggle(lf, -1)
            var menu = filter(function(el){
                return /\/login\/$/g.test(el.href)
            }, document.getElementById('usermenu').childNodes)
            if(!menu || !menu[0])
                throw Error('Must be in non-logined mode.')
            menu[0].click()
        },
        'void_login': function(){
            var lf = document.getElementById('loginform')
            if(!lf)
                throw Error('Must be in non-logined mode.')
            toggle(lf, 1)
            document.getElementById('id_username').value = ''
            var pass = document.getElementById('id_password')
            pass.value = ''
            pass.nextSibling.click()
        },
        'bad_login': function(){
            var lf = document.getElementById('loginform')
            if(!lf)
                throw Error('Must be in non-logined mode.')
            toggle(lf, 1)
            document.getElementById('id_username').value = 'a'
            var pass = document.getElementById('id_password')
            pass.value = 'a'
            pass.nextSibling.click()
        },
        'show_more': function(){
            var lf = document.getElementById('loginform')
            if(!lf)
                throw Error('Must be in non-logined mode.')
            toggle(lf, 1)
            document.getElementById('register-more').click()
        },
        'register_fail': function(){
            var lf = document.getElementById('loginform')
            if(!lf)
                throw Error('Must be in non-logined mode.')
            toggle(lf, 1)
            toggle(document.getElementById('logdvmore'), 1)
            var re = document.getElementById('id_register-email')
            re.value = 'aa'
            re.nextSibling.click()
        },
        'register_success': function(){
            var lf = document.getElementById('loginform')
            if(!lf)
                throw Error('Must be in non-logined mode.')
            toggle(lf, 1)
            toggle(document.getElementById('logdvmore'), 1)
            var re = document.getElementById('id_register-email')
            re.value = Date().replace(/[\D-]/gi, '') + '@anicat.net'
            re.nextSibling.click()
        },
        'loggedform': function(){
            var menu = getElementsByClassName('rightmenu')[1]
            var a = filter(function(el){
                return /\/stat\/$/g.test(el.href)
                }, menu.childNodes)[0]
            if(a) a.click()
            var show = document.getElementById('show')
            show.options[2].selected = true
            show.onchange()
        },

        'logout': function(){
            var lf = document.getElementById('loginform')
            if(lf)
                throw Error('Must be in logined mode.')
            var menu = filter(function(el){
                return /\/logout\/$/g.test(el.href)
            }, document.getElementById('usermenu').childNodes)
            if(!menu || !menu[0])
                throw Error('Logout not found')
            menu[0].click()
        }
    }, {'all': ['show', 'void_login', 'bad_login', 'show_more',
        'register_fail', 'register_success', 'loggedform']})
})