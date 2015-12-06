
var env = process.env;
export var E = {};
E.MONGO_HOST = env.MONGO_HOST||'localhost';
E.MONGO_PORT = env.MONGO_PORT||'27017'
E.getItems = function(filter, callback: (items: Item[]) => void){
    E.records.find(filter).toArray(callback);
});

E.init = function(resolve, reject){
    E.server = new mongodb.Server(E.MONGO_HOST, E.MONGO_PORT, {
        auto_reconnect: true});
    E.db = new mongodb.Db(E.DB_NAME, E.server, {w: 1});
    pool.chain([E.db, 'open'], (err, db, next) => {
        if (err)
            return reject(err);
        db.collection('records', next);
    }, (err, records) => {
        if (err)
            return reject(err);
        E.records = records;
        return resolve();
    }]);
}


