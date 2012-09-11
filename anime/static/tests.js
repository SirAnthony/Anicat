
var tests = new (function(){

    this.test_message = function(){
        message.getMenu();
        message.create('');
    }

})();

addEvent(window, 'load', function(){

    var testname = document.location.hash.match(/^#test\/(\w+)/)[1];
    if(!testname)
        return;

    var test = tests['test_'+testname];
    if(!test)
        return;
    else
        test();

});



