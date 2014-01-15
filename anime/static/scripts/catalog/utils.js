/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Catalog utils
 *
 */

define(['catalog/list', 'catalog/search', 'base/ajax'],
function (list, searcher, ajax){

	var disabled_links = [
		new RegExp(/^\/search\//)
	]

	function disabled(target) {
		target = target || document.location.pathname
		for(var link in disabled_links)
			if(target.match(disabled_links[link]))
				return true;
		return false;
	}

	var hash_re = new RegExp('^/?(?:(?:search/(.*))|(?:(?:user/(\\d+)/)?show/(\\d+))?)/(?:sort/(-?\\w+)/)?(?:(\\d+)/?)?');


	//######################## URI Hash
	function parseURIHash(string){
		string = string.replace(/http:\/\/[^\/]+/g,'').replace(/^#?/g, '')
		var match = hash_re.exec(string)
		if(!match)
			return
		var request = 'list'
		var ret = {}
		var processor = list.processor
		if(match[1]){
			request = 'search'
			ret['string'] = match[1]
			processor = searcher.processor
		}else if(match[2] && !isUndef(match[3])){
			ret = extend(ret, {'user': match[2], 'status': match[3]})
		}
		var aret = extend(ret, {'order': match[4], 'page': match[5]})
		return [request, aret, processor]
	}

	function loadURIHash(string){
		if(disabled())
			return true
		if(!document.getElementById('dvid') && !searcher.loaded)
			return true
		var link = parseURIHash(string || document.location.hash)
		if(!link || !link[0])
			return false
		ajax.load.apply(ajax, link)
		return false
	}

	function load_this_href(event) {
		return loadURIHash(event.currentTarget.href);
	}

	//######################## Display mode
	function set_status(){
		var mode = this.value;
		if(!isNumber(mode))
			return;
		loadURIHash(mode < 0 ? '/' : '/show/' + mode + '/');
	}

	return {
		parseURI: parseURIHash,
		loadURI: loadURIHash,
		load_href: load_this_href,
		view_status: set_status
	}

})