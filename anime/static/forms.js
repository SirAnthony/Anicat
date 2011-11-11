
var forms = new (function forms_class(){

    this.getField = function(fieldname, data, id){
        var func = this['field_'+fieldname];
        if(!func)
            func = this.field_default;
        return func(data, id);
    }

    this.field_state = function(data, id){
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
            s.push('p', [{'span': {innerText: encd(data[g])}}])
        }
        return element.create('div', null, s);
    }

    this.field_bundle = function(data){
        var s = new Array();
        var num = numHash(data);
        for(var g=0; g<=num; g++){
            var cur = data[g];
            s.push('p', ['span', [
                {'a': {
                    href: '/card/' + cur.elemid + '/',
                    innerText: encd(cur.name),
                    className: 's s' + cur.elemid
                }}
            ]])
        }
        return element.create('div', null, s);
    }

    this.field_links = function(data){
        var s = new Array();
        for(var link in data){
            if(!data[link]) continue;
            s.push({'a': {className: 's0', href: !data[link], innerText: link}},
                   {'': {innerText: '\240'}});
        }
        return element.create('p', null, s);;
    }

    this.field_duration = function(data){
        return {'p': {innerText: data + ' min.'}};
    }

    this.field_default = function(data){
        return {'p': {innerText: data}};
    }

})();
