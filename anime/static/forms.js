
var forms = new (function forms_class(){

    this.getTitledField = function(fieldname, id, data){
        var func = this['title_'+fieldname];
        if(!func)
            func = this.title_default;
        return func.call(this, fieldname, id, data);
    }

    this.title_bundle = function(fieldname, id, data){
        var num = numHash(data);
        var bundleid = 0;
        if(data && (isString(data[num]) || isNumber(data[num])))
            bundleid = data[num];
        var fields = this.getField(fieldname, id, data);
        var current = ['tr', ['th', [{'input': {'type': 'hidden',
              'id': 'currentid_b_' + bundleid, 'value': id}}]]]
        if(fields.firstChild)
            element.insert(fields.firstChild, current);
        else
            element.appendChild(fields, current);
        return this.titledfield(fieldname, bundleid, fields);
    }

    this.title_default = function(fieldname, id, data){
        var fields = this.getField(fieldname, id, data);
        return this.titledfield(fieldname, id, fields)
    }

    this.titledfield = function(fieldname, id, fields){
        var title;
        switch(fieldname){
            case 'episodesCount': title = 'episodes:'; break;
            case 'release': title = 'released:'; break;
            case 'bundle': title = 'Bundled with:'; break;
            default: title = fieldname + ':'; break;
        }
        var childs = new Array();
        if(edit)
            childs.push({'a': {className: 'right',
                'href': edit.getFieldLink(id, fieldname),
                innerText: 'Edit', target: '_blank',
                onclick: (function(i, f){ return function(){
                    return edit.rf(i, f); }})(id, fieldname) }});
        childs.push({'h4': {innerText: capitalise(title)}});
        if(isArray(fields))
            childs.push.apply(childs, fields); //lolo
        else
            childs.push(fields);
        return element.create('div', null, childs);
    }

    this.getField = function(fieldname, id, data){
        var func = this['field_'+fieldname];
        if(!func)
            func = this.field_default;
        var el = func.call(this, data, id);
        if(!el.className)
            el.className = fieldname + id;
        return el;
    }

    this.field_state = function(data, id){
        var state = {'selected': null, 'value': null};
        if(!isString(data)){
            catalog_storage.disable();
            if(data){
                state.value = data.select[data.selected];
                state.selected = data.selected;
            }
        }else{
            if(!catalog_storage.enable())
                return {'span': {innerText: 'Enable local storage to use catalog anonymously.'}}
            else
                    state = catalog_storage.getStatus(id);
        }
        ret = [ {'span': {innerText: capitalise(state.value)}},
                {'input': {'type': 'hidden', 'name': 'card_userstatus_input', 'value': state.selected}}];
        if(data && data.completed && data.all){
            ret.push({'span': {className: 'right', innerText: data.completed + '/' + data.all}},
                     {'input': {'type': 'hidden', 'name': 'card_usercount_input', 'value': data.completed}});
        }
        return element.create('p', null, ret);
    }

    this.field_name = function(data){
        var s = new Array();
        var num = numHash(data);
        for(var g=0; g<=num; g++){
            s.push({'': {innerText: encd(data[g])}}, 'br');
        }
        return element.create('div', null, s);
    }

    this.field_bundle = function(data, id){
        var s = new Array();
        var num = numHash(data);
        if(data){
            if(isString(data[num]) || isNumber(data[num])){
                var classnm = 'bundle' + data.pop();
                num -= 1;
            }
            for(var g=0; g<=num; g++){
                var cur = data[g];
                s.push('tr', [
                    {'td': {innerText: (id == cur.elemid ? "►" : "")}},
                    {'td': {className: "bundle_number", innerText: g+1}},
                    'td', [{'a': {
                        href: '/card/' + cur.elemid + '/',
                        onclick: (function(c){ return function(){ return getCard(c); }})(cur.elemid),
                        innerText: encd(cur.name),
                        className: 's s' + cur.elemid
                    }}]
                ]);
            }
        }else{
            var classnm = 'bundlenull';
        }
        return element.create('table', {className: classnm}, s);

    }

    this.field_links = function(data){
        var s = new Array();
        for(var link in data){
            if(!data[link]) continue;
            s.push({'a': {'target': '_blank', href: data[link], innerText: link}},
                   {'': {innerText: '\240'}});
        }
        return element.create('p', null, s);
    }

    this.field_duration = function(data){
        return element.create('p', {innerText: data + ' min.'});
    }

    this.field_default = function(data){
        return element.create('p', {innerText: data});
    }

})();
