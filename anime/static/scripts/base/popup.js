/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Popup interface
 *
 */


define(['base/events', 'base/classes', 'base/message'],
    function(events, classes, message){

    var _pop = null;

    var self = {
        init: function(){
            this.addToTable()
        },

        pop: function(){
            if(!_pop)
                _pop = document.getElementById('popup');
            return _pop;
        },

        move: function(e){
            var p = message.eventPosition(e);
            if(visible(self.pop())){
                self.pop().style.top = p.y + 10 +'px';
                self.pop().style.left = p.x + 10 +'px';
            }
        },

        over: function(e){
            var p = message.eventPosition(e);
            self.pop().style.top = p.y + 'px';
            self.pop().style.left = p.x + 'px';
            events.add(this, 'mousemove', self.move);
            toggle(self.pop(), 1);
            self.pop().firstChild.innerText = this.innerText;
        },

        out: function(e){
            events.remove(this, 'mousemove', self.move);
            toggle(self.pop(), -1);
        },

        add: function(el){
            if(isArray(el) || isNodeList(el)){
                for(var i = 0; i < el.length; i++)
                    this.add(el[i]);
            }else if(isElement(el)){
                if(el.offsetHeight >= el.scrollHeight)
                    return;
                events.add(el, 'mouseover', this.over);
                events.add(el, 'mouseout', this.out);
            }
        },

        addToTable: function(node, cn){
            var el = (node) ? node : document.getElementById('tbdid');
            this.add(classes.getElements(cn || "title", el, 'td'));
        }
    };

    return self;
});