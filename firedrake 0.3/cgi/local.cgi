#!/bin/bash
echo "content-type: text/html"
echo

#nalozi config
config="`pwd`/config"
source $config
cat glava
script=localScript

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
#generiraj tabelo:
echo "$2 porti:<br>"
echo '<table width="100%" style="border: thin solid" align="center">'
echo "<tr>"
echo "<td width='90' style='border: thin solid'><b>Port </b>(ali range)</td>"
echo "<td style='border: thin solid'><b> IPji ali hosti, za katere je port odprt</b></td>"
echo "<td width='90' style='border: thin solid'> Opcija </td>"
echo "<td width='63' style='border: thin solid'>Opcija</td>"
echo "</tr>"

for vnos in $1; do
        port=`echo $vnos | awk -F- '{ print $1 }'`
        ipji=`echo $vnos | awk -F- '{ print $2 }'`
	ipji=`echo $ipji | sed -e "s/;/ /g"`
        echo '<tr>'
	if [[ $ipji = 0/0 ]]; then
        	echo "<td width='90' style='border: thin solid'>${port}</td>"
		echo "<td style='border: thin solid'>odprt za javnost</td>"
		echo "<td width='90' style='border: thin solid'><div align='center'>x</div></td>"
                echo "<td width='63' style='border: thin solid'><form name='odstrani_${port}' method='get' action='$script'>"
                echo "<input type='hidden' name='protokol' value='$2'>"
		echo "<input type='hidden' name='delete_port' value='$port'> <input type='submit' name='Submit' value='Odstrani'> </form>"
                echo "</td>"
        else
        	echo "<td width='90' style='border: thin solid'>${port}</td>"
     		echo "<form name='ipji_${port}' method='get' action='${script}'><td style='border: thin solid'>"
		echo "<input type='hidden' name='delete_from' value='$port'><input type='hidden' name='protokol' value='$2'>"
		for ip in $ipji; do
			echo "<input name='delete_IP' type='radio' value='${ip}'>${ip}<br> "
		done
		echo "</td>"
                echo "<td width='90' style='border: thin solid'>"
		echo "<input type='submit' name='Submit' value='Brisi izbrano'> </form>"
		echo "</td>"
       		echo "<td width='63' style='border: thin solid'><form name='odstrani_${port}' method='get' action='$script'>"
		echo "<input type='hidden' name='protokol' value='$2'>"
		echo "<input type='hidden' name='delete_port' value='$port'> <input type='submit' name='Submit' value='Odstrani'> </form>"
		echo "</td>"

        fi
	echo '</tr>'
done
echo "<tr>"
echo "<form name='dodaj_port' method='get' action='$script'><td width='90' style='border: thin solid'>"
echo "Port (22) ali range (22:24)<br><input type='text' size='11' maxlength='11' name='dodaj_port' value='22'></td>"
echo "<td style='border: thin solid'>IPji ali hosti, loceni s presledkom! Javni port (odprt za vse) = <b>prazno</b> <br><br><input name='dodaj_IP' type='text' size="50" value='216.239.37.99 81.91.109.74'></td>"
echo "<td width='90' style='border: thin solid'><div align='center'>x</div></td>"
echo "<td width='63' style='border: thin solid'><input type='hidden' name='protokol' value='$2'>"
echo "<input type='submit' name='Submit' value='Dodaj' onClick='window.location.reload()'></td></form>"
echo "</tr>"
echo '</table>'
}

#DODAJ PORT ali HOST PORTU
function dodaj_port() {
#iz configa preberi spremenljivko ODPRI_* in iz nje izloci vsebino
tmp_odpri=`cat $config | grep ODPRI_${1} | sed -e "s/'//g" | awk -F= '{print $2}'`

#zagotovi obstoj in korektnost zacasne datoteke
rm -f tmpvnos
touch tmpvnos

#zanka: za vsak port v configu preveri, ce dodajani port obstaja in ce, mu dodaj vrednosti
for vnos in $tmp_odpri; do
        port=`echo $vnos | awk -F- '{ print $1 }'`
        ipji=`echo $vnos | awk -F- '{ print $2 }'`
        if [ $FORM_dodaj_port = $port ] ; then

                #ce je port brez IPjev, odstrani 0/0, ki to oznacuje :)
                ipji=`echo $ipji | sed -e "s:0/0::g"`

                #ce IP ze obstaja, ga pobrisi :)
                for ip in $FORM_dodaj_IP; do
                        ipji=`echo $ipji | sed -e "s/$ip//g"`
			$iptables -D INPUT -p $1 -s $ip --dport $port -j ACCEPT
			$iptables -A INPUT -p $1 -s $ip --dport $port -j ACCEPT
                done
                FORM_dodaj_IP=`echo $FORM_dodaj_IP | tr " " ";"`
                ipji="${ipji};${FORM_dodaj_IP}"
        fi
        vnos="${port}-${ipji}"
        echo $vnos >> tmpvnos
done

if [ -ne $(cat tmpvnos | grep $FORM_dodaj_port) ]; then
#port ne obstaja
	for ip in $FORM_dodaj_IP; do
		$iptables -D INPUT -p $1 -s $ip --dport $FORM_dodaj_port -j ACCEPT
                $iptables -A INPUT -p $1 -s $ip --dport $FORM_dodaj_port -j ACCEPT
	done
        FORM_dodaj_IP=`echo $FORM_dodaj_IP | tr " " ";"`
        echo "${FORM_dodaj_port}-${FORM_dodaj_IP}" >> tmpvnos
fi

koncano=`cat tmpvnos`
koncano=`echo $koncano | sed -e "s/\n/ /g" | sed -e "s/-;/-/g" | sed -e "s:${FORM_dodaj_port}- :${FORM_dodaj_port}-0/0 :g"`
grep -v ODPRI_${1} $config > config.new && mv config.new $config
zadnji="ODPRI_${1}='${koncano}'"
zadnji=`echo $zadnji | sed -e "s:${FORM_dodaj_port}-':${FORM_dodaj_port}-0/0':g"`
echo $zadnji >> $config
rm -f tmpvnos
}

