

var filter = new (function(){

    this.init = function(){
        createScroll(document.getElementById('id_filter_genre_container'));
    }

    this.toggle = function(){
        toggle(document.getElementById('id_filter_container'));
    }

    this.clear = function(){
    }

    this.apply = function(){
        //var data =
    }

})();


addEvent(window, 'load', filter.init);
