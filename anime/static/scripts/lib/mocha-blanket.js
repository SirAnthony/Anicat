(function() {

    if(!mocha) {
        throw new Exception("mocha library does not exist in global namespace!");
    }


    /*
     * Mocha Events:
     *
     *   - `start`  execution started
     *   - `end`  execution complete
     *   - `suite`  (suite) test suite execution started
     *   - `suite end`  (suite) all tests (and sub-suites) have finished
     *   - `test`  (test) test execution started
     *   - `test end`  (test) test completed
     *   - `hook`  (hook) hook execution started
     *   - `hook end`  (hook) hook complete
     *   - `pass`  (test) test passed
     *   - `fail`  (test, err) test failed
     *
     */

    var OriginalReporter = mocha._reporter;

    var BlanketReporter = function(runner) {
            runner.on('start', function() {
                blanket.setupCoverage();
            });

            runner.on('end', function() {
                blanket.onTestsDone();
            });

            runner.on('suite', function() {
                blanket.onModuleStart();
            });

            runner.on('test', function() {
                blanket.onTestStart();
            });

            runner.on('test end', function(test) {
                blanket.onTestDone(test.parent.tests.length, test.state === 'passed');
            });

            element.appendChild(document.body, [{'div': {'id': 'urinal', 'style':
                {'position': 'absolute', 'top': '30px', 'right': '0px' }}}, [
                {'input': {'type': 'button', 'value': 'Tests',
                    'onclick': function() { toggle(this.nextSibling) }}},
                {'div': {'id': 'mocha', 'style': {'background': '#fff', 'margin':
                '0px', 'border': 'solid 1px #ccc'}}},
                {'div': {'id': 'messages'}}, {'div': {'id': 'fixtures'}},
                ]])

            // NOTE: this is an instance of BlanketReporter
            OriginalReporter.apply(this, arguments);
        };


    BlanketReporter.prototype = mocha._reporter.prototype;
    mocha.reporter(BlanketReporter);

    var oldRun = mocha.run,
        oldCallback = null;

    mocha.run = function (finishCallback) {
      oldCallback = finishCallback;
      console.log("waiting for blanket...");
    };
    blanket.beforeStartTestRunner({
        callback: function(){
            if (!blanket.options("existingRequireJS")){
                oldRun(oldCallback);
            }
            mocha.run = oldRun;
        }
    });
})();
