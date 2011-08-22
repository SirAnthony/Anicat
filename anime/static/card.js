
function hideEdits(){
    var h = document.getElementsByTagName('h4');
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

addEvent(window, 'load', hideEdits);
