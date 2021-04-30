#!/usr/bin/python

from termcolor import colored # Only for debugging
debug = True
def debugPrint(message):
    if debug:
        print "[DEBUG] " + str(message)

import dbus

from time import sleep

from btdevice import BTDevices

class BTAdapter(object):
	def __init__(self, adapterName):
		self.bus = dbus.SystemBus()
		if adapterName.startswith('/org/bluez'):
			self.path = adapterName
			self.name = adapterName.replace("/org/bluez","")
		elif adapterName!='' and adapterName.startswith('/')!=True:
			self.path='/org/bluez/' + adapterName
			self.name = adapterName
		else:
			self.path = '/org/bluez' + adapterName
			self.name = adapterName.replace("/","")
		self.object = self.bus.get_object('org.bluez',self.path)
		self.interface = dbus.Interface(self.object,'org.bluez.Adapter1')
		self.interfaceMedia = dbus.Interface(self.object,'org.bluez.Media1')
		self.properties = dbus.Interface(self.object,'org.freedesktop.DBus.Properties')

	@property
	def Path(self):
		return self.path

	@property
	def Name(self):
		return self.name

	@property
	def Devices(self):
		return BTDevices(self)

	@property
	def ConnectedDevice(self):
		devices = self.Devices
		for btdevice in devices:
			try:
				if devices[btdevice].Connected==True:
					return devices[btdevice]
			except:
				sleep(0)

	@property
	def ConnectedDevicePath(self):
		devices = self.Devices
		for btdevice in devices:
			if devices[btdevice].Connected==True:
				return devices[btdevice].path

	# Connect to known devices
	def AutoConnect(self):
		devices = self.Devices
		for btdevice in devices:
			if devices[btdevice].Connected:
				if devices[btdevice].Connected==True:
					return "already connected"
		for btdevice in devices:
			if devices[btdevice].Connect:
				try:
					devices[btdevice].Connect()
					sleep(1)
					devices[btdevice].Play()
					return "connected"
				except:
					print 'failed to connect'
					sleep(0)

	# Media methods
	def RegisterEndpoint(self,endpoint,properties):
		self.interface.RegisterEndpoint(endpoint,properties)
	def UnregisterEndpoint(self,endpoint):
		self.interface.UnregisterEndpoint(endpoint)
	def RegisterPlayer(self,player,properties):
		self.interface.RegisterPlayer(player,properties)
	def UnregisterPlayer(self,player):
		self.interface.UnregisterPlayer(player)

	# Adapter methods
	def StartDiscovery(self):
		self.interface.StartDiscovery()
	def StopDiscovery(self):
		self.interface.StopDiscovery()
	def RemoveDevice(self,device):
		self.interface.RemoveDevice(device)
	def SetDiscoveryFilter(self, ffilter):
		self.interface.SetDiscoveryFilter(ffilter)
	def GetDiscoveryFilters(self):
		return self.interface.GetDiscoveryFilters()

	# Adapter properties
	def GetProperty(self,name):
		return self.properties.Get('org.bluez.Adapter1',name)
	def SetProperty(self,name,val):
		if name == "DiscoverableTimeout" or name == "PairableTimeout":
			if type(val) != type(self.GetProperty(name)):
				val = dbus.UInt32(val)

		self.properties.Set('org.bluez.Adapter1',name,val)

	# Readonly properties
	@property
	def Address(self):
		return self.GetProperty("Address")
	@property
	def Name(self):
		return self.GetProperty("Name")
	@property
	def Class(self):
		return self.GetProperty("Class")
	@property
	def Discovering(self):
		return self.GetProperty("Discovering")
	@property
	def UUIDs(self):
		return self.GetProperty("UUIDs")
	@property
	def UUIDs(self):
		return self.GetProperty("Modalias")

	# Read/Write properties
	@property
	def Alias(self):
		return self.GetProperty("Alias")
	@Alias.setter
	def Alias(self,val):
		self.SetProperty("Alias",val)
	
	@property
	def Powered(self):
		return self.GetProperty("Powered")
	@Powered.setter
	def Powered(self,val):
		self.SetProperty("Powered",val)
	
	@property
	def Discoverable(self):
		return self.GetProperty("Discoverable")
	@Discoverable.setter
	def Discoverable(self,val):
		self.SetProperty("Discoverable",val)
	
	@property
	def Pairable(self):
		return self.GetProperty("Pairable")
	@Pairable.setter
	def Pairable(self,val):
		self.SetProperty("Pairable",val)
	
	@property
	def PairableTimeout(self):
		return self.GetProperty("PairableTimeout")
	@PairableTimeout.setter
	def PairableTimeout(self,val):
		self.SetProperty("PairableTimeout",val)

	@property
	def DiscoverableTimeout(self):
		return self.GetProperty("DiscoverableTimeout")
	@DiscoverableTimeout.setter
	def DiscoverableTimeout(self,val):
		self.SetProperty("DiscoverableTimeout",val)