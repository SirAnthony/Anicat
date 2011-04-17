// Ну без копирайта неинтересно, правда?
// Anicat js part v 1.99

var mCur; // Хранит текущую позицию мыши
var xmlHttp;
//var mfl = 0;	// 0 - никаких действий. 1 - меню открыто, заболкирован инпут под ним.
	     // 2 - заблокировано инпутом, закрыто.
var url = '/ajax/';
var edtdv = 0; // эта переменная определяет редактируется ли менюшка или нет
var timer;
var ua = navigator.userAgent.toLowerCase();

//##############################################################################
//##############################	Element   ##################################
//##############################################################################

var element = new ( function(){

	this.downTree = function(funct, obj, er){
		if(!funct || !obj) return;
		for(var i=0; i < obj.childNodes.length; i++){
			var e = funct(obj.childNodes[i]);
			if(e) return e;
		}
		if(er) return true;
	}

	this.addOption = function(obj, arr){
	    //isArray?
		if(arr.length){
			for(var i=0; i < arr.length; i++){
				var opt = this.create('option', {value: arr[i], text: arr[i]});
				this.appendChild(obj, [opt]);
			}
		//isHash?	
		}else{
			for(var i in arr){
				var opt = this.create('option', {value: i, text: arr[i]});
				this.appendChild(obj, [opt]);
			}
		}
	}

	this.getSelected = function(obj){
		var sel = obj.childNodes;
		var select;
		if(sel)
			for(select in sel){ if(sel[select].selected) break; }
		return select;
	}

	this.getChilds = function(obj){
		var childs = new Array();
		for(var i=0; i < obj.childNodes.length; i++){
			childs.push(obj.childNodes[i]);
		}
		return childs;
	}

	this.removeAllChilds = function(el){
		if(!el)
			return;
		while(el.hasChildNodes()){
			el.removeChild(el.lastChild);
		}
	}

	this.create = function(elem, params){
		if(!elem || elem == '') elem = 'text';
		var elm = document.createElement(elem);
		for (var i in params){ 
			elm[i] = params[i];
		}
		return elm;
	}

	this.remove = function(elem){
		if(!elem)
			return;
		if(isArray(elem)){
			for(var el in elem)
				this.remove(elem[el]);
		}else{
			this.removeAllChilds(elem);
			if(elem.parentNode)
			    elem.parentNode.removeChild(elem);
		}	
	}

	this.appendChild = function(obj, arr){
		var ar = new Array();
		ar = eval(arr);
		var l = ar.length;
		if(!l) l = 0;
		for(var i=0; i < l; i++){
			if(!ar[i] || (!isElement(ar[i]) && !isArray(ar[i]) && !isHash(ar[i]))) continue;
			if(isHash(ar[i])){
				var elems = ar[i];
				for(var key in elems){
					if(elems[key] && !isHash(elems[key]))
						continue;
					ar[i] = this.create(key, elems[key]);
				}
			}
			if(isArray(ar[i])){
				this.appendChild(ar[i-1], ar[i]);
			}else{
				obj.appendChild(ar[i]);
			}
		}
	}

	//Insert elem before(after if next) obj
	this.insert = function(obj, elem, next){
		if(isHash(elem)){
			var el;
			for(var key in elem){
				if(!isHash(elem[key])) continue;
				el = this.create(key, elem[key]);
			}
			elem = el;
		}
		var ins = next ? obj.nextSibling : obj
		obj.parentNode.insertBefore(elem, ins);
	}

	this.getOffset = function(obj, parent){
		parent = parent ? parent : document.body;
		var el = obj;
		var offset = {top: 0, left: obj.offsetLeft};
		while(el.parentNode.parentNode != parent){
			el = el.parentNode;
			offset.top += el.offsetTop;
			offset.left += el.offsetLeft;
		}
		return offset;
	}

})();

//##############################################################################
//##############################	Cookies   ##################################
//##############################################################################

