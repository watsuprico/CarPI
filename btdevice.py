#!/usr/bin/python

debug = True
def debugPrint(message):
    if debug:
        print str(message)

import dbus

import dbusrenderer

class BTPlayerItem:
	def __init__(self, itemName, player=None):
		if device is None:
			self.bus = dbus.SystemBus()
			self.path = itemName
		else:
			self.bus = device.bus
			self.playerPath = player.path
			if itemName.startswith('/org/bluez'):
				self.path = itemName
			elif itemName!='' and itemName.startswith('/')!=True and self.playerPath.endswith('/')!=True:
				self.path = '/org/bluez' + self.playerPath + '/' + itemName
			else:
				self.path = '/org/bluez' + self.playerPath + itemName

		self.object = self.bus.get_object('org.bluez',self.path)
		self.interface = dbus.Interface(self.object, 'org.bluez.MediaItem1')
		self.properties = dbus.Interface(self.object, 'org.freedesktop.DBus.Properties')

	# Item methods
	def Play(self):
		self.interface.Play()
	def AddtoNowPlaying(self):
		self.interface.AddtoNowPlaying()


	# Player properties
	def GetProperty(self,name):
		return self.properties.Get('org.bluez.MediaItem1',name)
	def SetProperty(self,name,val):
		self.properties.Set('org.bluez.MediaItem1',name,val)

	# Read only (which is everything)
	@property
	def Player(self):
		a=self.GetProperty('Player')
		if a is not None:
			return a
		else:
			return self.playerPath
	@property
	def Name(self):
		a=self.GetProperty('Name')
		if a is not None:
			return a
		else:
			return "Unavailable"
	@property
	def Type(self):
		a=self.GetProperty('Type')
		if a is not None:
			return a
		else:
			return "Unavailable"
	@property
	def FolderType(self):
		a=self.GetProperty('FolderType')
		if a is not None:
			return a
		else:
			return "Unavailable"
	@property
	def Playable(self):
		a=self.GetProperty('Playable')
		if a is not None:
			return a
		else:
			return False

	# Metadata stuff, similar to Player's Track info
	@property
	def Metadata(self):
		a=self.GetProperty('Metadata')
		if a is not None:
			return a
		else:
			return {}
	@property
	def Title(self):
		a=self.GetProperty('Title')
		if a is not None:
			return a
		else:
			return "Unavailable"
	@property
	def Artist(self):
		a=self.GetProperty('Artist')
		if a is not None:
			return a
		else:
			return "Unavailable"
	@property
	def Album(self):
		a=self.GetProperty('Album')
		if a is not None:
			return a
		else:
			return "Unavailable"
	@property
	def Genre(self):
		a=self.GetProperty('Genre')
		if a is not None:
			return a
		else:
			return "Unavailable"
	@property
	def NumberOfTracks(self):
		a=self.GetProperty('NumberOfTracks')
		if a is not None:
			return a
		else:
			return 0
	@property
	def Number(self):
		a=self.GetProperty('Number')
		if a is not None:
			return a
		else:
			return 0
	@property
	def Duration(self):
		a=self.GetProperty('Duration')
		if a is not None:
			return a
		else:
			return 0

