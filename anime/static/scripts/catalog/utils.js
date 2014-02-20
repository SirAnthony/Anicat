/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Catalog utils
 *
 */

define([
    'base/events', 'base/message', 'catalog/list',
    'catalog/search', 'base/ajax', 'base/request_processor',
    'catalog/forms'],
function (events, message, list, searcher, ajax, RequestProcessor, forms, edit){

    //################# Get menu with info
    function field_content(tag, num, event){
        event = event || window.event
        events.stop(event)
        message.toEventPosition(event)
        var qw = {'id': num}
        switch (tag){
            case 'title':
                qw['field'] = ['name', 'genre', 'links']
            break
            case 'episodes':
                qw['field'] = ['bundle', 'duration']
            break
            case 'id':
                var edit = require('catalog/edit')
                edit.status_menu_edit = true //Fuuu
                return edit.rf(num, 'state', event)
            break
            default:
                qw['field'] = tag
        }
        ajax.load('get', qw, {
            'get': function(resp){
                message.create();
                resp.text.order.forEach(function(curname) {
                    if(!curname || !resp.text[curname])
                        return
                    var current = resp.text[curname]
                    message.addTree(element.create('label', { 'for': curname + resp.id,
                                    innerText: capitalise(curname) + ':'}))
                    message.addTree(forms.getField(curname, resp.id, current))
                })
                message.show()
            }})
    }


    //######################## URI Hash

    var disabled_links = [
        new RegExp(/^\/search\//)
    ]

    function disabled(target) {
        target = target || document.location.pathname
        for(var link in disabled_links)
            if(target.match(disabled_links[link]))
                return true;
        return false;
    }

    var hash_re = new RegExp('^/?(?:(?:search/(.*))|(?:(?:user/(\\d+)/)?show/(\\d+))?)/(?:sort/(-?\\w+)/)?(?:(\\d+)/?)?');


    function parseURIHash(string){
        string = string.replace(/http:\/\/[^\/]+/g,'').replace(/^#?/g, '')
        var match = hash_re.exec(string)
        if(!match)
            return
        var request = 'list'
        var ret = {}
        var processor = list.processor
        if(match[1]){
            request = 'search'
            ret['string'] = match[1]
            processor = searcher.processor
        }else if(match[2] && !isUndef(match[3])){
            ret = extend(ret, {'user': match[2], 'status': match[3]})
        }
        var aret = extend(ret, {'order': match[4], 'page': match[5]})
        return [request, aret, processor]
    }

    function loadURIHash(string){
        if(disabled())
            return true
        if(!document.getElementById('dvid') && !searcher.loaded)
            return true
        var link = parseURIHash(string || document.location.hash)
        if(!link || !link[0])
            return false
        ajax.load.apply(ajax, link)
        return false
    }

    function load_this_href(event) {
        return loadURIHash(event.currentTarget.href);
    }

    //######################## Display mode
    function set_status(){
        var mode = this.value;
        if(!isNumber(mode))
            return;
        loadURIHash(mode < 0 ? '/' : '/show/' + mode + '/');
    }



    return {
        cnt: field_content,
        parseURI: parseURIHash,
        loadURI: loadURIHash,
        load_href: load_this_href,
        view_status: set_status
    }

})