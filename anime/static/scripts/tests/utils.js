/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Javascript tests utils
 *
 */

define(['base/request_processor', 'lib/should.min'], function (RequestProcessor, should){

	function set_processor(done, func){
		RequestProcessor.prototype._parsed = function() {
			RequestProcessor.prototype._parsed = function() {}
			func && func()
			done()
		}
	}

	function processor_setter(func) {
		func = func || function() {}
		return function() {
			RequestProcessor.prototype._parsed = func
		}
	}

	function mocha_it(call, after, condition) {
		condition = condition || 'should pass'
		it(condition, function(done){
			set_processor(done, after)
			call()
		})
	}

	return {
		should: should,
		it: mocha_it,
		set_processor: set_processor,
		processor_setter: processor_setter
	}
})