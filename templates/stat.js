
window.onload = function(){
	var h = element.create('div', {id: 'tohrs', className: 'cont_men'});
	h.style.position = 'absolute';
	setnums();
	element.appendChild(document.body,[h]);
}

function setnums(){
	var el = new Array();
	el = document.getElementsByName('num');	
	for(var i in el){
		el[i].onmouseover = function(){
			var h = document.getElementById('tohrs');			
			h.textContent = (this.textContent/60).toFixed(2) +'h. '+ (this.textContent/(60*24)).toFixed(2) + 'd.';
			var offset = getOffset(this);
			h.style.left = offset.left + this.offsetWidth/1.6 + 'px';
			h.style.top = offset.top - this.offsetHeight*2.8 + 'px';
			h.style.display = 'block';
		} 
		el[i].onmouseout = function(){
			var h = document.getElementById('tohrs');
			h.textContent = '';
			h.style.display = 'none';
		}
	}
} 