import * from mongodb

var env = process.env;
export var E = {};
E.MONGO_HOST = env.MONGO_HOST||'localhost';
E.MONGO_PORT = env.MONGO_PORT||'27017'

function check_err(name, db, rej, res, qw){
    return (err, data) => {
        if (!err)
            return res(data);
        return rej('mongodb.'+name+' '+db.name+
                '('+JSON.stringify(qw)+'): '+err);
    };
}

function promise(db, method){
    var argv = [];
    for (var i=2; i<arguments.length; i++)
        argv.push(arguments[i];
    return new Promise((res, rej) => {
        var args = argv.slice();
        args.push(check_err(method, db, rej, res, argv));
        db.collection[method].apply(db.collection, args);
    };
}

E.find_all = function(db, selector, opt){
    selector = selector||{};
    opt = opt||{};
    console.debug('mongodb find_all '+db.name+' '+
        JSON.stringify(selector));
    var cursor = db.collection.find(selector, opt.projection);
    if (opt.sort)
        cursor.sort(opt.sort);
    if (opt.limit)
        cursor.limit(opt.limit);
    if (opt.skip)
        cursor.skip(opt.skip);
    return new Promise((res, rej) => {
        cursor.toArray(check_err('find_all', db, rej,
            res, selector));
    };
};

E.find_one = function(db, selector, sort){
    selector = selector||{};
    var opt = {sort: sort};
    return promise(db, 'findOne', selector, opt);
};

E.save = function(db, obj){
    return promise(db, 'save', obj); };

E.insert = function(db, obj){
    return promise(db, 'insert', obj); };

E.connect = function(conn, db_name, collection){
    var timeout = 90000;
    var sock_timeout = 24*3600000;
    var url = 'mongodb://'+conn.host+':'+conn.port+'/'+db_name;
    var config = {
        server: {socketOptions: {connectTimeoutMs: timeout,
            socketTimeoutMS: sock_timeout, keepAlive: 1},
            auto_reconnect: true},
        replSet: {socketOptions: {connectTimeoutMS: timeout,
            socketTimeoutMS: sock_timeout, keepAlive: 1}},
        db: {},
    };
    var conn_args = [url, config];
    var db = {name: db_name+'.'+collection};
    return new Promise((res, rej) => {
        pool.chain([mongodb, 'connect', conn_args],
        check_err('connect.db', db, rej, (_db, next) => {
            db.db = _db;
            _db.serverConfig.on('close', (err) => { console.debug(err) });
            next();
        }), [ret.db, 'collection', collection],
        check_err('connect.coll', db, rej, (coll) => {
            console.log('opened collection '+collection);
            db.collection = coll;
            res(db);
        }));
    });
};

E.close = function(db){
    return new Promise((res, rej) => { db.db.close(res); }); };

