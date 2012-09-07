/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 */

var ua = navigator.userAgent.toLowerCase();

//######################## Global constants

var STATUSES = ["none", "want", "now", "done", "dropped", "partially watched"];

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

//##############################################################################
//##############################    Misc   #####################################
//##############################################################################

//######################## Messages process

var message = new (function(){

    this.strobj = new Array();

    this.timeout = null;
    this.closeable = false;
    this.onclose = null;

    this.getMenu = function(){
        if(!this.menu)
            this.menu = document.getElementById('menu');
        return this.menu;
    }

    //Clears message box and adds new p.
    this.create = function(str, timeout){
        this.clear();
        this.lock();
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
        this.menu.style.left = x + 'px';
        this.menu.style.top = y + 'px';
    }

    this.eventPosition = function(e){
        var x = 20;
        var y = 20;
        if(isIE)
            e = event;
        if(e.pageX || e.pageY){
            x = e.pageX;
            y = e.pageY;
        }else if(e.clientX || e.clientY){
            x = e.clientX + (document.documentElement.scrollLeft || document.body.scrollLeft) - document.documentElement.clientLeft;
            y = e.clientY + (document.documentElement.scrollTop || document.body.scrollTop) - document.documentElement.clientTop;
        }else if(e.target){
            x = e.target.offsetLeft;
            y = e.target.offsetTop;
        }
        return {x: x, y: y}
    }

    //Move messagebox to last event position.
    //Pop - старый костыль, но пока никак.
    this.toEventPosition = function(e){
        if(!this.getMenu())
            return;
        var p = this.eventPosition(e);
        this.toPosition(p.x, p.y);
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
            clearTimeout(this.timeout);
            if(m.onclose){
                m.onclose();
                m.onclose = null;
            }
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


//######################## Setup popups on long names
var popup = new (function(){

    var _pop = null;

    this.pop = function(){
        if(!_pop)
            _pop = document.getElementById('popup');
        return _pop;
    }

    this.move = function(e){
        var p = message.eventPosition(e);
        if(visible(popup.pop())){
            popup.pop().style.top = p.y + 10 +'px';
            popup.pop().style.left = p.x + 10 +'px';
        }
    }

    this.over = function(e){
        var p = message.eventPosition(e);
        popup.pop().style.top = p.y + 'px';
        popup.pop().style.left = p.x + 'px';
        addEvent(this, 'mousemove', popup.move);
        toggle(popup.pop(), 1);
        popup.pop().firstChild.innerText = this.innerText;
    };

    this.out = function(e){
        removeEvent(this, 'mousemove', popup.move);
        toggle(popup.pop(), -1);
    }

    this.add = function(el){
        if(isArray(el) || isNodeList(el)){
            for(var i = 0; i < el.length; i++)
                this.add(el[i]);
        }else if(isElement(el)){
            if(el.offsetHeight >= el.scrollHeight)
                return;
            addEvent(el, 'mouseover', this.over);
            addEvent(el, 'mouseout', this.out);
        }
    }

    this.addToTable = function(node, cn){
        var el = (node) ? node : document.getElementById('tbdid');
        this.add(getElementsByClassName((cn ? cn : "title"), el, 'td'));
    }

})();


//####################### Form data

function getFormData(form){
    var formData = {};
    element.downTree(function _f(elm){
        if(elm.tagName == "INPUT" || elm.tagName == "TEXTAREA" || elm.tagName == "SELECT"){
            switch(elm.type){
                case "checkbox":
                    formData[elm.name] = elm.checked;
                    break;
                case "radio":
                    if(elm.checked)
                        formData[elm.name] = elm.value;
                    break;
                case "select-multiple":
                    formData[elm.name] = map(function(opt){return opt.value},
                        filter(function(opt){ return opt.selected; }, elm.childNodes));
                    break;
                default:
                    formData[elm.name] = elm.value;
                    break;
            }
        }else{
            element.downTree(_f, elm);
        }
    }, form);
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


function hideRadio(s){
    var cld = s.parentNode.childNodes;
    map(function(pel){
        map(function(el){ if(el != s && el.type == "radio") el._chk = false }, pel.childNodes)},
        s.parentNode.parentNode.childNodes);
    if(s._chk){
        s._chk = s.checked = false;
        return;
    }
    s._chk = true;
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
        return (isUndef(string) ? '' : string);
    string = string.toString();
    string = string.replace(/\&quot;/gi, "\"");
    string = string.replace(/\&#37;/gi, "%");
    string = string.replace(/\&#39;/gi, "'");
    string = string.replace(/\&#92;/gi, "\\"); //"
    string = string.replace(/\&#47;/gi, "/");
    string = string.replace(/\&#43;/gi, "\+");
    string = string.replace(/\&#61;/gi, "=");
    string = string.replace(/\&lt;/gi, "<");
    string = string.replace(/\&gt;/gi, ">");
    string = string.replace(/\&#35;/gi, "#");
    string = string.replace(/\&amp;/gi, "&");
    return string
}

function capitalise(string){
    if(string)
        return string.charAt(0).toUpperCase() + string.slice(1);
}

var jsonToString = function(obj){
    if(isString(obj)) return "'" + obj + "'";
    else if(isArray(obj)){
        var ret = '';
        for(var i = 0; i < obj.length; i++)
            ret += jsonToString(obj[i]) + ',';
        return '[' + ret + ']';
    }else if(isHash(obj)){
        var ret = '';
        for(var i in obj)
            if(obj.hasOwnProperty(i))
                ret += jsonToString(i) + ': ' + jsonToString(obj[i]) + ',';
        return '{' + ret + '}';
    }
    return obj;
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

//################# Get menu with info

function cnt(tag, num, e){

    if(!e) var e = window.event;
    e.cancelBubble = true;
    if(e.stopPropagation) e.stopPropagation();
    message.toEventPosition(e);
    var qw = {'id': num}
    switch (tag){
        case 'title':
            qw['field'] = ['name', 'genre', 'links'];
        break;
        case 'episodes':
            qw['field'] = ['bundle', 'duration'];
        break;
        case 'id':
            edit.status_menu_edit = true; //Fuuu
            return edit.rf(num, 'state', e);
        break;
        default:
            qw['field'] = tag;
    }
    ajax.loadXMLDoc('get', qw, new RequestProcessor({
        'get': function(resp){
        message.create();
        for(var i in resp.text.order){
            var curname = resp.text.order[i];
            if(!curname || !resp.text[curname]) continue;
            var current = resp.text[curname];
            message.addTree(element.create('label', { 'for': curname + resp.id,
                            innerText: capitalise(curname) + ':'}));
            message.addTree(forms.getField(curname, resp.id, current));
        }
        message.show();
        }}));

}


// Additional functions

function map(callback, array, environ){
    if(!isFunction(callback))
        throw new TypeError(callback + " is not a function");
    var ret;
    if(isHash(array) && !isNodeList(array)){
        ret = {}
        for(var i in array)
            ret[i] = callback.call(environ, array[i]);
    }else{
        ret = new Array();
        for(var i = 0; i < array.length; i++)
            ret.push(callback.call(environ, array[i]));
    }
    return ret;
}

function filter(callback, array, environ){
    if(!isFunction(callback))
        throw new TypeError(callback + " is not a function");
    var ret;
    if(isArray(array) || isNodeList(array)){
        ret = new Array();
        for(var i = 0; i < array.length; i++)
            if(callback.call(environ, array[i])) ret.push(array[i]);
    }else if(isHash(array)){
        ret = new Object();
        for(var i in array)
            if(callback.call(environ, array[i])) ret[i] = array[i];
    }else
        throw new TypeError((typeof array) + " not supported by filter.");
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

function extend(oobj){
    var obj = oobj;
    var type = typeof obj;
    if(arguments.length >= 1)
        for(var i = 1; i < arguments.length; i++){
            var arg = arguments[i];
            if(!arg) continue;
            if(typeof arg != type)
                throw new TypeError('Argument type does not match');
            for(var name in arg)
                if(arg.hasOwnProperty(name)) obj[name] = arg[name];
        }
    return obj;
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
            s.insertRule(selector + '{' + rulesStr + '}', s.cssRules ? s.cssRules.length: 0);
        } else { /* IE */
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
        var rlength = rules ? rules.length: 0
        for( j = 0; j < rlength; j++){
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


addEvent(window, 'load', function(){ popup.addToTable(); });
