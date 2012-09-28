/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * add/edit classes module
 *
 */

//################################################################
//##################### Add #######################################
//################################################################

var add = new (function add_class(){

    var form = null;
    var loaded = false;
    var processor = null;
    var genreImport = null;

    this.init = function(){
        this.form = document.getElementById('addform');
        if(!this.form || !this.createForm()) return;
        this.loaded = true;
        this.processor = new RequestProcessor({'add': this.processResponse}, this);

        addEvent(document.getElementById('id_releaseType'), 'change', this.typeChange);
        this.genreHelperInit();
    }

    this.typeChange = function(){
        var ecount = document.getElementById('id_episodesCount');
        var edur = document.getElementById('id_duration');
        switch(this.value){
            case "":
                ecount.value = "";
                if(!edur.value) edur.value = "";
                break;
            case "0": // TV
                ecount.value = 13;
                if(!edur.value) edur.value = 25;
                break;
            case "2": // OAV
                ecount.value = 2;
                if(!edur.value) edur.value = 30;
                break;
            default:
                ecount.value = 1;
                break;
        }
    }

    this.genreHelperInit = function(){
        var genre = document.getElementById('id_genre');
        element.insert(genre, [{'span': {className: 'datetimeshortcuts'}},
            [{'a': {innerText: 'Import', 'id': 'ImportAddLink', onclick: function(){
                var form = document.getElementById('TitleHelperForm')
                if(toggle(form)) form.firstChild.focus(); }
            }}]]);
        var input = element.create('input', {'type': 'text'});
        element.insert(genre, [{'div': {'id': 'TitleHelperForm',
            'className': 'cont_men'}}, [input]]);
        genreImport = new Autocomplete(input, {}, ['title', 'type', 'release'], 'genre_list');
        genreImport.ajaxProcessor = function(resp){
            if(!resp.status) return;
            var opts = this.node.parentNode.nextSibling.options;
            map(function(elem){ if(elem) elem.selected = false;}, opts);
            map(function(g){
                for(var o in opts)
                    if(opts[o] && opts[o].innerText == g){
                        opts[o].selected = true; break; }
                }, resp.text.genre_list);
            toggle(this.node.parentNode);
        }
    }

    this.toggle = function(){
        if(!this.loaded) return;
        toggle(this.form);
    }

    this.createForm = function(){
        if(this.form)
            return this.form;
        return false; // Потом как-нибудь напишу
    }

    this.clearForm = function(){
        if(!this.form)
            return;
        element.remove(getElementsByClassName('error', this.form, 'span'));
        element.remove(getElementsByClassName('s3', this.form, 'span'));
        return true;
    }

    this.sendForm = function(e){
        if(!this.loaded)
            return;
        if(!!(e.clientX | e.clientY))
            message.toEventPosition(e);
        this.clearForm();
        var formData = getFormData(this.form);
        ajax.loadXMLDoc('add', formData, this.processor);
    }

    this.processResponse = function(resp){
        message.hide()
        if(!resp.status){
            this.processError(resp.text);
        }else{
            if(this.clearForm()){
                element.insert(this.form.lastChild, {'span': {className: 's3', innerText: 'Added'}});
                if(isNumber(resp.id)){
                    if(Card.get(resp.id))
                        window.location.replace('/card/' + resp.id + '/');
                    else
                        this.toggle();
                }else{
                    window.location.replace('/');
                }
            }
        }
    }

    this.processError = function(error){
        if(!this.loaded)
            return;
        for(var target in error){
            if(!target) continue;
            var obj = null;
            if(target == '__all__'){
                obj = element.create('div', {className: 'mainerror'});
                element.insert(this.form.firstChild, obj);
            }else{
                obj = document.getElementById('id_'+target);
            }
            if(!obj) continue;
            for(var e in error[target]){
                element.insert(obj, element.create('span', {
                        className: 'error left', innerText: error[target][e]}), 1);
            }
        }
    }

})();

//################################################################
//##################### Edit #######################################
//################################################################

