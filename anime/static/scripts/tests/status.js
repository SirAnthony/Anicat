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

    var _statuses = {'done': -1, 'ready': 0, 'running': 1}
    var _sinput = null
    var _status = _statuses.ready

    return {
        statuses: _statuses,

        init: function(){
            _sinput = _sinput || document.getElementById('test_status')
            if(!_sinput){
                _sinput = element.create('input', {'id': 'test_status', 'type': 'text'})
                element.appendChild(document.body, _sinput)
            }
            this.display()
        },

        status: function(){
            return _status
        },

        take: function(){
            _status++
            this.display()
        },

        put: function(){
            _status--
            this.display()
        },

        display: function(){
            _sinput.value = _status
        }
    }
})