#!/bin/bash

if [ "$EUID" -ne 0 ]
  then tput bold; tput setaf 1; echo "Not ROOT... opening as root..."; tput setaf 7
  curl -s https://resources.cnewb.co/CarPI/install.sh | sudo su
  exit
fi

BLACKLIST=/etc/modprobe.d/raspi-blacklist.conf
CONFIG=/boot/config.txt

VERSIONI="CarPI Version: 3; Installer: 1"

set_config_var() {
  lua - "$1" "$2" "$3" <<EOF > "$3.bak"
local key=assert(arg[1])
local value=assert(arg[2])
local fn=assert(arg[3])
local file=assert(io.open(fn))
local made_change=false
for line in file:lines() do
  if line:match("^#?%s*"..key.."=.*$") then
    line=key.."="..value
    made_change=true
  end
  print(line)
end

if not made_change then
  print(key.."="..value)
end
EOF
mv "$3.bak" "$3"
}

clear_config_var() {
  lua - "$1" "$2" <<EOF > "$2.bak"
local key=assert(arg[1])
local fn=assert(arg[2])
local file=assert(io.open(fn))
for line in file:lines() do
  if line:match("^%s*"..key.."=.*$") then
    line="#"..line
  end
  print(line)
end
EOF
mv "$2.bak" "$2"
}

get_config_var() {
  lua - "$1" "$2" <<EOF
local key=assert(arg[1])
local fn=assert(arg[2])
local file=assert(io.open(fn))
local found=false
for line in file:lines() do
  local val = line:match("^%s*"..key.."=(.*)$")
  if (val ~= nil) then
    print(val)
    found=true
    break
  end
end
if not found then
   print(0)
end
EOF
}

tput bold; tput setaf 2; echo "Updating Raspberry PI"; tput setaf 7
apt-get update
apt-get upgrade -y --fix-missing

tput bold; tput setaf 2; echo "Downloading install_2.sh"; tput setaf 7
curl -sS https://resources.cnewb.co/CarPI/install_2.sh > /home/pi/install_2.sh
chmod 777 /home/pi/install_2.sh

tput bold; tput setaf 2; echo "Installing FTP server"; tput setaf 7

apt-get install pure-ftpd -y
groupadd ftpgroup
useradd ftpuser -g ftpgroup -s /sbin/nologin -d /dev/null

tput bold; tput setaf 2; echo "Changing password"; tput setaf 7
echo 'pi:CarPI' | chpasswd
tput bold; tput setaf 2; echo "User Root"; tput setaf 7
echo 'root:CarPI' | chpasswd

tput bold; tput setaf 2; echo "Console on boot"; tput setaf 7
systemctl set-default multi-user.target
ln -fs /lib/systemd/system/getty@.service /etc/systemd/system/getty.target.wants/getty@tty1.service

tput bold; tput setaf 2; echo "Changing hostname"; tput setaf 7
CURRENT_HOSTNAME=`cat /etc/hostname | tr -d " \t\n\r"`
NEW_HOSTNAME="CarPI"
tput bold; tput setaf 2; echo $NEW_HOSTNAME > /etc/hostname; tput setaf 7
sed -i "s/127.0.1.1.*$CURRENT_HOSTNAME/127.0.1.1\t$NEW_HOSTNAME/g" /etc/hosts

tput bold; tput setaf 2; echo "Disabling VNC"; tput setaf 7
systemctl disable vncserver-x11-serviced.service &&
systemctl stop vncserver-x11-serviced.service &&

tput bold; tput setaf 2; echo "Disabling serial"; tput setaf 7
sed -i $CMDLINE -e "s/console=ttyAMA0,[0-9]\+ //"
sed -i $CMDLINE -e "s/console=serial0,[0-9]\+ //"
set_config_var enable_uart 0 $CONFIG

tput bold; tput setaf 2; echo "Disabling wait for network"; tput setaf 7
rm -f /etc/systemd/system/dhcpcd.service.d/wait.conf

tput bold; tput setaf 2; echo "Disabling Pi camera"; tput setaf 7
set_config_var start_x 0 $CONFIG
sed $CONFIG -i -e "s/^start_file/#start_file/"

tput bold; tput setaf 2; echo "Disabling one-wire"; tput setaf 7
sed $CONFIG -i -e "s/^dtoverlay=w1-gpio/#dtoverlay=w1-gpio/"

tput bold; tput setaf 2; echo "Forcing audio output"; tput setaf 7
amixer cset numid=3 "1"

whiptail --title "CarPI Installation" --backtitle "$VERSIONI" --msgbox "Please expand the filesystem using raspi-config (which will load next). Afterwards, reboot and run 'sudo bash install_2.sh'" 20 60 1
raspi-config

whiptail --title "CarPI Installation" --backtitle "$VERSIONI" --yesno "You need to reboot, afterwards please run 'sudo bash install_2.sh'. Would you like to reboot now?" 20 60 2
if [ $? -eq 0 ]; then # yes
	sync
    reboot
fi

tput bold; tput setaf 2; echo "Please reboot and run install 2 afterwards"; tput setaf 7