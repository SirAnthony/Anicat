
var user_storage = new (function(){

	this.loaded = false;

	this.init = function(){
		user_storage.loaded = !isUndef(localStorage);
		updateListFromStorage();
		this.enabled = user_storage.getItem('enabled') ? true : false;
	}

	this.enable = function(){
		if(!this.loaded) return;
		this.enabled = true;
		this.addItem('enabled', true);
	}
	
	this.disable = function(){
		this.enabled = false;
		this.removeItem('enabled');
	}

	this.getKeys = function(subkey){
		if(!this.loaded) return;
		var keys = new Array();
		if(subkey)
			var re = new RegExp('^'+subkey+'\\.');
		for(var i=0; i<localStorage.length; i++){
			var key = localStorage.key(i);
			if(/^anicat\./.test(key)){
				key = key.replace(/^anicat\./, '');
				if(!subkey || (re && re.test(key))){
					if(re)
						key = key.replace(re, '')
					keys.push(key);
				}
			}
		}
		return keys;
	}

	this.addItem = function(key, value){
		if(!this.loaded || !this.enabled) return true;
		localStorage["anicat." + key] = value;
	}

	this.getItem = function(key){
		if(!this.loaded) return;
		return localStorage["anicat." + key];
	}

	this.removeItem = function(key){
		if(!this.loaded || !this.enabled) return true;
		localStorage.removeItem("anicat." + key);
	}

	this.exist = function(key){
		if(!this.loaded || !this.enabled) return false;
		return !isUndef(localStorage["anicat." + key]);
	}

})();

function updateListFromStorage(){
	if(!user_storage.loaded) return;
	var keys = user_storage.getKeys('list');
	var colors = {};
	var rules = new Array();
	for(var i in keys){
		if(+keys[i] != keys[i])
			continue;
		var stat = user_storage.getItem('list.' + keys[i]);
		if(!colors[stat]){
			var rs = getStylesheetRule('.rs'+stat, 'background-color');
			rs = rs ? rs : '#FFF';
			var as = getStylesheetRule('.as'+stat, 'background-color');
			as = as ? as : '#FFF';
			colors[stat] = [rs, as];
		}
		rules.push(['.r'+keys[i], ['background-color', colors[stat][0]]])
		rules.push(['.a'+keys[i], ['background-color', colors[stat][1]]])
	}
	if(rules.length)
		addStylesheetRules(rules);
}

addEvent(window, 'load', user_storage.init);