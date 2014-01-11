/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Javascript tests status manager
 *
 */

 define(['base/events'], function(events){
    this.statuses = {'done': -1, 'ready': 0, 'running': 1};
    this.status = this.statuses.ready;
    this.sinput = null;

    this.init = function(){
		this.sinput = document.getElementById('test_status');
        if(!this.sinput){
            this.sinput = element.create('input', {'id': 'test_status', 'type': 'text'});
            element.appendChild(document.body, this.sinput);
        }
        this.display();
    };

    this.take = function(){
        this.status++;
        this.display();
    };

    this.put = function(){
        this.status--;
        this.display();
    };

    this.display = function(){
        this.sinput.value = this.status;
    };

    events.onload(this.init, this);
});