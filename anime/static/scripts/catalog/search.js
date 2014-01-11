/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Search module
 *
 */

//######################## Search
define(['base/message', 'base/events', 'base/ajax', 'base/request_processor',
    'catalog/table'],
	function(message, events, ajax, RequestProcessor, table){

    var self = {
        init: function(){
            this.sobj = document.getElementById('srch');
            this.result = document.getElementById('srchres');
            this.input = document.getElementById('sin'); //это как-то по другому нужно.
            this.loaded = (this.sobj && this.result && this.input);
        },

        toggle: function(){
            if(!this.loaded) return;
            if(toggle(this.sobj))
                this.input.focus();
        },

        send: function(page, e){
            if(!this.loaded) return;
            if(!page) page = 1;
            if(this.input.value.length < 3){
                element.removeAllChilds(this.result);
                element.appendChild(this.result, [{'p': {
                    innerText: 'Query must consist of at least 3 characters.'}}]);
            }else{
                var text = this.input.value.toLowerCase();
                message.toEventPosition(e);
                this.loadCall({'string': text}, page);
            }
        },

        loadCall: function(link, number, event){
            ajax.load('search', extend(link, {'page': number,
                    'link': undefined}), this.processor);
            return false;
        },

        putResult: function(rs){
            if(!this.loaded) return;
            message.hide();
            element.removeAllChilds(this.result);
            if(!rs.list.length){
               element.appendChild(this.result, [{'p': {innerText: 'Nothing found.'}}]);
            }else{
                var page = (rs.pages.current > 1) ? rs.pages.current + '/' : '';
                document.location.hash = rs.link.link + page;
                toggle(this.sobj, true);
                table.build(this.result, {'table': {'id': 'srchtbl'},
                    'pages': {'id': 'srchpg'}}, rs,
                    {'pages': {'func': this.loadCall, 'scope': this}});
            }
        }
    };

    self.processor = new RequestProcessor({'search': function(resp){
                            this.putResult(resp.text); }}, this);

    return self;
});