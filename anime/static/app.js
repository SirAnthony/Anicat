//##############################################################################
//##############################    Автодополнение   ###########################
//##############################################################################

function Autocomplete(object, objectattrs, types, retval){
    this.object = object;
    this.node = null;
    this.types = types;
    this.retfield = retval;
    this.text = '';
    this.processor = null;
    this.retintypes = false;
    this.opts = {
        delay: 1000,
        left: 0,
        top: 0,
        limit: 8,
    },

    this.selected = null;

    var timeout = null;

    for(var t in types){
        if(retval == types[t]){
            this.retintypes = true;
            break;
        }
    }

    if(types.indexOf('id') < 0){
        types.push('id');
    }


    this.init = function(){
        this.node = element.create('ul', objectattrs);
        element.insert(this.object, this.node, true);
        addEvent(this.object, 'keyup', (function(app){
                return function(e){ return app.keyevent.call(app, e); }})(this))
        this.text = this.object.value;
        this.processor = new RequestProcessor(this.processResponse, 'search', this)
    }

    this.visible = function(){
        return this.node.style.display == 'block';
    }

    this.keyevent = function(event){
        if(!event) event = window.event;
        var ret = true;
        var prevent = function(e){
            if(e.preventDefault) e.preventDefault();
            else e.returnValue = false;
            ret = false;
        }
        switch(event.keyCode){
            case 38: // up
                if(this.visible()) this.moveSelection(-1);
                prevent(event);
                break;
            case 40: // down
                if(this.visible()) this.moveSelection(1);
                prevent(event);
                break;
            case 9:  // tab
            case 13: // return
                if(this.visible() && this.selected)
                    this.setValue.call(this, this.selected);
                prevent(event);
            break;
            default:
                if(event.keyCode > 32) this.hide();
                this.selected = null;
                if (this.timeout) clearTimeout(this.timeout);
                this.timeout = setTimeout((function(t){
                    return function(){ t.process.call(t); }})(this),
                    this.opts.delay);
            break;
        }
        return ret;
    }

    this.hide = function(){
        toggle(this.node, false);
    }

    this.setSelection = function(elem){
        element.downTree(function(el){pclass.remove(el, "app_over");}, this.node);
        this.selected = elem;
        this.object.focus();
        pclass.add(this.selected, "app_over");
    }

    this.removeSelection = function(elem){
        element.downTree(function(el){pclass.remove(el, "app_over");}, this.node);
        if(this.selected == elem){
            this.selected = null;
        }
    }

    this.moveSelection = function(step){
        if(this.timeout)
            clearTimeout(this.timeout);
        element.downTree(function(el){pclass.remove(el, "app_over");}, this.node);
        var sign = step/Math.abs(step);
        if(!this.selected){
            this.selected = this.node.firstChild;
        }else{
            for(var i = 0; i < Math.abs(step); i++){
                var sel = ((sign > 0) ?
                    this.selected.nextSibling : this.selected.previousSibling);
                if(sel)
                    this.selected = sel;
            }
        }
        pclass.add(this.selected, "app_over");
    },

    this.process = function(){
        if(this.object.value.length < 2 || this.text == this.object.value)
            return;
        this.text = this.object.value;
        ajax.loadXMLDoc(url+'search/', {'fields': this.types,
                        'limit': this.opts.limit, 'string': this.text},
            this.processor);
    }

    this.processResponse = function(resp){
        var ul = this.object.nextSibling;
        element.removeAllChilds(ul);
        toggle(ul, true);
        if(!resp.status){
            element.appendChild(ul, {'li': {'innerText': resp.text}});
        }else{
            var list = resp.text.list;
            for(var i in list){
                var content = map(function(t){
                    return {'input': {'type': 'hidden', 'name': t, 'value': list[i][t]}};
                    }, types);
                content.push.apply(content, this.view(list[i]));
                element.appendChild(ul, [{'li': {'onclick': (function(app){
                    return function(){ app.setValue.call(app, this); }})(this),
                    'onmouseover': (function(app){
                    return function(){ app.setSelection.call(app, this); }})(this),
                    'onmouseout': (function(app){
                    return function(){ app.removeSelection.call(app, this); }})(this),
                    }}, content]);
            }
        }
    }

    this.setValue = function(elem){
        if(this.retintypes){
            var value = ''
            element.downTree(function(el){
                if(el.tagName == 'INPUT' && el.type == 'hidden' && el.name == retfield)
                    value = el.value;
            }, elem);
        }else{
            var id;
            element.downTree(function(el){
                if(el.tagName == 'INPUT' && el.type == 'hidden' && el.name == 'id')
                    id = el.value;
            }, elem);
            if(!id) return;
            ajax.loadXMLDoc(url+'get/', {'id': id, 'field': this.retfield},
                new RequestProcessor(this.ajaxProcessor, 'get', this));
        }
        element.downTree(function(el){pclass.remove(el, "app_over");}, this.node);
        this.selected = null;
    }

    this.view = function(){
        return []
    }

    // Ajax processor calls with Autocomplete object as this
    this.ajaxProcessor = function(resp){};


    this.highlight = function(str){
        if(this.text){
            var re = new RegExp("("+this.text+")", "ig");
            return str.replace(re, "<b>$1</b>");
        }
        return str;
    },


    this.init();
}
