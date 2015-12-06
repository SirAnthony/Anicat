
import strftime = require('strftime');

var DATE_FORMATS = [
    "%d.%m.%Y", "??.%m.%Y", "%d.??.%Y",
    "??.??.%Y", "%d.%m.??", "??.%m.??",
    "%d.??.??", "??.??.??",
];

export class DateMask {
    date: Date;
    mask: number;
    constructor(date, mask?){
        this.date = date;
        this.mask = mask||0;
        if (this.mask<0 || this.mask>DATE_FORMATS.length)
            throw new RangeError();
    }
    toString(){
        return strftime(DATE_FORMATS[mask], this.date); }
    data(){
        return {date: this.date, mask: this.mask}; }
}

export class DateRange {
    start: DateMask;
    end?: DateMask;
    constructor(start, end?){
        this.start = start;
        this.end = end;
    }
    toString(){
        return +this.start+(this.end ? ' - '+this.end : ''); }
    data(){
        return {start: this.start, end: this.end}; }
}
