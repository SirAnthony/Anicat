//################# Работа с аккуантом

//FIXME: как-то здесь плохо все

var user = new( function(){
       
    var info = null;
    var loaded = false;
    var registerForm = null; //Ох, костыли.
    
    this.inform = function(msg, obj){
        if(!this.loaded) return;
        var info = info;
        if(obj) info = obj;
        this.info.innerText = msg;
        this.info.style.display = 'block';
    }
    
    this.init = function(){
        this.info = document.getElementById('logininfo');
        this.loaded = true;
    }    
    
    this.toggle = function(){
        if(!this.loaded) return;
        login = document.getElementById('logdv');
        if(!login) return;
        if(login.style.display == 'block'){
            login.style.display = 'none';
        }else{
            login.style.display = 'block';
        }
    }
        
    this.login = function(){
        if(!this.loaded) return;
        this.info.style.display = 'none';
        var nick = document.getElementById('lname');
        var pass = document.getElementById('lpasswd');
        //var cb = document.getElementById('long').checked;
        nick = nick.value;
        pass = pass.value;
        if(!nick || !pass){
            inform('Not all fields are filled');
        }else{
            var qw = {'name': nick, 'pass': pass};        
            ajax.loadXMLDoc(url+'login/', qw);
        }
    }
    
    this.logout = function(){
        if(!this.loaded) return;
        //cookies.del('SESSION');
        var div = document.getElementById('logdiv');         
        element.removeAllChilds(div);
        div.parentNode.removeChild(div.nextSibling);
        var a = element.create('a', {href: '', onclick: function(){quickreg();},
                                innerText: 'Account', className: "nurl"});
        element.appendChild(div, [a]);
        var ldiv = element.create('div', {id: 'logdv'});
        var form = element.create('form', {id: 'login', className: 'thdtbl'});
        var i1 = element.create('input', {id: 'lname', type: 'text'});
        var i2 = element.create('input', {id: 'lpasswd', type: 'password'});
        var ib = element.create('input', {onclick: function(){quickreg();}, type: 'button',
                                value: 'Enter'});
        /*var ir = element.create('input', {id: 'long', type: 'checkbox'});
        var il = element.create('label', {'for': 'long', id: 'lngs', innerText: 'Remember'});*/
        var p = element.create('p', {id: 'logininfo'});
        element.appendChild(div.parentNode, [ldiv, [form, [i1, i2, ib, /*ir, il,*/ p]]]);    
        window.location.replace('/logout/');//Возможно, когда-нибудь будет без релоада 
    }
    
    this.loginSuccess = function(text){
        if(!this.loaded) return;
        var nick;
        ((text.name) ? nick = encd(text.name) : nick = '%USERNAME%');
        var form = document.getElementById('logdiv');
        var logdv = document.getElementById('logdv');                
        element.removeAllChilds(form);
        element.removeAllChilds(logdv);
        logdv.parentNode.removeChild(logdv);
        element.appendChild(form, [
            element.create('div', {id: 'logdiv'}), [
                element.create('span', {innerText: 'You logged as '+nick})
            ]
       ]);
    }
    
    this.loginFail = function(text){
        if(!this.loaded) return;
        document.getElementById('menu').style.display = 'none';
        this.inform(text);
    }
    
    this.quickreg = function(){
        if(!this.loaded) return;
        var dv = document.getElementById('menu');
        var displ = dv.style.display;
        if( displ == 'block'){
            dv.style.display = 'none';
        }else{
            var div = document.getElementById('mspan');
            var register = document.getElementById('register');
            if(!register && this.registerForm){
                element.removeAllChilds(div);
                element.appendChild(div, [this.registerForm]);
            }else{                
                if(!div.firstChild || !(div.childNodes[1] && div.childNodes[1] == register)){
                    element.removeAllChilds(div);
                    element.appendChild(div, [
                                {'elemType': 'form', 'id': 'register'}, [
                                    {'elemType': 'span', 'className': 'left', innerText: 'Quick registration'},
                                    {'elemType': 'label', 'for': 'id_username', innerText: 'Login:'},
                                    {'elemType': 'input', 'id': 'id_username', type: 'text'},
                                    {'elemType': 'label', 'for': 'id_email', innerText: 'E-Mail:'},
                                    {'elemType': 'input', 'id': 'id_email', type: 'text'},
                                    {'elemType': 'label', 'for': 'id_password1', innerText: 'Password:'},
                                    {'elemType': 'input', 'id': 'id_password1', type: 'password'},
                                    {'elemType': 'label', 'for': 'id_password2', innerText: 'Confirm:'},
                                    {'elemType': 'input', 'id': 'id_password2', type: 'password'},                                    
                                    {'elemType': 'input', type: 'button', onclick: function(){user.register();}, value: 'Ok'},
                                    {'elemType': 'input', type: 'button', onclick: function(){user.register('abort');}, value: 'Cancel'}]
                                ]);
                }
            }
            dv.style.display = 'block';
            try{
                dv.style.top = '60px';
                dv.style.left = document.getElementById('logdv').offsetLeft - dv.offsetWidth/2 + 'px';
            }catch(e){}
        }
    }
    
    this.register = function(cncl){
        if(!this.loaded) return;
        if(cncl == 'abort'){
            document.getElementById('menu').style.display = 'none';
        }else{
            var form = document.getElementById('register');
            var nick = document.getElementById('id_username');
            var pass = document.getElementById('id_password1');
            var passchk = document.getElementById('id_password2');
            var mail = document.getElementById('id_email');
            nick = nick.value;
            pass = pass.value;
            passchk = passchk.value;
            mail = mail.value.toLowerCase();
            errors = getElementsByClassName('error', form);
            for(var el in errors)
                element.remove(errors[el]);
            if(!this.registerForm)
                this.registerForm = form.parentNode.removeChild(form);
            var qw = {'username': nick, 'password1': pass, 'password2': passchk, 'email': mail};                        
            ajax.loadXMLDoc(url+'register/', qw);
        }    
    }
    
    this.registerFail = function(error){
        if(!this.loaded || !this.registerForm) return;
        var div = document.getElementById('mspan');
        element.removeAllChilds(div);
        element.appendChild(div, [this.registerForm]);
        for(var target in error){
            var obj = document.getElementById('id_'+target);
            if(!obj) continue;
            for(var e in error[target]){
                element.insert(obj.nextSibling,
                        element.create('span', {className: 'error left', innerText: error[target][e]}));
            }
        }
    }
    
})();
