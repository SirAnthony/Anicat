/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Field builder module
 *
 */

define(['base/storage'],
    function(catalog_storage){

    var title_sbst = {
        'episodesCount': 'episodes',
        'release': 'released',
        'bundle': 'Bundled with'
    };

    var statenames = {
        '0': "None", '1': "Want",
        '2': "Now", '3': "Done",
        '4': "Dropped", '5': "Partially watched"
    };

    var edit_links = {
        'image': 'Submit new'
    };

    return {
        getData: function(form){
            var formData = {};
            element.downTree(function _f(elm){
                if(elm.tagName == "INPUT" || elm.tagName == "TEXTAREA" || elm.tagName == "SELECT"){
                    switch(elm.type){
                        case "checkbox":
                            formData[elm.name] = elm.checked;
                            break;
                        case "radio":
                            if(elm.checked)
                                formData[elm.name] = elm.value;
                            break;
                        case "select-multiple":
                            formData[elm.name] = map(function(opt){ return opt.value; },
                                filter(function(opt){ return opt.selected; }, elm.childNodes, null, true));
                            break;
                        case "file":
                            formData[elm.name] = elm.files[0];
                            break;
                        default:
                            formData[elm.name] = elm.value;
                            break;
                    }
                }else{
                    element.downTree(_f, elm);
                }
            }, form);
            return formData;
        },

        getTitledField: function(fieldname, id, data){
            var func = this['title_'+fieldname];
            if(!func)
                func = this.title_default;
            return func.call(this, fieldname, id, data);
        },

        title_bundle: function(fieldname, id, data){
            var fields = this.getField(fieldname, id, data);
            return this.titledfield(fieldname,
                ((data && data.id) ? data.id : 0), fields);
        },

        title_default: function(fieldname, id, data){
            var fields = this.getField(fieldname, id, data);
            return this.titledfield(fieldname, id, fields);
        },

        titledfield: function(fieldname, id, fields){
            var title = (title_sbst[fieldname] || fieldname) + ':';
            var childs = [];
            if(require.defined('catalog/edit') && fieldname != 'this')
                childs.push(this.getEditLink(fieldname, id));
            childs.push({'h4': {innerText: capitalise(title)}});
            if(isArray(fields))
                childs.push.apply(childs, fields);
            else
                childs.push(fields);
            return element.create('div', null, childs);
        },

        getField: function(fieldname, id, data){
            var func = this['field_'+fieldname];
            if(!func)
                func = this.field_default;
            var el = func.call(this, data, id);
            if(!el.className)
                el.className = fieldname + id;
            return el;
        },

        getEditLink: function(fieldname, id){
            var func = this['editlink_'+fieldname];
            if(!func)
                func = this.editlink_default;
            return func.call(this, fieldname, id);
        },

        editlink_default: function(fieldname, id){
            if (!require.defined('catalog/edit'))
                return null;
            var edit = require('catalog/edit');
            var text = edit_links[fieldname] || 'Edit';
            return {'a': {'className': 'right', 'style': {'display': 'none'},
                    'href': edit.getFieldLink(id, fieldname),
                    'innerText': text, 'target': '_blank',
                    onclick: function(e){ return edit.rf(id, fieldname, e); }
            }};
        },

        // editlink_image: function(fieldname, id){
            // return {'a': {'className': 'right', 'style': {'display': 'none'},
            //         'href': edit.getFieldLink(id, fieldname),
            //         'innerText': 'Submit new', 'target': '_blank'}};
            // return this.editlink_default(fieldname, id, 'Submit new');
        // },

        field_state: function(data, id){
            var state = {'state': null, 'value': null};
            if(data && isHash(data)){
                state.value = data.select[data.state];
                state.state = data.state;
            }else{
                state = catalog_storage.getStatus(id, statenames);
                if(state.state < 0)
                    return {'span': {innerText: state.value}};
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
        },

        field_name: function(data){
            var s = new Array();
            var num = numHash(data);
            for(var g=0; g<=num; g++){
                s.push({'': {innerText: encd(data[g])}}, 'br');
            }
            return element.create('div', null, s);
        },

        field_bundle: function(data, id){
            var s = [];
            var bundleid = 0;
            if(data && data.bundles){
                bundleid = data.id;
                var bundle_num = 1;
                var _card = require('catalog/card');
                s = map(function(cur){ return element.create('tr', null, [
                    {'td': {innerText: (id == cur.id ? "►" : "")}},
                    {'td': {className: "bundle_number", innerText: bundle_num++}},
                    'td', [{'a': {
                        href: '/card/' + cur.id + '/',
                        onclick: function(e){ return _card.get(cur.id, e); },
                        innerText: encd(cur.title),
                        className: 's s' + cur.id
                    }}]]);
                }, data.bundles);
            }
            var classnm = 'bundle' + bundleid;
            var th = ['tr', ['th', [{'input': {'type': 'hidden',
                  'id': 'currentid_b_' + bundleid, 'value': id,
                  'name': 'currentid'}}]]];
            return element.create('table', {className: classnm}, [
                                            'thead', th, 'tbody', s]);

        },

        field_links: function(data){
            var s;
            if(isString(data)){
                s = {'span': {innerText: data}};
            }else if(isHash(data)){
                s = [];
                for(var link in data){
                    var datal = data[link];
                    if(!datal)
                        continue;
                    for(var el=0; el<datal.length; el++){
                        s.push({
                            'a': {'target': '_blank', href: datal[el], innerText: link}},
                            {'': {innerText: '\240'}});
                    }
                }
            }
            return element.create('p', null, s);
        },

        field_duration: function(data){
            return element.create('p', {innerText: data + ' min.'});
        },

        field_image: function(data){
            return element.create('p', {'style': {'display': 'none'}});
        },

        field_default: function(data){
            return element.create('p', {innerText: data});
        },

    };

});
