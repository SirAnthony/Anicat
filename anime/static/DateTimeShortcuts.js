// Inserts shortcut buttons after all of the following:
//     <input type="text" class="vDateField">
//     <input type="text" class="vTimeField">

var DateTimeShortcuts = {
    calendars: [],
    calendarInputs: [],
    clockInputs: [],
    calendarDivName1: 'calendarbox', // name of calendar <div> that gets toggled
    calendarDivName2: 'calendarin',  // name of <div> that contains calendar
    calendarLinkName: 'calendarlink',// name of the link that is used to toggle
    clockDivName: 'clockbox',        // name of clock <div> that gets toggled
    clockLinkName: 'clocklink',      // name of the link that is used to toggle
    shortCutsClass: 'datetimeshortcuts', // class of the clock and cal shortcuts
    admin_media_prefix: '',
    init: function(){
        // Get admin_media_prefix by grabbing it off the window object. It's
        // set in the admin/base.html template, so if it's not there, someone's
        // overridden the template. In that case, we'll set a clearly-invalid
        // value in the hopes that someone will examine HTTP requests and see it.
        if (window.__admin_media_prefix__ != undefined) {
            DateTimeShortcuts.admin_media_prefix = window.__admin_media_prefix__;
        } else {
            DateTimeShortcuts.admin_media_prefix = '/missing-admin-media-prefix/';
        }
        
        var ftype = ['vDateField', 'vTimeField']
        for(var i in ftype){
            var dates = getElementsByClassName(ftype[i], document, 'input');
            for(var date in dates){
                if(dates[date].getAttribute('type') == 'text'){
                    if(ftype[i] == 'vDateField')
                        DateTimeShortcuts.addCalendar(dates[date]);
                    else
                        DateTimeShortcuts.addClock(dates[date]);
                }
            }
        }
    },

    // Add clock widget to a given field
    addClock: function(inp){
        var num = DateTimeShortcuts.clockInputs.length;
        DateTimeShortcuts.clockInputs[num] = inp;

        // Shortcut links (clock icon and "Now" link)
        var shortcuts_span = element.create('span', {className: DateTimeShortcuts.shortCutsClass});
        
        element.appendChild(shortcuts_span, [
                            element.create('', {innerText: '\240'}),
                            element.create('a', {
                                onclick: (function(num, format){
                                    return function(){
                                        DateTimeShortcuts.handleClockQuicklink(num, new Date().strftime(format));
                                    }
                                })(num, get_format('TIME_INPUT_FORMATS')[0]),
                                innerText: gettext('Now')}),
                            element.create('', {innerText: '\240|\240'}),
                            element.create('a', {onclick: (function(num){
                                    return function(){DateTimeShortcuts.openClock(num);}
                                })(num), id: DateTimeShortcuts.clockLinkName + num}), [
                                element.create('img', {
                                        'src': DateTimeShortcuts.admin_media_prefix + 'img/admin/icon_clock.gif',
                                        'alt': gettext('Clock')})],
        ]);
        element.insert(inp, shortcuts_span, 1);

        // Create clock link div
        //
        // Markup looks like:
        // <div id="clockbox1" class="clockbox module">
        //     <h2>Choose a time</h2>
        //     <ul class="timelist">
        //         <li><a href="#">Now</a></li>
        //         <li><a href="#">Midnight</a></li>
        //         <li><a href="#">6 a.m.</a></li>
        //         <li><a href="#">Noon</a></li>
        //     </ul>
        //     <p class="calendar-cancel"><a href="#">Cancel</a></p>
        // </div>
        var time_format = get_format('TIME_INPUT_FORMATS')[0];
        var clock_box = element.create('div', {className: 'clockbox module',
                                        id: DateTimeShortcuts.clockDivName + num,
                                        onclick: DateTimeShortcuts.cancelEventPropagation});
        element.appendChild(document.body, [clock_box, [
            element.create('h2', {innerText: 'Choose a time'}),
            element.create('ul', {className: 'timelist'}),
                [element.create('li'), [
                    element.create('a', {innerText: gettext("Now"),
                        onclick: (function(num, format){
                            return function(){
                                DateTimeShortcuts.handleClockQuicklink(num, new Date().strftime(format));
                            }
                       })(num, time_format)})],
                element.create('li'), [
                    element.create('a', {innerText: gettext("Midnight"),
                        onclick: (function(num, format){
                            return function(){
                                DateTimeShortcuts.handleClockQuicklink(num, new Date(1970,1,1,0,0,0,0).strftime(format));
                            }
                       })(num, time_format)})],
                element.create('li'), [
                    element.create('a', {innerText: gettext("6 a.m."),
                        onclick: (function(num, format){
                            return function(){
                                DateTimeShortcuts.handleClockQuicklink(num, new Date(1970,1,1,6,0,0,0).strftime(format));
                            }
                       })(num, time_format)})],
                element.create('li'), [
                    element.create('a', {innerText: gettext("Noon"),
                        onclick: (function(num, format){
                            return function(){
                                DateTimeShortcuts.handleClockQuicklink(num, new Date(1970,1,1,12,0,0,0).strftime(format));
                            }
                       })(num, time_format)})],
                ],
            element.create('p', {className: 'calendar-cancel'}), [
                element.create('a', {innerText: gettext('Cancel'),
                    onclick: (function(num){ return function(){DateTimeShortcuts.dismissClock(num);}})(num)})
            ]
        ]]);

        clock_box.style.display = 'none';
        clock_box.style.position = 'absolute';
    },
    
    openClock: function(num){
        var clock_box = document.getElementById(DateTimeShortcuts.clockDivName+num)
        var clock_link = document.getElementById(DateTimeShortcuts.clockLinkName+num)
        
        if(clock_box.style.display == 'block'){
            DateTimeShortcuts.dismissCalendar(num);
            return;
        }

        var position = element.getOffset(clock_link);
        // Recalculate the clockbox position
        // is it left-to-right or right-to-left layout ?
        if(getStyle(document.body,'direction')!='rtl'){
            position.left -= 90;
        }else{
            // since style's width is in em, it'd be tough to calculate
            // px value of it. let's use an estimated px for now
            // TODO: IE returns wrong value for findPosX when in rtl mode
            //       (it returns as it was left aligned), needs to be fixed.
            position.left += 110;
        }
        clock_box.style.left = position.left + 'px';
        clock_box.style.top = Math.max(0, position.top - 130) + 'px';

        // Show the clock box
        clock_box.style.display = 'block';
        //addEvent(window.document, 'click',  function(){DateTimeShortcuts.dismissClock(num);});
    },
    
    dismissClock: function(num){
       document.getElementById(DateTimeShortcuts.clockDivName + num).style.display = 'none';
       window.document.onclick = null;
    },
    
    handleClockQuicklink: function(num, val){
       DateTimeShortcuts.clockInputs[num].value = val;
       DateTimeShortcuts.clockInputs[num].focus();
       DateTimeShortcuts.dismissClock(num);
    },
    
    // Add calendar widget to a given field.
    addCalendar: function(inp){
        var num = DateTimeShortcuts.calendars.length;

        DateTimeShortcuts.calendarInputs[num] = inp;
        
        var shortcuts_span = element.create('span', {className: DateTimeShortcuts.shortCutsClass});
        
        element.appendChild(shortcuts_span, [
                            element.create('', {innerText: '\240'}),
                            element.create('a', {
                                onclick: (function(num, format){
                                    return function(){
                                        DateTimeShortcuts.handleCalendarQuickLink(num, 0);
                                    }
                                })(num),
                                innerText: gettext('Today')}),
                            element.create('', {innerText: '\240|\240'}),
                            element.create('a', {onclick: (function(num){
                                    return function(){DateTimeShortcuts.openCalendar(num);}
                                })(num), id: DateTimeShortcuts.calendarLinkName + num}), [
                                element.create('img', {
                                        'src': DateTimeShortcuts.admin_media_prefix + 'img/admin/icon_calendar.gif',
                                        'alt': gettext('Calendar')})],
        ]);
        element.insert(inp, shortcuts_span, 1);
        
        // Create calendarbox div.
        //
        // Markup looks like:
        //
        // <div id="calendarbox3" class="calendarbox module">
        //     <h2>
        //           <a href="#" class="link-previous">&lsaquo;</a>
        //           <a href="#" class="link-next">&rsaquo;</a> February 2003
        //     </h2>
        //     <div class="calendar" id="calendarin3">
        //         <!-- (cal) -->
        //     </div>
        //     <div class="calendar-shortcuts">
        //          <a href="#">Yesterday</a> | <a href="#">Today</a> | <a href="#">Tomorrow</a>
        //     </div>
        //     <p class="calendar-cancel"><a href="#">Cancel</a></p>
        // </div>
        
        var cal_box = element.create('div', {className: 'calendarbox module',
                                        id: DateTimeShortcuts.calendarDivName1 + num,
                                        onclick: DateTimeShortcuts.cancelEventPropagation});

        element.appendChild(document.body, [cal_box, [
            element.create('div'), [ //В образце h2, а в коде div ололо
                element.create('a', {className: 'calendarnav-previous', innerText: '<', 
                    onclick: (function(num){return function(){DateTimeShortcuts.drawPrev(num);}})(num)}),
                element.create('a', {className: 'calendarnav-next',  innerText: '>',
                    onclick: (function(num){return function(){DateTimeShortcuts.drawNext(num);}})(num)})
                ],
            element.create('div', {className: 'calendar', id: DateTimeShortcuts.calendarDivName2 + num}),
            element.create('div', {className: 'calendar-shortcuts'}), [
                element.create('a', {innerText: gettext('Yesterday'),
                    onclick: (function(num){return function(){DateTimeShortcuts.handleCalendarQuickLink(num, -1);}})(num)}),
                element.create('', {innerText: '\240|\240'}),
                element.create('a', {innerText: gettext('Today'),
                    onclick: (function(num){return function(){DateTimeShortcuts.handleCalendarQuickLink(num, 0);}})(num)}),
                element.create('', {innerText: '\240|\240'}),
                element.create('a', {innerText: gettext('Tomorrow'),
                    onclick: (function(num){return function(){DateTimeShortcuts.handleCalendarQuickLink(num, 1);}})(num)}),
                ],
            element.create('p', {className: 'calendar-cancel'}), [
                element.create('a', {innerText: gettext('Cancel'),
                    onclick: (function(num){ return function(){DateTimeShortcuts.dismissCalendar(num);}})(num)})
            ]
        ]])

        cal_box.style.display = 'none';
        cal_box.style.position = 'absolute';

        DateTimeShortcuts.calendars[num] = new Calendar(DateTimeShortcuts.calendarDivName2 + num, DateTimeShortcuts.handleCalendarCallback(num));
        DateTimeShortcuts.calendars[num].drawCurrent();

    },

    openCalendar: function(num) {
        var cal_box = document.getElementById(DateTimeShortcuts.calendarDivName1+num);
        var cal_link = document.getElementById(DateTimeShortcuts.calendarLinkName+num);
        var inp = DateTimeShortcuts.calendarInputs[num];

        if(cal_box.style.display == 'block'){
            DateTimeShortcuts.dismissCalendar(num);
            return;
        }

        // Determine if the current value in the input has a valid date.
        // If so, draw the calendar with that date's year and month.
        if (inp.value) {
            var date_parts = inp.value.split('-');
            var year = date_parts[0];
            var month = parseFloat(date_parts[1]);
            if (year.match(/\d\d\d\d/) && month >= 1 && month <= 12) {
                DateTimeShortcuts.calendars[num].drawDate(month, year);
            }
        }

        var position = element.getOffset(cal_link);
        // Recalculate the clockbox position
        // is it left-to-right or right-to-left layout ?
        if(getStyle(document.body,'direction')!='rtl'){
            position.left -= 100;
        }else{
            // since style's width is in em, it'd be tough to calculate
            // px value of it. let's use an estimated px for now
            // TODO: IE returns wrong value for findPosX when in rtl mode
            //       (it returns as it was left aligned), needs to be fixed.
            position.left += 180;
        }
        cal_box.style.left = position.left + 'px';
        cal_box.style.top = Math.max(0, position.top - 175) + 'px';

        cal_box.style.display = 'block';
        //addEvent(window.document, 'click', function(){DateTimeShortcuts.dismissCalendar(num);});
    },

    dismissCalendar: function(num) {
        document.getElementById(DateTimeShortcuts.calendarDivName1+num).style.display = 'none';
        window.document.onclick = null;
    },

    drawPrev: function(num) {
        DateTimeShortcuts.calendars[num].drawPreviousMonth();
    },

    drawNext: function(num) {
        DateTimeShortcuts.calendars[num].drawNextMonth();
    },

    handleCalendarCallback: function(num) {
        format = get_format('DATE_INPUT_FORMATS')[0];
        // the format needs to be escaped a little
        format = format.replace('\\', '\\\\');
        format = format.replace('\r', '\\r');
        format = format.replace('\n', '\\n');
        format = format.replace('\t', '\\t');
        format = format.replace("'", "\\'");
        return (function(num, format){
            return function(y, m, d){
                DateTimeShortcuts.calendarInputs[num].value = new Date(y, m-1, d).strftime(format);
                DateTimeShortcuts.calendarInputs[num].focus();
                document.getElementById(DateTimeShortcuts.calendarDivName1+num).style.display='none';
            }
        })(num, format);
    },
    handleCalendarQuickLink: function(num, offset) {
       var d = new Date();
       d.setDate(d.getDate() + offset)
       DateTimeShortcuts.calendarInputs[num].value = d.strftime(get_format('DATE_INPUT_FORMATS')[0]);
       DateTimeShortcuts.calendarInputs[num].focus();
       DateTimeShortcuts.dismissCalendar(num);
    },
    cancelEventPropagation: function(e) {
        if (!e) e = window.event;
        e.cancelBubble = true;
        if (e.stopPropagation) e.stopPropagation();
    }
}

addEvent(window, 'load', DateTimeShortcuts.init);
