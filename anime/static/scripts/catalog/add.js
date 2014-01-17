/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Add class module
 *
 */

define([
    'base/events', 'base/message', 'base/ajax',
    'base/request_processor', 'catalog/autocomp'
],
function add_class(events, message, ajax, RequestProcessor, Autocomplete){

    var genreImport = null;

    return {
        form: null,
        loaded: false,
        processor: null,

        init: function(){
            this.form = document.getElementById('addform');
            if(!this.form || !this.createForm()) return;
            this.loaded = true;
            this.processor = new RequestProcessor({'add': this.processResponse}, this);
            events.add(document.getElementById('id_releaseType'),
                            'change', this.typeChange);
            this.genreHelperInit();

        },

        typeChange: function(){
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
        },

        genreHelperInit: function(){
            var genre = document.getElementById('id_genre');
            element.insert(genre, [{'span': {className: 'datetimeshortcuts'}},
                [{'a': {innerText: 'Import', 'id': 'ImportAddLink', onclick: function(){
                    var form = document.getElementById('TitleHelperForm');
                    if(toggle(form)) form.firstChild.focus(); }
                }}]]);
            var input = element.create('input', {'type': 'text'});
            element.insert(genre, [{'div': {'id': 'TitleHelperForm',
                'className': 'cont_men'}}, [input]]);
            genreImport = new Autocomplete(input, {}, ['title', 'type', 'release'], 'genre_list');
            genreImport.ajaxProcessor = function(resp){
                if(!resp.status) return;
                var opts = this.node.parentNode.nextSibling.options;
                for(var opt in opts)
                    if(opts[opt])
                        opts[opt].selected = false
                resp.text.genre_list.forEach(function(g){
                    for(var o in opts)
                        if(opts[o] && opts[o].innerText == g){
                            opts[o].selected = true;
                            break;
                        }
                });
                toggle(this.node.parentNode);
            };
        },

        toggle: function(){
            if(!this.loaded) return
            toggle(this.form)
            return false
        },

        createForm: function(){
            if(this.form)
                return this.form
            return false // Потом как-нибудь напишу
        },

        clearForm: function(){
            if(!this.form)
                return
            element.remove(getElementsByClassName('error', this.form, 'span'))
            element.remove(getElementsByClassName('s3', this.form, 'span'))
            return true
        },

        sendForm: function(e){
            if(!this.loaded)
                return
            if(!!(e.clientX | e.clientY))
                message.toEventPosition(e)
            this.clearForm()
            var formData = getFormData(this.form)
            ajax.load('add', formData, this.processor)
        },

        processResponse: function(resp){
            message.hide()
            if(!resp.status){
                this.processError(resp.text)
            }else{
                if(this.clearForm()){
                    element.insert(this.form.lastChild, {'span':
                        {className: 's3', innerText: 'Added'}})
                    if(isNumber(resp.id)){
                        if(Card.get(resp.id))
                            window.location.replace('/card/' + resp.id + '/')
                        else
                            this.toggle()
                    }else{
                        window.location.replace('/')
                    }
                }
            }
        },

        processError: function(error){
            if(!this.loaded)
                return
            for(var target in error){
                if(!target) continue
                var obj = null
                if(target == '__all__'){
                    obj = element.create('div', {className: 'mainerror'})
                    element.insert(this.form.firstChild, obj)
                }else{
                    obj = document.getElementById('id_'+target)
                }
                if(!obj) continue
                for(var e in error[target]){
                    element.insert(obj, element.create('span', {
                        className: 'error left', innerText: error[target][e]}), 1)
                }
            }
        }
    };
});