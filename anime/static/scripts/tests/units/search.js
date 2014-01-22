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
        'show': function(){
            var search = filter(function(el){
                return /\/search\/$/g.test(el.href); },
                document.getElementsByTagName('a'))[0];
            if(!search)
                throw Error('Search not found.');
            search.click();
        },
        'submit_blank': function(){
            toggle(document.getElementById('srch'), 1);
            var input = document.getElementById('sin');
            input.value = '';
            input.nextSibling.click();
        },
        'submit': function(){
            toggle(document.getElementById('srch'), 1);
            var input = document.getElementById('sin');
            input.value = 'zaa';
            input.nextSibling.click();
        },
        'pages': function(){
            var pg = document.getElementById('srchpg');
            pg.lastChild.click();
        }
    }, {'pages': ['submit'], 'all': ['show', 'submit_blank', 'submit', 'pages']}, true)
})