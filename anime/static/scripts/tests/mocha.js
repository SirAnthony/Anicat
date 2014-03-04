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
	var avaliable_tests = ['cnt', 'main', 'search']
		// ['add', 'card', 'cnt', 'filter',
		//, 'statistics', 'user']
	var tests_fullpath = map(function(name) {
				return 'tests/units/' + name }, avaliable_tests)

	avaliable_tests.forEach(function(testname){
		if(tests[testname])
			console.log('Multiple tests with name ' + testname + 'loaded')
		require(tests_fullpath, function(){
			for(var i = 0; i < arguments.length; ++i)
				tests[avaliable_tests[i]] = arguments[i] })
	})

	if (!document.getElementById('urinal'))
		element.appendChild(document.body, [{'div': {'id': 'urinal', 'style':
			{'position': 'absolute', 'top': '30px', 'right': '0px' }}}, [
			{'input': {'type': 'button', 'value': 'Run tests', 'id': 'test_c_bt'}},
			{'input': {'type': 'button', 'value': 'Results',
				onclick: function() { toggle(this.nextSibling) }}},
			{'div': {'id': 'mocha', 'style': {'background': '#fff', 'margin':
			'0px', 'border': 'solid 1px #ccc', 'display': 'none'}}},
			{'div': {'id': 'messages'}}, {'div': {'id': 'fixtures'}},
		]])

	return {
		init: function() {
			mocha.setup('bdd')
			var self = this;
			events.add(document.getElementById('test_c_bt'),
					'click', function(e) {	self.run() })
		},

		run: function() {
			mocha.run()
			toggle(document.getElementById('mocha'), 1)
		}
	}
})

