
var Card = new (function(){

    this.init = function(){
        Card.load();
    }

    this.load = function(){
        var card = document.getElementById('card') || document.getElementById('pagecard');
        if(!isOldIE)
            this.hideEdits(card);
        if(!card || !card.clientWidth) return;
        var imgbun;
        if(card.clientWidth < 750){
            imgbun = (card.clientWidth < 600) ? 200 : 300;
            card.firstChild.style.maxWidth = imgbun + 'px';
            card.firstChild.firstChild.lastChild.style.maxWidth = imgbun + 'px';
            imgbun += 40;
        }else{
            imgbun = card.firstChild.clientWidth + 40;
        }
        card.lastChild.style.maxWidth = card.clientWidth - imgbun + 'px';
    }

    this.hideEdits = function(p){
        if(!p) return;
        var h = new Array();
        var c = p.getElementsByTagName('h4');
        for(var i=0; i<c.length; i++) //google chrome, lol
            h.push(c[i]);
        if(!h.length) return;
        h.push(document.getElementById("cimg").lastChild);
        for(var element=0; element<h.length; element++){
            var c = h[element].previousSibling;
            var parent = h[element].parentNode;
            if(!c || c.tagName != "A")
                continue;
            toggle(c, -1);
            addEvent(parent, 'mouseover', (function(c){
                return function(){toggle(c, 1);}})(c));
            addEvent(parent, 'mouseout', (function(c){
                return function(){toggle(c, -1);}})(c));
        }
    }

    this.create = function(id, res){
        if(!id || !res)
            throw new Error('Bad data passed for card creration');
        var card = document.getElementById("card");
        var data = new Array();
        var fields = ['name', 'type', 'genre', 'episodesCount',
                    'duration', 'release', 'links', 'state']
        for(var i=0; i<fields.length; i++){
            data.push(forms.getTitledField(fields[i], id, res[fields[i]]));
        }
        element.appendChild(card, [
            {'div': {'id': 'imagebun', 'className': 'cardcol'}}, [
                {'div': {'id': 'cimg'}}, [
                    {'img': {'src': 'http://anicat.net/images/' + res.id + '/'}}],
                forms.getTitledField('bundle', id, res.bundle)
            ],
            {'div': {'id': 'main', 'className': 'cardcol'}}, data

        ]);
        this.place();
        this.load();
    }

    this.get = function(id, e){
        var card = document.getElementById("card");
        if(card){
            var tbl = document.getElementById("tbl");
            var w = document.documentElement.clientWidth - tbl.clientWidth - 100;
            element.removeAllChilds(card);
            card.style.width = w + 'px';
            if(w >= 500){
                message.toEventPosition(e);
                ajax.loadXMLDoc(url+'get/', {'id': id, 'card': true, 'field': [
                    'id', 'bundle', 'name', 'type', 'genre', 'episodesCount',
                    'duration', 'release', 'links', 'state']});
                return false;
            }
        }
        return true;
    }

    this.place = function(){
        var card = document.getElementById("card");
        if(!card) return;
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

})();

addEvent(window, 'load', Card.init);
