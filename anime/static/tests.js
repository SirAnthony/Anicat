
function TestRunner(tests, prepare){

    this.timer = {};
    this.tests = tests;
    this.prepare = {};

    for(var t in prepare){
        if(!isArray(prepare[t]))
            continue;
        this.prepare[t] = filter((function(tests){
            return function(el){
                if(tests[el] || prepare[el])
                    return true;
                else
                    throw Error('Test ' + e + 'not found in ' + tests + '.');
            };
        })(this.tests), prepare[t]);
    }


    this.run = function(name){
        var test = null;
        if(name)
            test = this.tests[name];
        else
            test = this.tests;
        var pn = this.prepare[name];
        if(pn){
            for(var pname in pn)
                this.run(pn[pname]);
        }
        if(isFunction(test))
            this.timer[test] = setTimeout((function(t, test){
                return function(){
                    test.call(t);
                    delete t.timer[test];
                };
            })(this, test), (hashCount(this.timer) + 1) * 1000);
    }

}


var Tests = new (function(){

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
    }, {'rsort': ['sort'], 'all': ['sort', 'rsort', 'page']});

    this.test_cnt = new TestRunner({
        'link': function(){
            var l = getElementsByClassName('link', document, 'td')[0];
            l.firstChild.click();
        },
        'id': function(){
            getElementsByClassName('id', document, 'td')[0].click()
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
            var state = document.getElementById('id_state');
            state.options[2].selected = true;
            state.onchange();
        },
    }, {'id_send': ['id'],
        'all': ['type', 'release', 'episodes', 'id', 'link']});

    this.test_card = new TestRunner({
        'open': function(){
            var l = getElementsByClassName('link', document, 'td')[0];
            l.firstChild.click();
        },
        'edit': function(){
            var card = document.getElementById('card');
            var elements = getElementsByClassName('right', card, 'a');
            for(var e = 0; e < elements.length; e++)
                elements[e].click();
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

    }, {'edit': ['open'], 'send': ['edit'], 'cancel': ['edit']});

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
            var el = getElementsByClassName('statwant', document.getElementById('statistic'), 'td')[0]
            el.parentNode.lastChild.click();
        },
        'open_link_now': function(){
            var el = getElementsByClassName('statnow', document.getElementById('statistic'), 'td')[0]
            el.parentNode.lastChild.click();
        },
        'open_link_done': function(){
            var el = getElementsByClassName('statdone', document.getElementById('statistic'), 'td')[0]
            el.parentNode.lastChild.click();
        },
        'open_link_drop': function(){
            var el = getElementsByClassName('statdropped', document.getElementById('statistic'), 'td')[0]
            el.parentNode.lastChild.click();
        },
        'open_link_part': function(){
            var el = getElementsByClassName('statpartially', document.getElementById('statistic'), 'td')[0]
            el.parentNode.lastChild.click();
        },
        'open_id': function(){
            getElementsByClassName('id', document, 'td')[0].click()
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
        'bad_login': function(){

        }
    });

    this.test_add = new TestRunner({
        'show': function(){
            if(!document.getElementById('addform'))
                return;
            var h = getElementsByClassName('leftmenu')[0];
            if(h.lastChild.href = '/add/')
                h.lastChild.click();
        },
        'fill_type': function(){ // Not works
            var form = document.getElementById('addform');
            if(!form)
                return;
            toggle(form, 1);
            var type = document.getElementById('id_releaseType');
            type.onchange();
            type.options[0].selected = false;
            type.options[1].selected = true;
            type.onchange();
            type.options[1].selected = false;
            type.options[2].selected = true;
            type.onchange();
            type.options[2].selected = false;
            type.options[3].selected = true;
            type.onchange();
        },
        'send_blank': function(){
            var form = document.getElementById('addform');
            if(!form)
                return;
            toggle(form, 1);
            form.lastChild.onclick({});
        }

    });

    this.test_filter = new TestRunner({
        'show': function(){
            var h = getElementsByClassName('leftmenu');
            h = filter(function(el){ if(!el.href) return true; }, h)[0]
            h.click();
        },
        'apply': function(){
            var fl = document.getElementById('id_filter_container');
            toggle(fl, 1);
            var rt = document.getElementById('id_filter_releaseType');
            rt.options[0].selected = true;
            fl.lastChild.previousSibling.click();
        },
        'clear': function(){
            var fl = document.getElementById('id_filter_container');
            toggle(fl, 1);
            var rt = document.getElementById('id_filter_releaseType');
            rt.options[0].selected = true;
            fl.lastChild.previousSibling.previousSibling.click();
        },
        'error': function(){
            var fl = document.getElementById('id_filter_container');
            toggle(fl, 1);
            document.getElementById('id_releasedAt_0').value = "a"
            fl.lastChild.previousSibling.click();
        },
    }, {'all': ['show', 'apply', 'clear', 'error']});

    this.start = function(){
        var testre = document.location.hash.match(/^#test\/(\w+)(\/(\w+))?/);
        if(!testre)
            return;
        var testname = testre[1];
        var subtest = testre[3];
        if(!testname)
            return;

        var test = this['test_'+testname];
        if(!test || !test.run)
            return;
        else
            test.run(subtest);

    }

})();


addEvent(window, 'load', function(){ Tests.start(); });
