// Ну без копирайта неинтересно, правда?
// Anicat js part v 1.99

var mCur; // Хранит текущую позицию мыши
var url = '/ajax/';
var timer;
var ua = navigator.userAgent.toLowerCase();

//##############################################################################
//##############################    Cookies   ##################################
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
//##############################    Classes   ##################################
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
//##############################    Misc   #####################################
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
        if(toggle(this.sobj))
            this.input.focus();
    }

    this.send = function(page){
        if(!this.loaded) return;
        if(!page) page = 0;
        var val;
        var sort;
        if(this.input.value.length < 3 && val != 'numberofep' && val != 'type'){
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
            message.toEventPosition();
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
            for(var i=0; i<rs.items.length; i++){
                var elem = rs.items[i];
                var row = element.create('tr',
                    {className: (elem.air ? 'air a' : 'r') + elem.id}, [
                        {'td': {'id': 'link' + elem.id, className: 'link'}}, [
                            {'a': {className: 'cardurl', 'target': '_blank',
                                'href': '/card/'+elem.id+'/',
                                onclick: ( function(id){
                                            return function(){return Card.get(id);};
                                        })(elem.id)}}, [
                                {'img': {'src': '/static/arrow.gif', 'alt': 'Go'}},
                            ]
                        ],
                        {'td': {'id': 'id' + elem.id, className: 'id',
                            onclick: ( function(i, j){
                                            return function(e){ cnt(i, j, e); };
                                        })('id', elem.id),
                            innerText: Number(i) + 1 + rs.items.length * rs.page }},
                        ]);
                tr.push(row);
                for(var column in elem){
                    if(column == 'air' || column == 'id') continue;
                    element.appendChild(row, [{'td': {'id': column + elem.id, className: column,
                                onclick: (function(i, j){ return function(e){ cnt(i, j, e); };})(column, elem.id),
                                    innerText: encd(elem[column])}}]);
                }
            }
            var srctbl = element.create('table', {'id': 'srchtbl', className: 'tbl', cellSpacing: 0});
            element.appendChild(this.result, [srctbl, ['thead', 'tbody', tr]]);
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

    this.getMenu = function(){
        if(!this.menu)
            this.menu = document.getElementById('menu');
        return this.menu;
    }

    //Clears message box and adds new p.
    this.create = function(str, timeout){
        this.clear();
        this.lock();
        //this.toEventPosition();
        if(!isString(str) && !isNumber(str) && !isUndef(str) && !isError(str))
            this.addTree(str);
        else
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
        this.strobj.push(elem);
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
        if(!this.getMenu())
            return;
        this.menu.parentNode.style.left = x + 'px';
        this.menu.parentNode.style.top = y + 'px';
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
        if(!this.getMenu())
            return;
        element.removeAllChilds(this.menu);
        element.appendChild(this.menu, this.strobj);
        toggle(this.menu, 1);
        if(time)
            this.timeout = time;
        if(this.timeout)
            timer = setTimeout(function(){toggle(document.getElementById('menu'), -1);}, this.timeout);
        addEvent(document, 'click', message.close);
        this.unlock();
    }

    //Close message.
    this.close = function(e){
        var m = this == document ? message : this;
        if(!m.closeable || !m.getMenu())
            return;
        var menu = m.getMenu();
        var target = e ? e.target : event.srcElement;
        var checkParent = function(obj){
            if(!obj) return true;
            if(obj != menu) return checkParent(obj.parentNode);
            return false;
        }
        if(checkParent(target)){
            m.hide();
            clearTimeout(timer);
        }
    }

    //Hide message. No closeable check.
    this.hide = function(){
        if(!message.getMenu())
            return;
        removeEvent(document, 'click', message.close);
        toggle(message.menu, -1);
    }

})();

//####################### Form data

function getFormData(form){
    var formData = {};
    var f = function(elm){
    if(elm.tagName == "INPUT" || elm.tagName == "TEXTAREA" || elm.tagName == "SELECT"){
        if(elm.type == "checkbox"){
            formData[elm.name] = elm.checked;
        }else if(elm.type == "select-multiple"){
            var values = new Array();
            element.downTree(function(opt){if(opt.selected) values.push(opt.value);}, elm);
                formData[elm.name] = values;
            }else if(elm.type != "button"){
                    formData[elm.name] = elm.value;
            }
        }else{
            element.downTree(f, elm);
        }
    }
    element.downTree(f, form);
    return formData;
}

//####################### Разная помойка


if(!Array.prototype.indexOf){
    Array.prototype.indexOf=function(obj,start){
        for(var i=(start||0),j=this.length;i<j;i++){
            if(this[i]==obj){return i;}
        }
        return -1;
    }
}

