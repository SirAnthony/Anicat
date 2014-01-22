/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Table builders module
 *
 */

define(['base/popup', 'catalog/utils'], function(popup, utils){

    var shortnames = {'type': 'releaseType', 'release': 'releasedAt',
                       'episodes': 'episodesCount'}
    var headnames = {'title': 'name', 'release': 'released'}

    return {
        longName: function(n){
            return shortnames[n] || n
        },

        headName: function(n){
            return headnames[n] || n
        },

        build: function(obj, attrs, data, calls){
            if(!obj)
                return
            attrs = extend({'table': {}, 'head': {}, 'body': {}, 'pages': {}}, attrs)
            calls = extend({'head': {}, 'pages': {}}, calls)
            element.removeAllChilds(obj)
            if(isArray(data.list) && data.list.length){
                if(isHash(data.link) && data.link.status)
                    element.appendChild(obj, {'h2': {'className': 'listtitle',
                        'innerText': capitalise(STATUSES[data.link.status]) + ' list'}})
                element.appendChild(obj, [{'table':
                    extend({className: 'tbl', cellSpacing: 0}, attrs.table)},[
                        {'thead': extend({className: 'thdtbl'}, attrs.head)},
                        this.buildHeader(data.head, data.link, calls.head),
                        {'tbody': attrs.body},
                        this.buildContent(data.list, data.pages.start)
                    ], this.buildPages(data, attrs.pages, calls.pages)
                ])
            }else{
                element.appendChild(obj, {'p': {'innerText': 'Nothing to display'}})
            }
        },

        buildHeader: function(data, link, callback){
            if(!isArray(data) || !data.length)
                return []
            var th = new Array()
            data.forEach(function(name){
                th.push.apply(th, this.getHeaderField(name, link, callback))
            }, this)
            return ['tr', th]
        },

        getHeaderField: function(name, link, callback){
            var func = this['header_'+name];
            if(!func)
                func = this.header_default;
            return func.call(this, name, link, callback);
        },

        header_air: function(name, link, callback) {
            return [{'th': {className: 'link'}}]
        },

        header_id: function(name, link, callback) {
            return [{'th': {className: 'id'}}, [
                {'a': {'innerText': '№', 'href': '/',
                'onclick': function(ev) {
                    return callback.func.call(callback.scope, {}, '', ev) }
                }}]]
        },

        header_default: function(name, link, callback) {
            var lname = this.longName(name)
            if(link.order == ((lname == 'title') ? undefined : lname))
                lname = '-' + lname
            var href = link.link.replace(/(.+)?\/sort\/\-?\w+\/?/gi, '$1'
                ) + 'sort/' + lname + '/'
            return [{'th': {className: name}}, [{'a': {
                'innerText': capitalise(this.headName(name)),
                'href': href, 'onclick': function(ev) {
                    return callback.func.call(callback.scope, link, lname, ev) }
                }}]]
        },


        buildContent: function(data, first){
            var rows = new Array()
            data.forEach(function(elem, i){
                var row = element.create('tr',
                    {className: (elem.air ? 'air a' : 'r') + elem.id}, [
                        {'td': {'id': 'link' + elem.id, className: 'link'}}, [
                            {'a': {className: 'cardurl', 'target': '_blank',
                                'href': '/card/'+elem.id+'/',
                                onclick: function(e){
                                    return Card.get(elem.id, e) }}}, [
                                {'img': {'src': '/static/arrow.png', 'alt': 'Go'}},
                            ]
                        ],
                        {'td': {'id': 'id' + elem.id, className: 'id',
                            onclick: function(e){
                                return utils.cnt('id', elem.id, e) },
                            innerText: Number(i) + first }},
                        ])
                rows.push(row)
                for(var column in elem){
                    if(column == 'air' || column == 'id') continue
                    var cell = this['cell_'+column]
                    if(!cell)
                        cell = this.cell_default
                    element.appendChild(row,
                            cell.call(this, elem.id, column, elem[column]))
                }
            }, this)
            return rows
        },

        buildPages: function(data, attrs, callback){
            var pages = data.pages
            if(!pages || !pages.items)
                return []
            var pnum = 0
            var pg = map(function (page){
                pnum++
                if(pages.current == pnum){
                    return element.create('span', {className: 'spanl', innerText: '[' + page + ']'})
                }else{
                    var href = data.link.link + pnum + '/'
                    return element.create('a', {innerText: page,
                        'onclick': function(e){ return callback.func.call(
                                callback.scope, data.link, pnum, e)
                            }, 'href': href })
                }
            }, pages.items, this)
            return element.create('div', attrs, pg)
        },

        cell_default: function(id, name, data){
            return {'td': {'id': name + id, className: name,
                onclick: function(e){ return utils.cnt(name, id, e) },
                innerText: encd(data) }}
        },

        cell_title: function(id, name, data){
            var c = this.cell_default(id, name, data)
            c = element.create('td', c.td)
            popup.add(c)
            return c
        }
    }
})