var cookies = new ( function(){

	this.set = function(name, value, expires, path, domain, secure){
		document.cookie = name + "=" + escape(value) +
		((expires) ? "; expires=" + expires : "") +
		((path) ? "; path=" + path : "") +
		((domain) ? "; domain=" + domain : "") +
		((secure) ? "; secure" : "");
	}

	this.del = function(name, path, domain){
		document.cookie = name + "=" +
		((path) ? "; path=" + path : "; path=/") +
		((domain) ? "; domain=" + domain : "") +
		"; expires=Thu, 01-Jan-70 00:00:01 GMT;";
	}

	this.get= function(name){
		var cookie = " " + document.cookie;
		var search = " " + name + "=";
		var setStr = null;
		if (cookie.length > 0) {
			var offset = 0;
			offset = cookie.indexOf(search);
			if (offset != -1) {
				offset += search.length;
				var end = 0;
				end = cookie.indexOf(";", offset);
				if (end == -1) end = cookie.length;
				setStr = unescape(cookie.substring(offset, end));
			}
		}
		return setStr;
	}
})();

//##############################################################################
//##############################	Classes   ##################################
//##############################################################################

var pclass = new ( function(){

	this.hasClass = function(ele, cls){
		if(!ele.className)
			return
		return ele.className.match(new RegExp('(\\s|^)'+cls+'(\\s|$)'));
	}

	this.add = function(ele, cls){
		if(!this.hasClass(ele, cls))
			ele.className += ' '+cls;
	}

	this.remove = function(ele, cls){
		if (this.hasClass(ele, cls)){
			var reg = new RegExp('(\\s|^)'+cls+'(\\s|$)');
			ele.className = ele.className.replace(reg,'');
		}
	}
})();

function clearOnFocus(text, obj){
	if(obj){
		obj.value = text;
	}
	return function(){
		if(this.value == text){
				this.value = '';
			}
	}
}

//##############################################################################
//##############################	Misc   #####################################
//##############################################################################

