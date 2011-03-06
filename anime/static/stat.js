
var stat = new ( function(){

    this.hrs = null;

    this.init = function(){
        this.hrs = element.create('div', {id: 'tohrs', className: 'cont_men'});
        this.hrs.style.position = 'absolute';
        element.appendChild(document.body, [this.hrs]);
        var el = document.getElementsByName('num');
        for(var i in el){
            el[i].onmouseover = function(){
                var offset = element.getOffset(this);
                stat.hrsShow(this.textContent, offset.left + this.offsetWidth/1.6, offset.top - this.offsetHeight*2.8);
            }
            el[i].onmouseout = stat.hrsHide;
        }
    }

    this.hrsShow = function(mins, x, y){
        if(!this.hrs)
            return;
        this.hrs.textContent = (mins/60).toFixed(2) +'h. '+ (mins/(60*24)).toFixed(2) + 'd.';
        this.hrs.style.left = x + 'px';
        this.hrs.style.top = y + 'px';
        this.hrs.style.display = 'block';
    }

    this.hrsHide = function(){
        var hrs = this != stat ? stat.hrs : this.hrs;
        if(!hrs)
            return;
        hrs.textContent = '';
        hrs.style.display = 'none';
    }

})();
