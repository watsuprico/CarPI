#!/usr/bin/python

# CarPI Web Host
# CarPI is a project developed by Watsuprico
# CarPI's objective is to make interfacing between the raspberry pi and car, driver and raspberry pi, and driver and raspberry pi easier
#	(Add bluetooth media streaming, utilize steering wheel controls to influence bluetooth media, and to interface with under-dash illumination (either with user settings or car data, like RPM))

# for some reason my leds over do the blue, R255 G255 and B100 make white



'''

TODO:

WLan0 -> BNEP0 bridge

For some reason, add a listener to dbus causes property lookups to fail ..? fix this

Notify user (audible tone) when a device connects/disconnects


Auto update script? When a bluetooth device comes online with NAP connection, begin the update process
	(IDEA:
	updateCarPI.sh
		After retrieving a NAP connection, run script
		Script checks current version (/var/CarPI/version) against latest public version (github.com?? fails-> resources.cnewb.co)
		If outdated, run latest version of /var/CarPI/updateCarPIFiles.sh?? (bash <(curl ))


	
	)

'''



# Setup
from __future__ import division

import subprocess
subprocess.Popen('sudo pigpiod', shell=True)




from termcolor import colored # Allow color in the term
debug = True
def debugPrint(message):
	if debug:
		print colored("[DEBUG] "+message, "yellow")

# Allow any characters (like jap ones)
import traceback
import sys
import os
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)


# Get commands from the CGI script
import socket
from threading import *
# Our end
CGISocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CGISocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
CGISocket.bind(("localhost", 8002))


# Bluetooth control
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)


from btadapter import BTAdapter
from btdevice import BTDevice,BTPlayer,BTPlayerItem,BTPlayers,BTPlayerItems,BTDevices
# from btagent import BTAgent, BTAgentManager
adapter = BTAdapter('hci0')


# LED Control
import LED

# OBDII
RPM="0"
SPEED="0"
ENGINE_LOAD="0"
COOLANT_TEMP="0"
FUEL_LEVEL="0"
AMBIANT_AIR_TEMP="0"

import json
import multiprocessing
from time import sleep
# Setup complete


def doUpdate():
	subprocess.Popen("curl -s https://resources.cnewb.co/CarPI/updateCarPIFiles.sh | sudo su")



print "Starting..."



print "Starting Pulse Audio...",
# Start Pulseaudio... (required for media / phone audio sink)
subprocess.Popen("sudo -u pi pulseaudio --start", shell=True) # This is required for the audio subsystem to work properly.
# I found that having pulse start by itself (somehow) would cause it to NOT accept phone audio (but it will accept media audio)
# By starting pulse here I KNOW it is running under the right user etc etc, (look bro, it just works this way)
print "done"



print "Setting bluetooth agent...",
subprocess.Popen("sudo hciconfig hci0 sspmode 0", shell=True) # Set SSPMode (required, )
subprocess.Popen("sudo python /var/CarPI/BTAgent.py", shell=True) # This allows unknown devices to connect IF they have the correct password.
print "done"

