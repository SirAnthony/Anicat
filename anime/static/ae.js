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
                var spans = getElementsByClassName(field+resp.id, null, 'span');
                resp.form.push({'input': {type: 'hidden', name: 'id', value: resp.id}});
                resp.form.push({'input': {type: 'hidden', name: 'model', value: resp.model}});
                if(resp.field)
                    resp.form.push({'input': {type: 'hidden', name: 'field', value: resp.field}});
                for(var i = 0; i < spans.length; i++){
                    var s = element.create('div', {className: 'editDiv edit_' + field + resp.id}, resp.form);
                    s.style.width = (field != 'links') ? '190px' : '300px';
                    element.insert(spans[i].parentNode.firstChild, {'a': {className: 'right',
                        innerText: 'Save', onclick: function(){ edit.send(this.parentNode); }}}, true);
                    element.remove(spans[i].parentNode.firstChild);
                    element.insert(spans[i], s);
                    element.remove(spans[i]);
                }
                return;
            }

            switch(resp.model){

                case 'state':
                    var statusdiv = document.getElementById('card_userstatus');
                    if(statusdiv){
                        var statusname = ({"0": "None", "1": "Want", "2": "Now", "3": "Done",
                            "4": "Dropped", "5": "Partially watched"})[resp.text.state]
                        element.remove((function(x){
                            var a = new Array();
                            for(var i in x)
                                if(x[i] && (x[i].tagName == "SPAN" || x[i].tagName == "FORM"
                                    || x[i].tagName == "INPUT")) a.push(x[i]);
                            return a;
                        })(statusdiv.childNodes));
                        element.appendChild(statusdiv, [{'span': {innerText: statusname}},
                            {'input': {type: 'hidden', name: 'card_userstatus_input', value: resp.text.state}}]);
                        if(resp.text.count){
                            element.appendChild(statusdiv, [{'span':
                                {innerText: resp.text.count + '/' + (function(){
                                    var n = document.getElementsByName('episodesCount');
                                    for(var i in n)
                                        if(n[i].tagName == "SPAN") return n[i].innerText;
                                    })(),
                                className: 'right'}}, {'input': {type: 'hidden',
                                            name: 'card_usercount_input', value: resp.text.count}}]);
                        }
                    }

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
                break;

                default:
                    var divs = getElementsByClassName('edit_' + field + resp.id, null, 'div');
                    for(var i = 0; i < divs.length; i++){
                        var v = (resp.text[resp.field] ? resp.text[resp.field] : resp.text);
                        var s = element.create('span', {className: field + resp.id}, forms.getField(field, v, resp.id));
                        element.insert(divs[i].parentNode.firstChild, {'a': {className: 'right',
                            'href': this.getFieldLink(resp.id, field), innerText: 'Edit',
                            target: '_blank', onclick: ((field == 'state') ? function(){
                            cardstatus(resp.text.id); return false;} : function(){
                                return edit.rf(resp.id, field);
                            })}}, true);
                        element.remove(divs[i].parentNode.firstChild);
                        element.insert(divs[i], s);
                        element.remove(divs[i]);
                    }
                break;

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
