/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Statistics functions
 *
 */


var statistics = new ( function(){

    this.hrs = null;
    this.stat = null;
    this.processor = new RequestProcessor({'stat': function(resp){
        if(!this.stat)
            throw Error('Statistics panel not exists.');
        message.hide();
        element.removeAllChilds(this.stat);
        if(!resp.status)
            element.appendChild(this.stat, [
                {'p': {'className': 'error', 'innerText': 'Error:'}},
                map(function(er){
                    return {'p': {'className': 'error', 'innerText': er}}
                }, resp.text)
            ]);
        else
            this.load(resp.text);
    }}, this);


    this.init = function(){
        this.hrs = element.create('div', {id: 'tohrs',
                className: 'cont_men', style: {position: 'absolute'}});
        this.stat = document.getElementById("statistic");
        element.appendChild(document.body, [this.hrs]);
        this.hrsSetup();
    }

    this.hrsSetup = function(){
        var el = getElementsByClassName('num', this.stat);
        for(var i in el){
            addEvent(el[i], 'mouseover', function(){
                var offset = element.getOffset(this);
                statistics.hrsShow(this.textContent,
                    offset.left + this.offsetWidth/1.6,
                    offset.top - this.offsetHeight*2.8);
            });
            addEvent(el[i], 'mouseout', (function(h){
                return function(){toggle(h, -1)} }
            )(this.hrs));
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

    this.load = function(data){
        if(!this.stat)
            return;
        var counter = 0;
        element.removeAllChilds(this.stat);
        element.appendChild(this.stat, [
            'table', ['thead', ['th', {'th': {'innerText': 'Items'}},
                {'th': {'innerText': 'Full duration', 'colSpan': '2'}},
                {'th': {'innerText': 'Watched', 'colSpan': '2'}}, 'th'],
                'tbody', map(function(el){
                    counter++;
                    return element.create('tr', {'className': 'stat'}, [
                        {'td': {'className': 'textleft stat' + el.name.toLowerCase(),
                            'innerText': capitalise(el.name) + ':'}},
                        {'td': {'innerText': el.count || 0 }},
                        {'td': {'innerText': el.full || 0, 'className': 'num'}},
                        {'td': {'className': 'textleft', 'innerText': 'min.'}},
                        {'td': {'innerText': el.custom || 0, 'className': 'num'}},
                        {'td': {'className': 'textleft', 'innerText': 'min.'}},
                        (el.name.toLowerCase() != 'total') ? {'a':
                            {'target': '_blank', 'className': 'blacklink',
                            'innerText': '↪', 'href': '/user/' +
                                + data.userid + '/show/' + counter +'/',
                            'onclick': function(){ return loadURIHash(this.href); }}
                            } : null
                    ]);
                }, data.stat)
            ]
        ]);
        this.hrsSetup();
    }


    this.loadStorage = function(){
        if(!this.stat)
            return;
        element.removeAllChilds(this.stat);
        var storage = user_storage.items('list');
        var items = new Array(0,0,0,0,0,0,0);
        for(var i in storage){
            var n = parseInt(storage[i]);
            if(n < 1 || n > 6) continue;
            items[n]++;
            items[6]++;
        }
        var counter = -1;
        var statuses = STATUSES;
        statuses.push("total");
        element.appendChild(this.stat, [
            'table', ['thead', ['th', {'th': {'innerText': 'Items'}}],
                'tbody', map(function(el){
                    counter++;
                    if(!counter)
                        return null;
                    return element.create('tr', {'className': 'stat'}, [
                        {'td': {'className': 'textleft stat' + statuses[counter],
                            'innerText': capitalise(statuses[counter]) + ':'}},
                        {'td': {'innerText': el || 0 }},
                    ]);
                }, items)
            ]
        ]);
    }


    this.getStat = function(){
        if(user.logined){
            ajax.loadXMLDoc('stat', {}, this.processor);
        }else if(catalog_storage.enabled){
            this.loadStorage();
        }else{
            element.removeAllChilds(this.stat);
            element.appendChild(this.stat, {'p': {'innerText':
                'Enable local storage to use catalog anonymously.'}});
        }
    }

    this.toggle = function(){
        if(!this.stat)
            return;
        if(!this.stat.childNodes.length)
            this.getStat();
        toggle(this.stat);
    }

})();


addEvent(window, 'load', function(){ statistics.init(); });