# Bluetooth listener
deviceUpdates = []
def MonitorDevice():
	from gi.repository import GLib
	# global newlyConnected
	newlyConnected = False

	def connected(device):
		global newlyConnected
		global currentDevice
		global deviceUpdates
		debugPrint("Device connected. device=%s" % device)
		deviceUpdates.append("Connected:%s" % device)
		newlyConnected = True
		currentDevice = adapter.ConnectedDevice
		# adapter.Discoverable = False
		adapter.Pairable = False
		if not bool(currentDevice.NConnected):
			debugPrint("Establishing Bluetooth NAP connection...")
			try:
				currentDevice.NConnect('nap')
			except:
				debugPrint("Failed to establish NAP connection")

		if bool(currentDevice.NConnected):
			debugPrint("NAP Connected! Interface: " + str(currentDevice.NInterface))
			doUpdate()

	def track_device(addr, properties, signature, device):
		global newlyConnected
		global currentDevice
		global deviceUpdates
		if 'Track' in properties:
			if newlyConnected==True:
				newlyConnected = False
				try:
					if currentDevice:
						player = currentDevice.CurrentPlayer
						sleep(2) # 1 doesn't work, 2 does ///??
						player.Play()
						debugPrint("New device now playing.")
				except:
					player = None
					debugPrint("Failed to begin play on new device.")
			
			debugPrint("Track data")
			# Song changed...
		elif 'Status' in properties:
			if str(properties["Status"]) == "paused":
				debugPrint("Player paused.")
				deviceUpdates.append("Status:paused")
			elif str(properties["Status"]) == "playing":
				debugPrint("Player playing.")
				deviceUpdates.append("Status:playing")
			else:
				debugPrint("Player %s" % properties["Status"])
				deviceUpdates.append("Status:%s" % properties["Status"])

		elif 'Position' in properties:
			debugPrint("Position data")
			# Current position updated (happens when the song changes, status changes, etc) NOT actually when the dur changes...
			return
		elif not 'Connected' in properties:
			# print(str(properties))
			# print("-------------")
			return
		elif currentDevice and bool(properties['Connected']):
			if currentDevice.path != device: # We already have a device connected... drop this one
				debugPrint("New connection denied.")
				BTDevice(device,adapter).Disconnect() # bye bye
		elif currentDevice == None and bool(properties['Connected']):
			connected(device)

		elif currentDevice and not bool(properties['Connected']):
			if currentDevice.path == device:
				debugPrint("Device disconnected. device=%s" % device)
				deviceUpdates.append("Disconnected:%s" % device)
				adapter.Discoverable = True # Allow devices to connect
				adapter.Pairable = True
				newlyConnected = False
				currentDevice = None

	#register your signal callback
	currentDevice.bus.add_signal_receiver(track_device,
							bus_name='org.bluez',
							signal_name='PropertiesChanged',
							dbus_interface='org.freedesktop.DBus.Properties',
							path_keyword='device')
	print("Waiting...")
	loop = GLib.MainLoop()
	loop.run()

# TODO:
# for some reason add_signal_receiver causes property grabs to fuck up..??? the whole thing hangs and eventually errors out, weird.


# Bluetooth settings...
print("Bluetooth ... ")
adapter.Alias = "CarPI Audio" # Rename adapter to something more presentable
print("| alias set")
adapter.Discoverable = True
adapter.DiscoverableTimeout = 0
print("| discoverable enabled")
adapter.Pairable = True # Allow connections
adapter.PairableTimeout = 0

print("| auto connecting...")
adapter.AutoConnect() # Auto connect to a near device

global currentDevice
currentDevice = adapter.ConnectedDevice
global player
play = None
if currentDevice:
	if currentDevice.Connected:
		adapter.Pairable = False
		try:
			
				player = currentDevice.CurrentPlayer
				sleep(2)
				player.Play()
				print("| connected! \\.")
		except:
			player = None
			print("| failed to connect! \\.")

		if not bool(currentDevice.NConnected):
			print("Establishing Bluetooth NAP connection...")
			try:
				currentDevice.NConnect('nap')
			except:
				print("Failed to establish NAP connection")
		
		if bool(currentDevice.NConnected):
			print("Bluetooth NAP connected! Interface: " + str(currentDevice.NInterface))
			doUpdate()