class BTMediaTransport:
	def __init__(self, transportPath, device=None):
		if device is None:
			self.bus = dbus.SystemBus()
			self.path = playerName
			self.name = playerName[-7:]
			self.adapterName = device.adapterName
			self.deviceName = device.name
		else:
			self.bus = device.bus
			self.devicePath = device.path
			self.adapterPath = device.adapterPath
			self.adapterName = device.adapterName
			self.deviceName = device.name

			if transportPath.startswith('/org/bluez'): # the path includes the device path etc
				self.path = transportPath
				self.name = transportPath[-3:]
			elif transportPath!='' and transportPath.startswith('/')!=True and self.devicePath.endswith('/')!=True:
				self.path = self.devicePath + '/' + transportPath
				self.name = transportPath
			else:
				self.path = self.devicePath + transportPath
				self.name = transportPath.replace('/','')

		self.object = self.bus.get_object('org.bluez',self.path)
		self.interface = dbus.Interface(self.object, 'org.bluez.MediaTransport1')
		self.properties = dbus.Interface(self.object, 'org.freedesktop.DBus.Properties')


	# Methods
	def Acquire(self):
		return self.interface.Acquire()
	def TryAcquire(self):
		return self.interface.TryAcquire()
	def Release(self):
		self.interface.Release()

	def GetProperty(self,name):
		return self.properties.Get('org.bluez.MediaTransport1',name)
	def SetProperty(self,name,val):
		self.properties.Set('org.bluez.MediaTransport1',name,val)

	# Properties
	@property
	def Device(self):
		return self.GetProperty("Device")
	@property
	def UUID(self):
		return self.GetProperty("UUID")
	@property
	def Codec(self):
		return self.GetProperty("Codec")
	@property
	def Configuration(self):
		return self.GetProperty("Configuration")
	@property
	def State(self):
		return self.GetProperty("State")
	@property
	def Endpoint(self):
		return self.GetProperty("Endpoint")


	# Read/Write
	@property
	def Delay(self):
		return self.GetProperty("Delay")
	@Delay.setter
	def Delay(self, value):
		self.SetProperty("Delay", value)

	@property
	def Volume(self):
		return self.GetProperty("Volume")
	@Volume.setter
	def Volume(self, value):
		self.SetProperty("Volume", value)


###############
# Player Item #
###############

