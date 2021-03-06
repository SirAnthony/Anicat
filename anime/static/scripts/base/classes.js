/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Classes interface
 *
 */

define(function(){
	return {
		'has': function(ele, cls){
			if(!ele.className)
				return;
			return ele.className.match(isString(cls) ?
				new RegExp('(\\s|^)'+cls+'(\\s|$)') : cls);
		},

		'add': function(ele, cls){
			if(!this.has(ele, cls))
				ele.className += ' '+cls;
		},

		'remove': function(ele, cls){
			if (this.has(ele, cls)){
				var reg = new RegExp('(\\s|^)'+cls+'(\\s|$)');
				ele.className = ele.className.replace(reg,'');
			}
		},

		'getElements': function(searchClass, node, tag) {
			node = node || document;
			tag = tag || '*';
			var self = this;
			var re = RegExp('(\\s|^)'+searchClass+'(\\s|$)');
			return filter(function(el){ self.has(el, re); },
				node.getElementsByTagName(tag));
		}
	};
});