# How we handle request from the web page
def handleWebCommand(webCommand):
	# config = loadConfig()

	global adapter
	global currentDevice
	global player

	currentDevice = adapter.ConnectedDevice
	try:
		if currentDevice:
			player = currentDevice.CurrentPlayer
	except Exception, e:
		debugPrint("ERROR reconnecting..." + str(e))
		# Probably no player loaded... SO let's reconnect...??
		currentDevice.Disconnect()
		currentDevice.Connect()
		player = None

	response=""

	print("Handling")

	if webCommand[:9]=="btConnect":
		try:
			device = adapter.Devices[webCommand[9:]]
			if not (device is None):
				if device.Connect:
					device.Connect()
					sleep(1)
					try:
						device.Play()
					except:
						return "sys_connected"
					return "sys_connected"
			return "sys_notfound"

		except Exception, e:
			debugPrint(str(e))
			return "sys_failed"
	elif webCommand[:12]=="btDisconnect":
		try:
			device = adapter.Devices[webCommand[12:]]
			if not (device is None):
				if device.Connected:
					if device.Connected==True:
						if device.Disconnect:
							device.Disconnect()
							return "sys_disconnected"
					return "sys_disconnected"
			return "sys_notfound"
		except Exception, e:
			debugPrint(str(e))
			return "sys_failed"
	elif webCommand[:8]=="btRemove":
		try:
			device = adapter.Devices[webCommand[8:]]
			if not (device is None):
				adapter.RemoveDevice("/org/bluez/" + adapter.name + "/" + str(webCommand[8:]))
				return "sys_removed"
			return "sys_notfound"
		except Exception, e:
			debugPrint(str(e))
			return "sys_failed"

	elif webCommand=="startDiscovery":
		adapter.StartDiscovery()
		response = "sys_start"
	elif webCommand=="stopDiscovery":
		adapter.StopDiscovery()
		response = "sys_stopped"
	elif webCommand=="autoConnect":
		adapter.AutoConnect()
		return "sys_complete"
	
	elif webCommand=="getDevices":
		devices = adapter.Devices
		response = '{"devices":['
		didDevice=False
		for device in devices:
			if didDevice==True:
				a=','
			else:
				a=''
			alias = ""
			connected = "0"
			if devices[device].Alias:
				alias = str(devices[device].Alias)
			if devices[device].Connected:
				connected = str(devices[device].Connected)
			response = response + a + ' {"alias":"' + alias + '", "connected":"' + connected + '", "name":"' + device + '"}'
			didDevice=True
		response = response + " ]}"


	elif webCommand=="getDeviceUpdates":
		# These are queued messages from the MonitorDeviceConnection process.
		response=json.dumps(deviceUpdates)

	elif webCommand=="play":
		player.Play()
		response="sys_play"
	elif webCommand=="pause":
		player.Pause()
		response="sys_paused"
	elif webCommand == 'stop':
		player.Stop()
		response="sys_pause\nsys_stopped"

	elif webCommand == "playpause":
		if player.Status != "playing":
			# LED.setColor("green",255)
			# LED.setColor("red",0)
			# LED.setColor("blue",0)
			player.Play()
			# LED.fadeOut("green",0.1)
			response="sys_play"
		else:
			# LED.setColor("green",0)
			# LED.setColor("red",255)
			# LED.setColor("blue",0)
			player.Pause()
			# LED.fadeOut("red",0.1)
			response="sys_pause"
	
	elif webCommand == 'next':
		player.Next()
		response='sys_next'
	elif webCommand == 'previous':
		player.Previous()
		response='sys_prev'
	elif webCommand == 'fastforward':
		player.FastForward()
		response='sys_fforward'
	elif webCommand == 'rewind':
		player.Rewind()
		response='sys_rewind'

	elif webCommand=="toggleShuffle":
		if player.Shuffle == "off":
			player.Shuffle = 'alltracks'
		else:
			player.Shuffle = 'off'
		response="sys_complete"

	elif webCommand=="toggleRepeat":
		if player.Repeat == "off":
			player.Repeat = 'alltracks'
		elif player.Repeat == "alltracks":
			player.Repeat = 'singletrack'
		else:
			player.Repeat = 'off'
		response="sys_complete"

	elif webCommand=='getMediaStatus':
		try:
			if player == None:
				response='{ "playerStatus": "offline", "title": "Unknown", "album": "No player connected" }'
			else:
				response='{ "playerStatus": "' + player.Status + '", '

				# Song info
				response=response+'"title": "' + player.Title + '", '
				response=response+'"artist": "' + player.Artist + '", '
				response=response+'"album": "' + player.Album + '", '

				# Device info
				response=response+'"device": "' + player.Device + '", '
				response=response+'"browsable": "' + str(player.Browsable) + '", '
				response=response+'"searchable": "' + str(player.Searchable) + '", '

				# Time items
				response=response+'"position": "'+str(player.Position)+'", '
				response=response+'"duration": "'+str(player.Duration)+'", '

				# Functions
				response=response+'"shuffle": "' + player.Shuffle + '", '
				response=response+'"repeat": "' + player.Repeat + '", '

				# Track data
				response=response+'"numberOfTracks": "' + str(player.NumberOfTracks) + '", '
				response=response+'"trackNumber": "' + str(player.TrackNumber) + '", '
				response=response+'"playlistPath": "' + str(player.Playlist) + '", '

				# Probably not avalible
				response=response+'"equalizer": "' + player.Equalizer + '", '
				response=response+'"scan": "' + player.Scan + '", '
				
				# Player info
				response=response+'"player": "' + player.Name + '", '
				response=response+'"playerType": "' + player.Type + '", '
				response=response+'"playerSubtype": "' + player.Subtype + '" }'
		except:
			# response = "{ title=\"\" album=\"Error retrieving data.\" }"
			response = response +  '"error": "Unknown error retrieving data." }'
			currentDevice = adapter.ConnectedDevice
			player = currentDevice.CurrentPlayer

	# elif webCommand=="setModeStatic":
	# 	config["mode"]="static"
	# 	saveConfig(config)
	# 	config = loadConfig()
	# 	response=config["mode"]
	# elif webCommand=="setModeBreathing":
	# 	config["mode"]="breathing"
	# 	saveConfig(config)
	# 	config = loadConfig()
	# 	response=config["mode"]

	# elif webCommand.startswith("setR"):
	# 	Stop=True
	# 	config["static"]["red"]=float(webCommand[4:])
	# 	saveConfig(config)
	# 	config = loadConfig()
	# 	response="red:"+str(config["static"]["red"])
	# elif webCommand.startswith("setG"):
	# 	Stop=True
	# 	config["static"]["green"]=float(webCommand[4:])
	# 	saveConfig(config)
	# 	config = loadConfig()
	# 	response="green:"+str(config["static"]["green"])
	# elif webCommand.startswith("setB"):
	# 	Stop=True
	# 	config["static"]["blue"]=float(webCommand[4:])
	# 	saveConfig(config)
	# 	config = loadConfig()
	# 	response="blue:"+str(config["static"]["blue"])


	elif webCommand=="getOBDIISpeed":
		response=getOBDIIInfo("Speed")
	elif webCommand=="getOBDIIRpm":
		response=getOBDIIInfo("RPM")
	elif webCommand=="getOBDII":
		# {"name": "value", ...}
		response='{"FUEL_LEVEL": "'+getOBDIIInfo("FuelLevel")+'", "COOLANT_TEMP": "'+getOBDIIInfo("CoolantTemp")+'", "ENGINE_LOAD": "'+getOBDIIInfo("EngineLoad")+'"}'
	else:
		return "sys_error\nUnknown command"

	return response.encode("utf-8")


