
var createScroll = function(){ throw 'Scroller not loaded'; };


addEvent(window, 'load', function() {

    var BROWSER_IS_IE7, BROWSER_SCROLLBAR_WIDTH, DOMSCROLL,
        DOWN, DRAG, KEYDOWN, KEYS, KEYSTATES, KEYUP, MOUSEDOWN,
        MOUSEMOVE, MOUSEUP, MOUSEWHEEL, NanoScroll, PANEDOWN, RESIZE,
        SCROLL, SCROLLBAR, TOUCHMOVE, UP, WHEEL, defaults, getBrowserScrollbarWidth;
    defaults = {
        paneClass: 'pane',
        sliderClass: 'slider',
        contentClass: 'content',
        scrollContentClass: 'scrollcontent',
        iOSNativeScrolling: false,
        preventPageScrolling: false,
        disableResize: false,
        alwaysVisible: false,
        flashDelay: 1500,
        sliderMinHeight: 20,
        sliderMaxHeight: null
    };
    SCROLLBAR = 'scrollbar';
    SCROLL = 'scroll';
    MOUSEDOWN = 'mousedown';
    MOUSEMOVE = 'mousemove';
    MOUSEWHEEL = 'mousewheel';
    MOUSEUP = 'mouseup';
    RESIZE = 'resize';
    DRAG = 'drag';
    UP = 'up';
    PANEDOWN = 'panedown';
    DOMSCROLL = 'DOMMouseScroll';
    DOWN = 'down';
    WHEEL = 'wheel';
    KEYDOWN = 'keydown';
    KEYUP = 'keyup';
    TOUCHMOVE = 'touchmove';
    BROWSER_IS_IE7 = window.navigator.appName === 'Microsoft Internet Explorer' && /msie 7./i.test(window.navigator.appVersion) && window.ActiveXObject;
    BROWSER_SCROLLBAR_WIDTH = null;
    KEYSTATES = {};
    KEYS = {
        up: 38,
        down: 40,
        pgup: 33,
        pgdown: 34,
        home: 36,
        end: 35
    };
    getBrowserScrollbarWidth = function() {
        var outer, outerStyle, scrollbarWidth;
        outer = document.createElement('div');
        outerStyle = outer.style;
        outerStyle.position = 'absolute';
        outerStyle.width = '100px';
        outerStyle.height = '100px';
        outerStyle.overflow = SCROLL;
        outerStyle.top = '-9999px';
        document.body.appendChild(outer);
        scrollbarWidth = outer.offsetWidth - outer.clientWidth;
        document.body.removeChild(outer);
        return scrollbarWidth;
    };
    NanoScroll = (function() {

        function NanoScroll(el, options) {
            this.el = el;
            this.options = options;
            BROWSER_SCROLLBAR_WIDTH || (BROWSER_SCROLLBAR_WIDTH = getBrowserScrollbarWidth());
            this.doc = document;
            this.win = window;
            this.generate();
            this.createEvents();
            this.addEvents();
            this.reset();
        }

        NanoScroll.prototype.preventScrolling = function(e, direction) {
            if (!this.isActive)
                return;
            if (e.type === DOMSCROLL) {
                if (direction === DOWN && e.originalEvent.detail > 0 || direction === UP && e.originalEvent.detail < 0)
                    e.preventDefault();
            } else if (e.type === MOUSEWHEEL) {
                if (!e.originalEvent || !e.originalEvent.wheelDelta)
                    return;
                if (direction === DOWN && e.originalEvent.wheelDelta < 0 || direction === UP && e.originalEvent.wheelDelta > 0)
                    e.preventDefault();
            }
        };

        NanoScroll.prototype.updateScrollValues = function() {
            var content = this.content;
            this.maxScrollTop = content.scrollHeight - content.clientHeight;
            this.contentScrollTop = content.scrollTop;
            this.maxSliderTop = this.paneHeight - this.sliderHeight;
            this.sliderTop = this.contentScrollTop * this.maxSliderTop / this.maxScrollTop;
        };

        NanoScroll.prototype.createEvents = function() {
            var _this = this;
            this.events = {
                down: function(e) {
                    _this.isBeingDragged = true;
                    _this.offsetY = e.pageY - element.getOffset(_this.slider).top;
                    pclass.add(_this.pane, 'active');
                    addEvent(_this.doc, MOUSEMOVE, _this.events[DRAG])
                    addEvent(_this.doc, MOUSEUP, _this.events[UP]);
                    return false;
                },
                drag: function(e) {
                    _this.sliderY = e.pageY - element.getOffset(_this.el).top - _this.offsetY;
                    _this.scroll();
                    _this.updateScrollValues();
                    if (_this.contentScrollTop >= _this.maxScrollTop && _this.el.onscrollend)
                        _this.el.onscrollend.apply(_this.el);
                    else if (_this.contentScrollTop === 0 && _this.el.onscrolltop)
                        _this.el.onscrolltop.apply(_this.el);
                    return false;
                },
                up: function(e) {
                    _this.isBeingDragged = false;
                    pclass.remove(_this.pane, 'active');
                    removeEvent(_this.doc, MOUSEMOVE, _this.events[DRAG])
                    removeEvent(_this.doc, MOUSEUP, _this.events[UP]);
                    return false;
                },
                resize: function(e) {
                    _this.reset();
                },
                panedown: function(e) {
                    _this.sliderY = (e.offsetY || e.layerY) - (_this.sliderHeight * 0.5);
                    _this.scroll();
                    _this.events.down(e);
                    return false;
                },
                scroll: function(e) {
                    if (_this.isBeingDragged)
                        return;
                    _this.updateScrollValues();
                    _this.sliderY = _this.sliderTop;
                    _this.slider.style.top = _this.sliderTop + 'px';
                    if (e == null)
                        return;
                    if (_this.contentScrollTop >= _this.maxScrollTop) {
                        if (_this.options.preventPageScrolling)
                            _this.preventScrolling(e, DOWN);
                        if(_this.el.onscrollend)
                            _this.el.onscrollend.apply(_this.el);
                    } else if (_this.contentScrollTop === 0) {
                        if (_this.options.preventPageScrolling)
                            _this.preventScrolling(e, UP);
                        if(_this.el.onscrolltop)
                            _this.el.onscrolltop.apply(_this.el);
                    }
                },
                wheel: function(e) {
                    if (e == null) {
                        return;
                    }
                    _this.sliderY += -e.wheelDeltaY || -e.delta;
                    _this.scroll();
                    return false;
                }
            };
        };

        NanoScroll.prototype.addEvents = function() {
            var events;
            this.removeEvents();
            events = this.events;
            if (!this.options.disableResize) {
                addEvent(this.win, RESIZE, events[RESIZE]);
            }
            addEvent(this.slider, MOUSEDOWN, events[DOWN]);
            addEvent(this.pane, MOUSEDOWN, events[PANEDOWN])
            addEvent(this.pane, MOUSEWHEEL, events[WHEEL]);
            addEvent(this.pane, DOMSCROLL, events[WHEEL]);
            addEvent(this.content, SCROLL, events[SCROLL]);
            addEvent(this.content, MOUSEWHEEL, events[SCROLL]);
            addEvent(this.content, DOMSCROLL, events[SCROLL]);
            addEvent(this.content, TOUCHMOVE, events[SCROLL]);
        };

        NanoScroll.prototype.removeEvents = function() {
            var events;
            events = this.events;
            removeEvent(this.win, RESIZE, events[RESIZE]);
            removeEvent(this.content, SCROLL, events[SCROLL])
            removeEvent(this.content, MOUSEWHEEL, events[SCROLL])
            removeEvent(this.content, DOMSCROLL, events[SCROLL])
            removeEvent(this.content, TOUCHMOVE, events[SCROLL])
            removeEvent(this.content, KEYDOWN, events[KEYDOWN])
            removeEvent(this.content, KEYUP, events[KEYUP]);
        };

        NanoScroll.prototype.generate = function() {
            var contentClass, scrollContentClass, options, paneClass, sliderClass;
            options = this.options;
            paneClass = options.paneClass, sliderClass = options.sliderClass;
            contentClass = options.contentClass, scrollContentClass = options.scrollContentClass;
            var pane = getElementsByClassName(paneClass, this.el);
            var slider = getElementsByClassName(sliderClass, this.el);
            if (!pane.length && !slider.length){
                this.pane = element.create('div', {className: paneClass});
                this.slider = element.create('div', {className: sliderClass});
                element.appendChild(this.el, [this.pane, [this.slider]]);
            }else{
                this.slider = slider[0];
                this.pane = pane[0];
            }
            this.content = getElementsByClassName(scrollContentClass, this.el);
            if(this.content)
                this.content = this.content[0];
            else
                this.content = getElementsByClassName(contentClass, this.el)[0];
            this.content.tabindex = 0;
            if (BROWSER_SCROLLBAR_WIDTH) {
                this.content.style.right = -BROWSER_SCROLLBAR_WIDTH + 'px';
                pclass.add(this.el, 'has-scrollbar');
            }
            if (options.iOSNativeScrolling)
                this.content.style.WebkitOverflowScrolling = 'touch'
            return this;
        };

        NanoScroll.prototype.restore = function() {
            this.stopped = false;
            toggle(this.pane, true);
            return this.addEvents();
        };

        NanoScroll.prototype.reset = function() {
            var content, contentHeight, contentStyle, contentStyleOverflowY, paneBottom, paneHeight, paneOuterHeight, paneTop, sliderHeight;
            if (!getElementsByClassName(this.options.paneClass, this.el).length)
                this.generate().stop();
            if (this.stopped)
                this.restore();
            content = this.content;
            contentStyle = content.style;
            contentStyleOverflowY = contentStyle.overflowY;
            if (BROWSER_IS_IE7)
                this.content.style.height = this.content.height() + 'px';
            contentHeight = content.scrollHeight + BROWSER_SCROLLBAR_WIDTH;
            paneHeight = this.pane.offsetHeight;
            paneTop = parseInt(this.pane.style.top, 10) || 10;
            paneBottom = parseInt(this.pane.style.bottom, 10) || 10;
            paneOuterHeight = paneHeight + paneTop + paneBottom;
            sliderHeight = Math.round(paneOuterHeight / contentHeight * paneOuterHeight);
            if (sliderHeight < this.options.sliderMinHeight)
                sliderHeight = this.options.sliderMinHeight;
            else if ((this.options.sliderMaxHeight != null) && sliderHeight > this.options.sliderMaxHeight)
                sliderHeight = this.options.sliderMaxHeight;
            if (contentStyleOverflowY === SCROLL && contentStyle.overflowX !== SCROLL)
                sliderHeight += BROWSER_SCROLLBAR_WIDTH;
            this.maxSliderTop = paneOuterHeight - sliderHeight;
            this.contentHeight = contentHeight;
            this.paneHeight = paneHeight;
            this.paneOuterHeight = paneOuterHeight;
            this.sliderHeight = sliderHeight;
            this.slider.style.height = sliderHeight + 'px';
            this.events.scroll();
            toggle(this.pane, true);
            this.isActive = true;
            if (this.pane.offsetHeight >= content.scrollHeight && contentStyleOverflowY !== SCROLL) {
                toggle(this.pane, false);
                this.isActive = false;
            } else if (this.el.clientHeight === content.scrollHeight && contentStyleOverflowY === SCROLL) {
                toggle(this.slider, false)
            } else {
                toggle(this.slider, true);
            }
            if (this.options.alwaysVisible) {
                this.pane.style.opacity = 1;
                this.pane.style.visibility = 'visible';
            } else {
                this.pane.style.opacity = '';
                this.pane.style.visibility = '';
            }
            return this;
        };

        NanoScroll.prototype.scroll = function() {
            this.sliderY = Math.max(0, this.sliderY);
            this.sliderY = Math.min(this.maxSliderTop, this.sliderY);
            this.content.scrollTop = ((this.paneHeight - this.contentHeight + BROWSER_SCROLLBAR_WIDTH) * this.sliderY / this.maxSliderTop * -1);
            this.slider.style.top = this.sliderY + 'px';
            return this;
        };

        NanoScroll.prototype.scrollBottom = function(offsetY) {
            this.reset();
            this.content.scrollTop = (this.contentHeight - this.content.height() - offsetY);
            this.content["on" + MOUSEWHEEL].apply(this.content);
            return this;
        };

        NanoScroll.prototype.scrollTop = function(offsetY) {
            this.reset();
            this.content.scrollTop = (+offsetY);
            this.content["on" + MOUSEWHEEL].apply(this.content);
            return this;
        };

        NanoScroll.prototype.scrollTo = function(node) {
            var fraction, new_slider, offset;
            this.reset();
            offset = element.getOffset(node).top;
            if (offset > this.maxSliderTop) {
                fraction = offset / this.contentHeight;
                new_slider = this.maxSliderTop * fraction;
                this.sliderY = new_slider;
                this.scroll();
            }
            return this;
        };

        NanoScroll.prototype.stop = function() {
            this.stopped = true;
            this.removeEvents();
            toggle(this.pane, false);
            return this;
        };

        NanoScroll.prototype.flash = function() {
            var _this = this;
            this.reset();
            pclass.add(this.pane, 'flashed');
            setTimeout(function() {
                pclass.remove(_this.pane, 'flashed');
            }, this.options.flashDelay);
            return this;
        };

        return NanoScroll;

    })();

    createScroll = function(obj, settings){
        var _f = function(_this) {
            var options, scrollbar;
            if (!(scrollbar = _this.nanoscroller)) {
                options = extend({}, defaults, settings);
                _this.nanoscroller = scrollbar = new NanoScroll(_this, options);
            }
            if (settings && isObject(settings)) {
                extend(scrollbar.options, settings);
                if (settings.scrollBottom)
                    return scrollbar.scrollBottom(settings.scrollBottom);
                if (settings.scrollTop)
                    return scrollbar.scrollTop(settings.scrollTop);
                if (settings.scrollTo)
                    return scrollbar.scrollTo(settings.scrollTo);
                if (settings.scroll === 'bottom')
                    return scrollbar.scrollBottom(0);
                if (settings.scroll === 'top')
                    return scrollbar.scrollTop(0);
                if (settings.scroll && isElement(settings.scroll))
                    return scrollbar.scrollTo(settings.scroll);
                if (settings.stop)
                    return scrollbar.stop();
                if (settings.flash)
                    return scrollbar.flash();
            }
            return scrollbar.reset();
        }
        if(isElement(obj))
            _f(obj);
        else if(isString(obj))
            map(_f, getElementsByClassName(obj));
    }

});


