/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Filter module
 *
 */

define([
    'base/events', 'base/message', 'base/ajax',
    'base/request_processor', 'catalog/forms', 'catalog/list',
    'lib/scroller'
],
function (events, message, ajax, RequestProcessor, forms, list, nscroll){

    return {
        init: function(){
            var container = document.getElementById('id_filter_container')
            this.scroller = new nscroll(document.getElementById('id_filter_genre_container'))

            getElementsByClassName('nano', container).forEach(function(el){
                element.insert(el.firstChild, {'a':
                    {'innerText': 'Clear', 'className': 'right',
                    'onclick': function(){
                        this.parentNode.getElementsByTagName('option').forEach(
                            function(o){ o.selected = false; })}}});
                }, this);

            this.errorobj = getElementsByClassName('mainerror', container)[0];

            this.processor = new RequestProcessor({
                'filter': function(resp){
                    message.hide();
                    if(!resp.status)
                        this.processError(resp.text);
                    else
                        ajax.load('list', {}, this.processor);
                },
                'list': function(resp){
                    message.hide();
                    if(!resp.status)
                        this.processError(resp.text);
                    list.create(resp.text);
                }
            }, this);
        },

        toggle: function(){
            toggle(document.getElementById('id_filter_container'));
            this.scroller.reset();
            return false;
        },

        clear: function(){
            element.removeAllChilds(this.errorobj);
            getElementsByClassName('filter', document).forEach(function(el){
                element.downTree(function _f(elm){
                    if(elm.tagName == "INPUT" || elm.tagName == "SELECT"){
                        if(elm.type == "text")
                            elm.value = "";
                        else if(elm.type == "select-multiple")
                            elm.childNodes.forEach(function(opt){
                                opt.selected = false })
                        else if(elm.checked)
                            elm.checked = false
                    }else
                        element.downTree(_f, elm);
                }, el)
            }, this);
        },

        apply: function(){
            element.removeAllChilds(this.errorobj);
            var processed = {}
            getElementsByClassName('filter', document).forEach(function(el){
                var data = forms.getData(el);
                for(var i in data){
                    if(data.hasOwnProperty(i))
                        processed[i] = data[i];
                }
            }, this);
            ajax.load('filter', processed, this.processor);
        },

        processError: function(error){
            for(var target in error){
                if(!target) continue;
                for(var e in error[target])
                    element.appendChild(this.errorobj, element.create('span', {
                            className: 'error', innerText: target + ': '+ error[target][e]}), 1);
            }
        }
    }
});
