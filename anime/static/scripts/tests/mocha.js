/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Mocha test runner
 *
 */

define(['base/events'], function(events){

	var tests = []
	var avaliable_tests = ['cnt'] // ['add', 'card', 'cnt', 'filter', 'main',
			//'search', 'statistics', 'user']
	var tests_fullpath = map(function(name) {
				return 'tests/units/' + name }, avaliable_tests)

	avaliable_tests.forEach(function(testname){
		if(tests[testname])
			console.log('Multiple tests with name ' + testname + 'loaded')
		require(tests_fullpath, function(){
			for(var i = 0; i < arguments.length; ++i)
				tests[avaliable_tests[i]] = arguments[i] })
	})

	return {
		init: function() {
			mocha.setup('bdd')
			var c_bt = document.getElementById('test_c_bt')
			if(!c_bt)
				element.appendChild(document.body,
					c_bt = element.create('input', {'value': 'Next test',
					'id': 'test_c_bt', 'style': {'position': 'fixed',
					'right': '500px', 'bottom': '0px'},  'type': 'button'}))
			var self = this;
			events.add(c_bt, 'click', function(e) {	self.run() })
		},

		run: function() {
			mocha.run()
		}
	}
})

