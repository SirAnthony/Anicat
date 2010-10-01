#!search
########
<div id="srch">
	<!--<p id="chtext"><input type="checkbox" id="chsrch" onClick="searcher.showAdvance();" />Advanced Search</p>-->
	<p id="srchp">
		<!--<select id="advsrch" class="advsrch">
			<option value="null" selected="selected">Find by:</option>
			<option value="genre">Genre</option>
			$opts.
		</select>
		<select id="sortsrch" class="advsrch">
			<option value="null" selected="selected">Sort by:</option>
			<option value="genre">Genre</option>
			$opts.
		</select>
		-->
		<!--<input type="text" onkeyup="app.acomp(this, 'catalog', event);" /><br/>-->
		<input id="sin"  type="text" ondblclick="document.getElementById('sin').value='';" onkeydown="if(event.keyCode==13){searcher.send();} " />
		<input type="button" onclick="searcher.send();" value="Искать" />
	</p>
	<div id="srchres"></div>	
</div>
#################################################################### 
#!regfm
#######
###Now it's in js
<label for "register">Quick registration:</label>
<form id="register">
	<input id="name"  type="text" />
	<input id="passwd"  type="password" />
	<input type="button" onClick="register();" value="Register" />
</form>