/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Statistics functions
 *
 */


var stat = new ( function(){

    this.hrs = null;

    this.init = function(){
        stat.hrs = element.create('div', {id: 'tohrs',
                className: 'cont_men', style: {position: 'absolute'}});
        element.appendChild(document.body, [stat.hrs]);
        var el = document.getElementsByName('num');
        for(var i in el){
            addEvent(el[i], 'mouseover', function(){
                var offset = element.getOffset(this);
                stat.hrsShow(this.textContent, offset.left + this.offsetWidth/1.6, offset.top - this.offsetHeight*2.8);
            });
            addEvent(el[i], 'mouseout', (function(h){
                return function(){toggle(h, -1)} }
            )(stat.hrs));
        }
    }

    this.hrsShow = function(mins, x, y){
        if(!this.hrs)
            return;
        this.hrs.textContent = (mins/60).toFixed(2) +'h. '+ (mins/(60*24)).toFixed(2) + 'd.';
        this.hrs.style.left = x + 'px';
        this.hrs.style.top = y + 'px';
        toggle(this.hrs, 1);
    }

})();

addEvent(window, 'load', stat.init);
