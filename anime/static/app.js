/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Autocomplete classes module
 *
 */


function add_auto(obj, attrs, types, retval){
    var comp = new Autocomplete(obj, attrs, types, retval);
    //TODO: event removing
    obj.onfocus = undefined;
}

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

    if(types.indexOf('id') < 0){
        types.push('id');
    }

    for(var t in types){
        if(retval == types[t]){
            this.retintypes = true;
            break;
        }
    }


    this.init = function(){
        attrs = {'className': 'app'};
        attrs = extend(attrs, objectattrs);
        this.node = element.create('ul', attrs);
        element.insert(this.object, this.node, true);
        addEvent(this.object, 'keyup', (function(app){
                return function(e){ return app.keyevent.call(app, e); }})(this))
        this.text = this.object.value;
        this.processor = new RequestProcessor({'search': this.processResponse}, this)
    }

    this.visible = function(){
        return this.node.style.display == 'block';
    }

    this.keyevent = function(event){
        if(!event) event = window.event;
        var prevent = function(e){
            if(e.preventDefault)
                e.preventDefault();
            else
                e.returnValue = false;
            e.stopPropagation();
            return false;
        }
        switch(event.keyCode){
            case 38: // up
                if(this.visible()) this.moveSelection(-1);
                break;
            case 40: // down
                if(this.visible()) this.moveSelection(1);
                break;
            case 9:  // tab
            case 13: // return
                if(this.visible() && this.selected)
                    this.setValue.call(this, this.selected);
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
        return prevent(event);;
    }

    this.show = function(){
        toggle(this.node, true);
    }

    this.hide = function(){
        element.removeAllChilds(this.node);
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
        ajax.loadXMLDoc('search', {'fields': this.types,
                        'limit': this.opts.limit, 'string': this.text},
            this.processor);
    }

    this.processResponse = function(resp){
        message.hide();
        element.removeAllChilds(this.node);
        if(!resp.status){
            element.appendChild(this.node, {'li': {'innerText': resp.text}});
        }else{
            var list = resp.text.list;
            for(var i in list){
                var content = map(function(t){
                    return {'input': {'type': 'hidden', 'name': t, 'value': list[i][t]}};
                    }, types);
                content.push.apply(content, this.view(list[i]));
                element.appendChild(this.node, [{'li': {'onclick': (function(app){
                    return function(){ app.setValue.call(app, this); }})(this),
                    'onmouseover': (function(app){
                    return function(){ app.setSelection.call(app, this); }})(this),
                    'onmouseout': (function(app){
                    return function(){ app.removeSelection.call(app, this); }})(this),
                    }}, content]);
            }
        }
        this.show();
    }

    this.setValue = function(elem){
        if(this.retintypes){
            var value = ''
            element.downTree(function(el){
                if(el.tagName == 'INPUT' && el.type == 'hidden' && el.name == retval)
                    value = el.value;
            }, elem);
            this.object.value = value;
        }else{
            var id;
            element.downTree(function(el){
                if(el.tagName == 'INPUT' && el.type == 'hidden' && el.name == 'id')
                    id = el.value;
            }, elem);
            if(!id) return;
            ajax.loadXMLDoc('get', {'id': id, 'field': this.retfield},
                new RequestProcessor({'get': this.ajaxProcessor}, this));
        }
        this.removeSelection();
        this.hide();
    }

    // This function accepts data for current returned item and returns
    // its representation. Redefine this defenition for your data.
    this.view = function(data){
        return [{'p' : {'innerText': data.title}},
            {'span' : {'innerText': '[' + data.type + ']'}},
            {'span' : {'innerText': data.release}}
        ]
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
