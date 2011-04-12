//##############################################################################
//###############################	Аякс	####################################
//##############################################################################

var ajax = new (function(){

	var xmlHttp = null;
	var cookie = cookies;

	//################# Вызов аяксового обьекта.
	this.loadXMLDoc = function(url, qry){
		var request = '';
		if(!isHash(qry)){
			alert('Input is old');
			return;
		}

		setRequest();

		if(!(/^http:.*/.test(url) || /^https:.*/.test(url)))
			qry['csrfmiddlewaretoken'] = cookie.get('csrftoken');

		for(item in qry){
			if(!qry[item]) continue;
			if(request)
				request += '&';
			if(isArray(qry[item])){
				var e = new Array();
				for(var i in qry[item])
					e.push(item + '=' + qry[item][i]);
				request += e.join('&');
			}else{
				request += item + '=' + qry[item];
			}
		}

		xmlHttp = null;
		if(window.XMLHttpRequest){
			try{
				xmlHttp = new XMLHttpRequest();
			}catch(e){}
		}else if(window.ActiveXObject){
			try{
				xmlHttp = new ActiveXObject('Msxml2.XMLHTTP');
			}catch(e){
				try{
					xmlHttp = new ActiveXObject('Microsoft.XMLHTTP');
				}catch(e){}
			}
		}

		if (request){
			if (xmlHttp){
				xmlHttp.open("POST", url, true);
				xmlHttp.onreadystatechange = handleRequestStateChange;
				xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
				xmlHttp.send(request);
			}
		}
	}

	var setRequest = function(){
		message.create('Processing Request');
		message.addTree(element.create('img', {src: '/static/loader.gif'}));
		message.show();
		message.lock();
	}

	//################# обработка результатов
	var handleRequestStateChange = function(){
		try{
			//if (!app.appajax){
				/*if (xmlHttp.readyState == 1) { //Мозила
					setRequest();
				}
				if (xmlHttp.readyState == 2) { //А это специально для эстета оперы, которая статус 1 признавать не хочет.
					setRequest();
				}*/
			//}
			//if (xmlHttp.readyState == 3){}
			if (xmlHttp.readyState == 4) {
				//app.appajax = null;
				if (xmlHttp.status == 200){
					var resp = xmlHttp.responseText.replace(/\n/gi,'');
					if( /^\{.*\}$/.test(resp)){
						resp = eval("("+resp+")");
						processingResult(resp);
					}else if(xmlHttp.responseXML){ //Опера не отличает жсон от xml. лол.
						//ajxedt(xmlHttp.responseXML.documentElement);
					}
					message.unlock();
				}else{
					message.create('Status: '+xmlHttp.status);
					message.add('Не удалось получить данные: \u000A'+xmlHttp.statusText);
					message.addHTML(xmlHttp.responseText);
					message.show();
				}
			}
		}catch(e){
			alert('Caught Exception: ' + e);
		}
	}

	var processingResult = function(resp){
		var mspn = document.getElementById('mspan');
		try{
			switch(resp['response']){

				/*case 'app':
					app.retfunct(resp['text']);
				break;*/
				
				case 'add':
					add.processResponse(resp);
				break;

				case 'editok':
					if(resp.field == 'status'){
						message.hide();
						var rs = getStylesheetRule('.rs'+resp.text.status, 'background-color');
						rs = rs ? rs : '#FFF';
						var as = getStylesheetRule('.as'+resp.text.status, 'background-color');
						as = as ? as : '#FFF';
						var rules = [['.r'+resp.id, ['background-color', rs]],
									['.a'+resp.id, ['background-color', as]]];
						addStylesheetRules(rules);
					}
				break;

				case 'error':
					if(resp.text){
						throw new Error(resp.text);
					}else{
						throw new Error('Unknown error.');
					}
				break;

				case 'getok':
					element.removeAllChilds(mspn);
					for(var i in resp.text.order){
						var curname = resp.text.order[i];
						if(!curname) continue;
						if(!resp.text[curname]) continue;
						var current = resp.text[curname];
						var capCurname = curname.substr(0,1).toUpperCase() + curname.substr(1)
						var label = element.create('label', { 'for': curname + resp.text.id,
											innerText: capCurname + ':', name: resp.text.id});
						var sp = element.create('p', {'id': curname+resp.text.id, 'name': curname});
						var cld = new Array();
						if(isString(current)){
							sp.innerText = current;
						}else{
							if(curname == 'state'){
								sp = element.create('form', {'id': 'EditForm', name: 'status'});
								var sel = element.create('select', {id: 'stid', name: 'status',
									onchange: function(){
										var noe = document.getElementById('stnum');
										if(this.value != 2 && this.value != 4){
											element.remove(noe);
										}else{
											if(!noe)
												element.appendChild(this.parentNode, [{'input':
													{'type': 'hidden', name: 'count', value: 1}}]);
										}
										edit.send();
									}
								});
								cld.push(element.create('input', {'type': 'hidden', name: 'id',
														 'value': resp.text.id}));
								element.addOption(sel, current.select);
								if(current.selected){
									for(var i in sel.childNodes){
										if( sel.childNodes[i].value == current.selected)
											sel.childNodes[i].selected = true
									}
								}
								cld.push(sel);
								if(current.all){
									sel = element.create('select', {id: 'stnum', name: 'count',
										onchange: function(){ edit.send(); }});
									var arr = new Array();
									for(var i=1; i<=current.all; i++){arr[i] = i;}//Пиздец, а не способ!
									element.addOption(sel, arr);
									if(current.completed && sel.childNodes[current.completed]){
										var el = current.completed;
										sel.childNodes[el].selected = true;
									}else{sel.childNodes[0].selected = true;}
									sel.removeChild(sel.firstChild);
									cld.push(sel);
								}
								sel.focus();
							}else{
								var hid = ((current.tbl) ? current.tbl : "catalog");
								hid = element.create('input', {type: 'hidden', name: 'table', value: hid});
								//var edt = createElem('span',{className: 'edtl', 'name': i});
								/*if(!resp.text.edt && !resp.text[i][0]){continue;}
								if(resp.text.edt && !resp.text[i][0]){}else{}*/
								var num = numHash(current);
								for(var g=0; g<=num; g++){
									var cur = current[g];
									if(cur && isHash(cur)){
										var p = (curname == 'bundle') ? element.create('p',{name: cur.elemid}) :
																		   element.create('p',{'name': g});
										var s = (curname == 'bundle') ? element.create('span',{name: 'name'}) :
													element.create('span',{name: 'name', innerText: encd(cur.name)});
										cld.push(p, [s]);
										if(curname == 'bundle'){
											element.appendChild(s, [{'a':
												{href: '/card/'+cur.elemid+'/', innerText: encd(cur.name),
												className: 's' + (cur.job ? cur.job : 0)}}]);
										}
										if(cur.role){
											element.appendChild(p, [
												{'span': {name: 'role', innerText: ' as '+encd(cur.role)}}]);
										}
										if(cur.comm){
											element.appendChild(p, [
												{'span': {name: 'comm', innerText: '('+encd(cur.comm)+')'}}]);
										}
									}else{
										var s;
										if(curname == 'translation'){
											s = element.create('span', {name: 'name'});
											element.appendChild(s, [
												{'span': {name: 'trstart', innerText: encd(current[0][0])}}]);
											if(current[0][1])
												element.appendChild(s, [
													{'span': {innerText: ' - '}},
													{'span': {name: 'trend', innerText: encd(current[0][1])}}
												]);
										}else{
											if(curname == 'duration') current += ' min.';
											s = element.create('span', {name: 'name', innerText: encd(current)});
										}
										cld.push(element.create('p'), [s]);
									}
								}
							}
						}
						element.appendChild(mspn, [label, /*edt,*/ sp, cld]);
					}
				break;

				case 'logfail':
					user.loginFail(resp.text);
					throw new Error("Login error");
				break;

				case 'logok':
					message.hide();
					user.loginSuccess(resp.text);
					updateStylesheets('/css/');
				break;

				case 'regfail':
					user.registerFail(resp.text);
				break;

				case 'search':
					searcher.putResult(resp.text);
				break;
			}
		}catch(e){
			message.create(e);
			if(resp.text.text != 'notext'){
				message.add('Server response:');
				message.add(resp.text);
			}
			message.show();
		}
	}

})();