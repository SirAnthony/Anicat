/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Cookies interface
 *
 */

define(function(){

	return {
		'set': function(name, value, expires, path, domain, secure){
			document.cookie = name + "=" + escape(value) +
			((expires) ? "; expires=" + expires : "") +
			((path) ? "; path=" + path : "") +
			((domain) ? "; domain=" + domain : "") +
			((secure) ? "; secure" : "");
		},

		'del': function(name, path, domain){
			document.cookie = name + "=" +
			((path) ? "; path=" + path : "; path=/") +
			((domain) ? "; domain=" + domain : "") +
			"; expires=Thu, 01-Jan-70 00:00:01 GMT;";
		},

		'get': function(name){
			var cookie = " " + document.cookie;
			var search = " " + name + "=";
			var setStr = null;
			if (cookie.length > 0) {
				var offset = cookie.indexOf(search);
				if (offset != -1) {
					offset += search.length;
					var end = cookie.indexOf(";", offset);
					if (end == -1)
						end = cookie.length;
					setStr = unescape(cookie.substring(offset, end));
				}
			}
			return setStr;
		}
	};
});