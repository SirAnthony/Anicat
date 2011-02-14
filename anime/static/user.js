//################# Работа с аккуантом

//FIXME: как-то здесь плохо все

var user = new( function(){
       
    var info = null;
    var loaded = false;
    
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
            if(!div.firstChild || !(div.childNodes[1] && div.childNodes[1] == register)){
                element.removeAllChilds(div);
                element.appendChild(div, [
                                {'elemType': 'label', 'for': 'register', innerText: 'Quick registration'},
                                {'elemType': 'form', 'id': 'register'}, [
                                    {'elemType':'label', 'id': 'registerinfo', value: 'Some Fail'},
                                    {'elemType': 'label','for': 'rname', innerText: 'Login:'},
                                    {'elemType':'input', 'id': 'rname', type: 'text'},
                                    {'elemType':'label', 'for': 'rpass', innerText: 'Password:'},
                                    {'elemType':'input', 'id': 'rpass', type: 'password'},
                                    {'elemType':'label', 'for': 'rpasschk', innerText: 'Confirm:'},
                                    {'elemType':'input', 'id': 'rpasschk', type: 'password'},
                                    {'elemType':'label', 'for': 'rmail', innerText: 'E-Mail:'},
                                    {'elemType':'input', 'id': 'rmail', type: 'text'},
                                    {'elemType':'input', type: 'button', onclick: function(){user.register();}, value: 'Ok'},
                                    {'elemType':'input', type: 'button', onclick: function(){user.register('abort');}, value: 'Cancel'}]
                                ]);
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
            var infobj =  document.getElementById('registerinfo');
            var nick = document.getElementById('rname');
            var pass = document.getElementById('rpass');
            var passchk = document.getElementById('rpasschk');
            var mail = document.getElementById('rmail')
            nick = nick.value;
            pass = pass.value;
            passchk = passchk.value;
            mail = mail.value.toLowerCase();
            if(!nick || !pass || !mail){
                inform('Not all fields are filled', infobj);
            }else if(/[\W]/.test(nick) || /[\W]/.test(pass)){
                inform('Username and password can only consist of letters, digits or underscore characters', infobj);
            }else if(pass != passchk){
                inform('Passwords are different', infobj);
            }else if(!/^[\w.-]+@([a-z0-9\-]+\.)+[a-z]{2,6}$/i.test(mail)){
                inform('This e-mail is not valid', infobj);
            }else if(nick.length < 4){    
                inform('Name must be at least 4 characters', infobj);
            }else if(pass.length < 4){
                inform('Password must be at least 4 characters', infobj);
            }else{
                var qw = {'name': nick, 'pass': pass, 'mail': mail};                        
                ajax.loadXMLDoc(url+'/register/', qw);
                document.getElementById('menu').style.display = 'none';
            }                
        }    
    }
    
})();