# config
def loadConfig():
	with open('/var/CarPI/config.json') as configFile:
			config=json.load(configFile)
	debugPrint("Config loaded")
	return config

def saveConfig(config):
	with open('/var/CarPI/config.json', "w") as configFile:
		configFile.write(str(json.dumps(config, sort_keys=True,indent=4, separators=(',', ': '))))
	debugPrint("Config saved")
	return "sys_complete"

# LED




# LED while loop
def led():
	while 1:
		config = loadConfig()
		debugPrint("Mode: " + config["mode"])
		if config["mode"]=="static":
				LED.fadeToRGB(float(config["static"]["red"]),float(config["static"]["green"]),float(config["static"]["blue"]),.25,True)
		elif config["mode"]=="breathing":
			for color in config["breathing"]:
					LED.fadeToRGB(float(color["red"]),float(color["green"]),float(color["blue"]),float(color["fadeDuration"]),True)
					sleep(float(color["timeout"]))
		elif config["mode"]=="disabled":
			sleep(1)

# LCD screen
def LCD():
	import time
	import serial

	# configure the serial connections (the parameters differs on the device you are connecting to)
	# ser = serial.Serial(
	#	 port='/dev/ttyUSB0',
	#	 baudrate=38400,
	#	 parity=serial.PARITY_ODD,
	#	 stopbits=serial.STOPBITS_TWO,
	#	 bytesize=serial.SEVENBITS
	# )

	# ser.isOpen()

	# print 'Setting parematers . . .'
	# ser.write("ate0\r\n") # No echo, I know what I sent
	# ser.write("atspb\r\n") # MS-CAN bus 
	# ser.write("atcaf0\r\n") # Disable automatic formatting! (This fixes data errors when sending / receiving MS-CANBUS data) (Mazda - MSCAN addr:290/291)
	# ser.write("atr0\r\n") # Disable responses (For my car, when sending a message to addr290 (the radio LCD), it would always return the next message from the radio.)
	# ser.flush()

	# print 'RUNNING'
	# while 1 :
	#	 ser.write("atsh 290\r\n") # The first 7 characters for the LCD screen. MUST INCLUDE 'c0' AT THE BEGINING
	#	 ser.flush()
	#	 sleep(0.01)
	#	 ser.write("c041424344454647\r\n") # ABCDEFG
	#	 ser.flush()
	#	 sleep(0.01)
	#	 ser.write("atsh 291\r\n") # The second 7 characters. MUST INCLUDE '85' (no idea why)
	#	 ser.flush()
	#	 sleep(0.01)
	#	 ser.write("8548495051525354\r\n") # HIJKLMN
	#	 ser.flush()
	#	 sleep(1)


