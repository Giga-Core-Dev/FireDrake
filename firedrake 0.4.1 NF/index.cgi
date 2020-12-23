#!/usr/bin/perl
#index module of the Firedrake project.
#Copyright (C) Anze Cesar
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General
#Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option)
#any later version.
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
#the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#General Public License for more details.
#You should have received a copy of the GNU General Public License along with this program; if not, write to the
#Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#Author's contact: anze.cesar@gmail.com

use login;
use userManager;
use strict;
use CGI;

my $ver = '0.4.1';

my $cgi = new CGI;
my $uname = $cgi->param('username');
my $passw = $cgi->param('password');

my $addr = $cgi->remote_addr;
my $ref = $cgi->referer;
my $ssid = $cgi->cookie('SSiD');
my $module = $cgi->param('module');

my $sess = login->new($ver, 0, "ces.psychorealm.org", $cgi);

sub paintMenu{
	print "<b>Menu:</b><br>\n";
	print "<a href='index.cgi?module=Logout'>::Logout::</a><br>\n";
	print "<a href='index.cgi?module=UM'>::User Manager::</a><br>\n";
}

sub paintIndex{
	open (INDEX,"index.html") or $sess->printm("Could not open index.html - check apache error log.");
	my @index = <INDEX>;
	close (INDEX);
	my $line;
	my $L="lol\n";
	my $C="indeed\n";
	foreach $line(@index) {
		if($line =~ m/^!!l!!/) {
			paintMenu();
		}
		elsif($line =~ m/^!!c!!/) {
			if($module eq "UM") {
				my $um = userManager->new($ver, 0, "ces.psychorealm.org", $cgi, $sess);
				$um->paintMain();
			}
			else {
				paintMain();
			}
		}
		else {
			$line =~ s/!VER/$ver/;
			print "$line";
		}
	}
}

sub paintMain() {
	print "nothing exists here yet :)";
}

if(!$uname && !$ssid){
	$sess->firstTime();
}
elsif(!$ssid) {
	if ($sess->auth($uname, $passw) eq "paint"){
		paintIndex(1);
	}
}
elsif($ssid) {
	my $SStatus = $sess->checkSession($ssid);
	if($module eq "Logout") {
		$sess->logout();
		print	$cgi->end_html;
		exit (0);
	}
	if ($SStatus eq "OK") {
	##All is ok, let the man in :)
		$sess->extend();
		paintIndex();
	} elsif ($SStatus eq "NO") {
	##IMPOSTER!
		print
		$cgi->header .
		$cgi->start_html(-title=> "Firedrake $ver - Login" ,
				 -style=>{'src' => 'simple.css'});
		$sess->printm("<font id=\"error\">Warning!</font><br>\nYour session ID is invalid or expired<br>\n<a href=\"$ref\">Back</a>");
	} elsif ($SStatus eq "E1") {
		print
		$cgi->header .
		$cgi->start_html(-title=> "Firedrake $ver - Error" ,
				 -style=>{'src' => 'simple.css'});
		$sess->printm("<font id=\"error\">Error.</font><br>\nUnable to open sessions.<br>\n Please contact your administrator.<br>\n<a href=\"$ref\">Back</a>");
	}
}

print	$cgi->end_html;
exit (0);