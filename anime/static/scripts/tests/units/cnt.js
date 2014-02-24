/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Javascript tests
 *
 */

define(['tests/utils'], function (utils){

	return describe('cnt', function() {

		afterEach(utils.processor_setter())

		describe('link', function() {
			utils.it(function() {
				var l = getElementsByClassName('link', document, 'td')[0]
				l.firstChild.click()
			})
		})

		describe('id', function() {
			utils.it(function() {
				getElementsByClassName('id', document, 'td')[0].click()
			})
		})

		describe('title', function() {
			utils.it(function() {
				getElementsByClassName('title', document, 'td')[0].click()
			})
		})

		describe('episodes', function() {
			utils.it(function() {
				getElementsByClassName('episodes', document, 'td')[0].click()
			})
		})

		describe('episodes', function() {
			utils.it(function() {
				getElementsByClassName('episodes', document, 'td')[0].click()
			})
		})

		describe('release', function() {
            utils.it(function() {
				getElementsByClassName('release', document, 'td')[0].click()
			})
		})

		describe('type', function() {
			utils.it(function() {
				getElementsByClassName('type', document, 'td')[0].click()
			})
		})

		describe('id_send', function() {
			utils.it(function() {
                    getElementsByClassName('id', document, 'td')[0].click()
                }, function() {
					var state = document.getElementById('id_state')
					var selected = element.getSelected(state)
					var new_sel = selected
					while(new_sel == selected)
						new_sel = Math.floor((Math.random() * state.options.length) + 1);
					state.options[new_sel].selected = true
					state.onchange()
			})
		})
	})
})
