/*
calendar.js - Calendar functions by Adrian Holovaty
*/

// CalendarNamespace -- Provides a collection of HTML calendar-related helper functions
var CalendarNamespace = {
    monthsOfYear: gettext('January February March April May June July August September October November December').split(' '),
    daysOfWeek: gettext('M T W T F S S').split(' '),
    firstDayOfWeek: parseInt(get_format('FIRST_DAY_OF_WEEK')) + 1,
    getDaysInMonth: function(m, year) {
        var d = new Date(year, m, 0);
        return d.getDate();
    },
    strptime: function(strDate) {
        var date = new Date();
        date.setHours(0, 0, 0, 0);
        if(/\d{2}\.\d{2}\.\d{4}/.test(strDate)){
            var dateParts = strDate.split(".");
            date.setFullYear(dateParts[2]);
            date.setMonth(dateParts[1] - 1);
            date.setDate(dateParts[0]);
        }else{
            var sec = Date.parse(strDate);
            if(sec)
                date.setTime(sec);
        }
        return date;
    },
}

// Calendar -- A calendar instance
function Calendar(inp, div_id, callback) {
    // div_id (string) is the ID of the element in which the calendar will
    //   be displayed
    // callback (string) is the name of a JavaScript function that will be
    //   called with the parameters (year, month, day) when a day in the
    //   calendar is clicked
    this.div_id = div_id;
    this.callback = callback;
    this.input = inp
    this.today = new Date();
    this.currentMonth = this.today.getMonth() + 1;
    this.currentYear = this.today.getFullYear();
}

Calendar.prototype = {
    draw: function(month, year, div_id, callback) { // month = 1-12, year = 1-9999
        var today = new Date();
        today.setHours(0, 0, 0, 0);
        var todayDay = today.getDate();
        var todayMonth = today.getMonth()+1;
        var todayYear = today.getFullYear();
        var todayClass = '';
        var selected = CalendarNamespace.strptime(this.input.value);

        month = parseInt(month);
        year = parseInt(year);

        var startingPos = new Date(year, month-1, 1 - CalendarNamespace.firstDayOfWeek).getDay();
        var days = CalendarNamespace.getDaysInMonth(month, year);

        var weeks = new Array();
        weeks.push(element.create('tr', null, map(function(j){
            return {'th': { innerText: CalendarNamespace.daysOfWeek[(j + CalendarNamespace.firstDayOfWeek) % 7]}};
            }, range(0, 6))));
        var row;
        var currentDay = 1;
        var currentDate = new Date(year, month-1, currentDay);
        for(var i = 0; currentDay <= days; i++){
            currentDate.setDate(currentDay);
            var todayClass = '';
            if(i % 7 == 0){
                row = element.create('tr');
                weeks.push(row);
            }
            if(currentDate - today == 0)
                todayClass = 'today';
            if(currentDate - selected == 0)
                todayClass += ' selected';
            if(i < startingPos){
                element.appendChild(row, [{'td': {
                    innerText: ' ', style: {backgroundColor: '#f3f3f3'}}
                }]);
            }else{
                element.appendChild(row, [
                    {'td': {className: todayClass}}, [
                        {'a': {
                            innerText: currentDay,
                            onclick: (function(callback, year, month, currentDay){
                                    return function(){ callback(year, month, currentDay); }
                                })(callback, year, month, currentDay)
                        }}
                    ]
                ]);
                currentDay++;
            }
        }

        while(row.childNodes.length < 7){
            element.appendChild(row, [{'td': {
                    innerText: ' ', style: {backgroundColor: '#f3f3f3'}}
                }]);
        }

        var calDiv = document.getElementById(div_id);
        element.removeAllChilds(calDiv);
        element.appendChild(calDiv, ['table', ['tbody', weeks]])
        var caption = calDiv.previousSibling.getElementsByTagName('caption');
        if(!caption || !caption[0])
            element.appendChild(calDiv.previousSibling, [
            {'caption': {innerText: CalendarNamespace.monthsOfYear[month-1] + ' ' + year}}]);
        else
            caption[0].innerText = CalendarNamespace.monthsOfYear[month-1] + ' ' + year;
    },

    drawInput: function() {
        var selected = CalendarNamespace.strptime(this.input.value);
        this.currentMonth = selected.getMonth() + 1;
        this.currentYear = selected.getFullYear();
        this.drawCurrent();
    },

    drawCurrent: function() {
        this.draw(this.currentMonth, this.currentYear, this.div_id, this.callback);
    },

    drawDate: function(month, year) {
        this.currentMonth = month;
        this.currentYear = year;
        this.drawCurrent();
    },

    drawPreviousMonth: function() {
        if (this.currentMonth == 1) {
            this.currentMonth = 12;
            this.currentYear--;
        }else{
            this.currentMonth--;
        }
        this.drawCurrent();
    },

    drawNextMonth: function() {
        if (this.currentMonth == 12) {
            this.currentMonth = 1;
            this.currentYear++;
        }else{
            this.currentMonth++;
        }
        this.drawCurrent();
    },

    drawPreviousYear: function() {
        this.currentYear--;
        this.drawCurrent();
    },

    drawNextYear: function() {
        this.currentYear++;
        this.drawCurrent();
    }
}


