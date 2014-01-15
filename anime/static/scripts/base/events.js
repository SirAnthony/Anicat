/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Cross-browser event handlers.
 *
 */

define(function() {
    return {

        add: function(obj, evType, fn){
            if(!obj) return false;
            if(obj.addEventListener){
                obj.addEventListener(evType, fn, false);
                return true;
            }else if(obj.attachEvent){
                var r = obj.attachEvent("on" + evType, fn);
                return r;
            }else{
                return false;
            }
        },

        remove: function(obj, evType, fn) {
            if(!obj) return false;
            if(obj.removeEventListener){
                obj.removeEventListener(evType, fn, false);
                return true;
            }else if(obj.detachEvent){
                obj.detachEvent("on" + evType, fn);
                return true;
            }else{
                return false;
            }
        },

        onload: function(fn, environ, args) {
            if(document.readyState === "complete")
                fn.apply(environ, args);
            else
                this.add(window, 'load', function(){ fn.apply(environ, args); });
        },

        add_action: function(module, raw_name, object) {
            var elements = []
            if(object){
                elements.push(object);
            }else{
                var name = raw_name.split("/").pop();
                elements = getElementsByClassName('module-' + name);
            }

            elements.forEach(function(elem){
                var method = elem.getAttribute("data-method");
                if(!method)
                    return;
                var action = elem.getAttribute("data-action") || 'click';
                var params = elem.getAttribute("data-params");
                params = params ? JSON.parse(params) : [];
                this.add(elem, action, function(event){
                    if(!event)
                        event = window.event;
                    if(module[method].apply(module,
                            params.concat(event)) === false){
                        if(event.preventDefault)
                            event.preventDefault();
                        else
                            event.returnValue = false;
                        return false;
                    }
                })
            }, this)
        }
    };
});
