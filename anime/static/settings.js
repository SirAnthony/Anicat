

function hideType(){
    var sel = document.getElementById("requestDisplay");
    var selected = element.getSelected(sel);
    var elements = sel.options;
    if(sel.options[selected].value == 'all'){
        var divs = getElementsByClassName('request', sel.parentNode.parentNode, 'div');
        for(elem in divs)
            divs[elem].style.display = 'block';
    }else{
        selected -= 1;
        for(var i=0; i<elements.length; i++){
            var divs = getElementsByClassName('request'+i, sel.parentNode.parentNode, 'div')
            for(elem in divs){
                if(i == selected)
                    divs[elem].style.display = 'block';
                else
                    divs[elem].style.display = 'none';
           }
        }
    }

}

function settingsInit(){
    addEvent(document.getElementById("requestDisplay"), 'change', hideType);
}

addEvent(window, 'load', settingsInit);