var searcher = new ( function(){

	this.init = function(){
		this.sobj = document.getElementById('srch');
		this.result = document.getElementById('srchres');
		this.input = document.getElementById('sin'); //это как-то по другому нужно.
		if(this.sobj && this.result && this.input) this.loaded = true;
	}

	this.toggle = function(){
		if(!this.loaded) return;
		if(this.sobj.style.display == 'block'){
			this.sobj.style.display = 'none';
		}else{
			this.sobj.style.display = 'block';
			this.input.focus();
		}
	}

	this.showAdvance = function(){
		if(!this.loaded) return;
		/*var cb = document.getElementById('chsrch').checked;
		if (!cb){
			document.getElementById('advsrch').style.display = 'none';
			document.getElementById('sortsrch').style.display = 'none';
		}else{
			document.getElementById('advsrch').style.display = 'block';
			document.getElementById('sortsrch').style.display = 'block';
	   */
	}

	this.send = function(page){
		if(!this.loaded) return;
		if(!page) page = 0;
		//var text =  document.getElementById('sin');
		var val; // = document.getElementById('advsrch').value;
		var sort; // = document.getElementById('sortsrch').value;
		if(this.input.textLength < 3 && val != 'numberofep' && val != 'type'){
			element.removeAllChilds(this.result);
			element.appendChild(this.result, [{'p': {
				innerText: 'Query must consist of at least 3 characters.'}}]);
		}else if( /\.{2,3}/.test(this.input.value) || /\.{1}(\s{1}|\S{1})\.{1}/.test(this.input.value) ){
			element.removeAllChilds(this.result);
			element.appendChild(this.result, [{'p': {innerText: 'Invalid request.'}}]);
		}else{
			var text = this.input.value.toLowerCase();
			if(!val) val = 'name';
			var qw = {'page': page, 'field': val, 'string': text, 'sort': sort};
			var menu = document.getElementById('menu');
			message.toPosition(40, 65);
			ajax.loadXMLDoc(url+'search/',qw);
		}
	}

	this.putResult = function(rs){
		if(!this.loaded) return;
		message.hide();
		element.removeAllChilds(this.result);
		if(!rs.count || !rs.items.length){
		   element.appendChild(this.result, [{'p': {innerText: 'Nothing found.'}}]);
		}else{
			var tr = new Array();
			for(i in rs.items){
				var elem = rs.items[i];
				var row = element.create('tr', {className: (elem.air ? 'air a' : 'r') + elem.id});
				tr.push(row);
				element.appendChild(row, [
									{'td': {'id': 'link' + elem.id, className: 'link'}}, [
										{'a': {className: 'cardurl', 'target': '_blank',
															'href': '/card/'+elem.id+'/'}}, [
											{'img': {'src': '/static/arrow.gif', 'alt': 'Go'}},
											]
										],
									{'td': {'id': 'id' + elem.id, className: 'id',
									onclick: (  function(i, j){ 
													return function(){ cnt(i, j); };
												})('id', elem.id),
											 innerText: Number(i) + 1 + rs.items.length * rs.page }},
									]);
				for(var column in elem){
					if(column == 'air' || column == 'id') continue;
					element.appendChild(row, [{'td': {'id': column + elem.id, className: column, 
								onclick: (function(i, j){ return function(){ cnt(i, j); };})(column, elem.id),
									innerText: encd(elem[column])}}]);
				}
				/*if(elem.job){
				   pclass.add(row, 'r' + elem.job + ((elem.air) ? 'on': '' ));
				}*/
			}
			var srctbl = element.create('table', {'id': 'srchtbl', className: 'tbl', cellSpacing: 0});
			element.appendChild(this.result, [srctbl, tr]);
			if(rs.count > rs.items.length){
				var pg = new Array();
				for( var i = 1; i <= Math.ceil(rs.count / 20); i++){
					if(rs.page == i-1){
						pg.push(element.create('span', {innerText: '[' + i + ']'}));
					}else{
						pg.push(element.create('a', {innerText: i, 
								onclick: (function(pg){ return function(){ searcher.send(pg);};})(i-1)}));
					}
				}
				element.appendChild(this.result, [{'div': {'id': 'srchpg'}}, pg]);
			}
			showFN(srctbl);
		}
	}

})();

//######################## Messages process

