//add-edit classes module
//var seturl = '/cgi-bin/aniseted.pl';
//################################################################
//##################### Add #######################################
//################################################################

var add = new (function add_class(){

	var form = null;
	var loaded = false;

	this.init = function(){
		add.form = document.getElementById('addform');
		if(!add.form && !add.createForm()) return;
		add.loaded = true;
	}

	this.toggle = function(){
		if(!this.loaded) return;
		if(this.form.style.display == 'block'){
			this.form.style.display = 'none';
		}else if(!edit.visible){
			this.form.style.display = 'block';
		}
	}

	this.createForm = function(){
		if(this.form)
			return this.form;
		return false; // Потом как-нибудь напишу
	}

	this.clearForm = function(){
		if(!this.form)
			return;
		element.remove(getElementsByClassName('error', this.form, 'span'));
		element.remove(getElementsByClassName('s3', this.form, 'span'));
		return true;
	}

	this.sendForm = function(e){
		if(!this.loaded)
			return;
		if(!(e.clientX | e.clientY))
			return;
		this.clearForm();
		var formData = getFormData(this.form);
		ajax.loadXMLDoc(url+'add/', formData);
	}

	this.processResponse = function(resp){
	    message.hide()
		if(!resp.status){
			this.processError(resp.text);
		}else{
			if(this.clearForm()){
				element.insert(this.form.lastChild, {'span': {className: 's3 left', innerText: 'Added'}});
				if(isNumber(resp.text))
					window.location.replace('/card/' + resp.text + '/');
				else
					window.location.replace('/');
			}
		}
	}

	this.processError = function(error){
		if(!this.loaded)
			return;
		for(var target in error){
		    if(!target) continue;
			var obj = null;
			if(target == '__all__'){
				obj = element.create('div', {className: 'mainerror'});
				element.insert(this.form.firstChild, obj);
			}else{
				obj = document.getElementById('id_'+target);
			}
			if(!obj) continue;
			for(var e in error[target]){
				element.insert(obj, element.create('span', {
						className: 'error left', innerText: error[target][e]}), 1);
			}
		}
	}

})();

//################################################################
//##################### Edit #######################################
//################################################################

