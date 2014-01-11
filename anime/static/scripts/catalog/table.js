/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Table builders module
 *
 */

define(['base/popup'], function(popup){

    var shortnames = {'type': 'releaseType', 'release': 'releasedAt',
                       'episodes': 'episodesCount'};
    var headnames = {'title': 'name', 'release': 'released'};

    this.longName = function(n){
        return (shortnames[n] ? shortnames[n] : n);
    };

    this.headName = function(n){
        return (headnames[n] ? headnames[n] : n);
    };

    this.build = function(obj, attrs, data, calls){
        if(!obj)
            return;
        attrs = extend({'table': {}, 'head': {}, 'body': {}, 'pages': {}}, attrs);
        calls = extend({'head': {}, 'pages': {}}, calls);
        element.removeAllChilds(obj);
        if(isArray(data.list) && data.list.length){
            if(isHash(data.link) && data.link.status)
                element.appendChild(obj, {'h2': {'className': 'listtitle',
                    'innerText': capitalise(STATUSES[data.link.status]) + ' list'}});
            element.appendChild(obj, [{'table':
                extend({className: 'tbl', cellSpacing: 0}, attrs.table)},[
                    {'thead': extend({className: 'thdtbl'}, attrs.head)},
                    this.buildHeader(data.head, data.link, calls.head),
                    {'tbody': attrs.body},
                    this.buildContent(data.list, data.pages.start)
                ], this.buildPages(data, attrs.pages, calls.pages)
            ]);
        }else{
            element.appendChild(obj, {'p': {'innerText': 'Nothing to display'}});
        }
    };

    this.buildHeader = function(data, link, callback){
        if(!isArray(data) || !data.length)
            return [];
        var th = new Array();
        map(function(name){
            if(name == 'air'){
                th.push({'th': {className: 'link'}});
            }else if(name == 'id'){
                th.push.apply(th, [{'th': {className: 'id'}}, [
                    {'a': {'innerText': '№', 'href': '/',
                    'onclick': function(ev) {
                        return callback.func.call(callback.scope, {}, '', ev);}
                    }}]]);
            }else{
                var lname = table.longName(name);
                if(link.order == ((lname == 'title') ? undefined : lname))
                    lname = '-' + lname;
                var href = link.link.replace(/(.+)?\/sort\/\-?\w+\/?/gi, '$1'
                    ) + 'sort/' + lname + '/';
                th.push.apply(th, [{'th': {className: name}}, [{'a': {
                'innerText': capitalise(table.headName(name)),
                'href': href, 'onclick': function(ev) {
                    return callback.func.call(callback.scope, link, lname, ev);
                }}}]]);
            }
        }, data);
        return ['tr', th];
    };

    this.buildContent = function(data, first){
        var rows = new Array();
        for(var i=0; i<data.length; i++){
            var elem = data[i];
            var row = element.create('tr',
                {className: (elem.air ? 'air a' : 'r') + elem.id}, [
                    {'td': {'id': 'link' + elem.id, className: 'link'}}, [
                        {'a': {className: 'cardurl', 'target': '_blank',
                            'href': '/card/'+elem.id+'/',
                            onclick: ( function(id){
                                        return function(e){return Card.get(id, e);};
                                    })(elem.id)}}, [
                            {'img': {'src': '/static/arrow.png', 'alt': 'Go'}},
                        ]
                    ],
                    {'td': {'id': 'id' + elem.id, className: 'id',
                        onclick: ( function(i, j){
                                        return function(e){ cnt(i, j, e); };
                                    })('id', elem.id),
                        innerText: Number(i) + first }},
                    ]);
            rows.push(row);
            for(var column in elem){
                if(column == 'air' || column == 'id') continue;
                var cell = this['cell_'+column];
                if(!cell)
                    cell = this.cell_default;
                element.appendChild(row,
                        cell.call(this, elem.id, column, elem[column]));
            }
        }
        return rows;
    };

    this.buildPages = function(data, attrs, callback){
        var pages = data.pages;
        if(!pages || !pages.items)
            return [];
        var pg = new Array();
        for(var p=0; p < pages.items.length; p++){
            if(pages.current == p+1){
                pg.push(element.create('span', {className: 'spanl', innerText: '[' + pages.items[p] + ']'}));
            }else{
                var href = data.link.link + (p+1) + '/';
                pg.push(element.create('a', {innerText: pages.items[p],
                    'onclick': (function(num){ return function(e){
                        return callback.func.call(callback.scope, data.link, num, e);};})(p+1),
                    'href': href
                    }));
            }
        }
        return element.create('div', attrs, pg);
    };

    this.cell_default = function(id, name, data){
        return {'td': {'id': name + id, className: name,
            onclick: (function(i, j){
                return function(e){ cnt(i, j, e); };})(name, id),
            innerText: encd(data)}};
    };

    this.cell_title = function(id, name, data){
        var c = this.cell_default(id, name, data);
        c = element.create('td', c.td);
        popup.add(c);
        return c;
    };

});

