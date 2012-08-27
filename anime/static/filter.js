/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Filter module
 *
 */

var Filter = new (function(){

    this.errorobj = null;
    this.processor = null;

    this.init = function(){
        createScroll(document.getElementById('id_filter_genre_container'));
        map(function(el){
            element.insert(el.firstChild, {'a':
                {'innerText': 'Clear', 'className': 'right',
                'onclick': function(){ map(function(o){ o.selected = false; },
                    this.parentNode.getElementsByTagName('option'))}}});
            }, getElementsByClassName('nano',
                document.getElementById("id_filter_container")));
        this.errorobj = getElementsByClassName('mainerror',
                        document.getElementById('id_filter_container'))[0];

        this.processor = new RequestProcessor({
            'filter': function(resp){
                message.hide();
                if(!resp.status)
                    this.processError(resp.text);
                else
                    ajax.loadXMLDoc('list', {}, this.processor);
            },
            'list': function(resp){
                message.hide();
                if(!resp.status)
                    this.processError(resp.text);
                var dvid = document.getElementById('dvid');
                table.build(dvid, {'table': {'id': 'tbl'},
                                    'body': {'id': 'tbdid'}}, resp.text);
                var pgp = document.getElementById('pg');
                if(pgp){
                    pgp = pgp.previousSibling;
                    element.remove(pgp.nextSibling);
                }else
                    pgp = (dvid.nextSibling) ? dvid.nextSibling : dvid;
                element.insert(pgp, table.buildPages(resp.text.pages,
                        {'id': 'pg'}));
            }
        }, this);
    }

    this.toggle = function(){
        toggle(document.getElementById('id_filter_container'));
    }

    this.clear = function(){
        element.removeAllChilds(this.errorobj);
        map(function(el){
            element.downTree(function _f(elm){
                if(elm.tagName == "INPUT" || elm.tagName == "SELECT"){
                    if(elm.type == "text") elm.value = "";
                    else if(elm.type == "select-multiple")
                        map(function(opt){ opt.selected = false; }, elm.childNodes);
                    else if(elm.checked) elm.checked = false;
                }else
                    element.downTree(_f, elm);
            }, el)}, getElementsByClassName('filter', document));
    }

    this.apply = function(){
        element.removeAllChilds(this.errorobj);
        var processed = {}
        map(function(el){
            var data = getFormData(el);
            for(var i in data){
                if(data.hasOwnProperty(i))
                    processed[i] = data[i];
            }
        }, getElementsByClassName('filter', document));
        ajax.loadXMLDoc('filter', processed, this.processor);
    }

    this.processError = function(error){
        for(var target in error){
            if(!target) continue;
            for(var e in error[target])
                element.appendChild(this.errorobj, element.create('span', {
                        className: 'error', innerText: target + ': '+ error[target][e]}), 1);
        }
    }

})();


addEvent(window, 'load', function(){ Filter.init.call(Filter); });
