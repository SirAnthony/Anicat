/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Card module
 *
 */

 var Card;

define(['base/events', 'base/message', 'base/user', 'base/ajax',
    'base/request_processor', 'catalog/forms'],
    function (events, message, user, ajax, RequestProcessor, forms){

    var self = {
        init: function(){
            this.processor = new RequestProcessor({'card': function(resp){
                message.hide();
                this.create(resp.id, resp.text);
            }}, this);
            this.load();
            user.addEvent(this.place, this);
        },

        load: function(){
            var card = document.getElementById('card') || document.getElementById('pagecard');
            if(!isOldIE)
                this.hideEdits(card);
            if(!card || !card.clientWidth || !card.childNode) return;
            var imgbun;
            if(card.clientWidth < 750){
                imgbun = (card.clientWidth < 600) ? 200 : 300;
                card.firstChild.style.maxWidth = imgbun + 'px';
                card.firstChild.firstChild.firstChild.style.maxWidth = imgbun + 'px';
                imgbun += 40;
            }else{
                imgbun = card.firstChild.clientWidth + 40;
            }
            card.lastChild.previousSibling.style.maxWidth = card.clientWidth - imgbun - 20 + 'px';
        },

        hideEdits: function(p){
            if(!p) return
            if(!require.defined('catalog/edit')) return;
            var edit = require('catalog/edit')
            var h = filter(function(ci) { return ci && ci.tagName == "A" },
                            getElementsByClassName('right', p))
            h.forEach(function(c){
                toggle(c, -1)
                events.add(c.parentNode, 'mouseover', edit.showEdit)
                events.add(c.parentNode, 'mouseout', edit.hideEdit)
            })
        },

        create: function(id, res){
            if(!id || !res)
                throw new Error('Bad data passed for card creration');
            var card = document.getElementById("card");
            var fields = ['name', 'type', 'genre', 'episodesCount',
                        'duration', 'release', 'links', 'state'];
            var data = map(function(field){
                return forms.getTitledField(field, id, res[field]);
            }, fields);
            // FIXME: mess
            var bundle = forms.getTitledField('bundle', id, res.bundle);
            var link = null;
            if(isArray(bundle)){
                link = bundle.pop();
                bundle = bundle.pop();
            }
            element.appendChild(card, [
                {'div': {'id': 'imagebun', 'className': 'cardcol'}}, [
                    {'div': {'id': 'cimg'}}, [
                        {'img': {'src': 'http://anicat.net/images/' + res.id + '/'}},
                        forms.getEditLink('image', id),
                        forms.getField('image', res.id)],
                    link, bundle
                ],
                {'div': {'id': 'main', 'className': 'cardcol'}}, data,
                {'div': {'className': 'left'}}, [
                    {'a': {'innerText': '✕', 'onclick': this.close}},
                    {'a': {'innerText': '↪', 'href': '/card/' + id + '/', target: '_blank'}},
                ]

            ]);
            this.place(true);
            this.load();
        },

        close: function(){
            toggle(document.getElementById("card"), -1);
        },

        get: function(id, e){
            var card = document.getElementById("card");
            if(card){
                var tbl = document.getElementById("tbl");
                var w = document.documentElement.clientWidth - tbl.clientWidth - 70;
                element.removeAllChilds(card);
                card.style.width = w + 'px';
                if(w >= 500){
                    if(e) message.toEventPosition(e);
                    ajax.load('get', {'id': id, 'card': true, 'field': [
                        'id', 'bundle', 'name', 'type', 'genre', 'episodesCount',
                        'duration', 'release', 'links', 'state']}, this.processor);
                    return false;
                }
            }
            return true;
        },

        place: function(show){
            var card = document.getElementById("card");
            if(!card) return;
            if(show) toggle(card, true);
            var soffsety = (document.documentElement.scrollTop || document.body.scrollTop) - document.documentElement.clientTop;
            var scry = 0;
            if(isNumber(window.pageYOffset))
                scry = window.pageYOffset;
            else if(document.body && document.body.scrollTop)
                scry = document.body.scrollTop;
            else if(document.documentElement && document.documentElement.scrollTop)
                scry = document.documentElement.scrollTop;
            if(!user.logined){
                var l = document.getElementById('loginform');
                if(visible(l) && soffsety < l.scrollHeight)
                    soffsety = l.scrollHeight + 30 - (scry ? 0 : 40);
            }
            card.style.top = soffsety + (scry ? 5 : 40) + 'px';
        }
    };

    Card = self;
    return self;
});