#PORTU ODSTRANI HOST
function odstrani_host() {
#iz configa preberi spremenljivko ODPRI_* in iz nje izloci vsebino
tmp_odpri=`cat $config | grep ODPRI_${1} | sed -e "s/'//g" | awk -F= '{print $2}'`

#tagotovi obstoj in korektnost zacasne datoteke
rm -f tmpvnos
touch tmpvnos

#zanka: poisce izbrani port in mu odstrani zeljeni host
        for vnos in $tmp_odpri; do
        port=`echo $vnos | awk -F- '{ print $1 }'`
        ipji=`echo $vnos | awk -F- '{ print $2 }'`
        if [ $FORM_delete_from = $port ] ; then
        	ipji=`echo $ipji | sed -e "s/$FORM_delete_IP//g" | sed -e "s/;;/;/g"`
		$iptables -D INPUT -p $1 -s $FORM_delete_IP --dport $FORM_delete_from -j ACCEPT
        fi
        vnos="${port}-${ipji}"
	#vnos=`echo $vnos | sed -e "s:${port}- :${port}-0/0:g"`
        echo $vnos >> tmpvnos
done

koncano=`cat tmpvnos`
koncano=`echo $koncano | sed -e "s/\n/ /g" | sed -e "s/-;/-/g" | sed -e "s:${FORM_delete_from}- :${FORM_delete_from}-0/0 :g"`
koncano=`echo $koncano | sed -e "s/; / /g"`
grep -v ODPRI_${1} $config > config.new && mv config.new $config
zadnji="ODPRI_${1}='${koncano}'"
zadnji=`echo $zadnji | sed -e "s:${FORM_delete_from}-':${FORM_delete_from}-0/0':g" | sed -e "s/;'/'/g"`
echo $zadnji >> $config
rm -f tmpvnos

#Zagotovi sveze podatke za tabelo ^^
#source $config
}

#ODSTRANI PORT
function odstrani_port() {
#iz configa preberi spremenljivko ODPRI_* in iz nje izloci vsebino
tmp_odpri=`cat $config | grep ODPRI_${1} | sed -e "s/'//g" | awk -F= '{print $2}'`

#tagotovi obstoj in korektnost zacasne datoteke
rm -f tmpvnos
touch tmpvnos

#zanka: poisce izbrani port in mu odstrani zeljeni host
for vnos in $tmp_odpri; do
        port=`echo $vnos | awk -F- '{ print $1 }'`
        ipji=`echo $vnos | awk -F- '{ print $2 }'`
	if [ $FORM_delete_port != $port ] 
	then
                vnos="${port}-${ipji}"
                echo $vnos >> tmpvnos
	else
		ipji=`echo $ipji | tr ";" " "`
		for ip in $ipji; do
			$iptables -D INPUT -p $1 -s $ip --dport $FORM_delete_port -j ACCEPT
		done
        fi
done

koncano=`cat tmpvnos`
koncano=`echo $koncano | sed -e "s/\n/ /g"`
grep -v ODPRI_${1} $config > config.new && mv config.new $config
echo "ODPRI_${1}='${koncano}'" >> $config
rm -f tmpvnos

#Zagotovi sveze podatke za tabelo ^^
#source $config
}

#preverjanje vnosnih podatkov
function preveri_vnos () {
if [ -z "$1" ]
then
  status=0
fi

c_ena=`echo $1 |sed -e "s/;/@/g"`
case "$c_ena" in
*[a-zA-Z]*) status=0;;  # vsebuje crke
*@*       ) status=0;;  # nedovoljen znak
*-*       ) status=0;;
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
source $config
if [[ "$FORM_Submit" = "Odstrani" ]] 
then
	odstrani_port $FORM_protokol
	echo "<p align="center" class="status">izbrali ste odstranitev porta $FORM_delete_port :) </p>"
	source $config
	#klic funkcije za izris tabele
	naredi_tabelo "$ODPRI_TCP" TCP
	echo "<br>"
	naredi_tabelo "$ODPRI_UDP" UDP

elif [[ "$FORM_Submit" = "Brisi izbrano" ]]
then
	odstrani_host $FORM_protokol
	echo "<p align="center" class="status">Portu ${FORM_delete_from} odstranjen $FORM_delete_IP :) </p>"
	source $config
	#klic funkcije za izris tabele
	naredi_tabelo "$ODPRI_TCP" TCP
	echo "<br>"
	naredi_tabelo "$ODPRI_UDP" UDP

elif [[ "$FORM_Submit" = "Dodaj" ]]
then
	echo "<p align="center" class="status">dodan $FORM_protokol port ${FORM_dodaj_port}, omejen z ${FORM_dodaj_IP} :)</p>"
	preveri_vnos "$FORM_dodaj_IP" dodaj_port $FORM_protokol
	source $config
	#klic funkcije za izris tabele
	naredi_tabelo "$ODPRI_TCP" TCP
	echo "<br>"
	naredi_tabelo "$ODPRI_UDP" UDP

else
	echo "<p align="center" class="status">Pripravljen ... Izberi dejanje :)</p>"
	#klic funkcije za izris tabele
	naredi_tabelo "$ODPRI_TCP" TCP
	echo "<br>"
	naredi_tabelo "$ODPRI_UDP" UDP

fi
cat noga
