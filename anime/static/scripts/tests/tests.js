/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Javascript tests
 *
 */

define(['base/events', 'tests/runner'], function(events, TestRunner){

    this.ajax_calls = new Array();
    this.break_after = true; // false;

    this.test_main = new TestRunner({
        'page': function(){
            var pager = document.getElementById('pg');
            pager.getElementsByTagName('a')[0].click();
        },
        'sort': function(){
            var th = getElementsByClassName('episodes', document, 'th')[0];
            th.firstChild.click();
        },
        'rsort': function(){
            var th = getElementsByClassName('episodes', document, 'th')[0];
            th.firstChild.click();
        }
    }, {'rsort': ['sort'], 'all': ['rsort', 'page', 'sort']}, true);

    this.test_cnt = new TestRunner({
        'link': function(){
            var l = getElementsByClassName('link', document, 'td')[0];
            l.firstChild.click();
        },
        'id': function(){
            getElementsByClassName('id', document, 'td')[0].click();
        },
        'title': function(){
            getElementsByClassName('title', document, 'td')[0].click();
        },
        'episodes': function(){
            getElementsByClassName('episodes', document, 'td')[0].click();
        },
        'release': function(){
            getElementsByClassName('release', document, 'td')[0].click();
        },
        'type': function(){
            getElementsByClassName('type', document, 'td')[0].click();
        },
        'id_send': function(){
            var state = document.getElementById('id_state');
            state.options[2].selected = true;
            state.onchange();
        },
    }, {'id_send': ['id'],
        'all': ['type', 'release', 3000, 'episodes', 'title', 'id', 'link', 'id_send']});

    this.test_card = new TestRunner({
        'open': function(){
            var l = getElementsByClassName('link', document, 'td')[0];
            l.firstChild.click();
        },
        'edit': function(){
            var card = document.getElementById('card');
            var elements = getElementsByClassName('right', card, 'a');
            for(var e = 0; e < elements.length; e++){
                if(elements[e].innerText != 'Submit new')
                    elements[e].click();
            }
        },
        'send': function(){
            var card = document.getElementById('card');
            var elements = getElementsByClassName('right', card, 'a');
            for(var e = 0; e < elements.length; e++)
                if(elements[e].innerText == 'Save')
                    elements[e].click();
        },
        'cancel': function(){
            var card = document.getElementById('card');
            var elements = getElementsByClassName('right', card, 'a');
            for(var e = 0; e < elements.length; e++)
                if(elements[e].innerText == 'Cancel')
                    elements[e].click();
        },

    }, {'edit': ['open'], 'send': ['edit'], 'cancel': ['edit'],
        'all': ['edit', 5000, 'send', 5000, 'cancel']});

    this.test_statistics = new TestRunner({
        'show': function(){
            var stat = document.getElementById('statistic');
            if(!stat.childNodes.length || stat.style.display != 'block'){
                var menu = document.getElementById('usermenu');
                if(menu.nextSibling)
                    menu = menu.nextSibling;
                menu.firstChild.click();
            }
        },
        'open_link_want': function(){
            var el = getElementsByClassName('statwant', document.getElementById('statistic'), 'td')[0];
            el.parentNode.lastChild.click();
        },
        'open_link_now': function(){
            var el = getElementsByClassName('statnow', document.getElementById('statistic'), 'td')[0];
            el.parentNode.lastChild.click();
        },
        'open_link_done': function(){
            var el = getElementsByClassName('statdone', document.getElementById('statistic'), 'td')[0];
            el.parentNode.lastChild.click();
        },
        'open_link_drop': function(){
            var el = getElementsByClassName('statdropped', document.getElementById('statistic'), 'td')[0];
            el.parentNode.lastChild.click();
        },
        'open_link_part': function(){
            var el = getElementsByClassName('statpartially', document.getElementById('statistic'), 'td')[0];
            el.parentNode.lastChild.click();
        },
        'open_id': function(){
            getElementsByClassName('id', document, 'td')[0].click();
        },
        'id_send': function(){
            var state = document.getElementById('id_state');
            state.options[3].selected = true;
            state.onchange();
        }
    }, {'change': ['show', 'open_id', 'id_send'], 'all': ['change', 'open_link'],
        'open_link': ['show', 'open_link_want', 'open_link_now', 'open_link_done',
        'open_link_drop', 'open_link_part'],
        'open_link_want': ['show'], 'open_link_now': ['show'], 'open_link_done': ['show'],
        'open_link_drop': ['show'], 'open_link_part': ['show'],});

    this.test_user = new TestRunner({
        'show': function(){
            var lf = document.getElementById('loginform');
            if(!lf)
                throw Error('Must be in non-logined mode.');
            toggle(lf, -1);
            var menu = filter(function(el){
                return /\/login\/$/g.test(el.href);
            }, document.getElementById('usermenu').childNodes);
            if(!menu || !menu[0])
                throw Error('Must be in non-logined mode.');
            menu[0].click();
        },
        'void_login': function(){
            var lf = document.getElementById('loginform');
            if(!lf)
                throw Error('Must be in non-logined mode.');
            toggle(lf, 1);
            document.getElementById('id_username').value = '';
            var pass = document.getElementById('id_password');
            pass.value = '';
            pass.nextSibling.click();
        },
        'bad_login': function(){
            var lf = document.getElementById('loginform');
            if(!lf)
                throw Error('Must be in non-logined mode.');
            toggle(lf, 1);
            document.getElementById('id_username').value = 'a';
            var pass = document.getElementById('id_password');
            pass.value = 'a';
            pass.nextSibling.click();
        },
        'show_more': function(){
            var lf = document.getElementById('loginform');
            if(!lf)
                throw Error('Must be in non-logined mode.');
            toggle(lf, 1);
            document.getElementById('register-more').click();
        },
        'register_fail': function(){
            var lf = document.getElementById('loginform');
            if(!lf)
                throw Error('Must be in non-logined mode.');
            toggle(lf, 1);
            toggle(document.getElementById('logdvmore'), 1);
            var re = document.getElementById('id_register-email');
            re.value = 'aa';
            re.nextSibling.click();
        },
        'register_success': function(){
            var lf = document.getElementById('loginform');
            if(!lf)
                throw Error('Must be in non-logined mode.');
            toggle(lf, 1);
            toggle(document.getElementById('logdvmore'), 1);
            var re = document.getElementById('id_register-email');
            re.value = Date().replace(/[\D-]/gi, '') + '@anicat.net';
            re.nextSibling.click();
        },
        'loggedform': function(){
            var menu = getElementsByClassName('rightmenu')[1];
            var a = filter(function(el){
                return /\/stat\/$/g.test(el.href);
                }, menu.childNodes)[0];
            if(a) a.click();
            var show = document.getElementById('show');
            show.options[2].selected = true;
            show.onchange();
        },

        'logout': function(){
            var lf = document.getElementById('loginform');
            if(lf)
                throw Error('Must be in logined mode.');
            var menu = filter(function(el){
                return /\/logout\/$/g.test(el.href);
            }, document.getElementById('usermenu').childNodes);
            if(!menu || !menu[0])
                throw Error('Logout not found');
            menu[0].click();
        }
    }, {'all': ['show', 'void_login', 'bad_login', 'show_more',
        'register_fail', 'register_success', 'loggedform']});

    this.test_add = new TestRunner({
        'show': function(){
            if(!document.getElementById('addform'))
                return;
            var h = getElementsByClassName('leftmenu')[0];
            if(h.lastChild.href == '/add/')
                h.lastChild.click();
        },
        'fill_type': function(){ // Not works
            var form = document.getElementById('addform');
            if(!form)
                return;
            toggle(form, 1);
            var type = document.getElementById('id_releaseType');
            add.typeChange.call(type);
            type.options[0].selected = false;
            type.options[1].selected = true;
            add.typeChange.call(type);
            type.options[1].selected = false;
            type.options[2].selected = true;
            add.typeChange.call(type);
            type.options[2].selected = false;
            type.options[3].selected = true;
            add.typeChange.call(type);
        },
        'fill_genre': function(){
            var form = document.getElementById('addform');
            if(!form)
                return;
            toggle(form, 1);
            var link = document.getElementById('ImportAddLink');
            link.click();
            link.click();
            var genre = document.getElementById('id_genre');
            genre.options[2].selected = true;
            genre.options[3].selected = true;
        },
        'fill_date': function(){
            var form = document.getElementById('addform');
            if(!form)
                return;
            toggle(form, 1);
            var date = document.getElementById('id_releasedAt');
            date.value = '25.09.2012';
        },
        'fill_title': function(){
            var form = document.getElementById('addform');
            if(!form)
                return;
            toggle(form, 1);
            var title = document.getElementById('id_title');
            title.value = Date().replace(/[\D-]/gi, '');
        },
        'send_blank': function(){
            var form = document.getElementById('addform');
            if(!form)
                return;
            toggle(form, 1);
            form.lastChild.onclick({});
        },
        'calendar': function(){
            var form = document.getElementById('addform');
            if(!form)
                return;
            toggle(form, 1);
            var cal = getElementsByClassName('datetimeshortcuts', form, 'span').pop();
            if(!cal || !cal.firstChild)
                throw Error('Calendar not found');
            cal.firstChild.click();
            cal.firstChild.click();
            var box = getElementsByClassName('calendarbox').pop();
            map(function(el){ el.click && el.click(); }, box.getElementsByTagName('a'));
        },
        'submit': function(){
            var form = document.getElementById('addform');
            if(!form)
                return;
            toggle(form, 1);
            form.lastChild.click();
        }
    }, {'all': ['show', 'send_blank', 'fill_type', 'calendar', 'submit', 5000, 'show'],
    'submit': ['fill_type', 'calendar', 'fill_genre', 'fill_date', 'fill_title']});

    this.test_filter = new TestRunner({
        'show': function(){
            var h = document.getElementsByTagName('a');
            h = filter(function(el){
                return /^filter/gi.test(el.innerText); }, h, null, true)[0];
            h.click();
        },
        'apply': function(){
            var fl = document.getElementById('id_filter_container');
            toggle(fl, 1);
            var rt = document.getElementById('id_filter_releaseType');
            rt.options[0].selected = true;
            fl.lastChild.previousSibling.click();
        },
        'clear_select': function(){
            var fl = document.getElementById('id_filter_container');
            toggle(fl, 1);
            var rt = document.getElementById('id_filter_releaseType');
            rt.options[0].selected = true;
            rt.parentNode.parentNode.firstChild.click();
        },
        'clear': function(){
            var fl = document.getElementById('id_filter_container');
            toggle(fl, 1);
            var rt = document.getElementById('id_filter_releaseType');
            rt.options[0].selected = true;
            fl.lastChild.previousSibling.previousSibling.click();
            fl.lastChild.previousSibling.click();
        },
        'error': function(){
            var fl = document.getElementById('id_filter_container');
            toggle(fl, 1);
            document.getElementById('id_releasedAt_0').value = "a";
            fl.lastChild.previousSibling.click();
        },
    }, {'all': ['show', 'apply', 'clear', 'clear_select',
                'error']});

    this.test_search = new TestRunner({
        'show': function(){
            var search = filter(function(el){
                return /\/search\/$/g.test(el.href); },
                document.getElementsByTagName('a'))[0];
            if(!search)
                throw Error('Search not found.');
            search.click();
        },
        'submit_blank': function(){
            toggle(document.getElementById('srch'), 1);
            var input = document.getElementById('sin');
            input.value = '';
            input.nextSibling.click();
        },
        'submit': function(){
            toggle(document.getElementById('srch'), 1);
            var input = document.getElementById('sin');
            input.value = 'zaa';
            input.nextSibling.click();
        },
        'pages': function(){
            var pg = document.getElementById('srchpg');
            pg.lastChild.click();
        }
    }, {'pages': ['submit'], 'all': ['show', 'submit_blank', 'submit', 'pages']}, true);

    this.start = function(){
        var testre = document.location.hash.match(/^#test\/(\w+)(\/(\w+))?/);
        if(!testre)
            return;
        var testname = testre[1];
        var subtest = testre[3];
        if(!testname)
            return;

        // Redefine ajax.load to setup status to running when called
        AjaxClass.prototype.load = function(url, qry, processor){
            Tests.ajax_calls.push([this, url, qry, processor]);
            StatusManager.take();
            ajax.loadXMLDoc.call(ajax, url, qry, processor);
        };

        // Define postprocessor for requests
        RequestProcessor.prototype._parsed = function(){
            StatusManager.put();
            if(!Tests.ajax_calls.pop())
                StatusManager.take(); // Parser was called without server call
        };

        var test = this['test_'+testname];
        if(!test || !test.run)
            return;
        else
            test.run(subtest);

    };

    if(this.break_after){
        events.onload(function(){
            this.continue_bt = document.getElementById('test_c_bt');
            if(!this.continue_bt){
                this.continue_bt = element.create('input', {'value': 'next',
                    'id': 'test_c_bt', 'style': {'position': 'fixed',
                    'right': '500px', 'bottom': '0px'},  'type': 'button'});
                element.appendChild(document.body, this.continue_bt);
            }
        }, this);
    }

    events.onload(this.start, this);
});