var message = new (function(){

	this.strobj = new Array();

	this.timeout = null;
	this.closeable = false;

	this.getSpan = function(){
		if(!this.span)
			this.span = document.getElementById('mspan');
		return this.span;
	}

	//Clears message box and adds new p. 
	this.create = function(str, timeout){
		this.clear();
		this.lock();
		this.add(str);
		this.timeout = timeout;
	}

	//Adds new p element.
	this.add = function(str){
		if(!str) return;
		this.strobj.push(element.create('p', {innerText: str}));
	}

	//Adds element tree.
	this.addTree = function(elem){
		if(!elem) return;
		var p = element.create('p');
		element.appendChild(p, [elem])
		this.strobj.push(p);
	}

	//Adds html string to message.
	//FIXME: innerHTML is bad. 
	this.addHTML = function(str){
		if(!str) return;
		var p = element.create('p', {innerHTML: str});
		var styles = p.getElementsByTagName('style');
		for(style in styles){
			var st = styles[style];
			if(!isElement(st)) continue;
			//st.innerText = st.innerText.replace('/html.*}/gi', '');
		}
		this.strobj.push(p);
	}

	//Adds string to last string.
	this.addToLast = function(str){
		if(!str) return;
		this.strobj[this.strobj.length].innerText += str;
	}

	//Remove all elements.
	this.clear = function(){
		while(this.strobj.length)
			element.remove(this.strobj.shift());
	}

	this.toPosition = function(x, y){
		if(!this.getSpan())
			return;
		this.span.parentNode.style.left = x + 'px';
		this.span.parentNode.style.top = y + 'px';
	}

	//Move messagebox to last event position.
	//Pop - старый костыль, но пока никак.
	this.toEventPosition = function(pop){
		var dv;
		pop ? dv = document.getElementById('popup') : dv = document.getElementById('menu');

		if(!dv)
			return;
		var x = 20;
		var y = 20;
		if(isIE){
			e = event;
			if(e.pageX || e.pageY){
				x = e.pageX;
				y = e.pageY;
			}else if(e.clientX || e.clientY){
				x = e.clientX + (document.documentElement.scrollLeft || document.body.scrollLeft) - document.documentElement.clientLeft;
				y = e.clientY + (document.documentElement.scrollTop || document.body.scrollTop) - document.documentElement.clientTop;
			}
		}else{
			if( mCur.y+170 >= document.firstChild.clientHeight )
				mCur.y = mCur.y - 70;
			if( mCur.x+200 >= document.firstChild.clientWidth )
				mCur.x = mCur.x - 100;
			y = mCur.y;
			x = mCur.x;
		}
		dv.style.top = y + 'px';
		dv.style.left = x + 'px';
	}

	// Prevents menu from closing
	this.lock = function(){
		this.closeable = false;
	}

	this.unlock = function(){
		this.closeable = true;
	}

	//Show message.
	this.show = function(time){
		if(!this.getSpan())
			return;
		element.removeAllChilds(this.span);
		element.appendChild(this.span, this.strobj);
		this.span.parentNode.style.display = 'block';
		if(time)
			this.timeout = time;
		if(this.timeout)
			timer = setTimeout("document.getElementById('menu').style.display='none';", this.timeout);
		this.unlock();
	}

	//Close message.
	this.close = function(e){
		var m = this == document ? message : this;
		if(!m.closeable || !m.getSpan())
			return;
		var menu = m.span.parentNode;
		var target = e ? e.target : event.srcElement;
		var checkParent = function(obj){
			if(!obj) return true;
			if(obj != menu) return checkParent(obj.parentNode);
			return false;
		}
		if(checkParent(target)){
			menu.style.display = 'none';
			document.onclick = "undefined";
			clearTimeout(timer);
		}
	}

	//Hide message. No closeable check.
	this.hide = function(){
		if(!message.getSpan())
			return;
		message.span.parentNode.style.display = 'none';
	}

})();

//####################### Разная помойка

if(!Array.prototype.indexOf){
	Array.prototype.indexOf=function(obj,start){
		for(var i=(start||0),j=this.length;i<j;i++){
			if(this[i]==obj){return i;}
		}
		return -1;
	}
}

// Получим userAgent браузера и переведем его в нижний регистр
	// Определим Internet Explorer
	isIE = (ua.indexOf("msie") != -1 &&  ua.indexOf("webtv") == -1);
	// Opera
	isOpera = (ua.indexOf("opera") != -1);
/*	// Gecko = Mozilla + Firefox + Netscape
	isGecko = (ua.indexOf("gecko") != -1);
	// Safari
	isSafari = (ua.indexOf("safari") != -1);
	// Konqueror, используется в UNIX-системах
	isKonqueror = (ua.indexOf("konqueror") != -1);	
*/

if (! isIE) {
	if ( !isUndef(Node) && !isUndef(Node.prototype) && isFunction(Node.prototype.__defineGetter__)){
		Node.prototype.__defineGetter__("innerText", function() { return this.textContent; });	
		Node.prototype.__defineSetter__("innerText", function(val){this.textContent ="";
				this.appendChild(document.createTextNode(val));	});
	}
}


// Доставляет попапы на длинные имена. Срабатывает при загрузке
addEvent(window, 'load', function(){
	searcher.init();
	mv();
	showFN();
});

