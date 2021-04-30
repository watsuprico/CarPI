#!/bin/bash

if [ "$EUID" -ne 0 ]
  then tput bold; tput setaf 1; echo "Please run as root"; tput setaf 7
  exit
fi

VERSION="CarPI Version: 3.2 [1]; Updater: 4"



# thanks again stackoverflow
vercomp () {
    if [[ $1 == $2 ]]
    then
        return 0
    fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    # fill empty fields in ver1 with zeros
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++))
    do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++))
    do
        if [[ -z ${ver2[i]} ]]
        then
            # fill empty fields in ver2 with zeros
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]}))
        then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]}))
        then
            return 2
        fi
    done
    return 0
}

doupdate () { # doupdate currentVer targetVer
    vercomp $1 $2
    op='0'
    case $? in
        0) op='0';;
        1) op='0';;
        2) op='1';;
    esac
}

readVer= cat /var/CarPI/version
curVer=${readVer:-echo "3.2.1"} # probably a better way, idunno
newVer= curl -L https://resources.cnewb.co/CarPI/version.txt
targetVer=${newVer:-echo "0.0"}

doupdate $curVer $newVer
echo "Update needed?" $op
if [[ $op == 0 ]]
then
	echo "Update not needed."
	exit
fi

mkdir /var/www/ > /dev/null 2>&1
mkdir /var/www/html/ > /dev/null 2>&1
mkdir /var/www/html/logs/ > /dev/null 2>&1
mkdir /var/CarPI/ > /dev/null 2>&1


curl -s https://resources.cnewb.co/CarPI/directoryList.txt > /tmp/directoryList.txt
while read -r URL; do
	mkdir /var/CarPI/$URL > /dev/null 2>&1
	echo Creating dir: $URL
done < /tmp/directoryList.txt

# {
# 	curl -s https://resources.cnewb.co/CarPI/downloadList.txt > /tmp/downloadList.txt
# 	LENGTH=`sed -n '$=' /tmp/downloadList.txt`
# 	I=1
# 	while read -r URL; do
# 		PERCENT=$(echo $I $LENGTH | awk '{ print $1/$2 * 100 }')
# 		PERCENT=$(echo $PERCENT | awk '{ printf "%.0f\n", $1 }')
# cat <<EOF
# XXX
# $PERCENT
# Downloading: $URL ($I / $LENGTH)
# XXX
# EOF
# 		curl -sS http://resources.cnewb.co/CarPI/$URL > /var/CarPI/$URL
# 		I=$(($I + 1))
# 	done < /tmp/downloadList.txt

# cat <<EOF
# XXX
# 100
# Downloaded files.
# XXX
# EOF
# } | whiptail --title "CarPI File Update" --backtitle "$VERSION  --  Downloading files" --gauge "Downloading ..." 10 100 0

echo "Downloading tar..."
wget -O /var/CarPI/carpi.tar https://resources.cnewb.co/CarPI/carpi.tar
tar -C /var/CarPI/ -xvf /var/CarPI/carpi.tar

{
cat <<EOF
XXX
0
Moving CGI-BIN Script over
XXX
EOF
	mv /var/CarPI/Web/mediaControl2CGI.py /usr/lib/cgi-bin/mediaControl2CGI.py > /dev/null 2>&1

	
cat <<EOF
XXX
12.5
Moving web file: css/
XXX
EOF
	mv /var/CarPI/Web/css/ /var/www/html/css/ > /dev/null 2>&1

cat <<EOF
XXX
25
Moving web file: fonts/
XXX
EOF
	mv /var/CarPI/Web/fonts/ /var/www/html/fonts/ > /dev/null 2>&1

cat <<EOF
XXX
37.5
Moving web file: resources/
XXX
EOF
	mv /var/CarPI/Web/resources/ /var/www/html/resources/ > /dev/null 2>&1

cat <<EOF
XXX
50
Moving web file: index.html
XXX
EOF
	mv /var/CarPI/Web/index.html /var/www/html/index.html > /dev/null 2>&1

cat <<EOF
XXX
62.5
Moving web file: style.css
XXX
EOF
	mv /var/CarPI/Web/style.css /var/www/html/style.css > /dev/null 2>&1


cat <<EOF
XXX
75
Applying permissions
XXX
EOF
	chmod -R 777 /var/www/html/
	chmod -R 777 /var/www/html/logs/
	chmod -R 777 /var/CarPI/

cat <<EOF
XXX
87.5
Registering services
XXX
EOF
	systemctl enable /var/CarPI/carpi_web.service > /dev/null 2>&1
	systemctl enable /var/CarPI/carpi_obd-ii.service > /dev/null 2>&1


cat <<EOF
XXX
100
CarPI files updated
XXX
EOF
sleep 1s
} | whiptail --title "CarPI File Update" --backtitle "$VERSION  --  Finalizing" --gauge "Updating ..." 10 60 0

if [ "`systemctl is-active carpi_web`" != "active" ]; then
  systemctl start carpi_web
else
  systemctl restart carpi_web
fi
if [ "`systemctl is-active carpi_obd-ii`" != "active" ]; then
  systemctl start carpi_obd-ii
else
  systemctl restart carpi_obd-ii
fi

systemctl status carpi_web
systemctl status carpi_obd-ii

# whiptail --title "CarPI Installation" --backtitle "$VERSION" --msgbox "Completed" 10 60