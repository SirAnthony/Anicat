import * as express from "express";
import * as routes from "./routes/index";
import url = require('./url.js');
import config = require('../config.json');
var env = process.env;
var E = {};
export E;
E.html = __dirname+'/../html/'

E.init = function(){
    var urls : LinkData[] = url.init();
    var app = express();
    // Templates
    E.template = nunjucks.configure(E.html, {
        autoescape: true, express: app});
    routes.filters.init(E.template);
    // reverser.init(E.template);
    // Middlewares
    // app.use(cookie_parser());
    // app.use(body_parser());
    // app.use(csrf());
    // Views
    app.use('/static', express.static(E.html+'/static'));
    app.use(routes.wrapper);
    //routes.auth.init(app);
    urls.forEach((link: LinkData) => {
        app.use(url, routes.process.bind(null, link.renderer); });
    app.use(routes.default);
};

var app = E.init(app);
app.listen(env.PORT||config.port);