// Internet Explorer
isIE = (ua.indexOf("msie") != -1 &&  ua.indexOf("webtv") == -1);
// Internet Explorer < 8
isOldIE = (isIE && parseFloat(navigator.appVersion.split("MSIE")[1]) < 8);
// Opera
isOpera = (ua.indexOf("opera") != -1);
/*  // Gecko = Mozilla + Firefox + Netscape
isGecko = (ua.indexOf("gecko") != -1);
// Safari
isSafari = (ua.indexOf("safari") != -1);
// Konqueror, используется в UNIX-системах
isKonqueror = (ua.indexOf("konqueror") != -1);
*/


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
                toggle(document.getElementById('popup'), 1);
                document.getElementById('popups').innerText = this.innerText;
            }
            el.onmouseout = function(){
                toggle(document.getElementById('popup'), -1);
            }
        }
    }
}

function numHash(numh){ //for hash with numeric keys only
    var e=0;
    for(var r in numh){
        //if( /[^\d]/.test(r) )  continue;
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

function capitalise(string){
    if(string)
        return string.charAt(0).toUpperCase() + string.slice(1);
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

function toggle(elem, force){
    if(elem){
        if((!force && elem.style.display == 'block') || force < 0){
            elem.style.display = 'none';
        }else{
            elem.style.display = 'block';
            return true;
        }
    }
    return false;
}

function visible(elem){
    if(elem && elem.style.display == 'block')
        return true;
    return false;
}

//################# Отсюда берется положение менюшки

function mousePageXY(event){
    var x = 0, y = 0;

    if(document.attachEvent != null){ // Internet Explorer & Opera
        x = window.event.clientX + (document.documentElement.scrollLeft ?
            document.documentElement.scrollLeft : (document.body ? document.body.scrollLeft : 0));
        y = window.event.clientY + (document.documentElement.scrollTop ?
            document.documentElement.scrollTop : (document.body ? document.body.scrollTop : 0));
    }else if(!document.attachEvent && document.addEventListener){ // Gecko
        x = event.clientX + window.scrollX;
        y = event.clientY + window.scrollY;
    }else{// Do nothing
        throw new Error('Bad browser.');
    }
    return {"x":x, "y":y};
}

//################# Get menu with info

function cnt(tag, num, e){

    if(!e) var e = window.event;
    e.cancelBubble = true;
    if(e.stopPropagation) e.stopPropagation();
    message.toEventPosition();
    var qw = {'id': num}
    switch (tag){
        case 'name':
            qw['field'] = ['name', 'genre', 'links'];
        break;
        case 'numberofep':
            qw['field'] = ['bundle', 'duration'];
        break;
        case 'id':
            edit.status_menu_edit = true; //Fuuu
            return edit.rf(num, 'state');
        break;
        default:
            qw['field'] = tag;
    }
    ajax.loadXMLDoc(url+'get/', qw);

}

// Additional functions

function map(callback, array, environ){
    if(!isFunction(callback))
        throw new TypeError(callback + " is not a function");
    var ret;
    if(isHash(array))
        ret = {}
    else
        ret = new Array();
    for(var i in array){
        ret[i] = callback.call(environ, array[i]);
    }
    return ret;
}

function range(start, end){
    var s = new Array();
    if(end >= start){
        for(var i=start; i <= end; i++){
            s.push(i);
        }
    }
    return s;
}

// Cross-browser event handlers.
function addEvent(obj, evType, fn){
    if(!obj) return false;
    if(obj.addEventListener){
        obj.addEventListener(evType, fn, false);
        return true;
    }else if(obj.attachEvent){
        var r = obj.attachEvent("on" + evType, fn);
        return r;
    }else{
        return false;
    }
}

function removeEvent(obj, evType, fn) {
    if(!obj) return false;
    if(obj.removeEventListener){
        obj.removeEventListener(evType, fn, false);
        return true;
    }else if(obj.detachEvent){
        obj.detachEvent("on" + evType, fn);
        return true;
    }else{
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
            s.addRule(selector, rulesStr);
        }
    }
}

function getStylesheetRule(ruleName, field){
    var value = null;
    var recls = new RegExp(ruleName.toLowerCase());
    var reimp = new RegExp('(\\s|^)' + field.toLowerCase() + ':[^;]+(!\\s*important)?\\s*;?');
    for( var i = 0; i < document.styleSheets.length; i++){
        var sheet = document.styleSheets[i];
        var rules = sheet.cssRules ? sheet.cssRules : sheet.rules;
        for( j = 0; j < rules.length; j++){
            var rule = rules[j];
            if(!rule.selectorText)
                continue;
            var text = rule.selectorText.toLowerCase();
            if(text.match(recls)){
                if(window.getComputedStyle)
                    value = rule.style.getPropertyValue(field);
                else if(isIE){
                    function camelize(text) {
                        return text.replace(/-+(.)?/g, function (match, chr) {
                            return chr ? chr.toUpperCase() : '';});
                    }
                    value = rule.style[camelize(field)];
                }
                if(rule.style.cssText && rule.style.cssText.toLowerCase().match(reimp))
                    return value;
            }
        }
    }
    return value;
}


addEvent(window, 'load', function(){
    searcher.init();
    showFN();
});

addEvent(document, 'mousemove', function(e){
    mCur = mousePageXY(e);
    var p = document.getElementById('popup');
    if(visible(p)){
        p.style.top = mCur.y + 10 +'px';
        p.style.left = mCur.x + 10 +'px';
    }
});