// ----------------------------------------------------------------------------
// Get the computed style for and element
// ----------------------------------------------------------------------------
function getStyle(oElm, strCssRule){
    var strValue = "";
    if(document.defaultView && document.defaultView.getComputedStyle){
        strValue = document.defaultView.getComputedStyle(oElm, "").getPropertyValue(strCssRule);
    }else if(oElm.currentStyle){
        strCssRule = strCssRule.replace(/\-(\w)/g, function (strMatch, p1){
            return p1.toUpperCase();
        });
        strValue = oElm.currentStyle[strCssRule];
    }
    return strValue;
}

//-----------------------------------------------------------------------------
// Date object extensions
// ----------------------------------------------------------------------------
Date.prototype.getCorrectYear = function() {
    // Date.getYear() is unreliable --
    // see http://www.quirksmode.org/js/introdate.html#year
    var y = this.getYear() % 100;
    return (y < 38) ? y + 2000 : y + 1900;
}

Date.prototype.getTwelveHours = function() {
    hours = this.getHours();
    if (hours == 0) {
        return 12;
    }else{
        return hours <= 12 ? hours : hours-12
    }
}

Date.prototype.getTwoDigitMonth = function() {
    return (this.getMonth() < 9) ? '0' + (this.getMonth()+1) : (this.getMonth()+1);
}

Date.prototype.getTwoDigitDate = function() {
    return (this.getDate() < 10) ? '0' + this.getDate() : this.getDate();
}

Date.prototype.getTwoDigitTwelveHour = function() {
    return (this.getTwelveHours() < 10) ? '0' + this.getTwelveHours() : this.getTwelveHours();
}

Date.prototype.getTwoDigitHour = function() {
    return (this.getHours() < 10) ? '0' + this.getHours() : this.getHours();
}

Date.prototype.getTwoDigitMinute = function() {
    return (this.getMinutes() < 10) ? '0' + this.getMinutes() : this.getMinutes();
}

Date.prototype.getTwoDigitSecond = function() {
    return (this.getSeconds() < 10) ? '0' + this.getSeconds() : this.getSeconds();
}

Date.prototype.getISODate = function() {
    return this.getCorrectYear() + '-' + this.getTwoDigitMonth() + '-' + this.getTwoDigitDate();
}

Date.prototype.getHourMinute = function() {
    return this.getTwoDigitHour() + ':' + this.getTwoDigitMinute();
}

Date.prototype.getHourMinuteSecond = function() {
    return this.getTwoDigitHour() + ':' + this.getTwoDigitMinute() + ':' + this.getTwoDigitSecond();
}

Date.prototype.strftime = function(format) {
    var fields = {
        c: this.toString(),
        d: this.getTwoDigitDate(),
        H: this.getTwoDigitHour(),
        I: this.getTwoDigitTwelveHour(),
        m: this.getTwoDigitMonth(),
        M: this.getTwoDigitMinute(),
        p: (this.getHours() >= 12) ? 'PM' : 'AM',
        S: this.getTwoDigitSecond(),
        w: '0' + this.getDay(),
        x: this.toLocaleDateString(),
        X: this.toLocaleTimeString(),
        y: ('' + this.getFullYear()).substr(2, 4),
        Y: '' + this.getFullYear(),
        '%' : '%'
    };
    var result = '', i = 0;
    while (i < format.length) {
        if (format.charAt(i) === '%') {
            result = result + fields[format.charAt(i + 1)];
            ++i;
        }else{
            result = result + format.charAt(i);
        }
        ++i;
    }
    return result;
}

