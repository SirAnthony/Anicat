//#################### Настройки

function setdisp(){
		
	var qw = 'display=';
   var dv = document.getElementById('discont');
   
	var f = function(elm){
   	if(elm.tagName == 'DIV'){
   		qw += elm.id+',';
   		if(elm.id == 'Main') qw += 'id,';
			allelements(check,elm);
			qw = qw.replace(/,$/g, "");
			qw += ';';
		}
   }
   
	var check = function(obj){
		if(obj.nodeName == "LABEL"){		
			var chkd = obj.firstChild.checked; 
			if(chkd == true )				
				qw += obj.firstChild.name+',';
				if(obj.firstChild.name == 'translation') qw += 'enddate,';			
		}
   }
      
	allelements(f, dv);
	
	//alert(qw);
	loadXMLDoc(seturl, qw);		
}
