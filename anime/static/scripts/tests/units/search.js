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

    return describe('search', function() {

        afterEach(utils.processor_setter())

        describe('show', function() {
            it('should pass', function() {
                var search = filter(function(el){
                    return /\/search\/$/g.test(el.href) },
                    document.getElementsByTagName('a'))[0]
                if(!search)
                    throw Error('Search not found.')
                search.click()
            })
        })
        describe('submit_blank', function(){
            it('should pass', function() {
                toggle(document.getElementById('srch'), 1)
                var input = document.getElementById('sin')
                input.value = ''
                input.nextSibling.click()
                var t = document.getElementById('srchres').firstChild.innerText
                t.should.be.exactly('Query must consist of at least 3 characters.')
            })
        })

        describe('submit', function(){
            utils.it(function() {
                toggle(document.getElementById('srch'), 1)
                var input = document.getElementById('sin')
                input.value = 'nar'
                input.nextSibling.click()
            }, function() {
                var srchres = document.getElementById('srchres')
                srchres.firstChild.id.should.equal('srchtbl')
                srchres.lastChild.id.should.equal('srchpg')
            })
        })
        describe('pages', function(){
            utils.it(function() {
                var pg = document.getElementById('srchpg')
                pg.lastChild.click()
            }, function() {
                var srchres = document.getElementById('srchres')
                var txt = srchres.firstChild.lastChild.firstChild.children[1].innerText
                txt.should.equal('21')
            })

        })
    })
})