var edit = new (function edit_class(){

    var processor = null;

    this.status_menu_edit = false;

    this.edits = {'name': '/name', 'bundle': '/bundle',
                 'type': 'releaseType', 'release': 'releasedAt,endedAt',
                 'links': '/links', 'state': '/state', 'image': '/image'};
    this.fields = {'releaseType': 'type', 'releasedAt,endedAt': 'release'};

    var restorable_elems = {};

    this.hideEdit = function(){ map(function(el){ toggle(el, -1) },
                        getElementsByClassName('right', this)); }
    this.showEdit = function(){ map(function(el){ toggle(el, 1) },
                        getElementsByClassName('right', this)); }


    this.getFieldName = function(n){
        if(this.fields[n])
            return this.fields[n];
        return n;
    }

    this.rf = function(id, field, e){
        if(!user.logined && field == 'state'){
            processor.setRequest()
            processor.parse({'response': 'form', 'status': true,
                                    'id': id, 'model': field});
            message.unlock()
        }else
            this.requestForm(id, field);
        message.toEventPosition(e);
        return false;
    }

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
        ajax.loadXMLDoc('form', q, processor);
    }

    this.getFieldLink = function(id, name){
        if(!id) id = 0;
        if(this.edits[name]){
            if(this.edits[name].charAt(0) == '/')
                return '/edit' + this.edits[name] + '/' + id + '/';
            else
                return '/edit/anime/' + id + '/' + this.edits[name] + '/';
        }else{
            return '/edit/anime/' + id + '/' + name + '/';
        }
    }

    this.init = function(){
        this.loaded = true;
        processor = new RequestProcessor({'form': this.processForm,
                                    'edit': this.processResponse}, this);
    }


    this.send = function(form){
        if(!form)
            return;
        var formData = this.getFormData(form);
        if(!user.logined && formData.model == 'state'){
            processor.setRequest();
            formData['set'] = true;
            formData['response'] = 'edit';
            processor.parse(formData);
            message.unlock()
        }else{
            ajax.loadXMLDoc('set', formData, processor);
        }
        var errors = getElementsByClassName('error', form);
        element.remove(errors);
    }


    this.getFormData = function(form){
        var formData = getFormData(form);
        if(!user.logined && formData.model == 'state'){
            formData.status = true;
            if(formData.state)
            formData.text = {'state': formData.state, 'select': (function(x){
                var s = {};
                for(var i = 0; i < x.childNodes.length; i++){
                    s[x.childNodes[i].value] = x.childNodes[i].innerText;
                }
                return s;})(document.getElementById('id_state'))
            }
            delete formData.state;
        }
        return formData;
    }


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
                'label': 'State', 'onchange': function(){ return edit.send(this.parentNode.parentNode); },
                'choices': [['0', 'None'], ['1', 'Want'], ['2', 'Now'], ['3', 'Done'], ['4', 'Dropped'], ['5', 'Partially watched']],
            }}];
        }


        if(!resp.form)
            throw new Error('Server did not return form.')

        if(this.status_menu_edit){
            message.create()
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
        for(var i = 0; i < spans.length; i++){
            var spani = spans[i];
            var s = element.create('div', {className: 'editDiv edit_' + fid}, resp.form);
            if(spani.parentNode != message.getMenu()){
                var editlink = getElementsByClassName('right', spani.parentNode, 'a')[0];
                s.style.width = (field != 'links') ? '190px' : '300px';
                element.insert(editlink, {'a': {'className': 'right', 'innerText': 'Cancel',
                    'onclick': function(e){ edit.restore(this.parentNode, e); }}});
                element.insert(editlink, {'span': {'className': 'right', 'innerText': '|'}});
                element.insert(editlink, {'a': {'className': 'right', 'innerText': 'Save',
                        'onclick': function(e){ edit.send(this.parentNode, e); }}});
                removeEvent(spani.parentNode, 'mouseover', this.showEdit);
                removeEvent(spani.parentNode, 'mouseout', this.hideEdit);
                element.remove(editlink);
            }else{
                message.onclose = function(e){
                    for(var i = 0; i < restorable_flds.length; i++)
                        edit.restore(restorable_flds[i]);
                }
            }
            element.insert(spani, s);
            element.remove(spani, true);
        }
    }


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
    }


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
    }


    this.restore = function(elem, e){
        var data = getFormData(elem);
        var field =  this.getFieldName(data.field ? data.field : data.model);
        var fid = field + data.id;
        this.putEdit(elem, field, data.id);
        element.remove(getElementsByClassName('editDiv', elem));
        element.appendChild(elem, restorable_elems[fid]);
        delete restorable_elems[fid];
    }


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
            }})(capitalise(field))});
        return [add_field];
    }

    this.fillField = function(fieldname, resp){
        var func = this['fill_'+fieldname];
        if(!func)
            func = this.fill_default;
        func.call(this, fieldname, resp);
    }

    this.fill_default = function(field, resp){
        var divs = getElementsByClassName('edit_' + field + resp.id, null, 'div');
        this.putFields.call(this, divs, field, resp.id, resp);
    }

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
    }

    this.fill_state = function(field, resp){
        if(!user.logined){
            catalog_storage.addStatus(resp.id, resp.text.state);
        }

        this.fill_default.call(this, field, resp);

        var rs = getStylesheetRule('.rs'+resp.text.state, 'background-color');
        rs = rs ? rs : '#FFF';
        var as = getStylesheetRule('.as'+resp.text.state, 'background-color');
        as = as ? as : '#FFF';
        var sl = getStylesheetRule('.sl'+resp.text.state, 'color');
        sl = sl ? sl : '#000';
        var rules = [['.r'+resp.id, ['background-color', rs]],
                    ['.a'+resp.id, ['background-color', as]],
                    ['.s'+resp.id, ['color', sl, true]]];
        addStylesheetRules(rules);
        if(statistics)
            statistics.getStat();
    }

    this.putFields = function(divs, field, id, resp){
        var text = (resp.text[resp.field] ? resp.text[resp.field] : resp.text);
        for(var i = 0; i < divs.length; i++){
            var s = forms.getField(field, id, text);
            this.putEdit(divs[i].parentNode, field, id);
            element.insert(divs[i], s);
            element.remove(divs[i]);
        }
    }

    this.putEdit = function(elem, field, id){
        var links = getElementsByClassName('right', elem);
        element.insert(links[0] || elem.firstChild,
                                forms.getEditLink(field, id));
        element.remove(links);
        addEvent(elem, 'mouseover', this.showEdit);
        addEvent(elem, 'mouseout', this.hideEdit);
    }

})();



addEvent(window, 'load', function(){ add.init(); });
addEvent(window, 'load', function(){ edit.init(); });
