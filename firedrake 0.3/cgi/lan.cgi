#!/bin/bash
echo "content-type: text/html"
echo
#nalozi config
config="`pwd`/config"
source $config
script=$lanScript
d_root="http://psychorealm.org/firewall"
cat glava

# Procesiranje forma:
for Q in $(echo ${QUERY_STRING} | tr "&" " ") ; do
        ime=`echo $Q | awk -F= '{ print $1 }'`
        vrednost=`echo $Q | awk -F= '{ print $2 }' | tr "+" " "`
        eval "export FORM_${ime}='${vrednost}'"
done
#Vrednosti, ki smo jih vnasali v formo se obdelajo, naredimo spremenljivke FORM_imeelementa=vsebina_elementa

#############################################################################################################################################
#Funkcije:

function naredi_tabelo() {
for vnos in ${1}
do
        IP=`echo $vnos | awk -F- '{ print $1 }'`
        porti=`echo $vnos | awk -F- '{ print $2 }'`
	porti=`echo $porti | tr ";" " "`
	echo "<div align='center'><table width='768'  style='border: thin solid'><tr>"
	echo "<td width='120' style='border-right: thin solid'><img src='${d_root}/cmp.gif' width='120' height='121'></td>"
    	echo "<td width='92' style='border-right: thin solid'>IP:<br><b>${IP}</b></td>"
	echo "<td width='538'><table width='100%'  border='0'>"
	echo "<tr><form name='tcp_${IP}' method='get' action='$script'>"
        echo "<td width='433' style='border-bottom: thin solid'>TCP:"
	for port in $porti
	do
		echo " <input name='odstrani_port' type='radio' value='${port}'>${port}" 
	done
	echo "</td>"
        echo "<td width='91' style='border-bottom: thin solid'><input type='hidden' name='ip' value='$IP'>"
	echo "<input type='hidden' name='protokol' value='TCP'>"
	echo "<input type='submit' name='Submit' value='Odstrani port'></td></form></tr>"
	echo "<tr><form name='udp_${IP}' method='get' action='$script'><td width='433' style='border-bottom: thin solid'>UDP:"
	for udp_vnos in ${2}
	do
		udp_IP=`echo $udp_vnos | awk -F- '{ print $1 }'`
	        udp_porti=`echo $udp_vnos | awk -F- '{ print $2 }'`
        	udp_porti=`echo $udp_porti | tr ";" " "`
		if [[ $udp_IP == $IP ]]
		then
			for udp_port in $udp_porti
			do
				echo "<input name='odstrani_port' type='radio' value='${udp_port}'>${udp_port}"
			done
		fi
	done
        echo "<td width='91' style='border-bottom: thin solid'><input type='hidden' name='ip' value='${IP}'>"
	echo "<input type='hidden' name='protokol' value='UDP'>"
	echo "<input type='submit' name='Submit' value='Odstrani port'></td></form></tr>"
	echo "<tr>"
        echo "<td><table width="100%"><tr><td><form name='dodaj_tcp-${IP}' method='get' action='$script'>TCP:"
	echo "<input type='hidden' name='protokol' value='TCP'><input type='hidden' name='ip' value='$IP'>"
	echo "<input name='dodaj' type='text' size="10"> <input type='submit' name='Submit' value='Dodaj'></form></td>"
	echo "<td><form name='dodaj_udp_${IP}' method='get' action='$script'>UDP:<input type='hidden' name='protokol' value='UDP'>"
	echo "<input type='hidden' name='ip' value='$IP'><input name='dodaj' type='text' size="10">"
	echo "<input type='submit' name='Submit' value='Dodaj'>"
	echo "</form></td></tr></table></td>"
        echo "<td><form name='odstrani_${IP}' method='get' action='$script'><div align='center'><input type='hidden' name='odstrani_IP' value='${IP}'>"
	echo "<input type='submit' name='Submit' value='Odstrani IP'>"
	echo "</div></form></td></tr></table></td>"
  	echo "</tr></table><br><br></div>"
done

echo "<div align='center'><table width='768'  style='border: thin solid'><tr>"
echo "<td width='120' style='border-right: thin solid'><img src='${d_root}/add.gif' width='120' height='121'></td>"
echo "<td width='92' style='border-right: thin solid'><p>Dodaj IP</p></td>"
echo "<td width='538'><div align='center'> Tu lahko dodate racunalnik, za katerega zelite omogociti deljenje interneta.<br>"
echo "Primer: 192.168.0.3<br><form name='dodaj_IP' method='get' action='$script'>"
echo "<input name='dodaj_IP' type='text' size='15' maxlength='15'><input type='submit' name='Submit' value='Dodaj IP'>"
echo "</form></div></td></tr></table></div>"
}

function dodaj_port () {
tmp_forward=`cat $config | grep FORWARD_${1} | sed -e "s/'//g" | awk -F= '{print $2}'`
rm -f tmpvnos
touch tmpvnos
for vnos in $tmp_forward; do
        IP=`echo $vnos | awk -F- '{ print $1 }'`
        porti=`echo $vnos | awk -F- '{ print $2 }'`
        if [ $FORM_ip = $IP ] ; then
                porti="${porti};${FORM_dodaj}"
        fi
        vnos="${IP}-${porti}"
        echo $vnos >> tmpvnos
done
koncano=`cat tmpvnos`
koncano=`echo $koncano | sed -e "s/\n/ /g"`
grep -v FORWARD_${1} $config > config.new && mv config.new $config
vpisi="FORWARD_${1}='${koncano}'"
vpisi=`echo $vpisi | sed -e "s/-;/-/g" | sed -e "s/; / /g"`
echo $vpisi >> $config
rm -f tmpvnos

#Zagotovi sveze podatke za tabelo ^^
source $config
}