class BTPlayer:
	def __init__(self, playerName, device=None):
		if device is None:
			self.bus = dbus.SystemBus()
			self.path = playerName
			self.name = playerName[-7:]
			self.adapterName = device.adapterName
			self.deviceName = device.name
		else:
			self.bus = device.bus
			self.devicePath = device.path
			self.adapterPath = device.adapterPath
			self.adapterName = device.adapterName
			self.deviceName = device.name

			if playerName.startswith('/org/bluez'):
				self.path = playerName
				self.name = playerName[-7:]
			elif playerName!='' and playerName.startswith('/')!=True and self.devicePath.endswith('/')!=True:
				self.path = self.devicePath + '/' + playerName
				self.name = playerName
			else:
				self.path = self.devicePath + playerName
				self.name = playerName.replace('/','')

		self.object = self.bus.get_object('org.bluez',self.path)
		self.interfacePlayer = dbus.Interface(self.object, 'org.bluez.MediaPlayer1')
		self.interfaceFolder = dbus.Interface(self.object, 'org.bluez.MediaFolder1')
		self.properties = dbus.Interface(self.object, 'org.freedesktop.DBus.Properties')

	@property
	def Items(self):
		return BTPlayerItems(self)

	# Player methods
	def Play(self):
		self.interfacePlayer.Play()
	def Pause(self):
		self.interfacePlayer.Pause()
	def Stop(self):
		self.interfacePlayer.Stop()
	def Next(self):
		self.interfacePlayer.Next()
	def Previous(self):
		self.interfacePlayer.Previous()
	def FastForward(self):
		self.interfacePlayer.FastForward()
	def Rewind(self):
		self.interfacePlayer.Rewind()

	# Special stuff
	def PlayPause(self): # Either sends the play command if it's paused or the pause command if it's playing
		if self.Status=="paused":
			self.interfacePlayer.Play()
		elif self.Status!="error":
			self.interfacePlayer.Pause()

	# Player properties
	def GetPlayerProperty(self,name):
		try:
			return self.properties.Get('org.bluez.MediaPlayer1',name)
		except:
			return None
	def SetPlayerProperty(self,name,val):
		self.properties.Set('org.bluez.MediaPlayer1',name,val)

	# Track stuff
	@property
	def Track(self): # For compatibility
		a=self.GetPlayerProperty('Track')
		if not (a is None):
			return a
		else:
			return "Unavailable"

	# Special track stuff
	@property
	def Title(self): # 'Title' value inside 'Track'
		a=self.GetPlayerProperty('Track')
		if not (a is None):
			if not (a['Title'] is None):
				return a['Title']
			else:
				return "Unavailable"
		else:
			return "Unavailable"
	@property
	def Artist(self): # 'Artist' value inside 'Track'
		a=self.GetPlayerProperty('Track')
		if not (a is None):
			if not (a['Artist'] is None):
				return a['Artist']
			else:
				return "Unavailable"
		else:
			return "Unavailable"
	@property
	def Album(self): # 'Album' value inside 'Track'
		a=self.GetPlayerProperty('Track')
		if not (a is None):
			if not (a['Album'] is None):
				return a['Album']
			else:
				return "Unavailable"
		else:
			return "Unavailable"
	@property
	def Genre(self): # 'Genre' value inside 'Track'
		a=self.GetPlayerProperty('Track')
		if not (a is None):
			if not (a['Genre'] is None):
				return a['Genre']
			else:
				return "Unavailable"
		else:
			return "Unavailable"
	@property
	def NumberOfTracks(self): # 'NumberOfTracks' value inside 'Track'
		a=self.GetPlayerProperty('Track')
		if not (a is None):
			if not (a['NumberOfTracks'] is None):
				return a['NumberOfTracks']
			else:
				return 0
		else:
			return 0
	@property
	def TrackNumber(self): # 'TrackNumber' value inside 'Track'
		a=self.GetPlayerProperty('Track')
		if not (a is None):
			if not (a['TrackNumber'] is None):
				return a['TrackNumber']
			else:
				return 0
		else:
			return 0
	@property
	def Duration(self): # 'Duration' value inside 'Track'
		a=self.GetPlayerProperty('Track')
		if not (a is None):
			if not (a['Duration'] is None):
				return a['Duration']
			else:
				return 0
		else:
			return 0


	# Read only
	@property
	def Status(self):
		a=self.GetPlayerProperty('Status')
		if not (a is None):
			return a
		else:
			return "error"
	@property
	def Position(self):
		a=self.GetPlayerProperty('Position')
		if not (a is None):
			return a
		else:
			return 0
	@property
	def Device(self):
		a=self.GetPlayerProperty('Device')
		if not (a is None):
			return a
		else:
			return self.devicePath
	@property
	def Name(self):
		a=self.GetPlayerProperty('Name')
		if not (a is None):
			return a
		else:
			return "disabled"
	@property
	def Type(self):
		a=self.GetPlayerProperty('Type')
		if not (a is None):
			return a
		else:
			return "disabled"
	@property
	def Subtype(self):
		a=self.GetPlayerProperty('Subtype')
		if not (a is None):
			return a
		else:
			return "disabled"
	@property
	def Browsable(self):
		a=self.GetPlayerProperty('Browsable')
		if not (a is None):
			return a
		else:
			return False
	@property
	def Searchable(self):
		a=self.GetPlayerProperty('Searchable')
		if not (a is None):
			return a
		else:
			return False
	@property
	def Playlist(self):
		a=self.GetPlayerProperty('Playlist')
		if not (a is None):
			return a
		else:
			return ""

	# Read/Write
	@property
	def Equalizer(self):
		a=self.GetPlayerProperty('Equalizer')
		if a is not None:
			return a
		else:
			return "disabled"
	@Equalizer.setter
	def Equalizer(self,val):
		if self.Equalizer!="disabled":
			self.SetPlayerProperty('Equalizer',val)
	
	@property
	def Repeat(self):
		a=self.GetPlayerProperty('Repeat')
		if a is not None:
			return a
		else:
			return "disabled"
	@Repeat.setter
	def Repeat(self,val):
		if self.Repeat!="disabled":
			self.SetPlayerProperty('Repeat',val)
	
	@property
	def Shuffle(self):
		a=self.GetPlayerProperty('Shuffle')
		if a is not None:
			return a
		else:
			return "disabled"
	@Shuffle.setter
	def Shuffle(self,val):
		if self.Shuffle!="disabled":
			self.SetPlayerProperty('Shuffle',val)
	
	@property
	def Scan(self):
		a=self.GetPlayerProperty('Scan')
		if a is not None:
			return a
		else:
			return "disabled"
	@Scan.setter
	def Scan(self,val):
		if self.Scan!="disabled":
			self.SetPlayerProperty('Scan',val)


	# Folder methods
	def Search(self,val,ffilter):
		return self.interfaceFolder.Search(val,ffilter)
	def ListItems(self,ffilter):
		return self.interfaceFolder.ListItems(ffilter)
	def ChangeFolder(self, folder):
		self.interfaceFolder.ChangeFolder(folder)


	# Folder properties
	def GetFolderProperty(self,name):
		try:
			return self.properties.Get('org.bluez.MediaFolder1',name)
		except:
			return None

	@property
	def NumberOfItems(self):
		a=self.GetFolderProperty('NumberOfItems')
		if a is not None:
			return a
		else:
			return 0
	# @property
	# def Name(self):
	# 	a=self.GetFolderProperty('Name')
	# 	if a is not None:
	# 		return a
	# 	else:
	# 		return "Unavailable"


