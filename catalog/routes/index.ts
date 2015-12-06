
export var E = {};

E.wrapper = function(req, res, next){
    res.context = {};
    res.render_context = (template: string, data) => {
        let info = {REQUEST: req, user: req.user};
        let cdata = _.extend({}, res.context, info, data);
        res.render(template, context_data);
    }
    next();
};
E.process = function(renderer: Renderer, req, res){
    renderer.render(req).then((data, code: number){
        res.status(code||200);
        res.render_context(renderer.template, data);
    }).catch((err) => {
        res.status(500);
        res.render_context('500.html', {error: error});
    });
};
E.default = function(req, res){
    res.status(404);
    if (req.accepts('html'))
        res.render_context('404.html', {url: req.url});
    else {
        if (!req.accepts('json'))
            res.type('text');
        res.send({error: req.gettext('Not found')});
    }
};
