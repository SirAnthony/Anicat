//add-edit classes module
//var seturl = '/cgi-bin/aniseted.pl';
//################################################################
//##################### Add #######################################
//################################################################

var add = new (function add_class(){
    
    var form = null;
    var loaded = false;
    
    this.init = function(){
        this.createForm();
        this.form = document.getElementById('addfrm');
        if(!this.form) return;
        this.loaded = true;
    } 
    
    this.toggle = function(){
        if(!this.loaded) return;
        if(this.form.style.display == 'block'){
            this.form.style.display = 'none';
            app.opts.top = 0;
            app.opts.left = 0;        
        }else if(!edit.visible){
            this.form.style.display = 'block';
        }    
    }
    
    this.createForm = function(){
        var form = element.create('form', {id: 'addfrm', className: 'cont_men'});
        this.form = form;
        var dv = element.create('div', {className: 'frmdv'});
        element.appendChild(form, [dv, 
            element.create('a', {onclick: function(){add.addField({'pname':'Name:'});}, innerText: 'Add name'}),
            element.create('br'), 
            element.create('a', {onclick: function(){add.getCustomField();}, innerText: 'More'})
        ]);
        this.addField({'pname': 'Base name:', 'pnumberofep': 'Number of episodes:'});
        var select = element.create('select', {'name': 'ptype'});
        element.addOption(select, ['TV', 'OAV', 'Movie', 'SMovie', 'TV-Sp', 'ONA']);
        element.appendChild(dv, [
            element.create('label', {className: 'ac'+ (((dv.childNodes.length % 2) != 0) + 1),
                            innerText: 'Type:'}), [select]]);
        this.addField({'psize': 'Specials count:', 'ptranslation': 'Translation:', 'pduration': 'Duration:'});
        cbox = new Array();
        genres = ['action','adventure','children','comedy','cyberpunk','daily life', 'detective','drama',
                    'ecchi','fairy tale','fantastic','fantasy','hentai','history','horror','mahō shōdjo',
                    'martial arts','mecha','music','mystery','parody','police','postapocalyptic','psychology',
                    'romance','samurai','school','shōjo','shōdjo-ai','shōnen','sport','steampunk','thriller',
                    'vampires','war','yaoi','yuri']
        for(var i in genres){
            gname = genres[i].charAt(0).toUpperCase()+genres[i].slice(1)
            var label = element.create('label', {innerText: gname})
            element.appendChild(label, [element.create('input', {'type': 'checkbox', 'name': genres[i]})]);
            cbox.push(label);
        }
        element.appendChild(dv, [ element.create('label', { 'name': 'pgenre', innerText: 'Genre:'}), cbox]);
        element.appendChild(dv, [
            element.create('input', {className: 'ac'+ (((dv.childNodes.length % 2) != 0) + 1), 'type': 'button',
                        value: 'Clear', onclick: function(){add.clearForm();}}),
            element.create('input', {className: 'ac'+ (((dv.childNodes.length % 2) != 0) + 1), 'type': 'button',
                        value: 'Ok', onclick: function(){add.sendForm();}})]);
        form.style.display = 'none';
        element.appendChild(document.body, [form]);
    }
    
    this.addField = function(fields){
        if(!this.form) return;
        var div = this.form.firstChild;
        var dchild = div.childNodes.length;
        for(var fname in fields){
            element.appendChild(div, [
                element.create('label', {className: 'ac'+(((dchild % 2) != 0) + 1), innerText: fields[fname]}),
                [element.create('input', {'type': 'text', 'name': fname})]])
            dchild++;
        }
    }
    
    this.clearForm = function(){
        if(!this.loaded) return;
        element.removeAllChilds(this.form);
        document.body.removeChild(this.form);
        this.createForm();
        this.toggle();
    }
    
    this.getCustomField = function(a, funct){
        /*var proto;
        var ar;
        if(!a) a = 'people';
        ((a.value)? ar = a.value : ar = a);
        if(!funct) funct = this.addCustomField;
        add_class.prototype.area = a;
        switch(ar){
            case 'organisation':
                proto = add_class.prototype.ores;
            break;
            default:
                proto = add_class.prototype.pres;
            break;
        }
        if(!proto){
            var params = {
                method: 'all',
                area: ar+'bun',
                local: 'job'
            }
            app.getarr(funct, params);
        }else{
            funct(proto);
        }*/
    }  
    
    this.addCustomField = function(text){        
        /*this.res = eval(text);
        this.res.push('new');
        writeProto();
        var form = document.getElementById('addfrm');
        var div = createElem('div', {className: 'adddiv'}); //use fieldset
        var name = createElem('input',{name: 'pname',
            onkeyup: function(event){
                var area = this.previousSibling.value;
                app.opts.top = 35;
                app.opts.left = 276;
                app.acomp(this, area, event);}
        });
        var job = createElem('select',{
            name: 'pjob',
            onchange: function(){
                if(this.selectedIndex == this.length -1){
                    var o = createElem('input',{ name: 'pjob'});                                
                    o.onfocus = clearOnFocus('Staff', o);                    
                    this.parentNode.insertBefore(o, this);
                    this.parentNode.removeChild(this);
                }else if(this.value == 'Cast'){
                    var o = createElem('input',{ name: 'pcast'});
                    o.onfocus = clearOnFocus('as...', o);
                    this.parentNode.insertBefore(o, this.nextSibling);
                }else{//remove cast
                    var f = function(obj){if(obj.name == 'pcast')
                        obj.parentNode.removeChild(obj);}
                    allelements(f, this.parentNode);
                }
            }});
        var who = createElem('select',{
            onchange: function(){
                var f = function(obj){if(obj.name == 'pcast')
                    obj.parentNode.removeChild(obj);}
                allelements(f, this.parentNode);
                add.getfield(this, add.createjob);
            }});        
        var hr = document.createElement('hr');        
        var comment = createElem('input',{ name: 'pcomm'});        
        name.onfocus = clearOnFocus('Name...', name);        
        comment.onfocus = clearOnFocus('Comment...', comment);        
        var opt = createElem('option',{ value: 'Staff', text: 'Staff'});
        appChild(job,[opt]);        
        addopt(who, ['people','organisation']);        
        addopt(job, this.res);
        var a = document.getElementById('a_elm');
        appChild(div,[who,name,job,comment,hr]);
        form.insertBefore(div, form.lastChild);
        var ot = div.offsetTop; 
        if( ot < 200)
            div.style.marginTop = 280+'px';
        */                        
    }
    
    this.sendForm = function(){
        //TODO: Меню в отдельный клас давно пора с методами setText или типа того.
        var dv = document.getElementById('menu');
        dv.style.top = '200px';
        dv.style.left = '600px';
        var fm = document.getElementById('addfrm');
        var check = this.checkForm(fm)
        if(check == 'ok'){
            var qw = 'add&string=catalog';
            var a = function(elm){
                if( elm.tagName == "INPUT" || elm.tagName == "TEXTAREA" || elm.tagName == "SELECT"){
                    if(elm.type != "button" && elm.type != "hidden"){
                        var val = rsemicolon(elm.value.replace(/\n/g, "<br/>"));
                        var nm = elm.name;
                        if(nm) nm += ','
                        if(!/;$/.test(qw)) qw += ',';
                        qw += nm+val;
                    }
                }
            }
            var f = function(elm){
                if(elm.tagName == 'DIV'){
                    allelements(a,elm);
                    if(!/;$/.test(qw))
                        qw += ';';
                }
            }
            element.downTree(f,fm);
            //alert(qw);
            //clearProto();
            //if(!isIE){ loadXMLDoc(url, qw);
            //}else{ alert('Enjoy ur ie.');}
            //document.getElementById('addfrm').style.display = 'none';
        }else{
            alert(check);
        }  
    }
    
    this.checkForm = function(form){        
        var f = function(elm){
            if(elm.tagName == 'DIV'){
                var funct = function(a){return add.checkFunction(a);};
                var e = element.downTree(funct, elm);
                return e;
            }
        }
        var e = element.downTree(f, form, 1);
        return e;        
    }
    
    this.checkFunction = function(elm){
        if( elm.tagName == "INPUT" || elm.tagName == "TEXTAREA" || elm.tagName == "SELECT"){
            if(elm.type != "button"){
                switch(elm.name){                    
                    case 'pname':
                        if(elm.value == 'Name...' || !elm.value || /^\s+$/.test(elm.value)){
                             return 'Bad name';}
                    break;
                    case 'pjob':
                        if(!elm.value || /^\s+$/.test(elm.value)){
                            return 'Specialisation incorrect';
                        }else if(/[^A-Za-z0-9 -]/.test(elm.value)){
                             return 'Specialisation must consist of letters, digits, spaces and dashes.';
                        }
                    break;
                    case  'pcast':
                        if(!elm.value || /^\s+$/.test(elm.value) || elm.value == 'as..'){
                            elm.value = '';
                        }else if(/[^A-Za-z0-9 '-_]/.test(elm.value)){ //'
                            return 'Role  must consist of letters, digits, spaces and dashes.';
                        }
                    break;
                    case  'pcomm':
                        if(elm.value == 'Comment...') elm.value = '';
                    break;
                }
            }
        }
    }
    
    /*this.res = new Array();
    
    var clearProto = function(){
        add_class.prototype.area = 'undefined';
        add_class.prototype.ores = 'undefined';
        add_class.prototype.pres = 'undefined';
    }
    var writeProto = function(){
        var area;
        ((add_class.prototype.area.value)? 
            area=add_class.prototype.area.value : area = add_class.prototype.area); 
        switch(area){
            case 'organisation':
                if(!add_class.prototype.ores)
                    add_class.prototype.ores = this.res;                
            break;
            default:
                if(!add_class.prototype.pres)
                    add_class.prototype.pres = this.res;                
            break;
        }
    } 
    
    this.createjob = function(text){        
        this.res = eval(text);        
        writeProto();
        var node = add_class.prototype.area;
        var pjob = allelements(function(e){if(e.name=='pjob') return e;},node.parentNode,1);
        if(pjob.tagName!="SELECT"){
            var npjob = createElem('select',{ name: 'pjob',
            onchange: function(){
                if(this.selectedIndex == this.length -1){
                    var o = createElem('input',{ name: 'pjob'});                                
                    o.onfocus = clearOnFocus('Staff', o);                    
                    this.parentNode.insertBefore(o, this);
                    this.parentNode.removeChild(this);
                }
            }});
            pjob.parentNode.insertBefore(npjob, pjob);
            pjob.parentNode.removeChild(pjob);
            pjob = npjob;                
        }
        for(var i=pjob.options.length-1;i>=0;i--){pjob.remove(i);}
        this.res.push('new');
        addopt(pjob, this.res);
                
    }
    
    this.setnum = function(){ // Маленькая такая функция, которая занимается фигней
        // уже не занимается
        var cng = document.getElementById('type');
        var num = document.getElementById('numberofep');    
        switch(cng.value){
            case 'TV':
                num.value = '25';
            break;            
            case 'OAV':
                num.value = '2';
            break;
            default:
                num.value = '1';
            break;
        }
    }
    
    this.clear = function(){
    
        var fm = document.getElementById('addfrm');    
        for(var i=0; i < fm.childNodes.length; i++){        
            for(var g=0; g<fm.childNodes[i].childNodes.length-1; g++){
                var frm = fm.childNodes[i].childNodes[g];
                if( frm.tagName == "INPUT" || frm.tagName == "TEXTAREA"){
                    if(frm.type != "button") frm.value = "";                    
                }                    
            }
        }
    }
    
    this.checkFunction = function(elm){
        if( elm.tagName == "INPUT" || elm.tagName == "TEXTAREA" || elm.tagName == "SELECT"){
            if(elm.type != "button"){
            if(elm.id ==  'name'){if(!elm.value || /^\s+$/.test(elm.value)){return 'Имя не заполнено';}};                    
                switch(elm.name){                    
                    case  'pname':
                        if(elm.value == 'Name...' || !elm.value || /^\s+$/.test(elm.value)){
                             return 'Имя не заполнено';}
                    break;
                    case  'pjob':
                        if(!elm.value || /^\s+$/.test(elm.value)){return 'Специализация не заполнена';
                         }else if(/[^A-Za-z0-9 -]/.test(elm.value)){
                             return 'Специализация может содержать только символы латинского алфавита, цифры пробелы и тире';
                        }
                    break;
                    case  'pcast':
                        if(!elm.value || /^\s+$/.test(elm.value) || elm.value == 'as..'){
                            elm.value = '';
                        }else if(/[^A-Za-z0-9 '-_]/.test(elm.value)){ //'
                            return 'Роль может содержать только символы латинского алфавита, цифры, пробелы, одинарную кавычку и тире';
                        }
                    break;
                    case  'pcomm':
                        if(elm.value == 'Comment...') elm.value = '';
                    break;
                }
            }
        }
    }
    
    var checkForm = function(form){        
        var f = function(elm){
            if(elm.tagName == 'DIV'){
                var funct = function(a){return add.checkFunction(a);};
                var e = allelements(funct, elm);
                return e;
            }
        }
        var e = allelements(f,form, 1);
        return e;        
    }
    
    this.accept = function(){    
    
        var dv = document.getElementById('menu');
        dv.style.top = '200px';
        dv.style.left = '600px';
        var fm = document.getElementById('addfrm');
        var check = checkForm(fm)
        if(check == 'ok'){                         
            var qw = 'add&string=catalog';            
            var a = function(elm){
                if( elm.tagName == "INPUT" || elm.tagName == "TEXTAREA" || elm.tagName == "SELECT"){                    
                    if(elm.type != "button" && elm.type != "hidden"){
                        var val = rsemicolon(elm.value.replace(/\n/g, "<br/>"));                        
                        var nm = elm.name;
                        if(nm) nm += ','
                        if(!/;$/.test(qw)) qw += ',';                                
                        qw += nm+val;                        
                    }
                }
            }
            var f = function(elm){
                if(elm.tagName == 'DIV'){ 
                    allelements(a,elm);
                    if(!/;$/.test(qw)) 
                        qw += ';';
                }
            }            
            allelements(f,fm);                
            //alert(qw);
            clearProto();
            if(!isIE){ loadXMLDoc(url, qw);
            }else{ alert('U use ie. Enjoy your adis');}
            //document.getElementById('addfrm').style.display = 'none';                            
        }else{
            alert(check);
        }    
    }     
*/
})();

//################################################################
//##################### Edit #######################################
//################################################################

var edit = new (function edit_class(){

    var visible = false;
    
    this.init = function(){
        this.loaded = true;
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
        return {main: edtdv, ul: ul,     fs: fs, leg: leg};
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
                qw +=    ',pcomm,'+rsemicolon(elm.comm.value);
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

//################# Редактироване полей.

/*function edt(tag,num,e){

    if(!mfl){
        mfl = 2;        
        document.getElementById('menu').style.display = 'none';
        menupos();    
        elm = document.getElementById(tag+num);
        //долой обходные маневры. будем получать ширину по ид элементов шапки
        var cs = elm.offsetWidth - 5; 
        if(!elm.firstChild){
            elm.innerHTML = '<input type="text" id="edtbox"    value="" onkeydown="if(event.keyCode==13){acpedt(event)}">';    
        }else{
            elm.innerHTML = '<input type="text" id="edtbox" onkeydown="if(event.keyCode==13){acpedt(event)}" value="'+elm.firstChild.nodeValue+'">';
        }
        var ebox = document.getElementById('edtbox');
        ebox.style.width = cs + 'px'; 
        ebox.select();
        edtdv = 1;        
        document.onclick = acpedt;
            
    }
}*/

//################# Применение изменений.

/*function acpedt(e){
    
    var idd = elm.id; //глобальность плохо сказывается
    var keydwn = false;
    if(e && e.type == "keydown"){keydwn = true;}
    var target=e?e.target:event.srcElement;
    var tpar = target.parentNode;
    if(!keydwn && ( target == elm || tpar == elm )){
    }else{
        var eid = idd.replace(/\D+/, "");
        var tag = idd.replace(/\d+/, "");
        var value = elm.firstChild.value;        
        value = value.replace(/\n/g, "<br/>");
        if(tag == "numberofep"){
            if(!/[\d]/.test(value) || value < 0){value = "-1";}
        }                                
        var qw = "edit="+tag+"&id="+eid+"&string="+value;        
        loadXMLDoc(url, qw);
        //elm.innerHTML = elm.firstChild.value;
        document.onclick = undefined;
        edtdv = 0;        
    }    
}*/


//Для редактирования менюшки обычные способы смогли бы подойти, но это прийдется делать через жопу
//Поэтому будет еще одна функция

//################# Редактирование меню.

function mnedt(elid,nam,e){
/*    
    if(!edtdv){
        elm = document.getElementById(elid+nam);
        var ebox;
        if(elid == 'anothername'){
            if(elm.innerHTML == 'Править'){
                elm.innerHTML = '<textarea rows="10" cols="50" id="edta" wrap="hard"></textarea>';
            }else{
                var wdt = elm.parentNode.offsetWidth;
                if(wdt < 345){wdt = 345;}
                var rtx = elm.innerHTML.replace(/<br>/ig, "\n");            
                elm.innerHTML = '<textarea rows="7" id="edta" wrap="hard">'+rtx+'</textarea>';
                document.getElementById('edta').style.width = wdt-1+'px';;
            }
            ebox = document.getElementById('edta');
        }else{
            if(elm.innerHTML == 'Править'){
                elm.innerHTML = '<input type="text" onkeydown="if(event.keyCode==13){acpedt(event)}" id="edtbox" value="">';
                document.getElementById('edtbox').style.width = elm.parentNode.offsetWidth-1+'px';
            }else{
                elm.innerHTML = '<input type="text" onkeydown="if(event.keyCode==13){acpedt(event)}" id="edtbox" value="'+elm.innerHTML+'">';
                document.getElementById('edtbox').style.width = elm.parentNode.offsetWidth-1+'px';
            }
            ebox = document.getElementById('edtbox');
        }
        ebox.focus();
        edtdv = 1;    
        document.onclick = acpedt;    
    }
*/
}
