/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Messages interface
 *
 */

define(['base/events'], function(events) {
    var strobj = [];
    var timeout = null;

    var self = {
        closeable: false,
        onclose: null,

        getMenu: function(){

            if(!this.menu)
                this.menu = document.getElementById('menu');
            return this.menu;
        },

        //Clears message box and adds new p.
        create: function(str, timeout){
            this.clear();
            this.lock();
            if(!isString(str) && !isNumber(str) && !isUndef(str) && !isError(str))
                this.addTree(str);
            else
                this.add(str);
            this.timeout = timeout;
        },

        //Adds new p element.
        add: function(str){
            if(!str) return;
            strobj.push(element.create('p', {innerText: str}));
        },

        //Adds element tree.
        addTree: function(elem){
            if(!elem) return;
            strobj.push(elem);
        },

        //Adds html string to message.
        //FIXME: innerHTML is bad.
        addHTML: function(str){
            if(!str) return;
            var p = element.create('p', {innerHTML: str});
            var styles = p.getElementsByTagName('style');
            for(var style in styles){
                var st = styles[style];
                if(!isElement(st)) continue;
                //st.innerText = st.innerText.replace('/html.*}/gi', '');
            }
            strobj.push(p);
        },

        //Adds string to last string.
        addToLast: function(str){
            if(!str) return;
            strobj[strobj.length].innerText += str;
        },

        //Remove all elements.
        clear: function(){
            while(strobj.length)
                element.remove(strobj.shift());
        },

        toPosition: function(x, y){
            if(!this.getMenu())
                return;
            this.menu.style.left = x + 'px';
            this.menu.style.top = y + 'px';
        },

        eventPosition: function(e){
            var x = 20;
            var y = 20;
            if(isIE)
                e = event;
            if(e.pageX || e.pageY){
                x = e.pageX;
                y = e.pageY;
            }else if(e.clientX || e.clientY){
                x = e.clientX + (document.documentElement.scrollLeft || document.body.scrollLeft) - document.documentElement.clientLeft;
                y = e.clientY + (document.documentElement.scrollTop || document.body.scrollTop) - document.documentElement.clientTop;
            }else if(e.target){
                x = e.target.offsetLeft;
                y = e.target.offsetTop;
            }
            return {x: x, y: y};
        },

        //Move messagebox to last event position.
        //Pop - старый костыль, но пока никак.
        toEventPosition: function(e){
            if(!this.getMenu())
                return;
            var p = this.eventPosition(e);
            this.toPosition(p.x, p.y);
        },

        // Prevents menu from closing
        lock: function(){
            this.closeable = false;
        },

        unlock: function(){
            this.closeable = true;
        },

        //Show message.
        show: function(time){
            if(!this.getMenu())
                return;
            element.removeAllChilds(this.menu);
            element.appendChild(this.menu, strobj);
            toggle(this.menu, 1);
            if(time)
                this.timeout = time;
            if(this.timeout)
                timer = setTimeout(function(){toggle(document.getElementById('menu'), -1);}, this.timeout);
            events.add(document, 'click', self.close);
            this.unlock();
        },

        //Close message.
        close: function(e){
            if(!self.closeable || !self.getMenu())
                return;
            var menu = self.getMenu();
            var target = e ? e.target : event.srcElement;
            var checkParent = function(obj){
                if(!obj) return true;
                if(obj != menu) return checkParent(obj.parentNode);
                return false;
            };
            if(checkParent(target)){
                self.hide();
                clearTimeout(this.timeout);
                if(self.onclose){
                    self.onclose();
                    self.onclose = null;
                }
            }
        },

        //Hide message. No closeable check.
        hide: function(){
            if(!self.getMenu())
                return;
            events.remove(document, 'click', self.close);
            toggle(self.menu, -1);
        }
    };

    return self;
});