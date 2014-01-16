require.config({
    paths: {
        base: 'base',
        catalog: 'catalog',
        lib: 'lib',
        tests: 'tests'
    },
    //urlArgs: "bust=" + (new Date()).getTime()
});


// Start the main app logic.
require([
	'base/events', 'base/user', 'base/popup',
    'base/storage', 'catalog/search', 'catalog/statistics',
    'catalog/card', 'catalog/filter', 'catalog/edit',
    'catalog/utils',
],
function (events, user, popup, storage, searcher, statistics,
    card, filter, edit, utils) {
	'use strict';

    var actions = [];

	function add_init(module, name, skip){
        if (skip)
            return;
        module = module || require(name);
        if (module.init)
            events.onload(module.init, module)
        actions.push([module, name])
	}

    events.onload(storage.init, storage);

    var modules = [
        [user, 'base/user'],
        [searcher, 'catalog/search'],
        [statistics, 'catalog/statistics'],
        [card, 'catalog/card'],
        [filter, 'catalog/filter'],
        [edit, 'catalog/edit'],
        [null, 'catalog/add', !user.logined],
        [popup, 'base/popup'],
        [utils, 'catalog/utils']
    ]

    modules.forEach(function(module){
        add_init.apply(this, module)
    })

    events.onload(function(){
        actions.forEach(function(elem){
            events.add_action.apply(events, elem);
        });
    })

    events.onload(utils.loadURI);
});