function odstrani_port () {
tmp_forward=`cat $config | grep FORWARD_${1} | sed -e "s/'//g" | awk -F= '{print $2}'`
rm -f tmpvnos
touch tmpvnos
for vnos in $tmp_forward; do
        IP=`echo $vnos | awk -F- '{ print $1 }'`
        porti=`echo $vnos | awk -F- '{ print $2 }'`
        if [ $FORM_ip = $IP ] ; then
                porti=`echo $porti | sed -e "s/$FORM_odstrani_port//g"`
                porti=`echo $porti | sed -e "s/;;/;/g"`
        fi
        vnos="${IP}-${porti}"
        echo $vnos >> tmpvnos
done
koncano=`cat tmpvnos`
koncano=`echo $koncano | sed -e "s/\n/ /g"`
grep -v FORWARD_${1} $config > config.new && mv config.new $config
vpisi="FORWARD_${1}='${koncano}'"
vpisi=`echo $vpisi | sed -e "s/-;/-/g" | sed -e "s/; / /g"`
echo $vpisi >> $config
rm -f tmpvnos

#Zagotovi sveze podatke za tabelo ^^
source $config
}

function dodaj_ip () {
tmp_forward=`cat $config | grep FORWARD_${1} | sed -e "s/'//g" | awk -F= '{print $2}'`
rm -f tmpvnos
touch tmpvnos
status="1"
for vnos in $tmp_forward; do
        IP=`echo $vnos | awk -F- '{ print $1 }'`
        porti=`echo $vnos | awk -F- '{ print $2 }'`
        if [ $FORM_dodaj_IP == $IP ] ; then
                status=0
        fi
done

if [ $status != "0" ]
then
        tmp_forward="$tmp_forward ${FORM_dodaj_IP}-"
fi
grep -v FORWARD_${1} $config > config.new && mv config.new $config
echo "FORWARD_${1}='${tmp_forward}'" >> $config

#Zagotovi sveze podatke za tabelo ^^
source $config
}

function odstrani_ip () {
tmp_forward=`cat $config | grep FORWARD_${1} | sed -e "s/'//g" | awk -F= '{print $2}'`
rm -f tmpvnos
touch tmpvnos
for vnos in $tmp_forward; do
        IP=`echo $vnos | awk -F- '{ print $1 }'`
        porti=`echo $vnos | awk -F- '{ print $2 }'`
        if [ $FORM_odstrani_IP != $IP ] ; then
                vnos="${IP}-${porti}"
		echo $vnos >> tmpvnos
        fi
done
koncano=`cat tmpvnos`
koncano=`echo $koncano | sed -e "s/\n/ /g"`
grep -v FORWARD_${1} $config > config.new && mv config.new $config
vpisi="FORWARD_${1}='${koncano}'"
vpisi=`echo $vpisi | sed -e "s/-;/-/g" | sed -e "s/; / /g"`
echo $vpisi >> $config
rm -f tmpvnos

#Zagotovi sveze podatke za tabelo ^^
source $config
}

#preverjanje vnosnih podatkov
function preveri_vnos () {
if [ -z "$1" ]
then
  status=0
fi

c_ena=`echo $1 |sed -e "s/;/@/g" | sed -e "s/ /_/g"`
case "$c_ena" in
*[a-zA-Z]*) status=0;;  # vsebuje crke
*@*       ) status=0;;  # nedovoljen znak
*-*       ) status=0;;
*_*       ) status=0;;
*         ) status=1;;  # je cist
esac

if [ $status != 0 ]
then
$2 "$3"
else
echo "<p align="center" class="error"><strong>NAPAKA!!! Vas vnos vsebuje prepovedane znake :)</strong></p>"
fi
}

#############################################################################################################################################
#Program:

if [[ "$FORM_Submit" = "Odstrani port" ]]
then
        echo "<p align="center" class="status">Odstranjen port $FORM_odstrani_port IP-ju $FORM_ip :)</p>"
	odstrani_port $FORM_protokol
	naredi_tabelo "$FORWARD_TCP" "$FORWARD_UDP"
elif [[ "$FORM_Submit" = "Odstrani IP" ]]
then
        echo "<p align="center" class="status">Odstranjen IP $FORM_odstrani_IP :)</p>"
	odstrani_ip TCP
	odstrani_ip UDP
	naredi_tabelo "$FORWARD_TCP" "$FORWARD_UDP"
elif [[ "$FORM_Submit" = "Dodaj" ]]
then
        echo "<p align="center" class="status">Dodan $FORM_protokol port $FORM_dodaj za IP $FORM_ip</p>"
	preveri_vnos $FORM_dodaj dodaj_port $FORM_protokol
	naredi_tabelo "$FORWARD_TCP" "$FORWARD_UDP"
elif [[ "$FORM_Submit" = "Dodaj IP" ]]
then
        echo "<p align="center" class="status">Dodan IP $FORM_dodaj_IP :)</p>"
	preveri_vnos $FORM_dodaj_IP dodaj_ip TCP
	preveri_vnos $FORM_dodaj_IP dodaj_ip UDP
        naredi_tabelo "$FORWARD_TCP" "$FORWARD_UDP"
else
        echo "<p align="center" class="status">Pripravljen ... Izberi dejanje :)</p>"
	naredi_tabelo "$FORWARD_TCP" "$FORWARD_UDP"
fi
cat noga
