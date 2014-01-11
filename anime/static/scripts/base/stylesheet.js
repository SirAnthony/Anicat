


define(function() {

    return {
        base_styles: [
            // Single item class, type class, field, default color,
            ['.r', '.rs', 'background-color',   '#FFF'],
            ['.a', '.as', 'background-color',   '#FFF'],
            ['.s', '.sl', 'color',              '#000', true]
        ],

        update: function(name, link){
            var a = document.getElementsByTagName('link');
            for(var i=0; i<a.length; i++){
                var s = a[i];
                if(s.rel.toLowerCase().indexOf('stylesheet') >= 0 && s.href){
                    var path = s.href.replace(/^https?:\/\/[^\/]+/i, '');
                    path = path.replace(/\?.*$/i, '');
                    if(!name || path == name){
                        s.href = s.href+'?'+(new Date().valueOf());
                    }
                }
            }
        },

        add: function(decls) {
            if (!decls.length)
                return;

            var style = document.createElement('style');
            document.getElementsByTagName('head')[0].appendChild(style);
            if (!window.createPopup) /* For Safari */
               style.appendChild(document.createTextNode(''));
            var s = document.styleSheets[document.styleSheets.length - 1];
            for (var i=0, dl = decls.length; i < dl; i++) {
                var j = 1, decl = decls[i], selector = decl[0], rulesStr = '';
                if (Object.prototype.toString.call(decl[1][0]) === '[object Array]') {
                    decl = decl[1];
                    j = 0;
                }
                for (var rl=decl.length; j < rl; j++) {
                    var rule = decl[j];
                    rulesStr += rule[0] + ':' + rule[1] + (rule[2] ? ' !important' : '') + ';\n';
                }

                if (s.insertRule)
                    s.insertRule(selector + '{' + rulesStr + '}', s.cssRules ? s.cssRules.length: 0);
                else /* IE */
                    s.addRule(selector, rulesStr);
            }
        },

        get: function(ruleName, field, default_val){
            var value = null;
            var recls = new RegExp(ruleName.toLowerCase());
            var reimp = new RegExp('(\\s|^)' + field.toLowerCase() + ':[^;]+(!\\s*important)?\\s*;?');
            for( var i = 0; i < document.styleSheets.length; i++){
                var sheet = document.styleSheets[i];
                var rules = sheet.cssRules ? sheet.cssRules : sheet.rules;
                var rlength = rules ? rules.length : 0;
                for( j = 0; j < rlength; j++){
                    var rule = rules[j];
                    if(!rule.selectorText)
                        continue;
                    var text = rule.selectorText.toLowerCase();
                    if(text.match(recls)){
                        if(window.getComputedStyle)
                            value = rule.style.getPropertyValue(field);
                        else if(isIE){
                            value = rule.style[camelize(field)];
                        }
                        if(rule.style.cssText && rule.style.cssText.toLowerCase().match(reimp))
                            return value;
                    }
                }
            }
            return value ? value : default_val;
        }
    };
});
