//################# Работа с аккуантом

//FIXME: как-то здесь плохо все

var user = new( function(){

    var loaded = false;
    var logined = false;

    this.inform = function(msg, obj){
        if(!this.loaded) return;
        var info = obj;
        if(!info)
            throw new Error('Bad object passed for error rendering.');
        info.innerText = msg;
        toggle(info, 1);
        Card.place();
    }

    this.init = function(){
        var info = document.getElementById('logininfo');
        if(!info){
            user.logined = true;
            catalog_storage.disable();
        }else{
            catalog_storage.enable();
        }
        user.loaded = true;
    }

    this.toggle = function(){
        if(!this.loaded) return true;
        var logdv = document.getElementById('logdv');
        if(!logdv) return true;
        toggle(logdv);
        Card.place();
        return false;
    }

    this.more = function(){
        if(!this.loaded) return;
        var logdv = document.getElementById('logdvmore');
        if(!logdv) return;
        toggle(logdv);
        Card.place();
    }

    this.login = function(){
        if(!this.loaded || user.logined) return true;
        toggle(document.getElementById('logininfo'), -1);
        var rform = document.getElementById('login');
        var formData = getFormData(rform);
        ajax.loadXMLDoc(url+'login/', formData);
        return false;
    }

    this.alterlogin = function(url){
        if(!this.loaded || user.logined) return true;
        if(url == 'openid'){
            toggle(document.getElementById('login_openid'));
        }else{
            toggle(document.getElementById('socialinfo'), -1);
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
        return false;
    }

    this.logout = function(){
        if(!this.loaded) return;
        this.logined = false;
        var div = document.getElementById('logdiv');
        element.removeAllChilds(div);
        while(div.nextSibling)
            element.remove(div.nextSibling);
        element.appendChild(div, [{'a': {href: '', innerText: 'Account'}}]);
        element.appendChild(div.parentNode, [{'div': {id: 'logdv'}}, [
                                        {'form': {id: 'login', className: 'thdtbl',
                                            onsubmit: function(){ user.login(); return false;}}}, [
                                            {'input': {id: 'id_username', type: 'text', name: 'username'}},
                                            {'input': {id: 'id_password', type: 'password', name: 'password'}},
                                            {'input': {type: 'submit', value: 'Login'}},
                                            {'p': {id: 'logininfo', className: 'error'}}]]]);
        catalog_storage.disable();
        window.location.replace('/logout/'); //Возможно, когда-нибудь будет без релоада, только зачем?
    }

    this.loginSuccess = function(text){
        if(!this.loaded) return;
        var nick;
        var form = document.getElementById('logdiv');
        ((text.name) ? nick = encd(text.name) : nick = '%USERNAME%');
        element.remove(document.getElementById('logdv'));
        element.removeAllChilds(form);
        element.appendChild(form, [
            {'span': {className: 'delimiter', innerText: '|'}}, {'span': {}}, [
                {'a': {'href': '/settings/', title: 'User settings', innerText: nick}}],
            {'span': {className: 'delimiter', innerText: '|'}},
            {'a': {href: '/logout/', innerText: 'Logout', onclick: function(){user.logout();}}}
        ]);
        element.appendChild(form.parentNode, [
            {'div': {className: 'rightmenu'}}, [
                {'a': {href: '/stat/', innerText: 'Statistics'}},
                {'span': {className: 'delimiter', innerText: '|'}},
                {'div': {className: 'select'}}, [
                    {'select': {id: 'show', onchange: function(){setshow();}}},
                    element.addOption(false, {'a': 'All', '0': 'None', '1': 'Want', '2': 'Now',
                                    '3': 'Watched', '4': 'Dropped', '5': 'Partially watched'}),
                    {'span': {innerText: 'Display Mode\xa0\xa0⇵'}},
                ]
            ]
        ]);
        element.appendChild(document.getElementsByTagName("head")[0], [
            {'script': {'type': 'text/javascript', 'src': '/static/ae.js'}}
        ]);
        this.logined = true;
        catalog_storage.disable();
    }

    this.loginFail = function(text, obj){
        if(!this.loaded) return;
        var info = document.getElementById(obj ? obj : 'logininfo');
        this.inform(text.__all__ ? text.__all__ : ( // Everything better with lambda
            function(arr){
                var s = '';
                for(el in arr) s += el + ': ' + arr[el] + ' ';
                return s;
            })(text), info);
    }

    this.register = function(cncl){
        if(!this.loaded) return true;
        var form = document.getElementById('register');
        var formData = getFormData(form);
        var errors = getElementsByClassName('error', form);
        element.remove(errors);
        ajax.loadXMLDoc(url+'register/', formData);
        return false;
    }

    this.registerFail = function(error){
        if(!this.loaded) return;
        for(var target in error){
            var obj = document.getElementById('id_register-'+target);
            if(!obj) continue;
            for(var e in error[target]){
                element.insert(obj, {'span': {className: 'error right', innerText: error[target][e]}}, true);
            }
        }
    }

})();

var catalog_storage = new (function(){

    this.enabled = false;

    this.getStatus = function(id, types){
        var num = 0;
        var value = null;
        if(typeof user_storage != "undefined" && user_storage.loaded){
            this.enable()
            num = user_storage.getItem('list.'+id);
            if(!num) num = 0;
            if(types) value = types[num];
        }else{
            value = 'Enable local storage to use catalog anonymously.';
        }
        return {'state': num, 'value': value}
    }

    this.addStatus = function(id, value){
        if(!this.enabled)
            throw new Error('Local storage not enabled.');
        if(!id)
            throw new Error('Bad item id.');
        if(!value)
            value = 0;
        return user_storage.addItem('list.'+id, value);
    }

    this.enable = function(){
        if(typeof user_storage != "undefined" && user_storage.loaded){
            if(!user_storage.enabled) user_storage.enable();
            this.enabled = true;
            return true;
        }
    }

    this.disable = function(){
        this.enabled = false;
        if(typeof user_storage != "undefined" && user_storage.loaded){
            if(user_storage.enabled) user_storage.disable();
            return true;
        }
    }


})();

addEvent(window, 'load', user.init);
