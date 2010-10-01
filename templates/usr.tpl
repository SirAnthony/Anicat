#!logform
#########
<div id="logdiv" class="rightmenu">
	<a onclick="user.toggle();" class="nurl">Account</a>	
</div>
<div id="logdv">	
	<form id="login" class="thdtbl">	
		<a onclick="user.quickreg();" class="nurl">Registration</a>
		<input id="lname"  type="text" />
		<input id="lpasswd"  type="password" />
		<input type="button" onclick="user.login();" value="Login" />
		<label id="lngs"><input type="checkbox" id="long"/>Remember</label>	
		<p id="logininfo"></p>
	</form>
</div>
#!logged
########
<div id="logdiv" class="rightmenu">	
		<span><a href="/" title="User settings">$username.</a></span>	
		<a class="nurl" onclick="user.logout();">Logout</a>	
</div>
#!add
#####
<div class="leftmenu">
	|&nbsp;<a class="nurl" onclick="add.show();">Add</a>&nbsp;
</div>
#!show
######
<div class="rightmenu" style="margin-top: 1px;">
	<a href="/stat/" class="nurl">Statistics</a>	
	<select id="show" onChange="setshow();">
		<option value="null" selected>Display Mode</option>
		<option value="all">All</option>
		<option value="want">Want</option>
		<option value="now">Now</option>
		<option value="ok">Watched</option>
		<option value="dropped">Dropped</option>
	</select>
</div>
#!nmshow
########
<div class="rightmenu" style="margin-top: 1px;">
	<a href="/stat/" class="nurl">Statistics</a>
</div>
#!addfrm
########
<form id="addfrm" class="cont_men">
	<div class="frmdv">
		<label for="pname" class="ac1">Название:</label>
		<label for="panothername" class="ac2">Альтернативные названия:</label><br>
		<input type="text" name="pname"class="ac1" />
		<textarea name="panothername" class="ac2"></textarea><br>		
		<label for="ptype" class="ac1">Тип:</label><br>
		<select name="ptype" onChange="add.setnum();"class="ac1">
			<option selected value="TV">TV</option>
			<option value="OAV">OAV</option>
			<option value="Movie">Movie</option>
			<option value="SMovie">SMovie</option>
			<option value="TV-Sp">TV-Sp</option>
			<option value="ONA">ONA</option>
		</select><br>
		<label for="pnumberofep" class="ac1">Количество эпизодов:</label><br>
		<input type="text" name="pnumberofep" class="ac1"><br>
		<label for="psize" class="ac1">Дополнительно:</label>
		<label for="pgenre" class="ac2">Жанр:</label><br>
		<input type="text" name="psize" class="ac1" />
		<input type="text" name="pgenre" class="ac2" /><br>
		<label for="ptranslation" class="ac1">Трансляция:</label>
		<label for="pduration" class="ac2">Продолжительность:</label><br>
		<input type="text" name="ptranslation" class="ac1" />
		<input type="text" name="pduration" class="ac2" /><br>
		<input type="button" class="ac1" onclick="add.clear();" value="Очистить" class="ac1" />
		<input type="button" class="ac2" onclick="add.accept();" value="Добавить" class="ac2" />
	</div>	
	<a id='a_elm' onclick="add.getfield();">Add</a>
</form>
#!ids
#####
<div id="ids">
	<span id="idsa"></span><br/>
	<input type="button" value="Clear" onclick="document.getElementById('idsa').innerHTML= '';" />
</div>
<div class="app_men" id="app">
</div>