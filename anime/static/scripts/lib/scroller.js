

define(['base/events', 'base/classes'],
function (events, classes){

    var SCROLLBAR = 'scrollbar', SCROLL = 'scroll', MOUSEDOWN = 'mousedown',
        MOUSEMOVE = 'mousemove', MOUSEWHEEL = 'mousewheel', MOUSEUP = 'mouseup',
        RESIZE = 'resize', DRAG = 'drag', UP = 'up', PANEDOWN = 'panedown',
        DOMSCROLL = 'DOMMouseScroll', DOWN = 'down', WHEEL = 'wheel',
        KEYDOWN = 'keydown', KEYUP = 'keyup', TOUCHMOVE = 'touchmove',
        BROWSER_IS_IE7 = (isIE >= 7 && isIE < 8), KEYSTATES = {}, KEYS = {
            up: 38, down: 40, pgup: 33, pgdown: 34, home: 36, end: 35
    }

    var defaults = {
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
    }

    function getBrowserScrollbarWidth() {
        var outer = element.create('div', {'style': { position: 'absolute',
            width: '100px', height: '100px', overflow: SCROLL, top: '-9999px'}})
        element.appendChild(document.body, outer)
        var scrollbarWidth = outer.offsetWidth - outer.clientWidth
        element.remove(outer)
        return scrollbarWidth
    }

    function ScrollerEvents(_this) {
        var self = this
        this.down = function(event) {
            _this.isBeingDragged = true
            _this.offsetY = event.pageY - element.getOffset(_this.slider).top
            classes.add(_this.pane, 'active')
            events.add(_this.doc, MOUSEMOVE, self.drag)
            events.add(_this.doc, MOUSEUP, self.up)
            return false
        }

        this.drag = function(event) {
            _this.sliderY = event.pageY - element.getOffset(_this.el).top - _this.offsetY
            _this.scroll()
            _this.updateScrollValues()
            if (_this.contentScrollTop >= _this.maxScrollTop && _this.el.onscrollend)
                _this.el.onscrollend.apply(_this.el)
            else if (_this.contentScrollTop === 0 && _this.el.onscrolltop)
                _this.el.onscrolltop.apply(_this.el)
            return false
        }

        this.up = function(event) {
            _this.isBeingDragged = false
            classes.remove(_this.pane, 'active')
            events.remove(_this.doc, MOUSEMOVE, self.drag)
            events.remove(_this.doc, MOUSEUP, self.up)
            return false
        }

        this.resize = function(event) {
            _this.reset()
        }

        this.panedown = function(event) {
            _this.sliderY = (event.offsetY || event.layerY) - (_this.sliderHeight * 0.5)
            _this.scroll()
            self.down(event)
            return false
        }

        this.scroll = function(event) {
            if (_this.isBeingDragged)
                return
            _this.updateScrollValues()
            _this.sliderY = _this.sliderTop
            _this.slider.style.top = _this.sliderTop + 'px'
            if (event === null)
                return
            if (_this.contentScrollTop >= _this.maxScrollTop) {
                if (_this.options.preventPageScrolling)
                    _this.preventScrolling(event, DOWN)
                if(_this.el.onscrollend)
                    _this.el.onscrollend.apply(_this.el)
            } else if (_this.contentScrollTop === 0) {
                if (_this.options.preventPageScrolling)
                    _this.preventScrolling(event, UP)
                if(_this.el.onscrolltop)
                    _this.el.onscrolltop.apply(_this.el)
            }
        }

        this.wheel = function(event) {
            if (!event)
                return
            _this.sliderY += -event.wheelDeltaY || -event.delta
            _this.scroll()
            return false
        }

        return this
    }


    function NanoScroll(elem, options) {
            this.el = elem
            this.doc = document
            this.win = window
            this.events = ScrollerEvents(this)
            this.setScrollbar(elem, options)
            this.generate()
            this.addEvents()
            this.reset()
    }

    NanoScroll.prototype.scrollWidth = getBrowserScrollbarWidth()
    NanoScroll.prototype.setScrollbar = function(elem, options) {
        var scrollbar
        if (!(scrollbar = elem.nanoscroller)) {
            options = extend(defaults, options)
            elem.nanoscroller = scrollbar = this
        }

        if (options && isHash(options)) {
            scrollbar.options = extend(scrollbar.options, options)
            if (options.scrollBottom)
                return scrollbar.scrollBottom(options.scrollBottom)
            if (options.scrollTop)
                return scrollbar.scrollTop(options.scrollTop)
            if (options.scrollTo)
                return scrollbar.scrollTo(options.scrollTo)
            if (options.scroll === 'bottom')
                return scrollbar.scrollBottom(0)
            if (options.scroll === 'top')
                return scrollbar.scrollTop(0)
            if (options.scroll && isElement(options.scroll))
                return scrollbar.scrollTo(options.scroll)
            if (options.stop)
                return scrollbar.stop()
            if (options.flash)
                return scrollbar.flash()
        }
        return scrollbar.reset()
    }

    NanoScroll.prototype.preventScrolling = function(e, direction) {
        if (!this.isActive)
            return
        if (e.type === DOMSCROLL) {
            if (direction === DOWN && e.originalEvent.detail > 0 || direction === UP && e.originalEvent.detail < 0)
                e.preventDefault()
        } else if (e.type === MOUSEWHEEL) {
            if (!e.originalEvent || !e.originalEvent.wheelDelta)
                return
            if (direction === DOWN && e.originalEvent.wheelDelta < 0 || direction === UP && e.originalEvent.wheelDelta > 0)
                e.preventDefault()
        }
    }

    NanoScroll.prototype.updateScrollValues = function() {
        var content = this.content
        this.maxScrollTop = content.scrollHeight - content.clientHeight
        this.contentScrollTop = content.scrollTop
        this.maxSliderTop = this.paneHeight - this.sliderHeight
        this.sliderTop = this.contentScrollTop * this.maxSliderTop / this.maxScrollTop
    }

    NanoScroll.prototype.addEvents = function() {
        this.removeEvents()
        var evs = this.events
        if (!this.options.disableResize)
            events.add(this.win, RESIZE, evs.resize)
        events.add(this.slider, MOUSEDOWN, evs.down)
        events.add(this.pane, MOUSEDOWN, evs.panedown)
        events.add(this.pane, MOUSEWHEEL, evs.wheel)
        events.add(this.pane, DOMSCROLL, evs.wheel)
        events.add(this.content, SCROLL, evs.scroll)
        events.add(this.content, MOUSEWHEEL, evs.scroll)
        events.add(this.content, DOMSCROLL, evs.scroll)
        events.add(this.content, TOUCHMOVE, evs.scroll)
    }

    NanoScroll.prototype.removeEvents = function() {
        var evs = this.events
        events.remove(this.win, RESIZE, evs.resize)
        events.remove(this.content, SCROLL, evs.scroll)
        events.remove(this.content, MOUSEWHEEL, evs.scroll)
        events.remove(this.content, DOMSCROLL, evs.scroll)
        events.remove(this.content, TOUCHMOVE, evs.scroll)
        events.remove(this.content, KEYDOWN, evs.scroll)
        events.remove(this.content, KEYUP, evs.scroll)
    }

    NanoScroll.prototype.generate = function() {
        var options = this.options
        this.pane = getElementsByClassName(options.paneClass, this.el)[0]
        this.slider = getElementsByClassName(options.sliderClass, this.el)[0]
        if (!this.pane && !this.slider){
            this.pane = element.create('div', {className: options.paneClass})
            this.slider = element.create('div', {className: options.sliderClass})
            element.appendChild(this.el, [this.pane, [this.slider]])
        }
        this.content = getElementsByClassName(options.scrollContentClass, this.el)[0]
        if(!this.content)
            this.content = getElementsByClassName(options.contentClass, this.el)[0]
        this.content.tabindex = 0
        if (this.scrollWidth) {
            this.content.style.right = -this.scrollWidth + 'px'
            classes.add(this.el, 'has-scrollbar')
        }
        if (options.iOSNativeScrolling)
            this.content.style.WebkitOverflowScrolling = 'touch'
        return this
    }

    NanoScroll.prototype.restore = function() {
        this.stopped = false
        toggle(this.pane, 1)
        return this.addEvents()
    }

    NanoScroll.prototype.reset = function() {
        var content, paneTop, paneBottom, sliderHeight
        if (!getElementsByClassName(this.options.paneClass, this.el).length)
            this.generate().stop()
        if (this.stopped)
            this.restore()
        toggle(this.pane, 1)
        toggle(this.slider, 1)
        content = this.content
        if (BROWSER_IS_IE7)
            this.content.style.height = this.content.height() + 'px'
        this.contentHeight = content.scrollHeight + this.scrollWidth
        this.paneHeight = this.pane.offsetHeight
        paneTop = parseInt(this.pane.style.top, 10) || 10
        paneBottom = parseInt(this.pane.style.bottom, 10) || 10
        this.paneOuterHeight = this.paneHeight + paneTop + paneBottom
        sliderHeight = Math.round(this.paneOuterHeight / this.contentHeight * this.paneOuterHeight)
        if (sliderHeight < this.options.sliderMinHeight)
            sliderHeight = this.options.sliderMinHeight
        else if ((this.options.sliderMaxHeight != null) && sliderHeight > this.options.sliderMaxHeight)
            sliderHeight = this.options.sliderMaxHeight
        if (content.style.overflowY === SCROLL && content.style.overflowX !== SCROLL)
            sliderHeight += this.scrollWidth
        this.maxSliderTop = this.paneOuterHeight - sliderHeight
        this.sliderHeight = sliderHeight
        this.slider.style.height = sliderHeight + 'px'
        this.events.scroll()
        toggle(this.pane, 1)
        this.isActive = true
        if (this.pane.offsetHeight >= content.scrollHeight && content.style.overflowY !== SCROLL) {
            toggle(this.pane, -1)
            this.isActive = false
        } else if (this.el.clientHeight === content.scrollHeight && content.style.overflowY === SCROLL) {
            toggle(this.slider, -1)
        } else {
            toggle(this.slider, 1)
        }
        if (this.options.alwaysVisible) {
            this.pane.style.opacity = 1
            this.pane.style.visibility = 'visible'
        } else {
            this.pane.style.opacity = ''
            this.pane.style.visibility = ''
        }
        return this
    }

    NanoScroll.prototype.scroll = function() {
        this.sliderY = Math.max(0, this.sliderY)
        this.sliderY = Math.min(this.maxSliderTop, this.sliderY)
        this.content.scrollTop = ((this.paneHeight - this.contentHeight +
                        this.scrollWidth) * this.sliderY / this.maxSliderTop * -1)
        this.slider.style.top = this.sliderY + 'px'
        return this
    }

    NanoScroll.prototype.scrollBottom = function(offsetY) {
        this.reset()
        this.content.scrollTop = (this.contentHeight - this.content.height() - offsetY)
        events.emit(this.content, MOUSEWHEEL)
        return this
    }

    NanoScroll.prototype.scrollTop = function(offsetY) {
        this.reset()
        this.content.scrollTop = (+offsetY)
        events.emit(this.content, MOUSEWHEEL)
        return this
    }

    NanoScroll.prototype.scrollTo = function(node) {
        var fraction, new_slider, offset
        this.reset()
        offset = element.getOffset(node).top
        if (offset > this.maxSliderTop) {
            fraction = offset / this.contentHeight
            new_slider = this.maxSliderTop * fraction
            this.sliderY = new_slider
            this.scroll()
        }
        return this
    }

    NanoScroll.prototype.stop = function() {
        this.stopped = true
        this.removeEvents()
        toggle(this.pane, -1)
        return this
    }

    NanoScroll.prototype.flash = function() {
        var _this = this
        this.reset()
        pclass.add(this.pane, 'flashed')
        setTimeout(function() {
            pclass.remove(_this.pane, 'flashed')
        }, this.options.flashDelay)
        return this
    }

    return NanoScroll;
})