class BTDevice:
	def __init__(self, deviceName, adapter=None):
		if adapter is None:
			self.bus = dbus.SystemBus()
			self.path = deviceName
			self.name = deviceName[-21:]
			self.adapterName = adapter.name
		else:
			self.bus = adapter.bus
			self.adapterPath = adapter.path
			self.adapterName = adapter.name
			if deviceName.startswith('/org/bluez'):
				self.path = deviceName
				self.name = deviceName.replace('/org/bluez','')
			elif deviceName!='' and deviceName.startswith('/')!=True and self.adapterPath.endswith('/')!=True: # If the device name is not empty, it does not start with a '/' and the adapter name doesn't end with a '/' add one
				self.path = '/org/bluez/' + adapter.name + '/' + deviceName
				self.name = deviceName
			else:
				self.path = '/org/bluez/' + adapter.name + deviceName
				self.name = deviceName.replace('/','')
			
		self.object = self.bus.get_object('org.bluez',self.path)
		self.interface = dbus.Interface(self.object,'org.bluez.Device1')
		self.interfacePlayer = dbus.Interface(self.object,'org.bluez.MediaControl1')
		self.interfaceNetwork = dbus.Interface(self.object,'org.bluez.Network1')
		self.properties = dbus.Interface(self.object,'org.freedesktop.DBus.Properties')

	@property
	def Players(self):
		return BTPlayers(self)

	@property
	def CurrentPlayer(self):
		return self.Players[str(self.Player).replace(str(self.path) + "/","")]

	def MediaTransports(self):
		return BTTransports(self)
	

	@property
	def Path(self):
		return self.path

	# Player methods (Deprecated)
	def Play(self):
		self.interfacePlayer.Play()
	def Pause(self):
		self.interfacePlayer.Pause()
	def Stop(self):
		self.interfacePlayer.Stop()
	def Next(self):
		self.interfacePlayer.Next()
	def Previous(self):
		self.interfacePlayer.Previous()
	def VolumeUp(self): # Don't work
		self.interfacePlayer.VolumeUp()
	def VolumeDown(self): # Don't work
		self.interfacePlayer.VolumeDown()
	def FastFoward(self):
		self.interfacePlayer.FastFoward()
	def Rewind(self):
		self.interfacePlayer.Rewind()

	# Device methods
	def Connect(self):
		self.interface.Connect()
	def Disconnect(self):
		self.interface.Disconnect()
	def ConnectProfile(self,uuid):
		self.interface.ConnectProfile(uuid)
	def DisconnectProfile(self,uuid):
		self.interface.DisconnectProfile()
	def Pair(self):
		self.interface.Pair()
	def CancelPairing(self):
		self.interface.CancelPairing()

	# Network methods
	def NConnect(self, uuid):
		return self.interfaceNetwork.Connect(uuid)
	def NDisconnect(self):
		self.interfaceNetwork.Disconnect()



	# Device properties

	def GetNetworkProperty(self,name):
		return self.properties.Get('org.bluez.Network1',name)
	def GetControlProperty(self,name):
		return self.properties.Get('org.bluez.MediaControl1',name)
	def GetProperty(self,name):
		return self.properties.Get('org.bluez.Device1',name)
	def SetProperty(self,name,val):
		self.properties.Set('org.bluez.Device1',name,val)

	# Network properties
	@property
	def NConnected(self):
		return self.GetNetworkProperty('Connected')

	@property
	def NInterface(self):
		return self.GetNetworkProperty('Interface')

	@property
	def NUUID(self):
		return self.GetNetworkProperty('UUID')


	@property
	def BatteryPercentage(self):
		return self.properties.Get('org.bluez.Battery1','Percentage')

	# Readonly properties
	@property
	def Address(self):
		return self.GetProperty("Address")
	@property
	def AddressType(self):
		return self.GetProperty("AddressType")
	@property
	def Name(self):
		return self.GetProperty("Name")
	@property
	def Icon(self):
		return self.GetProperty("Icon")
	@property
	def Class(self):
		return self.GetProperty("Class")
	@property
	def Appearance(self):
		return self.GetProperty("Appearance")
	@property
	def UUIDs(self):
		return self.GetProperty("UUIDs")
	@property
	def Paired(self):
		return self.GetProperty("Paired")
	@property
	def Connected(self):
		return self.GetProperty("Connected")
	@property
	def Adapter(self):
		return self.GetProperty("Adapter")
	@property
	def LegacyPairing(self):
		return self.GetProperty("LegacyPairing")
	@property
	def Modalias(self):
		return self.GetProperty("Modalias")
	@property
	def RSSI(self):
		return self.GetProperty("RSSI")
	@property
	def TxPower(self):
		return self.GetProperty("TxPower")
	@property
	def ManufacturerData(self):
		return self.GetProperty("ManufacturerData")
	@property
	def ServiceData(self):
		return self.GetProperty("ServiceData")
	@property
	def ServicesResolved(self):
		return self.GetProperty("ServicesResolved")
	@property
	def AdvertisingFlags(self):
		return self.GetProperty("AdvertisingFlags")

	# Player stuff
	@property
	def PlayerConnected(self):
		return self.GetControlProperty("Connected")
	@property
	def Player(self):
		return self.GetControlProperty("Player")

	# Read/Write properties
	@property
	def Trusted(self):
		return self.GetProperty("Trusted")
	@Trusted.setter
	def Trusted(self,val):
		self.SetProperty("Trusted",val)
	
	@property
	def Blocked(self):
		return self.GetProperty("Blocked")
	@Blocked.setter
	def Blocked(self,val):
		self.SetProperty("Blocked",val)
	
	@property
	def Alias(self):
		return self.GetProperty("Alias")
	@Alias.setter
	def Alias(self,val):
		self.SetProperty("Alias",val)


# Return a list of devices for a BTAdapter
def BTDevices(adapter):
	devices={}
	paths=dbusrenderer.render(adapter.name)
	for btdevice in paths:
		devices[btdevice]=BTDevice(btdevice,adapter)
	return devices

def BTPlayers(device):
	players={}
	paths=dbusrenderer.render(device.adapterName + '/' + device.name)
	for btplayer in paths:
		if btplayer.startswith('player'):
			players[btplayer]=BTPlayer(btplayer,device)
	return players

def BTTransports(device):
	mediatransports={}
	paths=dbusrenderer.render(device.adapterName + '/' + device.name)
	for endpoints in paths:
		if endpoints.startswith('fd'):
			mediatransports[endpoints]=BTMediaTransport(endpoints,device)
	return mediatransports

def BTPlayerItems(player):
	items={}
	paths=dbusrenderer.render(player.path)
	for btplayeritem in paths:
		items[btplayeritem]=BTPlayerItem(btplayeritem,player)
	return items