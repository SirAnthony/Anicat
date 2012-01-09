
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
        if(!p) p = document;
        var h = new Array();
        h.push.apply(h, p.getElementsByTagName('h4'));
        if(!h.length) return;
        h.push(document.getElementById("cimg").lastChild);
        for(var element=0; element<h.length; element++){
            var c = h[element].previousSibling;
            var parent = h[element].parentNode;
            if(!c || c.tagName != "A")
                continue;
            c.style.display = "none";
            addEvent(parent, 'mouseover', (function(c){
                return function(){c.style.display = "block";}})(c));
            addEvent(parent, 'mouseout', (function(c){
                return function(){c.style.display = "none";}})(c));
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

    this.get = function(id){
        var card = document.getElementById("card");
        if(card){
            var dvid = document.getElementById("dvid");
            var tbl = document.getElementById("tbl");
            var w = dvid.clientWidth - tbl.clientWidth - 100;
            element.removeAllChilds(card);
            card.style.width = w + 'px';
            if(w >= 500){
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
        if(!user.logined && soffsety < 75){
            if(document.getElementById('logdv').style.display == 'block'){
                soffsety += 20;
                if(user.info.style.display == 'block')
                    soffsety += 17;
            }
        }
        card.style.top = soffsety + ((soffsety > card.parentNode.offsetTop) ? 5 : 40) + 'px';
    }

})();

addEvent(window, 'load', Card.init);
