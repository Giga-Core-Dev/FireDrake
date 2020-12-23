#!/usr/bin/perl
#user manager module of the Firedrake project.
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

package userManager;
use strict;

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
	if ($_[3]) {
		$self->{CGI} = $_[3];
	}
	else {
		exit(0);
	}
	if ($_[4]) {
		$self->{SESS} = $_[4];
	}
	else {
		exit(0);
	}
	bless($self, $class);
	return $self;
}

sub paintMain{
	my $self = shift;
	my $ver = $self->{VER};
	my $cgi = $self->{CGI};
	my $sess = $self->{SESS};
	my $action = $cgi->param('action');
	if($action eq "delete") {
		print("here you will be able to delete a user<br>\n");
	}elsif($action eq "chpass"){
		my $user = $cgi->param("user");
		print("you will be changing $user\047s password");
	}else{
		print "Wellcome to the user manager.\n<br>Here you can add or remove users.<br>\n";
		if ($self->showUsers() eq "E1"){
			$sess->printm("An error has occured wile trying to read users from file.<br>");
		}
	}
}

sub showUsers{
	my $self = shift;
	open(UF,".users") or return "E1";
	my @users = <UF>;
	close (UF);
	my @fields;
	my $line;
	print "The list of users currently avalible:<br>\n<table width='100%'>\n";
	foreach $line(@users) {
		@fields = split(' ', $line);
		if($fields[1]){
			print "<tr>\n<td>";
			print "$fields[0]</td>\n<td>";
			print "<a href=\042index.cgi?module=UM&action=delete&user=$fields[0]\042>:Delete:_";
			print "<a href=\042index.cgi?module=UM&action=chpass&user=$fields[0]\042>:Change password:</a></td>\n</tr>\n";
		}
	}
	print "</table>\n";
}

return (1);