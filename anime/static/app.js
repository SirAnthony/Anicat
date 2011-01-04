//##############################################################################
//##############################    Автодополнение   ###########################
//##############################################################################

var app = {
        
    appobj: null,
    appdiv: null,
    apparea: null,
    keyCode: null,
    res: new Array(),
    appajax: null,
    text: null,
    selected: -1,
    retfunct: null,
    appurl: '/cgi-bin/app.pl',
    timeout: null,    
    opts: {
        delay: 7500,
        kdelay: 1000,
        left: 0,
        top: 0
    },    
    
    acomp: function(obj, ar, e){        
        
        this.appobj = obj;
        this.setFocus(this.appobj);
        this.apparea = ar;
        if(!this.appdiv){
            this.appdiv = element.create('div', {className: 'app_div'});
            element.appendChild(document.body, [this.appdiv]);
        }
        if(!e) e = window.event;
        this.keyCode = e.keyCode;
        switch(e.keyCode) {
            case 38: // up
                if(this.appdiv.style.display == 'block') this.moveSelect(-1);
                if(e.preventDefault) e.preventDefault();
                else e.returnValue = false;
                break;
            case 40: // down
                if(this.appdiv.style.display == 'block') this.moveSelect(1);
                if(e.preventDefault) e.preventDefault();
                else e.returnValue = false;
                break;
            case 9:  // tab
            case 13: // return
                if(this.appdiv.style.display == 'block' && this.selected >= 0){
                    this.selectCur();
                    this.appobj.blur();
                }
                if(e.preventDefault) e.preventDefault();
                else e.returnValue = false;
            break;
            default:
                if(e.keyCode > 32) this.hideRes();
                this.selected = -1;
                if (this.timeout) clearTimeout(this.timeout);
                this.timeout = setTimeout(function(){app.change();}, this.opts.kdelay);
            break;
        }        
    },
    
    change: function(){
        if( this.keyCode == 46 || (this.keyCode > 8 && this.keyCode < 32) ) 
            return this.hideRes();
        if( this.text != this.appobj.value){        
            this.text = this.appobj.value;            
            if(this.appobj.textLength > 2){                                
                this.setpos(this.appdiv, this.appobj);
                var params = {
                    method: 'auto',
                    value: this.appobj.value,
                    area: this.apparea
                }
                this.getarr(this.autores, params);                 
            }else{
                this.hideRes();
            }
        }        
    },
    
    moveSelect: function(step){
        
        if (this.timeout) clearTimeout(this.timeout);
        var lis = getChilds(this.appdiv.firstChild);
        element.downTree(function(el){pclass.remove(el, "app_over");}, this.appdiv.firstChild);                         
        this.selected += step;
        if(this.selected <= 0){
            this.selected = 0;
        }else if(this.selected >= lis.length){
            this.selected = lis.length - 1;
        }
        pclass.add(lis[this.selected], "app_over");
    },

    getarr: function(funct,params){
        
        this.retfunct = funct;
        this.appajax = '1';
        qw = 'method='+
        ((params['method']) ? params['method'] : "none") +
        ((params['value']) ? "&string="+params['value'] : "") +
        ((params['area']) ? "&area="+params['area']: "") +
        ((params['local']) ? "&local="+params['local']: "");                        
        loadXMLDoc(this.appurl, qw);
    },
    
    autores: function(text){
        this.res = eval(text);
        if(this.appdiv.firstChild)
            this.appdiv.removeChild(this.appdiv.firstChild);
        var ul = document.element.createent('ul');                
        for (var i=0; i < this.res.length; i++) {
            var li = element.create('li', {
                innerHTML: this.highLight(this.res[i].name),  // change to append
                selectValue: this.res[i],
                onmouseover: function(){
                    if(app.timeout) clearTimeout(app.timeout);
                    var sel = (function(obj,c){
                        for(var i=0; i<c.length; i++){if(c[i]==obj)    return i;}
                    })(this, this.parentNode.childNodes);
                    if(app.selected >= 0){
                        var old = this.parentNode.childNodes[app.selected];
                        pclass.remove(old, "app_over");
                    }
                    pclass.add(this, "app_over");
                    app.selected = sel;
                },
                onmouseout: function(){
                    app.timeout = setTimeout(function(){app.hideRes();}, app.opts.delay);
                    pclass.remove(this, "app_over");
                    app.selected = -1;
                },
                onclick: function(e){
                    if(e.stopPropagation) e.stopPropagation();
                    else e.cancelBubble = true;
                    if(e.preventDefault) e.preventDefault();
                    else e.returnValue = false;                     
                    app.selectCur(this);
                }
            });
            element.appendChild(ul,[li]);
        }                
        element.appendChild(this.appdiv, [ul]);
        this.retfunct = null;        
        this.appdiv.style.display = 'block';
        if (this.timeout) clearTimeout(this.timeout);
        this.timeout = setTimeout(function(){app.hideRes();}, this.opts.delay);  
    },
    
    hideRes: function(){
        if (this.timeout) clearTimeout(this.timeout);
        if(this.appdiv.firstChild)
            this.appdiv.removeChild(this.appdiv.firstChild);
        this.appdiv.style.display = 'none';            
    },
    
    hideResult: function() {
        if (this.timeout) clearTimeout(this.timeout);
        this.timeout = setTimeout(function(){app.hideRes();}, 150);
    },
    
    selectCur: function(item){        
        if (this.timeout) clearTimeout(this.timeout);
        var s;
        if(item){
            s = item;            
        }else{
            var f = function(obj){if(pclass.hasClass(obj, "app_over")) return obj;}
            s = element.downTree(f, this.appdiv.firstChild, 1);
        }
        this.appobj.value = ((s.selectValue) ? s.selectValue.name : s.innerHTML);
        if(s.selectValue && s.selectValue.id){
            var id = ((this.appobj.nextSibling.name == "pid") ? this.appobj.nextSibling : (function(obj){
                    var el = element.create('input', {type: 'hidden', name: 'pid'});
                    obj.parentNode.insertBefore(el, obj.nextSibling);
                    return el;})(this.appobj));
            id.value = s.selectValue.id;
        }
        this.text = this.appobj.value;        
        this.hideRes();
    },    
    
    highLight: function(str){
        if(this.text){
            var re = new RegExp("("+this.text+")", "ig");            
            return str.replace(re, "<b>$1</b>");
        }
        return str;
    },
    
    setFocus: function(obj){
        if(!this.appobj.onfocus)
            this.appobj.onfocus = function(){this.hasFocus = true;};
        if(!this.appobj.onblur)
            this.appobj.onblur = function(){this.hasFocus = false; app.hideResult();};
    },
        
    setpos: function(){
        var os = getOffset(this.appobj);
        this.appdiv.style.top = os.top+this.appobj.offsetHeight+this.opts.top+'px';
        this.appdiv.style.left= os.left-this.appobj.offsetLeft+this.opts.left+'px';
    }
    
}
