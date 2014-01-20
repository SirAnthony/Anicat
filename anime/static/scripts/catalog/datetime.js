// Inserts shortcut buttons after all of the following:
//  <input type="text" class="vDateField">
//  <input type="text" class="vTimeField">

define(['base/events', 'calendar'], function(events, Calendar){

    var calendars = [],
    calendarDivName1 = 'calendarbox',    // name of calendar <div> that gets toggled
    calendarDivName2 = 'calendarin',     // name of <div> that contains calendar
    calendarLinkName = 'calendarlink',   // name of the link that is used to toggle
    shortCutsClass = 'datetimeshortcuts' // class of the clock and cal shortcuts

    function DateTimeShortcuts() {}


    DateTimeShortcuts.prototype.init = function() {
        // Get admin_media_prefix by grabbing it off the window object. It's
        // set in the admin/base.html template, so if it's not there, someone's
        // overridden the template. In that case, we'll set a clearly-invalid
        // value in the hopes that someone will examine HTTP requests and see it.
        var ftype = ['vDateField', 'vTimeField']
        getElementsByClassName(ftype[0], document, 'input').forEach(
            function(date){
                if(date.type == 'text')
                    this.add(date)
            }, this)
    }

    // Add calendar widget to a given field.
    DateTimeShortcuts.prototype.add = function(inp){
        if(inp.type != 'text')
            throw new Error('Only text input supported.')
        if(typeof Calendar == "undefined") //ie7
            return

        var self = this
        var num = calendars.length
        var calendar = new Calendar(inp, calendarDivName2 + num,
                                        this.handler, this.dismiss)
        calendars.push(calendar)

        element.insert(inp.previousSibling, [
            {'span': {className: shortCutsClass}}, [
                {'a': {onclick: function(){ self.open(calendar, num) },
                    id: calendarLinkName + num,
                    innerText: gettext('Calendar')}}]
        ])

        // Create calendarbox div.
        //
        // Markup looks like:
        //
        // <div id="calendarbox3" class="calendarbox module">
        //  <h2>
        //      <a href="#" class="link-previous">&lsaquo;</a>
        //      <a href="#" class="link-next">&rsaquo;</a> February 2003
        //  </h2>
        //  <div class="calendar" id="calendarin3">
        //      <!-- (cal) -->
        //  </div>
        //  <div class="calendar-shortcuts">
        //      <a href="#">Yesterday</a> | <a href="#">Today</a> | <a href="#">Tomorrow</a>
        //  </div>
        //  <p class="calendar-cancel"><a href="#">Cancel</a></p>
        // </div>

        var links = [
            ['left',  '<<\240',  calendar.drawPreviousYear],
            ['left',  '<',       calendar.drawPreviousMonth],
            ['right', '>>',      calendar.drawNextYear],
            ['right', '>\240',   calendar.drawNextMonth],
        ]

        var link_days = [
            ['Yesterday', -1],
            ['Today', 0],
            ['Tomorrow', 1],
        ]

        element.appendChildNoCopy(document.body, [{'div': {
                className: 'cont_men calendarbox module',
                id: calendarDivName1 + num, onclick: events.stop,
                style: {display: 'none', position: 'absolute'}}}, [
            'div', //В образце h2, а в коде div ололо
                map(function(link){
                return {'a': {className: link[0], innerText: link[1],
                    onclick: function(){ link[2].call(calendar) } }}}, links),
            {'div': {className: 'calendar', id: calendarDivName2 + num}},
            {'div': {className: 'calendar-shortcuts'}}, map(function(link){
                return {'a': {innerText: gettext(link[0]),
                    onclick: function(){ self.quickLink(calendar, link[1]) }}}
            }, link_days),
            {'p': {className: 'calendar-cancel'}}, [
                {'a': {innerText: gettext('Cancel'), onclick: calendar.dismiss }}
            ]
        ]])

        calendar.drawInput()
    }

    DateTimeShortcuts.prototype.open = function(calendar, num) {
        var cal_box = calendar.block().parentNode
        var cal_link = document.getElementById(calendarLinkName + num)
        var inp = calendar.input

        if(visible(cal_box))
            return calendar.dismiss()

        calendar.drawInput()
        var position = element.getOffset(cal_link)
        // Recalculate the clockbox position
        // is it left-to-right or right-to-left layout ?
        // since style's width is in em, it'd be tough to calculate
        // px value of it. let's use an estimated px for now
        // TODO: IE returns wrong value for findPosX when in rtl mode
        // (it returns as it was left aligned), needs to be fixed.
        position.left += (getStyle(document.body, 'direction') != 'rtl') ? -100 : 150
        cal_box.style.left = position.left + 'px'
        cal_box.style.top = Math.max(0, position.top - 90) + 'px'
        toggle(cal_box, 1)
    }

    DateTimeShortcuts.prototype.dismiss = function() {
        toggle(this.block().parentNode, -1)
    }

    DateTimeShortcuts.prototype.handler = function(y, m, d){
        // this - calendar instance
        // get_format('DATE_INPUT_FORMATS')[0] // Fix it in l18n
        var format = '%d.%m.%Y'
        this.input.value = new Date(y, m - 1, d).strftime(format)
        this.input.focus()
        this.dismiss()
    }

    DateTimeShortcuts.prototype.quickLink = function(calendar, offset) {
        var d = new Date()
        d.setDate(d.getDate() + offset)
        calendar.callback(d.getFullYear(), d.getMonth() + 1, d.getDate())
    }

    return new DateTimeShortcuts()
})