var edit = new (function edit_class(){

	var visible = false;
	
	this.init = function(){
		edit.loaded = true;
	}
	
	this.getForm = function(){
		return document.getElementById('EditForm');
	}

	this.send = function(){
		var form = this.getForm();
		if(!form || !form.name)
			return;
		var formData = getFormData(form);
		ajax.loadXMLDoc(url+'set/', formData);
	}

	/*this.edtdv;
	
	this.addElem = function(nam, elid, tbl, e){
		var div = document.getElementById(elid+nam);
		if(!div){
			this.edtdv = this.getForm();
			var li = createElem('li', {innerText: nam, name: elid, id: 'li'+elid+nam, 
									onclick: function(){ var d = document.getElementById(this.name+this.innerText);
									edit.showElem(d);}});
			var div =  createElem('div', {id: elid+nam, name: nam});
			fillContent(div, nam, elid, tbl);
			appChild(this.edtdv.ul, [li]);
			appChild(this.edtdv.fs, [div]);
		}		
		this.showElem(div);
	}

	var createForm = function(){
		var edtdv = createElem('div', {id: 'edit'});
		var ul = createElem('ul', {});
		var fs = createElem('fieldset', {id: 'edtcont'});
		var div = createElem('div', {});
		var leg = createElem('legend', {id: 'edtlegend'});
		var btnok = createElem('input', {type: 'button', value: 'Send', onclick: function(){edit.accept();}});
		var btnc = createElem('input', {type: 'button', value: 'Close',
																	onclick: function(){edit.removeForm();}});
		appChild(document.body, [edtdv, [ul, div, [fs, [leg], btnok, btnc]]]);
		return {main: edtdv, ul: ul, fs: fs, leg: leg};
	}

	this.removeForm = function(){
		this.edtdv = this.getForm();
		if(this.edtdv.fs.childNodes.length < 3){
			document.body.removeChild(this.edtdv.main);
		}else{
			var cur = this.getCurrentForm(); // так меньше нодов
			if(cur.div.previousSibling && cur.div.previousSibling.tagName == "DIV"){
				this.showElem(cur.div.previousSibling);
			}else{
				this.showElem(cur.div.nextSibling);
			}
			this.edtdv.ul.removeChild(cur.li);
			this.edtdv.fs.removeChild(cur.div);
		}
	}

	this.fillCont = function(resp, name, id){
		var dv = document.getElementById(id+name);
		removeAllChilds(dv);
		for(var i in resp){
			if(i == 'tbl') continue;
			var elem = resp[i];
			var p =  createElem('p', {name: i, ondblclick: function(){edit.formEdit(this);}});			
			var s =  createElem('span', {name: 'pname', innerText: elem.name});			
			var pid = ((elem.pid) ? createElem('input', {type: 'hidden', name: 'pid', value: elem.pid}) : undefined );
			var comm = ((elem.comm) ? createElem('span', {name: 'pcomm', innerText: '('+elem.comm+')'}) : undefined );
			var cast = ((elem.castas) ? createElem('span', {name: 'pcast', innerText: ' as '+elem.castas}) : undefined );
			appChild(dv, [p, [s, pid, comm, cast]]);
		}
		var h =  createElem('input', {name: 'table', type: 'hidden', value: resp.tbl});
		var p = createElem('p', {ondblclick: function(){
			var e =  createElem('p', {});
			this.parentNode.insertBefore(e, this);
			edit.formEdit(e);
		}});
		var s = createElem('span', {name: 'addedit', innerText: 'Add new'});
		appChild(dv, [h, p, [s]]);
	}

	var fillContent = function(dv, name, id, tbl){
		var img = createElem('img', {src: '/anime/templates/loader.gif'});
		appChild(dv, [img]);
		app.appajax = '1';
		var qw = 'eget='+id+'&string='+name;
		qw += ((tbl == 'catalog') ? '' : '_'+tbl );
		loadXMLDoc(url,qw);
	}

	this.getFields = function(pn){
		var f = function(el){if(el.name == 'pname') return el;}; // || /^p\d+$/.test(el.name)
		var name = allelements(f, pn, 1);
		if(name == 'ok') name = undefined;
		f = function(el){if(el.name == 'pcomm') return el;};
		var comm = allelements(f, pn, 1);
		if(comm == 'ok') comm = undefined;
		f = function(el){if(el.name == 'pcast') return el;};
		var cast = allelements(f, pn, 1);
		if(cast == 'ok') cast = undefined;
		f = function(el){if(el.name == 'pid' && el.type == 'hidden') return el;};
		var id = allelements(f, pn, 1);
		if(id == 'ok') id = undefined;
		return {'name': name, 'comm': comm, 'cast': cast, 'pid': id};
	}

	this.formEdit = function(cp){
		cp.ondblclick = "undefined"; 
		var nm = cp.parentNode.name;
		var fld = this.getFields(cp);
		var name = createElem('input', {type: 'text', name: 'pname',
													value: ((!fld.name) ? "" : fld.name.innerText),
													onkeyup: function(event){ 
														var area = function(el){
																if(el.tagName == "INPUT" && el.name == 'table') return el;};
														area = allelements(area, this.parentNode.parentNode, 1);
														app.opts.top = -94;
														app.opts.left = 161;
														app.acomp(this, area.value, event)}
													});
		if(!fld.name){name.onfocus = clearOnFocus('Name...', name);}
		var pid = ((fld.pid) ? createElem('input', {type: 'hidden', name: 'pid', value: fld.pid.value}) : undefined ); 
		var comm = ((!fld.comm) ? undefined : fld.comm.innerText.replace(/^\((.+)\)$/, "$1"));
		comm = createElem('input', {type: 'text', name: 'pcomm', value: comm});
		if(!comm.value || comm.value == "undefined")
			comm.onfocus = clearOnFocus('Comment...', comm);
		var cast = ((!fld.cast) ? undefined : fld.cast.innerText.replace(/^\s+as\s+/ig, ""));
		if(isElement(fld.cast) || nm == 'Cast'){
			cast = createElem('input', {type: 'text', name: 'pcast', value: cast});
			if(!cast.value || cast.value == "undefined") cast.onfocus = clearOnFocus('as...', cast);
		}
		removeAllChilds(cp);
		appChild(cp, [name, pid, comm, cast]);
	}

	this.showElem = function(dv){
		var f = function(el){el.style.display = 'none';};
		allelements(f, dv.parentNode);
		dv.style.display = 'block';
		f = function(el){removeClass(el, "sel"); addClass(el, "nosel")};
		allelements(f, this.edtdv.ul);
		f = document.getElementById('li'+dv.id);
		removeClass(f, "nosel");
		addClass(f, "sel");
		var name = document.getElementById('name'+f.name);
		this.edtdv.leg.innerText = 'Edit '+name.innerText+' '+dv.name;
	}

	this.getForm = function(){
		var ret;
		var edtdv = document.getElementById('edit');
		if(edtdv){
			ret = {main: edtdv,
							ul: edtdv.firstChild,
							fs: document.getElementById('edtcont'),
							leg: document.getElementById('edtlegend')};
		}else{
			ret = createForm();
		}
		return ret;
	}

	this.getCurrentForm = function(){
		if(!this.edtdv || !this.edtdv.fs) this.edtdv = this.getForm();
		var f = function(el){if(el.tagName == "DIV" && el.style.display == 'block') return el;};
		var div = allelements(f, this.edtdv.fs, 1);
		f = function(el){if(el.tagName == "INPUT" && el.name == 'table') return el;};
		f = allelements(f, div, 1);
		var li = document.getElementById('li'+div.id);
		this.edtdv.current = {div: div, li: li, tbl: f};
		return this.edtdv.current; // на всякий
	}

	var checkForm = function(form){
		var f = function(elm){
			if(elm.tagName == 'P'){
				var funct = function(a){return add.checkFunction(a);};
				var e = allelements(funct, elm);
				return e;
			}
		}
		var e = allelements(f,form, 1);
		return e;
	}

	this.accept = function(){
		var cur = this.getCurrentForm();
		var check = checkForm(cur.div);
		if(check == 'ok'){
			var qw = '';
			var cn = cur.div.childNodes;
			for(var i in cn){
				if(cn[i].tagName != "P") continue;
				var elm = this.getFields(cn[i]);
				if(!elm.name || elm.name.tagName != "INPUT") continue;
				if(cur.div.name == 'bundle' && !elm.id.value)
					alert(elm.name.value+': this element may not exists. Use autocomplete');
				qw += cur.tbl.value+',rid,';
				qw += ((elm.name.parentNode.name) ? rsemicolon(elm.name.parentNode.name) : '');
				qw += ',pname,'+rsemicolon(elm.name.value);
				qw += ',pcomm,'+rsemicolon(elm.comm.value);
				if(elm.pid) qw += ',pid,'+rsemicolon(elm.pid.value);
				if(elm.cast) qw += ',pcast,'+rsemicolon(elm.cast.value);
				qw += ',pjob,'+rsemicolon(cur.div.name)+';';
			}
			if(qw){
				qw = 'edit='+cur.li.name+'&string='+qw;
				//alert(qw);
				loadXMLDoc(url, qw);
			}
		}else{
			alert(check);
		}
	}

	this.processResult = function(res){
		var cur = this.getCurrentForm();
		var f = function(el, name){if(el.value == name) return el;}
		for(var i in res){
			for(var g in res[i]){ //перебрать
				var el = res[i][g];
				var obj = (function(name){
					for(var i in cur.div.childNodes){
						var one = cur.div.childNodes[i];
						if(one.tagName == "P"){
							for(var g in one.childNodes){ //перебрать обязательно!!
								if(one.childNodes[g].tagName != "INPUT") continue;
								return f(one.childNodes[g], name);
							}
						}
					}
				})(el.pname);
				obj = obj.parentNode;
				var flds =  this.getFields(obj);
				if(!el.pid) obj.name = flds.id.value;
				removeAllChilds(obj);
				appChild(obj, [createElem('span', {name: 'pname', innerText: el.pname})]);
				if(el.pcast) appChild(obj, [createElem('span', {name: 'pcast', innerText: ' as '+el.pcast})]);
				if(el.pcomm) appChild(obj, [createElem('span', {name: 'pcomm', innerText: '('+el.pcomm+')'})]);
				obj.ondblclick = function(){edit.formEdit(this);}
			}
		}
	}*/

})();

//################# Обработка и отправка формы.

function sndstat(sid, name){

	var p = document.getElementById(name+sid);
	var select = element.getSelected(p.firstChild);
	var q = {'field': name, 'id': sid, 'value': select}
	var num = p.childNodes[1];
	if(num){
		select = element.getSelected(num) + 1;
		q['count'] = select;
	}
	ajax.loadXMLDoc(url+'set/', q);
}

addEvent(window, 'load', add.init);
addEvent(window, 'load', edit.init);