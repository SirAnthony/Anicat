

var Filter = new (function(){

    this.errorobj = null;

    this.init = function(){
        createScroll(document.getElementById('id_filter_genre_container'));
        map(function(el){
            element.insert(el.firstChild, {'a':
                {'innerText': 'Clear', 'className': 'right',
                'onclick': function(){ map(function(o){ o.selected = false; },
                    this.parentNode.getElementsByTagName('option'))}}});
            }, getElementsByClassName('nano',
                document.getElementById("id_filter_container")));
        Filter.errorobj = getElementsByClassName('mainerror',
                        document.getElementById('id_filter_container'))[0];
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
        cookies.del('filter');
    }

    this.apply = function(){
        element.removeAllChilds(this.errorobj);
        var data = map(getFormData, getElementsByClassName('filter', document));
        var processed = {};
        map(function(el){
            for(var name in el)
                if(isArray(el[name]))
                    processed[name] = map(function(o){ return o.value; }, el[name]);
                else if(el[name])
                    processed[name] = el[name];
            }, data);
        ajax.loadXMLDoc(url+'filter/', processed, new RequestProcessor(
            function(resp){
                message.hide();
                if(!resp.status)
                    Filter.processError(resp.text);
            }
        ), 'filter');
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


addEvent(window, 'load', Filter.init);
