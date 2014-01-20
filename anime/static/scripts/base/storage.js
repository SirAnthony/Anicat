/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Local storage interface
 *
 */

define(['base/stylesheet', 'base/events'],
    function (stylesheet, events){


    function default_color(colors, _stat){
        if(!colors[_stat]){
            var styles = map(function(tmpl) { return [
                tmpl[1] + _stat, tmpl[2], tmpl[3]]; }, stylesheet.base_styles)
            colors[_stat] = map(function(a){
                    return stylesheet.get.apply(null, styles[a])
                }, range(0, styles.length-1))
        }
        return colors[_stat]
    }

    var self = new (function(){

        this.loaded = false
        this.keyprefix = "anicat."
        this.key_re = new RegExp(/^anicat\./)

        this.init = function(){
            if(this.loaded) return true
            this.loaded = !isUndef(localStorage)
            if(this.loaded){
                this.updateList()
                this.enabled = self.getItem('enabled') ? true : false
            }else{
                this.enabled = false
            }
            return this.loaded
        };

        this.enable = function(){
            if (!this.loaded) return false
            this.enabled = true
            this.addItem('enabled', true)
            return true
        };

        this.disable = function(){
            this.enabled = false
            this.removeItem('enabled')
        };

        this.interact = function(func, subkey){
            if(!this.loaded) return
            var re = subkey ? new RegExp('^'+subkey+'\\.') : null
            for(var i=0; i<localStorage.length; i++){
                var keyname = localStorage.key(i)
                if(this.key_re.test(keyname)){
                    var key = keyname.replace(this.key_re, '')
                    if(!subkey || (re && re.test(key)))
                        func(re ? key.replace(re, '') : key, keyname)
                }
            }
            return true
        };

        this.keys = function(subkey){
            if(!this.loaded) return
            var keys = []
            this.interact(function(key){ keys.push(key) }, subkey)
            return keys
        };

        this.values = function(subkey){
            if(!this.loaded) return
            var vals = []
            this.interact(function(key, keyname){
                vals.push(localStorage[keyname]) }, subkey)
            return vals
        }

        this.items = function(subkey){
            if(!this.loaded) return
            var items = {}
            this.interact(function(key, keyname){
                items[key] = localStorage[keyname] }, subkey)
            return items
        };

        this.addItem = function(key, value){
            if(!this.loaded || !this.enabled) return true
            localStorage[this.keyprefix + key] = value
        };

        this.getItem = function(key){
            if(!this.loaded) return
            return localStorage[this.keyprefix + key]
        };

        this.removeItem = function(key){
            if(!this.loaded || !this.enabled) return true
            localStorage.removeItem(this.keyprefix + key)
        };

        this.exist = function(key){
            if(!this.loaded || !this.enabled) return false
            return !isUndef(localStorage[this.keyprefix + key])
        };

        this.updateList = function(){
            if(!this.loaded)
                return
            var keys = this.keys('list')
            var colors = {}
            var rules = Array()

            keys.forEach(function(key){
                if(isNaN(key))
                    return
                var stat = self.getItem('list.' + key)
                var color = default_color(colors, stat)
                for (var k in stylesheet.base_styles){
                    var style = stylesheet.base_styles[k]
                    rules.push([style[0] + key, [style[2], color[k], style[4]]])
                }
            }, this)
            stylesheet.add(rules)
        };

    })();

    // Additional catalog functions
    self.getStatus = function(id, types){
        var num = 0;
        var value = null;
        if(this.loaded){
            this.enable();
            num = this.getItem('list.'+id) || 0;
            if(types) value = types[num];
        }else{
            state = -1;
            value = 'Enable local storage to use catalog off-line or anonymously.';
        }
        return {'state': num, 'value': value};
    };

    self.addStatus = function(id, value){
        if(!this.enabled)
            throw new Error('Local storage not enabled.');
        if(!id)
            throw new Error('Bad item id.');
        if(!value)
            value = 0;
        return this.addItem('list.'+id, value);
    };


    return self;
});