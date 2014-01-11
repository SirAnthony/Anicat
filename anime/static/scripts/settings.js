/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Settings functions
 *
 */

function hideType(){
    var sel = document.getElementById("requestDisplay");
    var selected = element.getSelected(sel);
    var elements = sel.options;
    if(sel.options[selected].value == 'all'){
        var divs = getElementsByClassName('request', sel.parentNode.parentNode, 'div');
        for(var elem; elem < divs.length; elem++)
            toggle(divs[elem], 1);
    }else{
        selected -= 1;
        for(var i=0; i<elements.length; i++){
            var divs = getElementsByClassName('request'+i, sel.parentNode.parentNode, 'div')
            for(var elem; elem < divs.length; elem++)
                toggle(divs[elem], (i == selected ? 1 : -1));
        }
    }

}

function settingsInit(){
    addEvent(document.getElementById("requestDisplay"), 'change', hideType);
}

addEvent(window, 'load', settingsInit);
