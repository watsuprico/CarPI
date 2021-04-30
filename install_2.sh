#!/bin/bash

if [ "$EUID" -ne 0 ]
  then tput bold; tput setaf 1; echo "Not running as root, restarting . . ."; tput setaf 7
  exec sudo /bin/bash "$0" "$@"
  exit
fi

VERSIONI="CarPI Version: 3; Installer: 1"

echo heartbeat >/sys/class/leds/led0/trigger
sleep 1s
echo heartbeat >/sys/class/leds/led1/trigger

tput bold; tput setaf 2; echo "Updating CarPI files"; tput setaf 7
bash <(curl -s https://resources.cnewb.co/CarPI/updateCarPIFiles.sh)


# https://www.reddit.com/r/raspberry_pi/comments/28ogmo/i_made_my_pi_an_incar_bluetooth_audio_receiver/
# https://freedesktop.org/wiki/Software/PulseAudio/Documentation/User/Bluetooth/
# https://scribles.net/enabling-hands-free-profile-on-raspberry-pi-raspbian-stretch-by-using-pulseaudio/

whiptail --title "CarPI Installation" --backtitle "$VERSIONI" --yesno "Use USB audio? This will disable the onboard audio" 20 60 2
if [ $? -eq 0 ]; then # yes
	tput bold; tput setaf 3; echo "Blacklisting onboard audio"; tput setaf 7
	echo "blacklist snd_bcm2835">>/etc/modprobe.d/raspi-blacklist.conf
	tput bold; tput setaf 3; echo "Fixing audio stuff (allowing usb audio)"; tput setaf 7
	sed -i '/options snd-usb-audio index=-2/s/^/#/g' /lib/modprobe.d/aliases.conf
	echo options snd-usb-audio index=0 >> /lib/modprobe.d/aliases.conf
	echo options snd_bcm2835 index=1 >> /lib/modprobe.d/aliases.conf
	echo options snd-usb-audio index=0 >> /etc/modprobe.d/alsa-base.conf
	echo options snd_bcm2835 index=1 >> /etc/modprobe.d/alsa-base.conf
fi


#python-gobject python-gobject-2 --fix-missing -y

# tput bold; tput setaf 2; echo "Installing bt_speaker.py"; tput setaf 7
# bash <(curl -s https://raw.githubusercontent.com/lukasjapan/bt-speaker/master/install.sh)
# tput bold; tput setaf 6; echo "Copying bt_speaker.py file"; tput setaf 7
# cp /var/CarPI/bt_speaker.py /opt/bt-speaker/bt_speaker.py
# chmod 777 /opt/bt-speaker/bt_speaker.py

tput bold; tput setaf 2; echo "Installing bluez and bluez-tools"; tput setaf 7
apt-get install bluez bluez-tools --fix-missing -y

tput bold; tput setaf 2; echo "Installing bluetooth phone utilities (ofono)"; tput setaf 7
apt-get install ofono --fix-missing -y
sudo systemctl start ofono

tput bold; tput setaf 3; echo "Installing PulseAudio"; tput setaf 7
sudo apt-get install pulseaudio pulseaudio-module-bluetooth --fix-missing -y

tput bold; tput setaf 3; echo "Patching PulseAudio and oFono"; tput setaf 7
sed -i -e '$i \load-module module-bluetooth-discover\n' /etc/pulse/system.pa
sed -i -e '$i \load-module module-bluetooth-policy\n' /etc/pulse/system.pa
adduser pulse bluetooth
sed -i -e '$i \  <policy user="pulse">\n    <allow send_destination="org.ofono"/>\n  </policy>\n' /etc/dbus-1/system.d/ofono.conf

if [ -e /usr/local/etc/pulse/default.pa ]
then
  echo "Configuring /usr/local/bin/pulseaudio to use ofono as headset backend"
  sed -i 's/module-bluetooth-discover$/module-bluetooth-discover headset=ofono/' /usr/local/etc/pulse/default.pa
fi

if [ -e /etc/pulse/default.pa ]
then
  echo "Configuring /usr/bin/pulseaudio to use ofono as headset backend"
  sed -i 's/module-bluetooth-discover$/module-bluetooth-discover headset=ofono/' /etc/pulse/default.pa
fi


tput bold; tput setaf 3; echo "Fixing up PulseAudio"; tput setaf 7
# Authorize PulseAudio - which will run as user pulse - to use BlueZ D-BUS interface:
cat <<EOF >/etc/dbus-1/system.d/pulseaudio-bluetooth.conf
<busconfig>

  <policy user="pulse">
    <allow send_destination="org.bluez"/>
    <allow send_destination="org.ofono"/>
  </policy>

</busconfig>
EOF
# cat <<EOF >/etc/systemd/system/pulseaudio.service
# [Unit]
# Description=Pulse Audio

# [Service]
# Type=simple
# ExecStart=/usr/bin/pulseaudio --system --disallow-exit --disable-shm --exit-idle-time=-1

# [Install]
# WantedBy=multi-user.target
# EOF
# systemctl daemon-reload
# systemctl enable pulseaudio.service


tput bold; tput setaf 3; echo "Applying fixes from some Reddit post ( https://www.reddit.com/r/raspberry_pi/comments/28ogmo/i_made_my_pi_an_incar_bluetooth_audio_receiver/ / https://goo.gl/kruLQ6 )"; tput setaf 7
echo 'ACTION=="add", KERNEL=="hci0", RUN+="/usr/bin/hciconfig hci0 up"' >> /etc/udev/rules.d/10-local.rules

cat <<EOF >/lib/systemmd/system/bluepower.target
[Unit]
Description=Bluetooth power keeper
Requires=sys-subsystem-bluetooth-devices-%i.device bluetooth.service
PartOf=sys-subsystem-bluetooth-devices-%i.device
After=bluetooth.service sys-subsystem-bluetooth-devices-%i.device suspend.target
Conflicts=shutdown.target systemd-sleep.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/dbus-send --system --type=method_call --dest=org.bluez /org/bluez/%I org.freedesktop.DBus.Properties.Set string:org.bluez.Adapter1 string:Powered variant:boolean:true
ExecStop=/usr/bin/dbus-send --system --type=method_call --dest=org.bluez /org/bluez/%I org.freedesktop.DBus.Properties.Set string:org.bluez.Adapter1 string:Powered variant:boolean:false

[Install]
WantedBy=bluetooth.target
EOF
systemctl enable bluepower.target
# echo '[Service]' >> /etc/systemd/system/getty@tty1.service.d/autologin.conf
# echo 'ExecStart=' >> /etc/systemd/system/getty@tty1.service.d/autologin.conf
# echo 'ExecStart=-/usr/bin/agetty --autologin pi --noclear %I 38400 linux' >> /etc/systemd/system/getty@tty1.service.d/autologin.conf

# # echo 'pulseaudio -D' >> /home/pi/.bashrc
# echo 'sudo pulseaudio --system &' >> /home/pi/.bashrc # Running as root seems to fix my call audio problems




tput bold; tput setaf 3; echo "Applying user patch"; tput setaf 7
sudo usermod -a -G lp pi


tput bold; tput setaf 2; echo "Installing required python stuff"; tput setaf 7
apt-get install git python-bluez bluez python python-gobject python-cffi python-dbus python-alsaaudio python-configparser sound-theme-freedesktop vorbis-tools --fix-missing -y



# Startup scripts, such as auto connect (obsolete)
# tput bold; tput setaf 3; echo "Adding startup line to rc.local"; tput setaf 7
# sed -i -e '$i \sudo chmod 777 /var/www/html/logs/startup &\n' /etc/rc.local
# sed -i -e '$i \sudo bash /var/CarPI/startup.sh >> /var/www/html/logs/startup\n' /etc/rc.local



# Set things so I can just cut power any time
sudo dphys-swapfile swapoff
sudo dphys-swapfile uninstall
sudo update-rc.d dphys-swapfile remove




# tput bold; tput setaf 3; echo "Enabling services"; tput setaf 7
# cp /var/CarPI/carpi_web.service /etc/systemd/system/
# cp /var/CarPI/carpi_obd-ii.service /etc/systemd/system/
# systemctl enable carpi_web.service
# systemctl enable carpi_obd-ii.service


whiptail --title "CarPI Installation" --backtitle "$VERSIONI" --yesno "Are you going to be using the web features such as remote control? (Yes > install web based tools ; No > finished)" 20 60 2
if [ $? -eq 0 ]; then # yes
	tput bold; tput setaf 2; echo "Installing required python stuff"; tput setaf 7
	apt-get install python-pip --fix-missing -y
	pip install termcolor

	tput bold; tput setaf 2; echo "Installing Pigpio"; tput setaf 7
	apt-get install pigpio python-pigpio python3-pigpio --fix-missing -y
	# sed -i -e '$i \sudo pigpiod & >> /var/www/html/logs/startup\n' 

	tput bold; tput setaf 2; echo "Installing OBD-Pi"; tput setaf 7
	apt-get install python-serial --fix-missing -y
	apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n libwxgtk2.8-dev --fix-missing -y
	apt-get install git-core --fix-missing -y

	tput bold; tput setaf 2; echo "Installing Apache2"; tput setaf 7
	apt-get install apache2 apache2-utils --fix-missing -y

	tput bold; tput setaf 2; echo "Installing MySQL"; tput setaf 7
	apt-get install mariadb-server-10.0 --fix-missing -y
	# apt-get install mysql-server --fix-missing -y
	whiptail --title "CarPI Installation" --backtitle "$VERSIONI" --msgbox "Next you'll setup a few things for MySQL" 20 60 2
	sudo mysql_secure_installation
	tput bold; tput setaf 2; echo "Installing PHP"; tput setaf 7
	apt-get install php-mysql php libapache2-mod-php --fix-missing -y

	tput bold; tput setaf 3; echo "Enabling CGI-BIN"; tput setaf 7
	cd /etc/apache2/mods-enabled
	ln -s ../mods-available/cgi.load
	tput bold; tput setaf 6; echo "Copying CGI-BIN script"; tput setaf 7
	cp /var/CarPI/Web/mediaControl2CGI.py /usr/lib/cgi-bin/mediaControl2CGI.py
	chmod 777 /usr/lib/cgi-bin/mediaControl2CGI.py

	tput bold; tput setaf 3; echo "Restarting Apache2"; tput setaf 7
	service apache2 reload

	whiptail --title "CarPI Installation" --backtitle "$VERSIONI" --yesno "Install and setup WiFi hotspot? (This is required for web based control in the car, unless you already have a network infrastructure in your car)" 20 60 2
	if [ $? -eq 0 ]; then # yes
		rfkill unblock wlan
		tput bold; tput setaf 6; echo "Installing dnsmasq and hostapd"; tput setaf 7
		sudo apt-get install dnsmasq hostapd -y
		sudo systemctl unmask hostapd
		sudo systemctl enable hostapd
		tput bold; tput setaf 6; echo "Stopping newly installed services"; tput setaf 7
		systemctl stop dnsmasq
		systemctl stop hostapd
		tput bold; tput setaf 6; echo "Configuring static IP"; tput setaf 7
		sed -i -e '$i \denyinterfaces wlan0\n' /etc/dhcpcd.conf
		sed -i -e '$i \allow-hotplug wlan0\niface wlan0 inet static\n    address 192.168.4.1\n    netmask 255.255.255.0\n    network 192.168.4.0\n' /etc/network/interfaces
		service dhcpcd restart
		ifdown wlan0
		ifup wlan0

		sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
		echo auto lo >> /etc/network/interfaces
		echo iface lo inet loopback >> /etc/network/interfaces
		echo auto eth0 >> /etc/network/interfaces
		echo iface eth0 inet dhcp >> /etc/network/interfaces
		echo interface=wlan0 >> /etc/dnsmasq.conf
		echo dhcp-range=192.168.4.2,192.168.4.22,255.255.255.0,24h >> /etc/dnsmasq.conf
		echo domain=carpi.com >> /etc/dnsmasq.conf

		# Disable ipv6
		echo net.ipv6.conf.all.disable_ipv6 = 1 >> /etc/sysctl.conf
		echo net.ipv6.conf.default.disable_ipv6 = 1 >> /etc/sysctl.conf


		echo country_code=US > /etc/hostapd/hostapd.conf
		echo interface=wlan0 >> /etc/hostapd/hostapd.conf
		echo driver=nl80211 >> /etc/hostapd/hostapd.conf
		echo ssid=CarPI WiFi >> /etc/hostapd/hostapd.conf
		echo hw_mode=g >> /etc/hostapd/hostapd.conf
		echo channel=7 >> /etc/hostapd/hostapd.conf
		echo wmm_enabled=0 >> /etc/hostapd/hostapd.conf
		echo macaddr_acl=0 >> /etc/hostapd/hostapd.conf
		echo auth_algs=1 >> /etc/hostapd/hostapd.conf
		echo ignore_broadcast_ssid=0 >> /etc/hostapd/hostapd.conf
		echo wpa=2 >> /etc/hostapd/hostapd.conf
		echo wpa_passphrase=t3@cher01 >> /etc/hostapd/hostapd.conf
		echo wpa_key_mgmt=WPA-PSK >> /etc/hostapd/hostapd.conf
		echo wpa_pairwise=TKIP >> /etc/hostapd/hostapd.conf
		echo rsn_pairwise=CCMP >> /etc/hostapd/hostapd.conf

		sed -i 's\#DAEMON_CONF=""\DAEMON_CONF="/etc/hostapd/hostapd.conf"\g' /etc/default/hostapd



		# IP tables stuff for bluetooth tether

		echo net.ipv4.ip_forward=1 > /etc/sysctl.d/routed-ap.conf

		sed -i 's/#net.ipv4.ip_forward=1$/net.ipv4.ip_forward=1/' /etc/sysctl.conf
		iptables -t nat -A POSTROUTING -o bnep0 -j MASQUERADE
		sh -c "iptables-save > /etc/iptables.ipv4.nat"
		sed -i -e '$i \sudo iptables-restore < /etc/iptables.ipv4.nat\n' /etc/rc.local
		
		# apt-get install bridge-utils --fix-missing -y
		# brctl addbr br0
		# brctl addif br0 bnep0
		# sed -i -e '$i \auto br0\n' /etc/network/interfaces
		# sed -i -e '$i \iface br0 inet manual\n' /etc/network/interfaces
		# sed -i -e '$i \bridge_ports eth0 wlan0\n' /etc/network/interfaces



		service hostapd start
		service dnsmasq start
	fi
fi





whiptail --title "CarPI Installation" --backtitle "$VERSIONI" --yesno "All complete. Please reboot and verify that all is operational. Reboot now?" 20 60 2
if [ $? -eq 0 ]; then # yes
	sync
    reboot
fi

tput bold; tput setaf 2; echo "All should be complete. Please reboot and check that all is operational."; tput setaf 7
cd ~