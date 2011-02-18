// Ну без копирайта неинтересно, правда?
// Anicat js part v 1.99

var mCur; // Хранит текущую позицию мыши
var xmlHttp;
var mfl = 0;    // 0 - никаких действий. 1 - меню открыто, заболкирован инпут под ним.
         // 2 - заблокировано инпутом, закрыто.
var elm; //
var url = '/ajax/';
var edtdv = 0; // эта переменная определяет редактируется ли менюшка или нет
var timer;
var ua = navigator.userAgent.toLowerCase();
var corovan = 0;

//##############################################################################
//##############################    Разное   ###################################
//##############################################################################

var element = new ( function(){
    
    this.downTree = function(funct, obj, er){
        if(!funct || !obj) return;
        for(var i=0; i < obj.childNodes.length; i++){
            var e = funct(obj.childNodes[i]);
            if(e) return e;
        }
        if(er) return 'ok';
    }
    
    this.addOption = function(obj, arr){
        if(arr.length){
            for(var i=0; i < arr.length; i++){            
                var opt = this.create('option', {value: arr[i], text: arr[i]});
                this.appendChild(obj, [opt]);
            }
        }else{
            for(var i in arr){
                var opt = this.create('option', {value: i, text: arr[i]});
                this.appendChild(obj, [opt]);
            }
        }
    }
    
    this.getChilds = function(obj){
        var childs = new Array();
        for(var i=0; i < obj.childNodes.length; i++){
            childs.push(obj.childNodes[i]);        
        }
        return childs;
    }
    
    this.removeAllChilds = function(el){
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
        this.removeAllChilds(elem);
        if(elem.parentNode)
            elem.parentNode.removeChild(elem);
    }      
    
    this.appendChild = function(obj, arr){
        var ar = new Array();
        ar = eval(arr);
        var l = ar.length;
        if(!l) l = 0;
        for(var i=0; i < l; i++){
            if(!ar[i] || (!isElement(ar[i]) && !isArray(ar[i]) && !isHash(ar[i]))) continue;
            if(isHash(ar[i])){
                var el = ar[i];
                var type = el['elemType'];
                delete el['elemType'];
                ar[i] = this.create(type, el);
            }
            if(isArray(ar[i])){
                this.appendChild(ar[i-1], ar[i]);
            }else{
                obj.appendChild(ar[i]);
            }
        }
    }
    
    this.insert = function(obj, elem){        
        obj.parentNode.insertBefore(elem, obj);
    }
})();

//################# Работа с куами.

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

//################# Классы

