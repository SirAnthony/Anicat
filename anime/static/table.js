/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Table builder module
 *
 */

var table = new ( function(){

    this.build = function(obj, attrs, data){
        if(!obj)
            return;
        attrs = extend({'table': {}, 'head': {}, 'body': {}}, attrs);
        element.removeAllChilds(obj);
        element.appendChild(obj, [{'table':
            extend({className: 'tbl', cellSpacing: 0}, attrs.table)},[
                {'thead': extend({className: 'thdtbl'}, attrs.head)},
                this.buildHeader(data.head),
                {'tbody': attrs.body},
                this.buildContent(data.list, data.pages.start)
            ]
        ]);
    }

    this.buildHeader = function(data){
        if(!data || !isArray(data))
            return [];
        return ['tr', map(function(name){
            if(name == 'air')
                return {'th': {className: 'link'}};
            else if(name == 'id')
                return {'th': {className: 'id', innerText: '№'}};
            return {'th': {className: name, innerText: capitalise(name)}};
        }, data)];
    }

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
                            {'img': {'src': '/static/arrow.gif', 'alt': 'Go'}},
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
    }

    this.buildPages = function(pages, attrs, callback, scope){
        if(!pages.items)
            return [];
        var pg = new Array();
        for(var p=0; p < pages.items.length; p++){
            if(pages.current == p+1){
                pg.push(element.create('span', {className: 'spanl', innerText: '[' + pages.items[p] + ']'}));
            }else{
                pg.push(element.create('a', {innerText: pages.items[p],
                    onclick: (function(num){ return function(e){
                         callback.call(scope, num, e);};})(p+1)}));
            }
        }
        return [{'div': attrs}, pg];
    }

    this.cell_default = function(id, name, data){
        return {'td': {'id': name + id, className: name,
            onclick: (function(i, j){
                return function(e){ cnt(i, j, e); };})(name, id),
            innerText: encd(data)}};
    }

    this.cell_title = function(id, name, data){
        var c = this.cell_default(id, name, data);
        c = element.create('td', c.td);
        popup.add(c);
        return c;
    }

})();
