
import * as when from 'when';
import url = require('urlreverser');

export class Router {
    constructor(opt){
        this.opt = opt; }
    render(req){ return when({}); }
    params(req, defaults){
        var data = {};
        defaults = defaults||{};
        var params = this.opt.url_params||[];
        params.forEach((name) => {
            var param = req.param(name, defaults[name]);
            if (param)
                data[name] = param;
        });
        return data;
    }
    reverse(req, params){
        var name = this.options.url;
        params = params||this.get_params(req);
        return url.reverse(name, params);
    }
}
