<?xml version="1.0"?>
<xsl:stylesheet version="2.0" 
	xmlns:xhtml="http://www.w3.org/1999/xhtml"
	xmlns="http://www.w3.org/1999/xhtml"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:xs="http://www.w3.org/2001/XMLSchema"
	exclude-result-prefixes="xhtml xsl xs">
	<xsl:output method="xml" version="1.0" encoding="UTF-8" doctype-public="-//W3C//DTD XHTML 1.1//EN" doctype-system="http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd" indent="yes"/>

	<xsl:template match="/">
		<html>
			<xsl:apply-templates/>
		</html>
	</xsl:template>
	
	<xsl:template match="xhtml:README">
	</xsl:template>
	
	<xsl:template match="xhtml:head">
		<head>
			<script type="text/javascript" src="/templates/script.js"></script>
			<script type="text/javascript" src="/templates/user.js"></script>
			<link href="/templates/style.css" type="text/css" rel="stylesheet" />
			<link href="/templates/user.css" type="text/css" rel="stylesheet" />
			<xsl:copy-of select="./*" />
		</head>
	</xsl:template>
	
	<xsl:template match="xhtml:body">
		<body>
			<xsl:apply-templates select="xhtml:header"/>
			<div id="imagebun" class="cardcol">
				<div id="cimg">
					<img src="/images/{xhtml:id}/>" />
				</div>
				<b>Bundled with:</b><br/>
				<table>
					<xsl:apply-templates select="xhtml:bundles"/>
				</table>
			</div>
			<div id="main" class="cardcol">
				<xsl:apply-templates select="xhtml:main"/>
			</div>
			<div class="cont_men" id="menu">
				<span id="mspan" class="mnspan"></span>
			</div>
			<div class="cont_men" id="popup">
				<span id="popups" class="mnspan"></span>
			</div>
			<div class="footer">
				v. <a style="font-size: 10pt; color: #000081" href="/changes.list">
					<xsl:value-of select="xhtml:version"/>
				</a>
				<br />
				Time: <xsl:value-of select="xhtml:time"/>s.
			</div>
		</body>
	</xsl:template>
	
	<xsl:template match="xhtml:header">
		<div id="header" class="thdtbl">
			<div class="leftmenu">
				<a class="nurl" href="/search/">Search</a>|
				<a class="nurl" href="/">Main page</a>|
				<a class="nurl" href="/card/">Random</a>	
			</div>		
			<xsl:choose>
				<xsl:when test="xhtml:userid>0">
					<div id="logdiv" class="rightmenu">	
						<a href="/anime/settings/" title="User settings">												
							<xsl:value-of select="xhtml:username"/>
						</a>	
						<a class="nurl" onclick="user.logout();">Logout</a>	
					</div>
					<div class="rightmenu" style="margin-top: 1px;">
						<a href="/anime/stat/{xhtml:userid}" class="nurl">Statistics</a>
					</div>
				</xsl:when>
				<xsl:otherwise>
					<div id="logdiv" class="rightmenu">
						<a onclick="vissrch('login');" class="nurl">Account</a>	
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
				</xsl:otherwise>
			</xsl:choose>
		</div>
		<br />		
	</xsl:template>
	
	<xsl:template match="xhtml:bundles">
		<xsl:for-each select="./*">
			<xsl:apply-templates select="."/>
		</xsl:for-each>
	</xsl:template>	
	
	<xsl:template match="xhtml:bundle">
		<tr>
			<td>
			<xsl:if test="xhtml:selected>0">
				 <img src="/templates/arrowblack.gif" />					
			</xsl:if>
			</td>
			<td align="right">
				<xsl:value-of select="xhtml:number"/>
			</td>
			<td>
				<a href="/card/{xhtml:id}" class="s{xhtml:class}" >
					<xsl:value-of select="xhtml:name"/>
				</a>
				<xsl:if test="xhtml:comment>0"> 
				(<xsl:value-of select="xhtml:comment"/>)
				</xsl:if>
				<br/>
			</td>
		</tr>
	</xsl:template>
	
	<xsl:template match="xhtml:main">		
		<xsl:apply-templates select="*[@name='name']" />
		<xsl:apply-templates select="*[@name='type']" />
		<xsl:apply-templates select="*[@name='genre']" />
		<xsl:apply-templates select="*[@name='numberofep']" />
		<xsl:apply-templates select="*[@name='duration']" />
		<xsl:apply-templates select="*[@name='size']" />
		<xsl:apply-templates select="*[@name='translation']" />
	</xsl:template>
	
	<xsl:template match="xhtml:maininfo">
		<div>
			<b><xsl:value-of select="xhtml:title"/>:</b>
			<br/>
			<xsl:value-of select="xhtml:content"/>
		</div>
	</xsl:template>
	
		<xsl:template match="xhtml:maininfo[@name='name']">
		<div>
			<b><xsl:value-of select="xhtml:title"/>:</b>
			<br/>
			<xsl:for-each select="xhtml:content/*">				
				<xsl:value-of select="."/><br />
			</xsl:for-each>
		</div>
	</xsl:template>
	
	<xsl:template match="xhtml:maininfo[@name='numberofep']">
		<div>
			<b>Episodes:</b>
			<br/>
			<xsl:value-of select="xhtml:content"/>
		</div>
	</xsl:template>
	
</xsl:stylesheet>