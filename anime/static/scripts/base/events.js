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
        }
    };
});
