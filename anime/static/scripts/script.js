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

//####################### Разная помойка


if(!Array.prototype.indexOf){
    Array.prototype.indexOf=function(obj,start){
        for(var i=(start||0),j=this.length;i<j;i++){
            if(this[i]==obj){return i;}
        }
        return -1;
    }
}


if(!Array.prototype.forEach){
    Array.prototype.forEach = function(fun, thisp){
        var len = this.length;
        if (typeof fun != "function")
            throw new TypeError()

        for (var i = 0; i < len; i++) {
            if (i in this)
                fun.call(thisp, this[i], i, this)
        }
    }
}

if(!NodeList.prototype.forEach)
    NodeList.prototype.forEach = Array.prototype.forEach

// Internet Explorer
isIE = (ua.indexOf("msie") != -1 &&  ua.indexOf("webtv") == -1 && parseFloat(navigator.appVersion.split("MSIE")[1]));
// Internet Explorer < 8
isOldIE = (isIE && isIE < 8);
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
        if( Number(r) > Number(e) ) e=r;
    }
    return e;
}

function hashCount(obj){ //for hash with numeric keys only
    var count = 0;
    for(var prop in obj) {
        if(obj.hasOwnProperty(prop))
            ++count;
    }
    return count;
}

function getElementsByClassName(searchClass, node, tag) {
    node = node || document;
    tag = tag || '*';
    var regexp = new RegExp('(\\s|^)'+searchClass+'(\\s|$)');
    return filter(function(ele){ return ele.className.match(regexp); },
                    node.getElementsByTagName(tag));
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

function camelize(text) {
    return text.replace(/-+(.)?/g, function (match, chr) {
        return chr ? chr.toUpperCase() : '';
    });
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
    ajax.load('get', qw, new RequestProcessor({
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

function map(callback, array, environ, forcearray){
    if(!isFunction(callback))
        throw new TypeError(callback + " is not a function");
    var ret;
    if(!forcearray && isHash(array) && !isNodeList(array)){
        ret = new Object();
        for(var k in array)
            ret[k] = callback.call(environ, array[k]);
    }else{
        ret = new Array();
        for(var i = 0; i < array.length; i++)
            ret.push(callback.call(environ, array[i]));
    }
    return ret;
}

function filter(callback, array, environ, forcearray){
    if(!array)
        return [];
    if(!isFunction(callback))
        throw new TypeError(callback + " is not a function");
    var ret;
    if(isArray(array) || isNodeList(array) || forcearray){
        ret = new Array();
        for(var i = 0; i < array.length; i++)
            if(callback.call(environ, array[i])) ret.push(array[i]);
    }else if(isHash(array)){
        ret = new Object();
        for(var k in array)
            if(callback.call(environ, array[k])) ret[k] = array[k];
    }else
        throw new TypeError((typeof array) + " not supported by filter.");
    return ret;
}

function range(start, end){
    var s = []
    if(end >= start){
        for(var i=start; i <= end; i++)
            s.push(i)
    }
    return s
}

function extend(oobj){
    var obj = oobj ? oobj.constructor() : {}
    var type = typeof obj
    for(var attr in oobj)
        if (oobj.hasOwnProperty(attr))
            obj[attr] = oobj[attr]

    if(arguments.length >= 1)
        for(var i = 1; i < arguments.length; i++){
            var arg = arguments[i]
            if(!arg)
                continue
            if(typeof arg != type)
                throw new TypeError('Argument type does not match')
            for(var name in arg)
                if(arg.hasOwnProperty(name))
                    obj[name] = arg[name]
        }
    return obj
}



