//add-edit classes module
//################################################################
//##################### Add #######################################
//################################################################

var add = new (function add_class(){

    var form = null;
    var loaded = false;

    this.init = function(){
        add.form = document.getElementById('addform');
        if(!add.form || !add.createForm()) return;
        add.loaded = true;
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
        if(!(e.clientX | e.clientY))
            return;
        this.clearForm();
        var formData = getFormData(this.form);
        ajax.loadXMLDoc(url+'add/', formData);
        message.toEventPosition(e);
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

    this.status_menu_edit = false;

    this.edits = {'name': '/name', 'bundle': '/bundle',
                 'type': 'releaseType', 'release': 'releasedAt,endedAt',
                 'links': '/links', 'state': '/state'};
    this.fields = {'releaseType': 'type', 'releasedAt,endedAt': 'release'};

    this.rf = function(id, field, e){
        if(!user.logined && field == 'state')
            ajax.processFormRequest({'status': true, 'id': id, 'model': field});
        else
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
        ajax.loadXMLDoc(url+'form/', q);
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
        edit.loaded = true;
    }

    this.send = function(form){
        if(!form)
            return;
        var formData = this.getFormData(form);
        if(!user.logined && formData.model == 'state'){
            formData['set'] = true;
            ajax.processSetRequest(formData);
        }else{
            ajax.loadXMLDoc(url+'set/', formData);
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

        var field = (resp.field ? resp.field : resp.model);
        if(this.fields[field]) field = this.fields[field];

        if(!user.logined && resp.model == 'state'){
            var s = catalog_storage.getStatus(resp.id, (resp.text ? resp.text.select : null));
            resp.form = [{"select": {"name": "state", "required": true, "value": s.state, "label": "State", "choices": [["0", "None"], ["1", "Want"], ["2", "Now"], ["3", "Done"], ["4", "Dropped"], ["5", "Partially watched"]], "id": "id_state"}}];
        }

        if(resp.status){
            if(!resp.form)
                throw new Error('Server did not return form.')

            if(this.status_menu_edit){
                message.create()
                message.addTree(element.create('label', {'for': field + resp.id,
                                innerText: capitalise(field) + ':'}));
                message.addTree(forms.getField(field, resp.id));
                message.show();
            }
            for(var fld=0; fld<resp.form.length; fld++){
                for(var type in resp.form[fld]){
                    var f = resp.form[fld];
                    if(type == 'select'){
                        if(f[type].choices && isString(f[type].choices) && /^range\(/.test(f[type].choices))
                            resp.form[fld][type].choices = eval(f[type].choices);
                        if(resp.model == 'state')
                            resp.form[fld][type].onchange = function(){ edit.send(this.parentNode.parentNode); };
                    }
                }
            }

            if(field == 'name' || field == 'bundle'){
                resp.form.push({'a': {name: 'id', className: 'right', innerText: 'Add field',
                onclick: (function(name){ return function(){
                    var num = (function(el){
                        var num = 0;
                        do{
                            if(el.tagName == 'INPUT' && el.type == 'text')
                                num += 1;
                        }while(el = el.nextSibling)
                        return num;
                    })(this.parentNode.firstChild);
                    var nm = name + ' ' + num;
                    element.insert(this,
                        {'input': {'type': 'text', 'id': 'id_'+nm, 'name': nm}});
                }})(capitalise(field))}});
            }

            var spans = getElementsByClassName(field+resp.id, null);
            resp.form.push({'input': {type: 'hidden', name: 'id', value: resp.id}});
            resp.form.push({'input': {type: 'hidden', name: 'model', value: resp.model}});

            if(resp.field)
                resp.form.push({'input': {type: 'hidden', name: 'field', value: resp.field}});
            for(var i = 0; i < spans.length; i++){
                var s = element.create('div', {className: 'editDiv edit_' + field + resp.id}, resp.form);
                if(!this.status_menu_edit){
                    s.style.width = (field != 'links') ? '190px' : '300px';
                    element.insert(spans[i].parentNode.firstChild, {'a': {className: 'right',
                        innerText: 'Save', onclick: function(e){ edit.send(this.parentNode, e); }}}, true);
                    element.remove(spans[i].parentNode.firstChild);
                }
                element.insert(spans[i], s);
                element.remove(spans[i]);
            }
            if(this.status_menu_edit)
                this.status_menu_edit = false;
        }else{
            if(isHash(resp.text)){
                for(var target in resp.text){
                    var obj;
                    if(target == '__all__'){
                        obj = document.getElementsByClassName('edit_' + field + resp.id);
                        if(obj) obj = obj[0].previousSibling;
                    }else{
                        obj = document.getElementById('id_'+target);
                    }
                    if(!obj) continue;
                    for(var e in resp.text[target]){
                        element.insert(obj.nextSibling, {'span': {
                            className: 'error', innerText: resp.text[target][e]}});
                    }
                }
            }else{
                throw new Error(resp.text);
            }
        }
    }

    this.processResponse = function(resp){

        if(!resp.id)
            resp.id = 0;

        message.hide();

        var field = (resp.field ? resp.field : resp.model);
        if(this.fields[field]) field = this.fields[field];

        if(resp.status){

            if(!resp.text)
                throw new Error('Server returned blank response.');

            this.fillField(field, resp);

        }else{
            // This should not occur
            throw new Error(resp.text);
        }
    }

    this.fillField = function(fieldname, resp){
        var func = this['field_'+fieldname];
        if(!func)
            func = this.field_default;
        func.call(this, fieldname, resp);
    }

    this.field_default = function(field, resp){
        var divs = getElementsByClassName('edit_' + field + resp.id, null, 'div');
        this.putFields.call(this, divs, field, resp.id, resp);
    }

    this.field_bundle = function(field, resp){
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

    this.field_state = function(field, resp){
        if(!user.logined){
            catalog_storage.addStatus(resp.id, resp.text.state);
        }

        this.field_default.call(this, field, resp);

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
    }

    this.putFields = function(divs, field, id, resp){
        var text = (resp.text[resp.field] ? resp.text[resp.field] : resp.text);
        for(var i = 0; i < divs.length; i++){
            var s = forms.getField(field, id, text);
            element.insert(divs[i].parentNode.firstChild, {'a': {
                className: 'right', 'href': this.getFieldLink(resp.id, field),
                innerText: 'Edit', style: {display: "none"}, target: '_blank',
                onclick: function(e){ return edit.rf(resp.id, field, e); }}},
                true);
            element.remove(divs[i].parentNode.firstChild);

            addEvent(divs[i].parentNode, 'mouseover', (function(c){
                return function(){toggle(c, 1);}})(divs[i].parentNode.firstChild));
            addEvent(divs[i].parentNode, 'mouseout', (function(c){
                return function(){toggle(c, -1);}})(divs[i].parentNode.firstChild));

            element.insert(divs[i], s);
            element.remove(divs[i]);
        }
    }

})();

addEvent(window, 'load', add.init);
addEvent(window, 'load', edit.init);
