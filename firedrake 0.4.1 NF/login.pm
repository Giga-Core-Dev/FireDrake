#!/usr/bin/perl
#Sessions module of the Firedrake project.
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

package login;
use strict;
use File::Copy;


sub new {
	my $proto = shift;
	my $class = ref($proto) || $proto;
	my $self  = {};
	if ($_[0]) {
		$self->{VER} = $_[0];
	} else {
		$self->{VER} = "UNDEFINED";
	}
	if ($_[1]) {
		$self->{LOG} = $_[1];
	} else {
		$self->{LOG} = 0;
	}
	if ($_[2]) {
		$self->{DOMAIN} = $_[2];
	} else {
		$self->{DOMAIN} = "localhost";
	}
	#if ($_[3]) {
		$self->{CGI} = $_[3];
	#}
	bless($self, $class);	
	return $self;
}
sub encrypt{
	##This is the encrypt method. It has two functions: One: initial encrypt;
	##Two: Secondary encrypt - for session ID matching :) - and other stuff :p
	my $self = shift;
	my $unencrypted_string = $_[0];
	if($_[1]){
		#`echo "encrypt: $_[0] -  $_[1]">> tmp`; #DEBUG
		return crypt($unencrypted_string, $_[1]);
	} else {
		my @salt_chars = ('a'..'z','A'..'Z','0'..'9');
		my $salt = $salt_chars[rand(63)] . $salt_chars[rand(63)];
		return crypt($unencrypted_string, $salt);
	}
}
sub checkSession {
	##This method compares the session ID from the cookie to the one in .sessions
	my $self = shift;
	my $Time = time-350;
	my $Stat = $self->colGarbage($Time);
	if ($Stat = "E2") {
		#return "E1";
	}
	open (SF,".sessions") or return "E1";
	my @sessions = <SF>;
	close (SF);
	##Potential dangerous behaviour ... will be fixed one day :)
	my @fields;
	my $Session;
	my $line;
	foreach $line(@sessions) {
		@fields = split(' ', $line);
		$Session = $self->encrypt($_[0], $fields[1]);
		#`echo "checkSession: $_[0] - $Session . $fields[1]" >> tmp`; #DEBUG
		if (($fields[1] eq $Session) && ($Time<$fields[2])) {
			return "OK";
		}
	}
	if($self->{LOG} > 0) {
		#This will probably need to be reformed :)
		`echo "SMM: $_[0]" >> .log`
	}
	return "NO";
}
sub colGarbage{
	## Clean the .sessions file :)
	my $self = shift;
	my $Time=$_[0];
	my @Fields;
	my $i;
	my @newSessions;
	my $line;
	my $SessLength;
	open(SF,".sessions") or return "E2";
	my @Sessions = <SF>;
	close(SF);
	open(SF,">.sessions") or return "E2";
	##Potential dangerous behaviour ... will be fixed one day :)
	foreach $line(@Sessions){
		@Fields = split(' ', $line);
		if($Fields[2]>$Time){
			#`echo "GBG: $line - time: $Fields[2] - criteria: $Time">>tmp`; #DEBUG
			print SF $line;
			$i++;
		}
	}
	close(SF);
	return "OK";
}
sub checkUser{
	##This method screens users from imposters :)
	my $self = shift;
	open(UF,".users") or return "E1";
	my @users = <UF>;
	close (UF);
	my @fields;
	my $user = $_[0];
	my $pass;
	my $line;
	my $tp=0;
	foreach $line(@users) {
		@fields = split(' ', $line);
		$pass = $self->encrypt($_[1], $fields[1]);
		if (($user eq $fields[0]) && ($pass eq $fields[1])) {
			return "OK";
		}
	}
	if($self->{LOG} > 0) {
		#This will probably need to be reformed :)
		`echo "UAA: $_[0]" >> .log`
	}
	return "NO";
}
sub auth{
	#If there is a username, but there is no cookie :)
	my $self = shift;
	my $uname = $_[0];
	my $passw = $_[1];
	my $cgi = $self->{CGI};
	my $ref = $cgi->referer;
	my $ver = $self->{VER};
	my $Ustat = $self->checkUser($uname,$passw);
	if($Ustat eq "OK"){
		## ID comfirmed, generate a SSiD and leave a cookie :)
		my $ssid=int(rand+10000000);
		my $cookie = $cgi->cookie(-name=>'SSiD',
					  -value=>"$ssid",
					  -domain=>"$self->{DOMAIN}",
					  -expires=>'+5m');
		my $cssid = $self->encrypt($ssid);
		my $ttime = time;
		my $session = "$uname $cssid $ttime";
		`echo $session >> .sessions`;
		####TODO: customize from here on :)
		print
		$cgi->header(-cookie=>$cookie) .
		$cgi->start_html(-title=> "Firedrake $ver" ,
				 -style=>{'src' => 'simple.css'});
#		print	"<b><font id='allok'>Wellcome $uname</font></b><br>\n";
#		print	"Your session id is $ssid<br>";
		return "paint";
	} elsif($Ustat eq "NO") {
	print
		$cgi->header .
		$cgi->start_html(-title=> "Firedrake $ver - Login" ,
				 -style=>{'src' => 'simple.css'});
 		$self->printm("<b><font id='error'>Access Denied!</font></b><br>\n<a href='$ref'>Retry&gt;&gt;</a>");
	} else {
		$cgi->header;
		$cgi->start_html(-title=> "Firedrake $ver - Login" ,
				 -style=>{'src' => 'simple.css'});
 		$self->printm("<br><b><font id=\"error\">Error!</font></b><br>\nSomething went wrong in the process.<br>\n<a href=\"$ref\">Retry&gt;&gt;</a>");
	}
}
sub firstTime{
	#if no username and no cookie exist - this usualy means  the script has
	#been called for the first time :)
	my $self = shift;
	my $cgi = $self->{CGI};
	my $ver = $self->{VER};
	my $browser = $cgi->user_agent("ie");
	print
		$cgi->header .
		$cgi->start_html(-title=> "Firedrake $ver - Login" ,
				 -style=>{'src' => 'simple.css'});
	if(!$browser){	
		open (LOGIN,"login.html") or $self->printm("Could not open login.html.<br>\nCheck apache error log.");
		my @login = <LOGIN>;
		close (LOGIN);
		my $line;
		foreach $line(@login) {
			$line =~ s/!VER/$ver/;
			print "$line";
		}
	}
	else{
		$self->printm("<b><font id='error'>This page does not work with IE at the moment.<br>\n Please check back with a browser which supports \
css properly :)\n</font></b>");
	}
}
sub logout{
	my $self = shift;
	my $cgi = $self->{CGI};
	my $ver = $self->{VER};
	my $cookie = $cgi->cookie(-name=>'SSiD',
					  -value=>"logedout",
					  -domain=>"$self->{DOMAIN}",
					  -expires=>'+2s');
	print
		$cgi->header(-cookie=>$cookie) .
		$cgi->start_html(-title=> "Firedrake $ver - Logout" ,
				 -style=>{'src' => 'simple.css'});
	$self->printm("<font id='allok'>Logout successful</font>");
	#TODO: delete session from file.
}
sub extend{
	my $self = shift;
	my $cgi = $self->{CGI};
	my $ver = $self->{VER};
	my $ssid = $cgi->cookie('SSiD');
	#`echo $ssid`;
	my $cookie = $cgi->cookie(-name=>'SSiD',
					  -value=>"$ssid",
					  -domain=>"$self->{DOMAIN}",
					  -expires=>'+5m');
	my $cssid = $self->encrypt($ssid);
	my $ttime = time;
	open (SF,".sessions") or $self->printm("<b><font id='error'>Error.</font></b><br>\nSession extension failed.<br>\nCould not open .sessions file!");
	my @sessions = <SF>;
	close (SF);
	##Potential dangerous behaviour ... will be fixed one day :)
	my @fields;
	my $Session;
	my $line;
	open (TSF, "+>.ts") or $self->printm("<b><font id='error'>Error.</font></b><br>\nCould not extend session.<br>\n Check directory permissions.");
	foreach $line(@sessions) {
		@fields = split(' ', $line);
		$Session = $self->encrypt($ssid, $fields[1]);
		if ($fields[1] ne $Session) {
			print TSF "$line\n";
		}
		else {
			$line = "$fields[0] $fields[1] $ttime";
			print TSF "$line\n";
		}
	}
	close (TSF);
	move (".ts", ".sessions") or $self->printm("<b><font id='error'>Error.</font></b><br>\nCould not extend session.<br>\n Check directory permissions.");
	unlink(".ts");
	print
		$cgi->header(-cookie=>$cookie) .
		$cgi->start_html(-title=> "Firedrake $ver" ,
				 -style=>{'src' => 'simple.css'});
}
sub printm{
	my $self = shift;
	my $cont = $_[0];
	my $ver = $self->{VER};
	open (MB,"message.html") or print "Could not open message.html - check apache error log.";
	my @message = <MB>;
	close (MB);
	my $line;
	foreach $line(@message) {
		if($line =~ m/^!!c!!/) {
			print "$cont\n";
		}
		else {
			$line =~ s/!VER/$ver/;
			print "$line";
		}
	}
}
return (1);