var pclass = new ( function(){

    this.hasClass = function(ele, cls){
        return ele.className.match(new RegExp('(\\s|^)'+cls+'(\\s|$)'));
    }

    this.add = function(ele, cls){
        if(!this.hasClass(ele, cls))
            ele.className += ' '+cls;
    }

    this.remove = function(ele, cls){
        if (this.hasClass(ele,cls)){
            var reg = new RegExp('(\\s|^)'+cls+'(\\s|$)');
            ele.className=ele.className.replace(reg,'');
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

//################# Поиск

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
        element.removeAllChilds(this.result);
        if(!page) page = 1;          
        //var text =  document.getElementById('sin');    
        var val; // = document.getElementById('advsrch').value;
        var sort; // = document.getElementById('sortsrch').value;
        if(this.input.textLength < 3 && val != 'numberofep' && val != 'type'){
            element.appendChild(this.result, [element.create('p', {
                innerText: 'Query must consist of at least 3 characters.'})]);
        }else if( /\.{2,3}/.test(this.input.value) || /\.{1}(\s{1}|\S{1})\.{1}/.test(this.input.value) ){
            element.appendChild(this.result, [element.create('p', {innerText: 'Invalid request.'})]);
        }else{
            var text = this.input.value.toLowerCase();
            var qw;
            if(val && val != 'null' && val != 'name'){
                qw = 'page='+page+'&search=' + val + '&string=' + text;
            }else{
                qw = 'page='+page+'&search=name&string=' + text;
            }
            if(sort && sort != 'null' && sort != 'name'){
                qw += '&sort=' + sort;
            }
            var menu = document.getElementById('menu');
            menu.style.top = 65 + 'px';
            menu.style.left = 40 + 'px';                
            ajax.loadXMLDoc(url,qw);
        }
    }
    
    this.putResult = function(rs){
        if(!this.loaded) return;
        if(rs.data == 'none'){
           element.appendChild(this.result, [element.create('p', {innerText: 'Nothing found.'})]);
        }else{
            var tr = new Array();
            for(i in rs.data){            
                var row = element.create('tr');
                tr.push(row);
                var elem = rs.data[i];
                element.appendChild(row, [
                                    element.create('td', {'id': 'link' + elem.id, className: 'link'}), [
                                        element.create('a', {className: 'cardurl', 'target': '_blank',
                                                                    'href': '/card/'+elem.id+'/'}), [
                                            element.create('img', {'src': '/templates/arrow.gif', 'alt': 'Go'}),
                                            ]
                                        ],
                                    element.create('td', {'id': 'id' + elem.id, className: 'id',
                                    onclick: (  function(i, j){ 
                                                    return function(){ cnt(i, j); };
                                                })('id', elem.id),
                                             innerText: Number(i) + 1 + rs.results * (rs.page - 1) }),
                                    ]);
                for(var helem in rs.header){
                    var column = rs.header[helem].name;
                    element.appendChild(row, [element.create('td', {'id': column + elem.id, className: column, 
                                onclick: (function(i, j){ return function(){ cnt(i, j); };})(column, elem.id),
                                    innerText: encd(elem[column])})]);
                }
                if(elem.job){
                   pclass.add(row, 'r' + elem.job + ((elem.air) ? 'on': '' ));
                }
            }
            element.appendChild(this.result, [element.create('table', {'id': 'srchtbl', className: 'tbl', 
                                            cellSpacing: 0}), tr]);
            if(rs.count > rs.results){
                var pg = new Array();
                for( var i = 1; i < (rs.count / rs.results + 1); i++){
                    if(rs.page == i){
                        pg.push(element.create('span', {innerText: '[' + i + ']'}));
                    }else{
                        pg.push(element.create('a', {innerText: i, 
                                onclick: (function(pg){ return function(){ searcher.send(pg);};})(i)}));
                    }
                }
                element.appendChild(this.result, [element.create('div', {'id': 'srchpg'}), pg]);
            }
        }
        if(rs.time)
            element.appendChild(this.result, [element.create('span', {innerText: 'Search time: '+rs.time+'s.'})]);
        document.getElementById('menu').style.display='none';        
    }
        
})();

//######################## Messages process

function message(str, timeout){
    
    this.strobj = new Array();
    
    this.timeout = timeout;
    
    this.getSpan = function(){
        if(!this.span)
            this.span = document.getElementById('mspan');
        return this.span;
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
    
    //Add html string to message.
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
    
    //Show message. 
    this.show = function(){
        if(!this.getSpan())
            return;
        element.removeAllChilds(this.span);
        element.appendChild(this.span, this.strobj);
        this.span.parentNode.style.display = 'block';
        if(this.timeout)
            timer = setTimeout("document.getElementById('menu').style.display='none';", this.timeout);
    }
    
    this.hide = function(){
        if(!this.getSpan())
            return;
        this.span.parentNode.style.display = 'none';
    }
    

    this.add(str);

};

//########################

function getOffset(obj){
    var el = obj;
    var offset = {top: 0, left: obj.offsetLeft};
    while(el.parentNode.parentNode.nodeName != "BODY"){
        el = el.parentNode;
        offset.top += el.offsetTop; 
        offset.left += el.offsetLeft;
    }
    return offset;    
}

//#######################

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
/*    // Opera
    isOpera = (ua.indexOf("opera") != -1);
    // Gecko = Mozilla + Firefox + Netscape
    isGecko = (ua.indexOf("gecko") != -1);
    // Safari
    isSafari = (ua.indexOf("safari") != -1);
    // Konqueror, используется в UNIX-системах
    isKonqueror = (ua.indexOf("konqueror") != -1);    
*/

/* 
if (! isIE) {
HTMLElement.prototype.__defineGetter__("innerText",
function () { return(this.textContent); });
HTMLElement.prototype.__defineSetter__("innerText",
function (txt) { this.textContent = txt; });
}
*/
if (! isIE) {
    if ( !isUndef(Node) && !isUndef(Node.prototype) && isFunction(Node.prototype.__defineGetter__)){
        Node.prototype.__defineGetter__("innerText", function() { return this.textContent; });    
        Node.prototype.__defineSetter__("innerText", function(val){this.textContent ="";
                this.appendChild(document.createTextNode(val));    });
    }
}


// Доставляет попапы на длинные имена. Срабатывает при загрузке
window.onload = function(){

    user.init();
    searcher.init();
    if(typeof(variableName) != "undefined") add.init();
    mv();
    //document.getElementById('srch').style.display = 'none';
    showFN();
    if(isIE){
        document.getElementById('ie').innerHTML = "В данном браузере проект работает некорректно. И вообще браузер-корявко."
        /*var cn = document.getElementById('menu');
        cn.removeChild(cn.firstChild);*/
    }
    //var wtr = document.getElementById('wtr')    
    //document.getElementById('dvid').style.width = wtr.scrollWidth+2+'px';
    //if(wtr.scrollWidth >= window.outerWidth){
        //document.getElementById('header').style.width = window.outerWidth + window.scrollMaxX - 32 + 'px';
    //}        
    
}

//Расставляет попапы с тем, что скрыто
function showFN(tbl){
    var el;
    (tbl) ? el=document.getElementById('srchtbl').firstChild:el=document.getElementById('tbdid');
    var elms = new Array();
    elms = getElementsByClassName("name", el, 'td');
    for(i in elms){
        var el = elms[i];        
        if(el.nextSibling && el.offsetHeight < el.nextSibling.offsetHeight)
            el.style.height = el.nextSibling.offsetHeight + 'px';
        if(el.offsetHeight < el.scrollHeight){
            el.onmouseover = function(){lngnm(this.innerText);}
            el.onmouseout = function(){lngnmo();}
        }
    }     
}

//Копирование в поле
function copyToClipboard(content) {    
    var ids = document.getElementById('idsa').innerHTML
    document.getElementById('idsa').innerHTML = ids + content+' ';
            
}


// Тоже попапы на длинные имена
function lngnm(par,e){    
        menupos(1);
        document.getElementById('popup').style.display = 'block';
        document.getElementById('popups').innerHTML = par;    
}
function lngnmo(){    
        document.getElementById('popup').style.display = 'none';     
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
        //if( /[^\d]/.test(r) )     continue;
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


//доп. функция
function setattr(obj){
    var res = '';
    for(var atr=0; atr<obj.attributes.length; atr++){
        if (obj.attributes[atr]){
            res += obj.attributes[atr].name+'="'+obj.attributes[atr].value+'" ';
        }
    }
    return res;
}

//Режимы отображения

function setshow(){
    var mode = document.getElementById('show').value;
    (mode == 'all') ? mode = '' : mode = '&show='+mode;
    url = location.href.replace(/[\?|\&]{1}\S+$/, "");
    if(location.href != url + mode){
        window.location.href = url + mode;
    }
}


//##############################################################################
//###############################    Меню   ####################################
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
        alert('У вас странный браузер');
    }
    return {"x":x, "y":y};
}

//################# Прячет менюшку

function hideDiv(e){
    var dv = document.getElementById('menu');
    var target=e?e.target:event.srcElement;
    var tpar=target.parentNode;
    if(tpar.parentNode != null){
        var tpar2=tpar.parentNode;    
        if(tpar2.parentNode != null){
            var tpar3=tpar2.parentNode;
            if(tpar3.parentNode != null){var tpar4=tpar3.parentNode;}
        }
    }
    if( target == dv || tpar == dv || tpar2 == dv || tpar3 == dv || tpar4 == dv){
    }else if(mfl == 1){
        dv.style.display = 'none';        
        document.onclick = "undefined";
        mfl = 0;
        clearTimeout(timer);
        
    } 
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
                document.onclick = hideDiv;        // Прятание меню
            }
        }
    }
}

