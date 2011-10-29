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

    this.getFieldName = function(id, name){
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

    this.getForm = function(){
        return document.getElementById('EditForm');
    }

    this.send = function(){
        var form = this.getForm();
        if(!form || !form.name)
            return;
        var formData = getFormData(form);
        ajax.loadXMLDoc(url+'set/', formData);
    }

})();

addEvent(window, 'load', add.init);
addEvent(window, 'load', edit.init);
