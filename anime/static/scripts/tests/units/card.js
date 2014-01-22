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
        'open': function(){
            var l = getElementsByClassName('link', document, 'td')[0]
            l.firstChild.click()
        },
        'edit': function(){
            var card = document.getElementById('card')
            var elements = getElementsByClassName('right', card, 'a')
            elements.forEach(function(elem){
                if(elem.innerText != 'Submit new')
                    elem.click()
            })
        },
        'send': function(){
            var card = document.getElementById('card')
            var elements = getElementsByClassName('right', card, 'a')
            elements.forEach(function(elem){
                if(elem.innerText != 'Save')
                    elem.click()
            })
        },
        'cancel': function(){
            var card = document.getElementById('card');
            var elements = getElementsByClassName('right', card, 'a');
            elements.forEach(function(elem){
                if(elem.innerText != 'Cancel')
                    elem.click()
            })
        },

    }, {'edit': ['open'], 'send': ['edit'], 'cancel': ['edit'],
        'all': ['edit', 5000, 'send', 5000, 'cancel']});
})