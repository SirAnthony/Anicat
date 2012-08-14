

var Filter = new (function(){

    this.init = function(){
        createScroll(document.getElementById('id_filter_genre_container'));
        map(function(el){
            element.insert(el.firstChild, {'a':
                {'innerText': 'Clear', 'className': 'right',
                'onclick': function(){ map(function(o){ o.selected = false; },
                    this.parentNode.getElementsByTagName('option'))}}});
            }, getElementsByClassName('nano',
                document.getElementById("id_filter_container")));
    }

    this.toggle = function(){
        toggle(document.getElementById('id_filter_container'));
    }

    this.clear = function(){
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
        var data = map(getFormData, getElementsByClassName('filter', document));
        var processed = {};
        map(function(el){
            for(var name in el)
                if(isArray(el[name]))
                    processed[name] = map(function(o){ return o.value; }, el[name]);
                else if(el[name]){
                    var names = name.toLowerCase().split('_');
                    if(!processed[names[0]])
                        processed[names[0]] = {};
                    if(names[1])
                        processed[names[0]][names[1]] = el[name];
                    else
                        processed[names[0]]['value'] = el[name];
                }
            }, data);
        ajax.loadXMLDoc(url+'filter/', processed, new RequestProcessor(
            function(resp){
                message.hide();
                if(!resp.status)
                    throw resp;
            }
        ), 'filter');
    }

})();


addEvent(window, 'load', Filter.init);
