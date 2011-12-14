//add-edit classes module
//var seturl = '/cgi-bin/aniseted.pl';
//################################################################
//##################### Add #######################################
//################################################################

var add = new (function add_class(){

    var form = null;
    var loaded = false;

    this.init = function(){
        add.form = document.getElementById('addform');
        if(!add.form && !add.createForm()) return;
        add.loaded = true;
    }

    this.toggle = function(){
        if(!this.loaded) return;
        if(this.form.style.display == 'block'){
            this.form.style.display = 'none';
        }else if(!edit.visible){
            this.form.style.display = 'block';
        }
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
    }

    this.processResponse = function(resp){
        message.hide()
        if(!resp.status){
            this.processError(resp.text);
        }else{
            if(this.clearForm()){
                element.insert(this.form.lastChild, {'span': {className: 's3 left', innerText: 'Added'}});
                if(isNumber(resp.text))
                    window.location.replace('/card/' + resp.text + '/');
                else
                    window.location.replace('/');
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

    var visible = false;

    this.status_menu_edit = false;

    this.edits = {'name': '/name', 'bundle': '/bundle',
                 'type': 'releaseType', 'release': 'releasedAt,endedAt',
                 'links': '/links', 'state': '/state'};
    this.fields = {'releaseType': 'type', 'releasedAt,endedAt': 'release'};

    this.rf = function(id, field, e){
        this.requestForm(id, field);
        return false;
    }

    this.requestForm = function(id, field){
        var m = 'anime';
        if(this.edits[field]){
            if(this.edits[field].charAt(0) == '/'){
                m = this.edits[field].slice(1);
                field = undefined;
            }else{
                field = this.edits[field];
            }
        }
        ajax.loadXMLDoc(url+'set/', {'id': id, 'model': m, 'field': field});
    }

    this.getFieldLink = function(id, name){
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
        var formData = getFormData(form);
        formData['set'] = true;
        ajax.loadXMLDoc(url+'set/', formData);
        var errors = getElementsByClassName('error', form);
        element.remove(errors);
    }

    this.processResponse = function(resp){

        /*if(!resp.status){
            if(resp.model == 'state' && resp.returned && catalog_storage.enabled){
                resp.text = {'state': resp.returned};
                user_storage.addItem('list.'+resp.id, resp.returned);
            }else{
                throw new Error(resp.text);
            }
        }*/

        message.hide();

        var field = (resp.field ? resp.field : resp.model);
        if(this.fields[field]) field = this.fields[field];

        if(resp.status){

            if(resp.form){
                if(this.status_menu_edit){
                    message.create()
                    message.addTree(element.create('label', {'for': field + resp.id,
                                    innerText: capitalise(field) + ':'}));
                    message.addTree(forms.getField(field, null, resp.id));
                    message.show();
                }
                for(var fld in resp.form){
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
                            innerText: 'Save', onclick: function(){ edit.send(this.parentNode); }}}, true);
                        element.remove(spans[i].parentNode.firstChild);
                    }
                    element.insert(spans[i], s);
                    element.remove(spans[i]);
                }
                if(!this.status_menu_edit)
                    this.status_menu_edit = false;
                return;
            }

            if(!resp.text)
                throw new Error('Server returned blank response.');

            var divs = getElementsByClassName('edit_' + field + resp.id, null, 'div');
            for(var i = 0; i < divs.length; i++){
                var v = (resp.text[resp.field] ? resp.text[resp.field] : resp.text);
                var s = forms.getField(field, v, resp.id);
                //s.className = field + resp.id;
                element.insert(divs[i].parentNode.firstChild, {'a': {className: 'right',
                    'href': this.getFieldLink(resp.id, field), innerText: 'Edit',
                    target: '_blank', onclick: function(){ return edit.rf(resp.id, field); }}},
                    true);
                element.remove(divs[i].parentNode.firstChild);
                element.insert(divs[i], s);
                element.remove(divs[i]);
            }

            if(resp.model == 'state'){
                var rs = getStylesheetRule('.rs'+resp.text.selected, 'background-color');
                rs = rs ? rs : '#FFF';
                var as = getStylesheetRule('.as'+resp.text.selected, 'background-color');
                as = as ? as : '#FFF';
                var sl = getStylesheetRule('.sl'+resp.text.selected, 'color');
                sl = sl ? sl : '#000';
                var rules = [['.r'+resp.id, ['background-color', rs]],
                            ['.a'+resp.id, ['background-color', as]],
                            ['.s'+resp.id, ['color', sl, true]]];
                addStylesheetRules(rules);
            }
        }else{
            for(var target in resp.text){
                var obj = document.getElementById('id_'+target);
                if(!obj) continue;
                for(var e in resp.text[target]){
                    element.insert(obj.nextSibling, {'span': {
                        className: 'error', innerText: resp.text[target][e]}});
                }
            }
        }
    }

})();

addEvent(window, 'load', add.init);
addEvent(window, 'load', edit.init);