def getOBDIIInfo(info):
	OBDIIClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Their end

	try:
		OBDIIClient.connect(("localhost",7000))
		OBDIIClient.send(info)
		Response=""
		Response=CGISocket.recv(1024).decode('utf-8')
		CGISocket.close()
		return Response
	except socket.error:
		return "Read Error"
	except Exception, e:
		return "sys_error - "+str(e)

def PhysicalMediaControls():
	print("Not done :^)")



# Socket command handling
class client(Thread):
	def __init__(self, socket, address):
		Thread.__init__(self)
		self._is_running = True
		self.sock = socket
		self.addr = address
		self.start()

	def stop(self):
		self._is_running = False

	def run(self):
		while self._is_running:
			webCommand = self.sock.recv(1024).decode()
			if webCommand:
				try:
					debugPrint(webCommand)
					response=handleWebCommand(webCommand)
					try:
						debugPrint('\nCommand recieved: ' + webCommand + '\nResponse: ' + response.decode('utf-8'))
					except Exception:
						debugPrint('\nError printing response/command, probably has unicode in it')
					self.sock.sendto(response,self.addr)
				except Exception,e:
					debugPrint("Error handing command! Err: " + str(e))
					self.sock.sendto("sys_error",self.addr)

			else:
				self.stop()



######################


def main():
	try:
		loadConfig()
		ledProcess=multiprocessing.Process(target=led)
		# ledProcess.start()

		# lcdProcess = multiprocessing.Process(target=LCD)
		#lcdProcess.start()

		monDevice=multiprocessing.Process(target=MonitorDevice)
		monDevice.start()
	
		CGISocket.listen(5)

		
		print 'Listening.'

		subprocess.Popen("sudo sh -c 'echo 1 > /sys/class/leds/led0/brightness'", shell=True)

		while 1:
			 conn,add=CGISocket.accept()
			 client(conn, add)
	
	except KeyboardInterrupt:
		print "\nGoodbye"
		subprocess.Popen("sudo sh -c 'echo 0 > /sys/class/leds/led0/brightness'", shell=True)
		# ledProcess.terminate()
		LED.fadeToRGB(0,0,0,0.005,False,True)
		try:
			carConnection.close()
		except:
			print colored("Failed to close carConnection", "red")

		os._exit(0)
	except Exception, e:
		print "Error!"
		print colored(str(e),"red")
		traceback.print_exc()		


	# ledProcess.terminate()
	LED.fadeToRGB(0,0,0,0.005,False,True)
	try:
		carConnection.close()
	except:
		print colored("Failed to close carConnection", "red")
	os._exit(0)

if __name__ == "__main__":
	main()