//Расставляет попапы с тем, что скрыто
function showFN(tbl, cn){
	var el = (tbl) ? tbl : document.getElementById('tbdid');
	var elms = getElementsByClassName((cn ? cn : "name"), el, 'td');
	for(i in elms){
		var el = elms[i];
		//Как-то оно не так.
		if(el.nextSibling && el.offsetHeight < el.nextSibling.offsetHeight)
			el.style.height = el.nextSibling.offsetHeight + 'px';
		pclass.add(el, 'left');
		if(el.offsetHeight < el.scrollHeight){
			el.onmouseover = function(){
				message.toEventPosition(1);
				document.getElementById('popup').style.display = 'block';
				document.getElementById('popups').innerText = this.innerText;
			}
			el.onmouseout = function(){
				document.getElementById('popup').style.display = 'none';
			}
		}
	}
}

//Покрадено
function isElement(object){return !!(object && object.nodeType == 1);}
function isArray(object){return object != null && typeof object == "object" &&
	'splice' in object && 'join' in object;}
function isHash(object) {
	return object && 
		typeof object=="object" &&
		(object==window||object instanceof Object) &&
		!object.nodeName &&
		!isArray(object);
}
function isFunction(object){return typeof object == "function";}
function isString(object){return typeof object == "string";}
function isNumber(object){return typeof object == "number";}
function isUndef(object){return typeof object == "undefined";}

function numHash(numh){ //for hash with numeric keys only
	var e=0;
	for(var r in numh){
		//if( /[^\d]/.test(r) )	 continue;
		if( Number(r) > Number(e) ) e=r;
	}
	return e;
}

function getElementsByClassName(searchClass, node, tag) {
	var classElements = new Array();
	if(node == null)
		node = document;
	if(tag == null)
		tag = '*';
	var els = node.getElementsByTagName(tag);
	var elsLen = els.length;
	for(var i = 0; i < elsLen; i++){
		if(pclass.hasClass(els[i], searchClass))
			classElements.push(els[i]);
	}
	return classElements;
}

//################# Преобразование переменных

