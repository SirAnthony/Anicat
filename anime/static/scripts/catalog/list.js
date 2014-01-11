/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * List builders module
 *
 */

define(['base/message', 'base/ajax', 'base/request_processor', 'catalog/table'],
	function(message, ajax, RequestProcessor, table){

    var self = {
        create: function(data){
            var dvid = document.getElementById('dvid');
            var page = (data.pages.current > 1) ? data.pages.current + '/' : '';
            document.location.hash = data.link.link + page;
            element.remove(document.getElementById('pg'));
            table.build(dvid, {'table': {'id': 'tbl'},
                'body': {'id': 'tbdid'}, 'pages': {'id': 'pg'}}, data, {
                    'head': {'func': this.sortCall, 'scope': this},
                    'pages': {'func': this.pageCall, 'scope': this}});
        },

        sortCall: function(link, order, event){
            ajax.load('list', extend(link, {'order': order,
                    'link': undefined, 'page': undefined}), this.processor);
            return false;
        },

        pageCall: function(link, number, event){
            ajax.load('list', extend(link, {'page': number,
                    'link': undefined}), this.processor);
            return false;
        }
    };

    self.processor = new RequestProcessor({
        'list': function(resp){
            message.hide();
            if(!resp.status)
                throw Error(resp.text);
            this.create(resp.text);
        }
    }, self);

    return self;
});