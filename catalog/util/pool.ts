
export var E = {};

function chainer(opts, next){
    var callback, ctx, args = [];
    if (typeof opts == 'function')
        callback = opts;
    if (Array.isArray(opts)){
        callback = opts[1];
        ctx = opts[0];
        args.push.apply(args, opts.slice(2));
    }
    if (ctx && typeof callback == "string")
        callback = ctx[callback];
    return function(){
        args.push.apply(args, arguments);
        if (typeof next != 'undefined')
            args.push(next);
        E.add(function(pcontinue){
            pcontinue();
            callback.apply(ctx, args);
        });
    };
}

E.chain = function(array, resolver){
    var func = resolver;
    for (var i = array.length - 1; i >= 0; --i)
        func = chainer(array[i], func);
    E.add(function(pcontinue){
        pcontinue();
        func();
    });
};

E.pool = function(){
    var max_running = 30;
    var running = 0;
    var pool = [];

    function resolver(){
        running--;
        process.nextTick(run);
        return Array.prototype.slice(arguments);
    }

    function run(){
        if (pool.length <= 0)
            return;
    	if (running > max_running)
            return process.nextTick(run);
    	for (var i=running; i<max_running; ++i){
            var callback = pool.shift();
            if (!callback)
                return;
            running++;
            callback(resolver);
    	}
    }

    this.add = function(callback){
        pool.push(callback);
        process.nextTick(run);
    };
};

E.Pool = new E.pool();
E.add = E.Pool.add;
