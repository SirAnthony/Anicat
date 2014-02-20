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
    var load_timer = null
    var load_stack = []

    function timeout_check() {
        load_timer = null
        var stack = load_stack
        load_stack = []
        stack.forEach(function(func) { func[0].apply(func[1], func[2]) })
    }

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

        emit: function(obj, evType, args, environ) {
            if(!obj)
                return false;
            environ = environ || obj
            obj["on" + evType].apply(environ, args)
        },

        stop: function(event) {
            event = event || window.event
            if(event.preventDefault)
                event.preventDefault();
            else
                event.returnValue = false;
            if(event.stopPropagation)
                event.stopPropagation();
            else
                event.cancelBubble = true;
            return false;
        },

        onload: function(fn, environ, args) {
            if(document.readyState === "complete")
                load_stack.push([fn, environ, args])
            else
                this.add(window, 'load', function(){ fn.apply(environ, args); });

            // Run everything in the next frame, not now
            if (load_stack.length > 0 && !load_timer)
                load_timer = setTimeout(timeout_check, 300)
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
                var self = this;
                this.add(elem, action, function(event){
                    event = event || window.event;
                    if(module[method].apply(module,
                            params.concat(event)) === false){
                        return self.stop(event);
                    }
                })
            }, this)
        }
    };
});
