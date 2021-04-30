#!/usr/bin/python

from termcolor import colored # Only for debugging
debug = True
def debugPrint(message):
    if debug:
        print colored("[DEBUG] " + str(message), "yellow")


class ConfigHandle:
	def __init__(self, configPath):
		self.configPath = configPath
		self.config={}

	@property
	def Path(self):
		return self.configPath

	# Adapter methods
	def Load(self):
		global config
		with open(self.configPath) as configFile:
				config=json.load(configFile)
		debugPrint("Config loaded")
		return "sys_complete"

	def Save(self):
		with open(self.configPath) as configFile:
			configFile.write(str(json.dumps(self.config, sort_keys=True,indent=4, separators=(',', ': '))))
		debugPrint("Config saved")
		return "sys_complete"

	# Read/Write properties
	@property
	def Config(self):
		return self.config
	@Config.setter
	def Config(self,val):
		self.config = val