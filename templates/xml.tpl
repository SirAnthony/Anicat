#!xhead
#######
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type='text/xsl' href='/templates/$name..xsl'?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
	<README>
		If you see this, your browser does not support xslt, and therefore don't need.<br />
		links version is not implemented yet.	
	</README>
	<head>
		<title>Anime catalog</title>
		<link rel="icon" href="/templates/favicon.ico" type="image/x-icon" />
	</head>
	<body>
#!bdend
#######
	</body>
</html>
#!header
########
<header>
	<userid>$id</userid>
	<username>$name.</username>
</header>
#!id
####
<id>$id.</id>
#!parent
########
<$tag.>
$data.
</$tag.>
#!cardbundle
############
<bundle>
	<selected>$selected.</selected>
	<number>$number.</number>
	<name>$name.</name>
	<comment>$comm.</comment>
	<id>$id.</id>
	<class>$color.</class>
</bundle>
#!cardmain
##########
<maininfo name="$name.">
	<title>$title.</title>
	<content>$content.</content>
</maininfo>
#!element
#########
<element>
    $data.
</element>
#!sxml
######
<par>
	<response>search</response>
	<pgs>$mxpg.</pgs>
	<pg>$page.</pg>
	<text>
		<table>$out.</table>
	</text>
	<end>$time.</end>
</par>
#!formget
#########
<id>$id.</id>
$val.