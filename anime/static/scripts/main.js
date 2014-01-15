require.config({
    paths: {
        base: 'base',
        catalog: 'catalog',
        plugins: 'plugins',
        tests: 'tests'
    },
    //urlArgs: "bust=" + (new Date()).getTime()
});


// Start the main app logic.
require([
	'base/events', 'base/user', 'base/popup',
    'base/storage', 'catalog/search', 'catalog/statistics',
    'catalog/card', 'catalog/utils'
],
function (events, user, popup, storage, searcher, statistics, card, utils) {
	'use strict';

    var actions = [];

	function add_init(module, name){
		events.onload(module.init, module);
        actions.push([module, name]);
	}

	function loadIf(cond, name){
		if (!cond)
			return;
		var module = require(name);
		module.init.apply(module);
        actions.push([module, name]);
	}

    events.onload(storage.init, storage);
	add_init(user, 'base/user');
	add_init(searcher, 'catalog/search');
	add_init(statistics, 'catalog/statistics');
	add_init(card, 'catalog/card');
	events.onload(function(){
		loadIf(user.logined, 'catalog/add');
		loadIf(user.logined, 'catalog/edit');
    });
    events.onload(popup.addToTable, popup);
    actions.push([utils, 'catalog/utils']);

    events.onload(function(){
        actions.forEach(function(elem){
            events.add_action.apply(events, elem);
        });
    })

    events.onload(utils.loadURI);
});
