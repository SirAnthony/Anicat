
var forms = new (function forms_class(){

    this.getField = function(fieldname, data, id){
        var func = this['field_'+fieldname];
        if(!func)
            func = this.field_default;
        return func(data, id);
    }

    this.field_state = function(data, id){
        var state = {'selected': null, 'value': null};
        if(!isString(data)){
            catalog_storage.disable();
            state.value = data.select[data.selected];
            state.selected = data.selected;
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
        return ret;
    }

    this.input_state = function(data, id){
        if(isString(data)){
            if(catalog_storage.enable())
                data = catalog_storage.getStatus(id);
            else
                return {'p': {innerText: data}}, {'p': {
                    innerText: 'Enable local storage to use catalog anonymously.'}};
        }else{
            catalog_storage.disable();
        }
        return createStatusForm(id, data.selected, data.select,
                                data.all, data.completed);
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
        for(var g=0; g<=num; g++){
            var cur = data[g];
            s.push('tr', [
                {'td': {innerText: (id == cur.elemid ? "►" : "")}},
                {'td': {innerText: g+1}},
                'td', [{'a': {
                    href: '/card/' + cur.elemid + '/',
                    innerText: encd(cur.name),
                    className: 's s' + cur.elemid
                }}]
            ]);
        }
        return element.create('table', null, s);
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
