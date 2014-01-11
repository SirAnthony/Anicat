require.config({
    paths: {
        base: 'base',
        catalog: 'catalog',
        plugins: 'plugins',
        tests: 'tests'
    },
    //urlArgs: "bust=" + (new Date()).getTime()
});

function loadIf(cond, name){
	if (!cond)
		return;
	var module = require(name);
	module.init.apply(module);
}

// Start the main app logic.
require(['base/events', 'base/user', 'base/popup', 'base/storage',
	'catalog/search', 'catalog/statistics', 'catalog/card'],
	function (events, user, popup, storage, searcher, statistics, card) {
	'use strict';
	events.onload(user.init, this);
	events.onload(searcher.init, searcher);
	events.onload(popup.addToTable, popup);
	events.onload(statistics.init, statistics);
	events.onload(storage.init, storage);
	events.onload(card.init, card);
	events.onload(function(){
		loadIf(user.logined, 'catalog/add');
		loadIf(user.logined, 'catalog/edit');
    });
	events.onload(loadURIHash);
});