function encd(string){
	//Convert codes into characters
	if(!string)
		return '';
	string = string.toString();
	string = string.replace(/\&quot;/gi, "\"");
	string = string.replace(/\&#37;/gi, "%");
	string = string.replace(/\&#39;/gi, "'");
	string = string.replace(/\&#92;/gi, "\\"); //"
	string = string.replace(/\&#47;/gi, "/");
	string = string.replace(/\&#43;/gi, "\+");
	string = string.replace(/\&#61;/gi, "=");
	string = string.replace(/\&lt/gi, "<");
	string = string.replace(/\&rt;/gi, ">");
	string = string.replace(/\&#35;/gi, "#");
	string = string.replace(/\&amp;/gi, "&");
	return string
}

function rsemicolon(prm){
	var astr = prm;
	astr = astr.replace(/;/g, "0x3B");
	astr = astr.replace(/,/g, "0x2C");
	return astr;
}


//Режимы отображения

function setshow(){
	var mode = document.getElementById('show').value;
	if(!mode && !isNumber(mode))
		return;
	(mode == 'a') ? mode = '/' : mode = '/show/'+mode+'/';
	if(window.location.pathname != mode){
		window.location.href = mode;
	}
}


//##############################################################################
//###############################	Меню   ####################################
//##############################################################################

//################# Отсюда берется положение менюшки

function mousePageXY(event){
	var x = 0, y = 0;

	if(document.attachEvent != null){ // Internet Explorer & Opera
		x = window.event.clientX + (document.documentElement.scrollLeft ? document.documentElement.scrollLeft : document.body.scrollLeft);
		y = window.event.clientY + (document.documentElement.scrollTop ? document.documentElement.scrollTop : document.body.scrollTop);
	}else if(!document.attachEvent && document.addEventListener){ // Gecko
		x = event.clientX + window.scrollX;
		y = event.clientY + window.scrollY;
	}else{// Do nothing
		alert('Bad browser.');
	}
	return {"x":x, "y":y};
}

//################# Эта функция доставляет положение менюшки и контролирует ее прятание

function mv(){
	document.onmousemove = function(e){

		mCur = mousePageXY(e);
		if(document.getElementById('popup')){
			if(document.getElementById('popup').style.display == "block"){
				document.getElementById('popup').style.top = mCur.y + 10 +'px';
				document.getElementById('popup').style.left = mCur.x + 10 +'px';
			}
		}

		if(document.getElementById('menu')){ 
			if(document.getElementById('menu').style.display == "block" && !edtdv){
				document.onclick = message.close; // Прятание меню
			}
		}
	}
}

//################# Get menu with info

function cnt(tag, num, e) {

	message.toEventPosition();
	var qw = {'id': num}
	switch (tag){
		case 'name':
			qw['field'] = ['name','genre'];
		break;
		case 'numberofep':
			qw['field'] = ['bundle','duration'];
		break;
		case 'id':
			qw['field'] = 'state';
		break;
		default:
			qw['field'] = tag;
	}
	ajax.loadXMLDoc(url+'get/', qw);

}

// Cross-browser event handlers.
function addEvent(obj, evType, fn) {
	if (obj.addEventListener) {
		obj.addEventListener(evType, fn, false);
		return true;
	} else if (obj.attachEvent) {
		var r = obj.attachEvent("on" + evType, fn);
		return r;
	} else {
		return false;
	}
}

function removeEvent(obj, evType, fn) {
	if (obj.removeEventListener) {
		obj.removeEventListener(evType, fn, false);
		return true;
	} else if (obj.detachEvent) {
		obj.detachEvent("on" + evType, fn);
		return true;
	} else {
		return false;
	}
}

function updateStylesheets(name, link){
	var a = document.getElementsByTagName('link');
	for(var i=0; i<a.length; i++){
		var s = a[i];
		if(s.rel.toLowerCase().indexOf('stylesheet') >= 0 && s.href){
			var path = s.href.replace(/^https?:\/\/[^\/]+/i, '');
			path = path.replace(/\?.*$/i, '');
			if(!name || path == name){
				s.href = s.href+'?'+(new Date().valueOf());
			}
		}
	}
}

function addStylesheetRules (decls) {
	var style = document.createElement('style');
	document.getElementsByTagName('head')[0].appendChild(style);
	if (!window.createPopup) { /* For Safari */
	   style.appendChild(document.createTextNode(''));
	}
	var s = document.styleSheets[document.styleSheets.length - 1];
	for (var i=0, dl = decls.length; i < dl; i++) {
		var j = 1, decl = decls[i], selector = decl[0], rulesStr = '';
		if (Object.prototype.toString.call(decl[1][0]) === '[object Array]') {
			decl = decl[1];
			j = 0;
		}
		for (var rl=decl.length; j < rl; j++) {
			var rule = decl[j];
			rulesStr += rule[0] + ':' + rule[1] + (rule[2] ? ' !important' : '') + ';\n';
		}

		if (s.insertRule) {
			s.insertRule(selector + '{' + rulesStr + '}', s.cssRules.length);
		}
		else { /* IE */
			s.addRule(selector, rulesStr, -1);
		}
	}
}

function getStylesheetRule(ruleName, field){
	var value = null;
	var recls = new RegExp(ruleName.toLowerCase());
	var reimp = new RegExp('(\\s|^)' + field.toLowerCase() + ':[^;]+!\\s*important\\s*;');
	for( var i = 0; i < document.styleSheets.length; i++){
		var sheet = document.styleSheets[i];
		var rules = sheet.cssRules ? sheet.cssRules : sheet.rules;
		for( j = 0; j < rules.length; j++){
			var rule = rules[j];
			if(!rule.selectorText)
				continue;
			var text = rule.selectorText.toLowerCase();
			if(text.match(recls)){
				if(isIE)
					value = rule.style[field];
				else if(window.getComputedStyle)
					value = rule.style.getPropertyValue(field);
				if(rule.cssText && rule.cssText.toLowerCase().match(reimp))
					return value;
			}
		}
	}
	return value;
}
