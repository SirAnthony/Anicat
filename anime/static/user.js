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
		user.info = document.getElementById('logininfo');
		user.loaded = true;
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
		var rform = document.getElementById('login');
		var formData = getFormData(rform);
		ajax.loadXMLDoc(url+'login/', formData);
	}

	this.logout = function(){
		if(!this.loaded) return;
		//cookies.del('SESSION');
		var div = document.getElementById('logdiv');
		element.removeAllChilds(div);
		while(div.nextSibling)
			element.remove(div.nextSibling);
		element.appendChild(div, [{'a': {href: '', onclick: function(){quickreg();},
								innerText: 'Account', className: "nurl"}}]);
		element.appendChild(div.parentNode, [{'div': {id: 'logdv'}}, [
										{'form': {id: 'login', className: 'thdtbl',
											onsubmit: function(){ user.login(); return false;}}}, [
											{'input': {id: 'id_username', type: 'text', name: 'username'}},
											{'input': {id: 'id_password', type: 'password', name: 'password'}},
											{'input': {type: 'submit', value: 'Login'}},
											{'p': {id: 'logininfo', className: 'error'}}]]]);
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
			{'span': {}}, [
				{'a': {'href': '/', title: 'User settings', innerText: nick}}],
			{'a': {className: 'nurl', innerText: 'Logout',
									onclick: function(){user.logout();}}}
		]);
		var select = element.create('select', {id: 'show', onchange: function(){setshow();}});
		element.appendChild(select, [{'option': {value: '', text: 'Display Mode', selected: 'selected'}}]);
		element.addOption(select, {'a': 'All', '0': 'None', '1': 'Want', '2': 'Now',
									'3': 'Watched', '4': 'Dropped', '5': 'Partially watched'});
		element.appendChild(form.parentNode, [
			{'div': {className: 'rightmenu'}}, [
				{'a': {href: '/stat/', className: 'nurl', innerText: 'Statistics'}},
				select
			]
		]);
		element.appendChild(document.getElementsByTagName("head")[0], [
		    {'script': {'type': 'text/javascript', 'src': '/static/ae.js'}}
		]);
	}

	this.loginFail = function(text){
		if(!this.loaded) return;
		document.getElementById('menu').style.display = 'none';
		this.inform(text.__all__);
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
								{'form': {'id': 'register'}}, [
									{'span': {'className': 'left', innerText: 'Quick registration'}},
									{'label': {'for': 'id_register-username', innerText: 'Login:'}},
									{'input': {'id': 'id_register-username', type: 'text', name: 'register-username'}},
									{'label': {'for': 'id_register-email', innerText: 'E-Mail:'}},
									{'input': {'id': 'id_register-email', type: 'text', name: 'register-email'}},
									{'label': {'for': 'id_register-password1', innerText: 'Password:'}},
									{'input': {'id': 'id_register-password1', type: 'password', name: 'register-password1'}},
									{'label': {'for': 'id_register-password2', innerText: 'Confirm:'}},
									{'input': {'id': 'id_register-password2', type: 'password', name: 'register-password2'}},
									{'input': {type: 'button', onclick: function(){user.register();}, value: 'Ok'}},
									{'input': {type: 'button', onclick: function(){user.register('abort');}, value: 'Cancel'}}]
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
		    var formData = getFormData(form);
			errors = getElementsByClassName('error', form);
			element.remove(errors);
			if(!this.registerForm)
				this.registerForm = form.parentNode.removeChild(form);
			ajax.loadXMLDoc(url+'register/', formData);
		}
	}

	this.registerFail = function(error){
		if(!this.loaded || !this.registerForm) return;
		var div = document.getElementById('mspan');
		element.removeAllChilds(div);
		element.appendChild(div, [this.registerForm]);
		for(var target in error){
			var obj = document.getElementById('id_register-'+target);
			if(!obj) continue;
			for(var e in error[target]){
				element.insert(obj.nextSibling, {'span': {className: 'error left', innerText: error[target][e]}});
			}
		}
	}

})();

addEvent(window, 'load', user.init);