/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Edit class module
 *
 */

define([
    'base/events', 'base/stylesheet', 'base/message', 'base/user',
    'base/storage', 'base/ajax', 'base/request_processor',
    'catalog/forms', 'catalog/statistics'
],
function (events, stylesheet, message, user, catalog_storage,
    ajax, RequestProcessor, forms, statistics){

    return (function(){

        this.status_menu_edit = false;
        this.edits = {'name': '/name', 'bundle': '/bundle',
                     'type': 'releaseType', 'release': 'releasedAt,endedAt',
                     'links': '/links', 'state': '/state', 'image': '/image'};
        this.fields = {'releaseType': 'type', 'releasedAt,endedAt': 'release'};
        var processor = null;
        var restorable_elems = {};

        this.hideEdit = function(){ map(function(el){ toggle(el, -1); },
                            getElementsByClassName('right', this)); };
        this.showEdit = function(){ map(function(el){ toggle(el, 1); },
                            getElementsByClassName('right', this)); };


        this.getFieldName = function(n){
            if(this.fields[n])
                return this.fields[n];
            return n;
        };

        this.rf = function(id, field, e){
            if(!user.logined && field == 'state'){
                processor.setRequest();
                processor.parse.call(processor, {'response': 'form', 'status': true,
                                        'id': id, 'model': field});
                message.unlock();
            }else
                this.requestForm(id, field);
            message.toEventPosition(e);
            return false;
        };

        this.requestForm = function(id, field){
            if(!id) id = 0;
            var q = {'id': id, 'model': 'anime', 'field': field};
            if(this.edits[field]){
                if(this.edits[field].charAt(0) == '/'){
                    q['model'] = this.edits[field].slice(1);
                    q['field'] = undefined;
                    if(q['model'] == 'bundle'){
                        var b = document.getElementById('currentid_b_' + id);
                        if(b) q['currentid'] = b.value;
                    }
                }else{
                    q['field'] = this.edits[field];
                }
            }
            ajax.load('form', q, processor);
        };

        this.getFieldLink = function(id, name){
            if(!id) id = 0;
            var fieldname = this.edits[name] || name;
            if(this.edits[name] && fieldname.charAt(0) == '/')
                return '/edit' + fieldname + '/' + id + '/';
            return '/edit/anime/' + id + '/' + fieldname + '/';
        };

        this.init = function(){
            this.loaded = true;
            processor = new RequestProcessor({'form': this.processForm,
                                        'edit': this.processResponse}, this);
        };


        this.send = function(form){
            if(!form)
                return;
            var formData = this.getFormData(form);
            if(!user.logined && formData.model == 'state'){
                processor.setRequest();
                formData['set'] = true;
                formData['response'] = 'edit';
                processor.parse.call(processor, formData);
                message.unlock();
            }else{
                ajax.load('set', formData, processor);
            }
            var errors = getElementsByClassName('error', form);
            element.remove(errors);
        };


        this.getFormData = function(form){
            var formData = forms.getData(form);
            if(!user.logined && formData.model == 'state'){
                formData.status = true;
                if(formData.state)
                    formData.text = {'state': formData.state, 'select': (function(x){
                        var s = {};
                        for(var i = 0; i < x.childNodes.length; i++)
                            s[x.childNodes[i].value] = x.childNodes[i].innerText;
                        return s;
                    })(document.getElementById('id_state'))};
                delete formData.state;
            }
            return formData;
        };


        this.processForm = function(resp){

            if(!resp.id)
                resp.id = 0;

            message.hide();

            var field = this.getFieldName(resp.field ? resp.field : resp.model);
            var fid = field+resp.id;

            if(!resp.status)
                return this.processError(resp.text, fid);


            if(!user.logined && resp.model == 'state'){
                var s = catalog_storage.getStatus(resp.id, (resp.text ? resp.text.select : null));
                resp.form = [{'select': {'name': 'state', 'required': true, 'value': s.state, 'id': 'id_state',
                    'label': 'State', 'onchange': function(){
                        return self.send(this.parentNode.parentNode); },
                    'choices': [['0', 'None'], ['1', 'Want'], ['2', 'Now'], ['3', 'Done'], ['4', 'Dropped'], ['5', 'Partially watched']],
                }}];
            }


            if(!resp.form)
                throw new Error('Server did not return form.');

            if(this.status_menu_edit){
                message.create();
                message.addTree(element.create('label', {'for': field + resp.id,
                                innerText: capitalise(field) + ':'}));
                message.addTree(forms.getField(field, resp.id));
                message.show();
                this.status_menu_edit = false;
            }

            resp.form.push.apply(resp.form, this.addField(field));

            var spans = getElementsByClassName(fid, null);
            restorable_elems[fid] = filter(function(sp){
                return sp.parentNode != message.getMenu(); }, spans);
            var restorable_flds = map(function(el){
                return el.parentNode; }, restorable_elems[fid]);

            resp.form.push({'input': {type: 'hidden', name: 'id', value: resp.id}});
            resp.form.push({'input': {type: 'hidden', name: 'model', value: resp.model}});

            if(resp.field)
                resp.form.push({'input': {type: 'hidden', name: 'field', value: resp.field}});
            var close_func = function(e){
                for(var g = 0; g < restorable_flds.length; i++)
                    self.restore(restorable_flds[g]);
            };
            for(var i = 0; i < spans.length; i++){
                var spani = spans[i];
                var sp = element.create('div', {className: 'editDiv edit_' + fid}, resp.form);
                if(spani.parentNode != message.getMenu()){
                    var editlink = getElementsByClassName('right', spani.parentNode, 'a')[0];
                    sp.style.width = (field != 'links') ? '190px' : '300px';
                    element.insert(editlink, {'a': {'className': 'right', 'innerText': 'Cancel',
                        'onclick': function(e){ self.restore(this.parentNode, e); }}});
                    element.insert(editlink, {'span': {'className': 'right', 'innerText': '|'}});
                    element.insert(editlink, {'a': {'className': 'right', 'innerText': 'Save',
                            'onclick': function(e){ self.send(this.parentNode, e); }}});
                    events.remove(spani.parentNode, 'mouseover', this.showEdit);
                    events.remove(spani.parentNode, 'mouseout', this.hideEdit);
                    element.remove(editlink);
                }else{
                    message.onclose = close_func;
                }
                element.insert(spani, sp);
                element.remove(spani, true);
            }
        };


        this.processResponse = function(resp){

            if(!resp.id)
                resp.id = 0;

            message.hide();

            var field = this.getFieldName(resp.field ? resp.field : resp.model);

            if(resp.status){
                if(!resp.text)
                    throw new Error('Server returned blank response.');
                this.fillField(field, resp);
            }else{
                // This should not occur
                throw new Error(resp.text);
            }
        };


        this.processError = function(text, fid){
            if(isHash(text)){
                for(var target in text){
                    var obj;
                    if(target == '__all__'){
                        obj = document.getElementsByClassName('edit_' + fid);
                        if(obj) obj = obj[0].previousSibling;
                    }else{
                        obj = document.getElementById('id_'+target);
                    }
                    if(!obj) continue;
                    for(var e in text[target]){
                        element.insert(obj.nextSibling, {'span': {
                            className: 'error', innerText: text[target][e]}});
                    }
                }
            }else{
                throw new Error(text);
            }
        };


        this.restore = function(elem, e){
            var data = forms.getData(elem);
            var field =  this.getFieldName(data.field ? data.field : data.model);
            var fid = field + data.id;
            this.putEdit(elem, field, data.id);
            element.remove(getElementsByClassName('editDiv', elem));
            element.appendChild(elem, restorable_elems[fid]);
            delete restorable_elems[fid];
        };


        this.addField = function(field){
            if(field != 'name' && field != 'bundle' && field != 'links')
                return [];
            var add_field = element.create('a', {name: 'id',
                className: 'right', innerText: 'Add field',
                onclick: (function(name){ return function(){
                    var num = filter(function(el){
                        return (el.tagName == 'INPUT' && el.type == 'text');
                        }, this.parentNode.childNodes).length;
                    var nm =  ((name == 'Links') ? 'Link' : name ) + ' ' + num;
                    var input = element.create('input', {'type': 'text', 'id': 'id_'+nm, 'name': nm});
                    element.insert(this, input);
                    if(name == 'Links'){
                        var nmt = 'Link type ' + num;
                        var choices = map(function(el){
                            return [el.value, el.innerText];
                        }, document.getElementById('id_Link type 0').childNodes);
                        element.insert(this, {"select": {'name': nmt,
                            "value": 0, "choices": choices,
                            "className": "linktype", "id": 'id_'+nm}});
                    }
                    if(name == 'Bundle')
                        Autocomplete(input, {'className': 'app bundle_app'},
                        ['title', 'type', 'release'], 'id');
                }; })(capitalise(field))});
            return [add_field];
        };

        this.fillField = function(fieldname, resp){
            var func = this['fill_'+fieldname];
            if(!func)
                func = this.fill_default;
            func.call(this, fieldname, resp);
        };

        this.fill_default = function(field, resp){
            var divs = getElementsByClassName('edit_' + field + resp.id, null, 'div');
            this.putFields.call(this, divs, field, resp.id, resp);
        };

        this.fill_bundle = function(field, resp){
            var divs = getElementsByClassName('edit_' + field + resp.id, null, 'div');
            if(!divs || divs.length == 0){
                if(resp.id){
                    divs = getElementsByClassName('edit_bundle0', null, 'div');
                }else if(resp.currentid){
                    var d = getElementsByClassName('editDiv', null, 'div');
                    divs_collect:
                    for(var i = 0; i < d.length; i++){
                        var c = d[i].firstChild;
                        do{
                            if(c.tagName == 'INPUT' && c.type == "hidden" &&
                                /currentid_b_/.test(c.id) && c.value == resp.currentid){
                                divs.push(d[i]);
                                continue divs_collect;
                            }
                        }while(c = c.nextSibling);
                    }
                }else{
                    throw new Error('Cannot process response.');
                }
            }
            var id = (resp.currentid ? resp.currentid : resp.id);
            if(resp.currentid && (isArray(resp.text) && !resp.text.length))
                resp.id = 0;
            this.putFields.call(this, divs, field, id, resp);
        };

        this.fill_state = function(field, resp){
            if(!user.logined)
                catalog_storage.addStatus(resp.id, resp.text.state);

            this.fill_default.call(this, field, resp);
            var rules = map(function(style){
                var st = stylesheet.get(style[1]+resp.text.state, style[2], style[3]);
                return [style[0]+resp.id, [style[2], st, style[4]]];
            }, stylesheet.base_styles);
            stylesheet.add(rules);
            statistics.getStat();
        };

        this.putFields = function(divs, field, id, resp){
            var text = (resp.text[resp.field] ? resp.text[resp.field] : resp.text);
            for(var i = 0; i < divs.length; i++){
                var s = forms.getField(field, id, text);
                this.putEdit(divs[i].parentNode, field, id);
                element.insert(divs[i], s);
                element.remove(divs[i]);
            }
        };

        this.putEdit = function(elem, field, id){
            var links = getElementsByClassName('right', elem);
            element.insert(links[0] || elem.firstChild,
                                    forms.getEditLink(field, id));
            element.remove(links);
            events.add(elem, 'mouseover', this.showEdit);
            events.add(elem, 'mouseout', this.hideEdit);
        };

        return this
    })();
});