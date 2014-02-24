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

    return describe('card', function() {

        afterEach(utils.processor_setter())

        describe('page', function() {
            utils.it(function() {
                var pager = document.getElementById('pg')
                pager.getElementsByTagName('a')[0].click()
            })
        })

        describe('sort', function() {
            utils.it(function() {
                var th = getElementsByClassName('episodes', document, 'th')[0]
                th.firstChild.click()
            })
        })

        describe('rsort', function(){
            utils.it(function() {
                var th = getElementsByClassName('episodes', document, 'th')[0]
                th.firstChild.click()
            })
        })
    })
})