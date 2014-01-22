/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Javascript tests
 *
 */

define(['tests/runner'], function (TestRunner){
	return new TestRunner({
        'page': function(){
            var pager = document.getElementById('pg')
            pager.getElementsByTagName('a')[0].click()
        },
        'sort': function(){
            var th = getElementsByClassName('episodes', document, 'th')[0]
            th.firstChild.click()
        },
        'rsort': function(){
            var th = getElementsByClassName('episodes', document, 'th')[0]
            th.firstChild.click()
        }
    }, {'rsort': ['sort'], 'all': ['rsort', 'page', 'sort']}, true)
})