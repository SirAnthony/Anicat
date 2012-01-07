
function cardLoad(){
    var card = document.getElementById('card') || document.getElementById('pagecard');
    hideEdits(card);
    if(!card) return
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

function hideEdits(p){
    if(!p) p = document;
    var h = p.getElementsByTagName('h4');
    h[h.length] = document.getElementById("cimg").lastChild;
    for(var element in h){
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

addEvent(window, 'load', cardLoad);
if(document.readyState == "complete")
    cardLoad();
