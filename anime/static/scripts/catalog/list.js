/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * List views
 *
 */

define(['base/message', 'catalog/view', 'catalog/table'],
	function(message, View, table){

	var List = View({
		prepare: function() {},
		create: function(data) {
			if (!this.prepare(data))
				return
			var page = (data.pages.current > 1) ? data.pages.current + '/' : '';
			document.location.hash = data.link.link + page;
			table.build(this.target, {'table': {'id': this.table_id},
				'body': {'id': this.body_id}, 'pages': {'id': this.page_id}}, data, {
					'head': {'func': this.sortCall, 'scope': this},
					'pages': {'func': this.pageCall, 'scope': this}})
		},
		sortCall: function(link, order, event){
			return this.load(extend(link, {'order': order,
					'link': undefined, 'page': undefined}));
		},
		pageCall: function(link, number, event){
			return this.load(extend(link, {'page': number, 'link': undefined}));
		}
	})

	var Table = new List({
		link: 'list',
		table_id: 'tbl',
		body_id: 'tbdid',
		page_id: 'pg',
		prepare: function() {
			this.target = document.getElementById('dvid')
			element.remove(document.getElementById('pg'))
			return true
		}
	}, {
		'list': function(resp){
			message.hide()
			if(!resp.status)
				throw Error(resp.text)
			this.create(resp.text)
		}
	})

	var Search = new List({
		link: 'search',
		table_id: 'srchtbl',
		body_id: 'srchbody',
		page_id: 'srchpg',
		init: function() {
			this.sobj = document.getElementById('srch')
			this.target = document.getElementById('srchres')
			this.input = document.getElementById('sin')
			this.loaded = (this.sobj && this.target && this.input)
		},
		toggle: function(){
			if(!this.loaded)
				return true
			if(toggle(this.sobj))
				this.input.focus()
			return false
		},
		send: function(page, e){
			if(!this.loaded)
				return true
			page = page || 1
			if(this.input.value.length < 3){
				element.removeAllChilds(this.target)
				element.appendChild(this.target, [{'p': {
					innerText: 'Query must consist of at least 3 characters.'}}])
			}else{
				var text = this.input.value.toLowerCase()
				message.toEventPosition(e)
				this.load({'string': text, 'page': page, 'link': void 0})
			}
			return false
		},
		prepare: function(data){
			if(!this.loaded)
				return false
			toggle(this.sobj, true);
			if (!data.list.length) {
				element.removeAllChilds(this.target)
				element.appendChild(this.target, [{'p': {innerText: 'Nothing found.'}}])
				return false
			}
			return true
		}

	}, {
		'search': function(resp){
			message.hide()
			if(!resp.status)
				throw Error(resp.text)
			this.create(resp.text)
		}
	})

	return {
		table: Table,
		search: Search
	}
});