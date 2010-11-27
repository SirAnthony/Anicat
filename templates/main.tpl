#!head
######
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
	<title>Anime catalog</title>
	<meta http-equiv="content-type" content="text/html; charset=UTF-8" />
	<link rel="icon" href="/templates/favicon.ico" type="image/x-icon" />
	<link rel="search" type="application/opensearchdescription+xml" title="Anime catalog" href="/templates/srch.xml" />
	<link href="/templates/style.css" type="text/css" rel="stylesheet" />
	<link href="/templates/user.css" type="text/css" rel="stylesheet" />
	<script type="text/javascript" src="/templates/script.js"></script>
	<script type="text/javascript" src="/templates/app.js"></script>
	<script type="text/javascript" src="/templates/ajax.js"></script>
	<script type="text/javascript" src="/templates/user.js"></script>
	<script type="text/javascript" src="/templates/ae.js"></script>
	$add.
</head>
<body>
#!header
########
<div id="header" class="thdtbl">
#!forms
#######
<div class="leftmenu">
	<a class="nurl" onclick="searcher.toggle();">&nbsp;Search</a>
	<input type="button" style="height: 22px;" onclick="corovan++; alert('Корованов ограблено:'+corovan);" value="Грабить корованы" />
	<a class="nurl" href="/card/">&nbsp;Random</a>	
</div>
#!nmforms
#########
<div class="leftmenu">
	<a class="nurl" href="/search/">Search</a>|
	<a class="nurl" href="/">Main page</a>|
	<a class="nurl" href="/card/">Random</a>	
</div>
#!tblhdr
########
<th id="$cls." class="$cls.">
	<a href="$url.$desc." rel="nofollow">$key.</a>
</th>
#!hdend
#######
<div id="ie" style="color: #FFFF00;"></div>
</div>
<br/>
#!table
#######
<div id="dvid" style="width: $w.px;">
	<table id="tbl" cellspacing="0" class="tbl">
		<thead class="thdtbl">
			<tr id="wtr">
				$hd.
			</tr>
		</thead>
		<tbody id="tbdid">
			$body.
		</tbody>
	</table>		
</div>
<div id="pg">
    $pg.
</div>
#!end
#######
<div class="cont_men" id="menu">
	<span id="mspan" class="mnspan"></span>
</div>
<div class="cont_men" id="popup">
	<span id="popups" class="mnspan"></span>
</div>
#!tr
####
<tr$tr. style="background-color: $bgcolor.">$cnt.</tr$tr.>
#!td
####
<td$td. class="$cls." id="$cls.$id." $jsfunct.>$cont.</td$td.>
#!acard
#######
<a href="/card/$id./" class="cardurl" target="_blank">
	<img src="/templates/arrow.gif" alt="Go" />
</a>
#!jshdr
########
<script type="text/javascript" src="/templates/$name..js"></script>