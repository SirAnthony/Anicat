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
                        this.buildContent(data.list, data.head, data.pages.start)
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
            var func = this['header_'+name] || this.header_default
            return func.call(this, name, link, callback)
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


        buildContent: function(data, head, first){
            var rows = new Array()
            data.forEach(function(elem, i){
                var row = element.create('tr',
                    {className: (elem.air ? 'air a' : 'r') + elem.id})
                head.forEach(function(column){
                    element.appendChild(row, this.getCell(elem.id, column,
                        column == 'id' ? Number(i) + first : elem[column]))
                }, this)
                rows.push(row)
            }, this)
            return rows
        },

        buildPages: function(data, attrs, callback){
            var pages = data.pages
            if(!pages || !pages.items)
                return []
            var pg = map(function (page, num){
                return this.getPage(page, data.link, num + 1, pages.current, callback)
            }, pages.items, this)
            return element.create('div', attrs, pg)
        },

        getPage: function(page, link, num, current, callback) {
            if (num == current)
                return {'span': {className: 'spanl', innerText: '[' + page + ']'}}
            return {'a': {innerText: page, onclick: function(e){
                    return callback.func.call(callback.scope, link, num, e)
                }, 'href': link.link + num + '/' }}
        },

        getCell: function(id, name, data){
            var cell = this['cell_'+name] || this.cell_default
            return cell.call(this, id, name, data)
        },

        cell_default: function(id, name, data){
            return {'td': {'id': name + id, className: name,
                onclick: function(e){ return utils.cnt(name, id, e) },
                innerText: encd(data) }}
        },

        cell_air: function(id, name, data){
            return element.create('td', {'id': 'link' + id, className: 'link'}, [
                    {'a': {className: 'cardurl', 'target': '_blank',
                    'href': '/card/' + id + '/',
                    onclick: function(e){ return Card.get(id, e) }}}, [
                        {'img': {'src': '/static/arrow.png', 'alt': 'Go'}}]])
        },

        cell_id: function(id, name, data){
            return {'td': {'id': 'id' + id, className: 'id',
                    onclick: function(e){ return utils.cnt('id', id, e) },
                    innerText: data }}
        },


        cell_title: function(id, name, data){
            var c = this.cell_default(id, name, data)
            c = element.create('td', c.td)
            popup.add(c)
            return c
        }
    }
})

