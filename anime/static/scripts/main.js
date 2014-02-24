require.config({
    paths: {
        base: 'base',
        catalog: 'catalog',
        lib: 'lib',
        tests: 'tests',
        calendar: 'lib/calendar'
    },
    shim: {
        calendar: {
            exports: 'Calendar'
        }
    }
    //urlArgs: "bust=" + (new Date()).getTime()
});

var DEBUG = true

// Start the main app logic.
require([
	'base/events', 'base/user', 'base/popup',
    'base/storage', 'catalog/search', 'catalog/statistics',
    'catalog/card', 'catalog/filter', 'catalog/edit',
    'catalog/utils', 'catalog/datetime'
],
function (events, user, popup, storage, searcher, statistics,
          card, filter, edit, utils, datetime) {

	'use strict';

	function init_module(module, name, skip){
        if (skip && (!isFunction(skip) || skip()))
            return;

        if (module) {
            if (module.init)
                module.init()
            events.add_action(module, name)
        } else {
            require([name], function(mod){
                init_module(mod, name)
            })
        }
	}

    events.onload(storage.init, storage);

    var modules = [
        [user, 'base/user'],
        [searcher, 'catalog/search'],
        [statistics, 'catalog/statistics'],
        [card, 'catalog/card'],
        [filter, 'catalog/filter'],
        [edit, 'catalog/edit'],
        [null, 'catalog/add', function() { return !user.logined }],
        [popup, 'base/popup'],
        [utils, 'catalog/utils'],
        [datetime, 'catalog/datetime'],
        [null, 'tests/mocha', function() { return !DEBUG }]
    ]

    events.onload(function(){
        modules.forEach(function(elem){ init_module.apply(null, elem) })
    })

    if (!DEBUG)
        events.onload(utils.loadURI)
});
