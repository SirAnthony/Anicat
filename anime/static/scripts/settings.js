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
    var sel = document.getElementById("requestDisplay")
    var selected = element.getSelected(sel)
    var value = sel.options[selected].value
    var divs = getElementsByClassName('request', sel.parentNode.parentNode, 'div')
    divs.forEach(function(div) {
        var type = div.getAttribute("data-request")
        toggle(div, (value < 0 || value == type) ? 1 : -1)
    })
}

require(['base/events'], function (events){
    events.onload(events.add, events, [
            document.getElementById("requestDisplay"), 'change', hideType])
})
