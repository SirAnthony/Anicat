/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * User module
 *
 */

define(['base/storage', 'base/message', 'base/stylesheet', 'base/ajax',
    'base/request_processor'],
    function (catalog_storage, message, stylesheet, ajax, RequestProcessor){

    var _processor = null;
    var _resize_events = [];

    function emit_resize(){
        for(var ev in _resize_events)
            _resize_events[ev][0].apply(_resize_events[ev].slice(1));
    }

    return {
        loaded: false,
        logined: false,

        inform: function(msg, obj){
            if(!this.loaded) return;
            var info = obj;
            if(!info)
                throw new Error('Bad object passed for error rendering.');
            info.innerText = msg;
            toggle(info.parentNode, 1);
            emit_resize();
        },

        init: function(){
            var info = document.getElementById('logininfo');
            if(!info){
                this.logined = true;
                catalog_storage.disable();
            }else{
                catalog_storage.enable();
            }
            this.loaded = true;
            _processor = new RequestProcessor({'login': function(resp){
                    message.hide();
                    if(resp.status){
                        this.loginSuccess(resp.text);
                        stylesheet.update('/css/');
                    }else
                        this.loginFail(resp.text);
                },
                'register': function(resp){
                    message.hide();
                    if(!resp.status){
                        this.registerFail(resp.text);
                    }else{
                        this.loginSuccess(resp.text);
                        stylesheet.update('/css/');
                    }
                }
            }, this);
        },

        toggle: function(){
            if(!this.loaded) return true;
            var loginform = document.getElementById('loginform');
            if(!loginform) return true;
            toggle(loginform);
            emit_resize();
            return false;
        },

        more: function(){
            if(!this.loaded) return;
            var ldvm = document.getElementById('logdvmore');
            if(!ldvm) return;
            toggle(ldvm);
            emit_resize();
        },

        login: function(e){
            if(!this.loaded || user.logined) return true;
            toggle(document.getElementById('logininfo').parentNode, -1);
            var rform = document.getElementById('login');
            var formData = getFormData(rform);
            ajax.load('login', formData, processor);
            message.toEventPosition(e);
            return false;
        },

        alterlogin: function(url){
            if(!this.loaded || user.logined) return true;
            if(url == 'openid'){
                var l = document.getElementById('login_openid').parentNode;
                toggle(l);
                if(!visible(l))
                    toggle(document.getElementById('socialinfo').parentNode, -1);
            }else{
                toggle(document.getElementById('socialinfo').parentNode, -1);
                var w = 700;
                var h = 500;
                var login_form = null;
                var prop = 'height=' + h + ',width=' + w + ',left=0,top=0,resizable=yes,scrollbars=yes,toolbar=no,menubar=no,location=yes,directories=no,status=yes';
                if(url == '/login/openid/'){
                    url = '';
                    login_form = document.getElementById('login_openid');
                }
                window.open(url, "Login", prop);
                if(login_form)
                    login_form.submit();
            }
            emit_resize();
            return false;
        },

        logout: function(){
            if(!this.loaded) return;
            this.logined = false;
            var div = document.getElementById('usermenu');
            element.removeAllChilds(div);
            while(div.nextSibling)
                element.remove(div.nextSibling);
            element.appendChild(div, [{'a': {href: '', innerText: 'Account'}}]);
            element.appendChild(div.parentNode, [{'div': {id: 'loginform'}}, [
                                            {'form': {id: 'login', className: 'thdtbl',
                                                onsubmit: function(){ user.login(); return false;}}}, [
                                                {'input': {id: 'id_username', type: 'text', name: 'username'}},
                                                {'input': {id: 'id_password', type: 'password', name: 'password'}},
                                                {'input': {type: 'submit', value: 'Login'}},
                                                {'p': {id: 'logininfo', className: 'error'}}]]]);
            catalog_storage.disable();
            window.location.replace('/logout/'); //Возможно, когда-нибудь будет без релоада, но зачем?
        },

        loginSuccess: function(text){
            if(!this.loaded) return;
            var form = document.getElementById('usermenu');
            var nick = text.name ? encd(text.name) : '%USERNAME%';
            var loginform = document.getElementById('loginform');
            element.insert(loginform, {'div': {'id': 'statistic', 'className': 'right'}});
            element.remove(loginform);
            element.removeAllChilds(form);
            element.appendChild(form, [
                {'span': {className: 'delimiter', innerText: '|'}}, {'span': {}}, [
                    {'a': {'href': '/settings/', title: 'User settings', innerText: nick}}],
                {'span': {className: 'delimiter', innerText: '|'}},
                {'a': {href: '/logout/', innerText: 'Logout', onclick: function(){user.logout();}}}
            ]);
            element.appendChild(form.parentNode, [
                {'div': {className: 'rightmenu'}}, [
                    {'a': {href: '/stat/', innerText: 'Statistics⇣',
                        'onclick': function(){
                            statistics.toggle(); return false; }}},
                    {'span': {className: 'delimiter', innerText: '|'}},
                    {'div': {className: 'select'}}, [
                        {'select': {id: 'show', onchange: function(){setshow();}}},
                        element.addOption(false, {'a': 'All', '0': 'None', '1': 'Want', '2': 'Now',
                                        '3': 'Watched', '4': 'Dropped', '5': 'Partially watched'}),
                        {'span': {innerText: 'Display Mode\xa0\xa0⇵'}},
                    ]
                ]
            ]);
            this.logined = true;
            statistics.getStat();
            catalog_storage.disable();
        },

        loginFail: function(text, obj){

            if(!this.loaded) return;
            var info = document.getElementById(obj ? obj : 'logininfo');
            this.inform(text.__all__ ? text.__all__ : ( // Everything better with lambda
                function(arr){
                    var s = '';
                    for(var el in arr) s += el + ': ' + arr[el] + ' ';
                    return s;
                })(text), info);
        },

        register: function(e){
            if(!this.loaded) return true;
            var form = document.getElementById('register');
            var formData = getFormData(form);
            var obj = document.getElementById('registerinfo');
            var errors = getElementsByClassName('error', obj);
            element.remove(errors);
            toggle(obj.parentNode, -1);
            ajax.load('register', formData, processor);
            message.toEventPosition(e);
            return false;
        },

        registerFail: function(error){
            if(!this.loaded) return;
            var obj = document.getElementById('registerinfo');
            if(!obj)
                return;
            for(var target in error){
                for(var e in error[target]){
                    element.appendChild(obj, {'span': {className: 'error', innerText: error[target][e]}}, true);
                }
            }
            toggle(obj.parentNode, 1);
            emit_resize();
        },

        addEvent: function(func, environ){
            _resize_events.push(Array.prototype.slice.call(arguments, 0));
        },

        removeEvent: function(func){
            _resize_events = filter(function(el){ return el[0] !== func;
                }, _resize_events);
        }
    };
});
