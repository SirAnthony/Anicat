#!stuser
########
<div>
	<p> User: $user.</p>
</div>
#!setmain
########
<div>
	<p> E-Mail: $mail.</p>
	<input type="button" value="Сменить E-Mail" />
	<p><input type="button" value="Сменить пароль"></p>
</div>
#!stmain
########
<div>
	<p>Statistics:</p>
	<table style="border-collapse: separate;">
		<thead>
			<th></th>
			<th>Items</th>
			<th colspan="2">Full duration</th>
			<th colspan="2">Watched</th>
		</thead>
		<tbody>
			$st.			
		</tbody>
	</table>
</div>
#!sttr
######
<tr style="text-align: right;  border-spacing: 3;">
	<td style="text-align: left;">$key.:</td>
	<td>$eps.</td>
	<td name="num">$dur.</td>
	<td>min.</td>
	<td name="num">$tot.</td>
	<td>min.</td>
</tr>
#!dispdiv
#########
<div id="$id.">
	<p>$id.</p>
	$dis.
</div>
#!setdisplay
############
<div>
	<form id="disset">
		<div id="discont">				
			$dis.
		</div>
		<input type="button" value="Save" onClick="setdisp();">
	</form>
</div>
#!dispcheck
###########
<label><input type="checkbox" name="$dis." $sel /> $dis. </label><br/>
#!cardimage
###########
<div id="cimg">
	<img src="/images/$id." />
</div>
#!cardbun
######
<tr>
	<td>
		$arr.	
	</td>
	<td align="right">
		$num..
	</td>
	<td>
		<a href="/card/$href." class="s$color.">$text.</a>$comm.<br/>
	</td>
</tr>
#!cardelem
#######
<p id="$id." class="cardelem">$name. $cast. $comm.</p>
#!cardinfo
##########
<div id="$prop.">
	<b>$prop.:</b>
	<br/>
	$val.		
</div>
#!div
###
<div id="$id." class="$classname.">
	$cont.
</div>
#!img
####
<img src="/templates/$name..gif" />
#!tabletag
#####
<table>
	$cont.
</table>
#!span
####
<span class="$class.">$cont.</span>
#!nocard
########
<div id="nocard">
	<p>No record found.</p>
</div>
#!nostat
########
<div id="nostat">
	<p>Anonymous doesn't keep statistics.</p>
</div>
#!nomail
########
<span style="color: #FF0000">Вы не ввели E-mail. Настоятельно рекомендуем сделать это!</span>
#!redirect
##########
Location: http://anicat.net/$location./

####################################################################
### Почтовые сообщения
####################################################################
#!regmessg
##########
From: Anime catalog <noreply@anicat.net>
To: $to
Subject: You were registered
X-Mailer: Anime catalog mail system v1.3

You were registered.
Your login $user..
Your password consists of a bunch of letters and numbers(md5-hash), so we can't tell it.
Should you forget it, blame yourself.
But you can always recover it.

This letter was written and sent by bot, so it isn't necessary to answer.
The robot gets bored sometimes, so he's pleased reading a letter or two.
If you received this letter, you are lucky.