function menupos(pop){
    
    var dv;
    pop ? dv = document.getElementById('popup') : dv = document.getElementById('menu');
    //dv = document.getElementById('menu');    
        
      if (document.all){// если ИЕ
        e = event;
        if (e.pageX || e.pageY){
            var x = e.pageX;
            var y = e.pageY;
        }else if (e.clientX || e.clientY){
            var x = e.clientX + (document.documentElement.scrollLeft || document.body.scrollLeft) - document.documentElement.clientLeft;
            var y = e.clientY + (document.documentElement.scrollTop || document.body.scrollTop) - document.documentElement.clientTop;
        }
        
        dv.style.top = y + 'px';
        dv.style.left = x + 'px';
    //то ставим относительно верхнего элемента - коем является абсолютный див
    // смотрите ниже
    
    }else{ // а если не ие (те мозилла)
        if ( mCur.y+170 >= document.firstChild.clientHeight ){mCur.y = mCur.y - 70;}
              dv.style.top = mCur.y+'px';
        if ( mCur.x+200 >= document.firstChild.clientWidth ){mCur.x = mCur.x - 100;}
              dv.style.left = mCur.x+'px';
    //то все просто - относительно страницы
     }
}

//################# Отрисовка менюшки

function cnt(tag,num,e) {
    
    
    if (mfl != 2){
        //var target=e?e.target:event.srcElement;        
        mfl = 1;
        menupos();
        elm = document.getElementById('name'+num);// В дальнейшем используется глобально
        var name = elm.firstChild.nodeValue;        
        var qw = 'get='+num;
        switch (tag){
            case 'name':
                qw += '&string=name,genre';
            break;
            case 'numberofep':
                qw += '&string=bundle,duration,size';
            break;
            case 'id':
                qw += '&string=state';
            break;
            default:
                qw += '&string='+ tag;
        }
        ajax.loadXMLDoc(url,qw);
    } 
}

//#################
 
//Больше никаких яблок с их кривыми неработающими решениями.

//#################


//##############################################################################
//##########################    Редактирование    ##############################
//##############################################################################

//################# Обработка и отправка формы.

function sndstat(sid, name){    
    
    var sel =  document.getElementById('stid').childNodes;
    var select;
    for(select in sel){ if(sel[select].selected) break; }
    sel = "edit="+name+"&id="+sid+"&string="+select;
    var num =  document.getElementById('stnum');
    if(num){        
        num = num.childNodes;
        var selnumb;
        for(selnumb in num){ if(num[selnumb].selected) break; }
        selnumb++
        sel += "&numnow="+selnumb;
    }
    ajax.loadXMLDoc(url, sel);
}

