
var forms = new (function forms_class(){

    this.getTitledField = function(fieldname, id, data){
        var func = this['title_'+fieldname];
        if(!func)
            func = this.title_default;
        return func.call(this, fieldname, id, data);
    }

    this.title_bundle = function(fieldname, id, data){
        var fields = this.getField(fieldname, id, data);
        return this.titledfield(fieldname,
            ((data && data.id) ? data.id : 0), fields);
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
        var state = {'state': null, 'value': null};
        var statenames = {"0": "None", "1": "Want", "2": "Now", "3": "Done", "4": "Dropped", "5": "Partially watched"}
        if(data && isHash(data)){
                state.value = data.select[data.state];
                state.state = data.state;
        }else if(!user.logined){
            if(!catalog_storage.enable())
                return {'span': {innerText: 'Enable local storage to use catalog anonymously.'}}
            else
                state = catalog_storage.getStatus(id, statenames);
        }
        ret = new Array();
        if(data){
            if(data.completed && data.all)
                ret.push({'span': {className: 'right', innerText: data.completed + '/' + data.all}});
            else if(data.rating)
                ret.push({'span': {className: 'right', innerText: data.rating}});
        }
        ret.push({'span': {innerText: capitalise(state.value)}});
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
        var bundleid = 0
        if(data && data.bundles){
            bundleid = data.id;
            var bundles = data.bundles;
            for(var g=0; g<bundles.length; g++){
                var cur = bundles[g];
                s.push('tr', [
                    {'td': {innerText: (id == cur.elemid ? "►" : "")}},
                    {'td': {className: "bundle_number", innerText: g+1}},
                    'td', [{'a': {
                        href: '/card/' + cur.elemid + '/',
                        onclick: (function(c){ return function(){ return Card.get(c); }})(cur.elemid),
                        innerText: encd(cur.name),
                        className: 's s' + cur.elemid
                    }}]
                ]);
            }
        }
        var classnm = 'bundle' + bundleid;
        var th = ['tr', ['th', [{'input': {'type': 'hidden',
              'id': 'currentid_b_' + bundleid, 'value': id,
              'name': 'currentid'}}]]];
        return element.create('table', {className: classnm}, [
                                        'thead', th, 'tbody', s]);

    }

    this.field_links = function(data){
        var s = new Array();
        if(isString(data)){
            s = {'span': {innerText: data}};
        }else if(isHash(data)){
            for(var link in data){
                if(!data[link]) continue;
                for(var el=0; el<data[link].length; el++){
                    s.push({'a': {'target': '_blank', href: data[link][el], innerText: link}},
                    {'': {innerText: '\240'}});
                }
            }
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
