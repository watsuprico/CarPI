#!/usr/bin/python

from __future__ import division

# OBD-II Host
# A hub for OBD-II data
# 	(Allows multiple programs to request OBD-II info without overworking the adapter) ((So this program polls the adapter and just updates variables which it hands out upon request))
#
# Supported:
#	[
#		{ Basics }
#		RPM (RPM , rpm)
#		Speed (SPEED , kph)
#
#		{ Temps }
#		Coolant Temperature (COOLANT_TEMP , celsius)
#		Engine Oil Temperature (OIL_TEMP , celsius)
#		Ambient Air Temperature	(AMBIANT_AIR_TEMP , celsius)
#		Intake Air Temperature (INTAKE_TEMP , celsius)
#
#		{ Fuel }
#		Fuel Pressure (FUEL_PRESSURE , kilopascal)
#		Fuel Rate (FUEL_RATE , liters_per_hour)
#		Fuel Level Input (FUEL_LEVEL , percent)
#
#		{ Other }
#		Engine Load (ENGINE_LOAD , percent)
#		Throttle Position (THROTTLE_POS , percent)
#		Engine Run Time (RUN_TIME , second)
#		Number of Warms-ups Since Codes Cleared (WARMUPS_SINCE_DTC_CLEAR, count)
#		Control Module Voltage (CONTROL_MODULE_VOLTAGE , volt)
#		Air Flow Rate (MAF) (MAF , grams_per_second)
#		Intake Manifold Pressure (INTAKE_PRESSURE , kilopascal)
#	]

# Setup
import xlwt

import os
from time import time
from random import  randint
import traceback

HZ = os.sysconf(os.sysconf_names['SC_CLK_TCK'])

def seconds_elapsed():
    system_stats = open('/proc/stat').readlines()
    process_stats = open('/proc/self/stat').read().split()
    for line in system_stats:
        if line.startswith('btime'):
            boot_timestamp = int(line.split()[1])
    age_from_boot_jiffies = int(process_stats[21])
    age_from_boot_timestamp = age_from_boot_jiffies / HZ
    age_timestamp = boot_timestamp + age_from_boot_timestamp
    return time() - age_timestamp

# MySQL
import MySQLdb
sqldb = MySQLdb.connect(host='localhost', db='obd-ii', user='root', passwd='?+SPWI7g]kd^/^E=p`<a1QD{6')
MySQLCur = sqldb.cursor()

# Allow any characters (like jap ones)
import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

from termcolor import colored # Allow color in the term

# Get commands from the CGI script (so I don't have to scrub dbus for every method just to pause the music (it's cpu intensive and highly ineffective))
import socket
from threading import *
# Our end
CGISocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CGISocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
CGISocket.bind(("localhost", 7000))

from time import sleep

# with open("/var/www/html/logs/obd_ii","w") as logFile:
# 	logFile.write("Cleared")

debug = True
def debugPrint(message):
	if debug:
		print colored("[DEBUG] "+message, "yellow")
		with open("/var/www/html/logs/obd_ii","a") as logFile:
			logFile.write("\n["+str(seconds_elapsed())+"][DEBUG] "+message)
def debugPrintOBDII(message):
	if debug:
		print colored("[DEBUG] "+message, "yellow")
		with open("/var/www/html/logs/obd_ii_adapter","a") as logFile:
			logFile.write("\n["+str(seconds_elapsed())+"][DEBUG] "+message)
def debugPrint1(message):
	if debug:
		print colored("[DEBUG] "+message, "yellow")
		with open("/var/www/html/logs/obd_ii-log","a") as logFile:
			logFile.write("\n["+str(seconds_elapsed())+"][DEBUG] "+message)

# OBD-II
import obd
updateDelay=0.05

carConnection = obd.OBD() #Auto connect
try:
	RPM=carConnection.query(obd.commands.RPM).value.magnitude
	sleep(updateDelay)
except Exception,e:
	RPM="Unsupported"
	debugPrint("Error! "+str(e))
try:
	Speed=carConnection.query(obd.commands.SPEED).value.to("mph").magnitude
	sleep(updateDelay)
except Exception,e:
	Speed="Unsupported"
	debugPrint("Error! "+str(e))

try:
	CoolantTemp=carConnection.query(obd.commands.COOLANT_TEMP).value.magnitude*1.8+32 # From Celsius > Fahrenheit
	sleep(updateDelay)
except Exception,e:
	CoolantTemp="Unsupported"
	debugPrint("Error! "+str(e))
try:
	EngineOilTemp=carConnection.query(obd.commands.OIL_TEMP).value.magnitude*1.8+32 # From Celsius > Fahrenheit
	sleep(updateDelay)
except Exception,e:
	EngineOilTemp="Unsupported"
	debugPrint("Error! "+str(e))
try:
	AmbientAirTemp=carConnection.query(obd.commands.AMBIANT_AIR_TEMP).value.magnitude*1.8+32 # From Celsius > Fahrenheit
	sleep(updateDelay)
except Exception,e:
	AmbientAirTemp="Unsupported"
	debugPrint("Error! "+str(e))
try:
	IntakeAirTemp=carConnection.query(obd.commands.INTAKE_TEMP).value.magnitude*1.8+32 # From Celsius > Fahrenheit
	sleep(updateDelay)
except Exception,e:
	IntakeAirTemp="Unsupported"
	debugPrint("Error! "+str(e))

try:
	FuelPressure=carConnection.query(obd.commands.COOLANT_TEMP).value.magnitude*.14503773773020923 #From kilopascal > psi
	sleep(updateDelay)
except Exception,e:
	FuelPressure="Unsupported"
	debugPrint("Error! "+str(e))
try:
	FuelLevelInput=carConnection.query(obd.commands.FUEL_LEVEL).value.magnitude
	sleep(updateDelay)
except Exception,e:
	FuelLevelInput="Unsupported"
	debugPrint("Error! "+str(e))

try:
	EngineLoad=carConnection.query(obd.commands.ENGINE_LOAD).value.magnitude
	sleep(updateDelay)
except Exception,e:
	EngineLoad="Unsupported"
	debugPrint("Error! "+str(e))
try:
	ThrottlePosition=carConnection.query(obd.commands.THROTTLE_POS).value.magnitude
	sleep(updateDelay)
except Exception,e:
	ThrottlePosition="Unsupported"
	debugPrint("Error! "+str(e))
try:
	EngineRunTime=carConnection.query(obd.commands.RUN_TIME).value.magnitude
	sleep(updateDelay)
except Exception,e:
	EngineRunTime="Unsupported"
	debugPrint("Error! "+str(e))
try:
	WarmsupSinceDTCCleared=carConnection.query(obd.commands.WARMUPS_SINCE_DTC_CLEAR).value.magnitude
	sleep(updateDelay)
except Exception,e:
	WarmsupSinceDTCCleared="Unsupported"
	debugPrint("Error! "+str(e))
try:
	ControlModuleVoltage=carConnection.query(obd.commands.CONTROL_MODULE_VOLTAGE).value.magnitude
	sleep(updateDelay)
except Exception,e:
	ControlModuleVoltage="Unsupported"
	debugPrint("Error! "+str(e))
try:
	AirFlowRate=carConnection.query(obd.commands.MAF).value.magnitude*0.0022 # Grams per second > pounds per second
	sleep(updateDelay)
except Exception,e:
	AirFlowRate="Unsupported"
	debugPrint("Error! "+str(e))
try:
	IntakeManifoldPressure=carConnection.query(obd.commands.INTAKE_PRESSURE).value.magnitude*.14503773773020923 #From kilopascal > psi
	sleep(updateDelay)
except Exception,e:
	IntakeManifoldPressure="Unsupported"
	debugPrint("Error! "+str(e))

updateCount=1

# Command handling
def handleCommand(command):
	global RPM
	global Speed

	global CoolantTemp
	global EngineOilTemp
	global AmbientAirTemp
	global IntakeAirTemp

	global FuelPressure
	global FuelLevelInput

	global EngineLoad
	global ThrottlePosition
	global EngineRunTime
	global WarmsupSinceDTCCleared
	global ControlModuleVoltage
	global AirFlowRate
	global IntakeManifoldPressure

	response=""

	if command=="RPM":
		response=str(RPM)
	elif command=="Speed":
		response=str(Speed)

	elif command=="CoolantTemp":
		response=str(CoolantTemp)
	elif command=="EngineOilTemp":
		response=str(EngineOilTemp)
	elif command=="AmbientAirTemp":
		response=str(AmbientAirTemp)
	elif command=="IntakeAirTemp":
		response=str(IntakeAirTemp)

	elif command=="FuelPressure":
		response=str(FuelPressure)
	elif command=="FuelLevelInput":
		response=str(FuelLevelInput)

	elif command=="EngineLoad":
		response=str(EngineLoad)
	elif command=="ThrottlePosition":
		response=str(ThrottlePosition)
	elif command=="EngineRunTime":
		response=str(EngineRunTime)
	elif command=="WarmsupSinceDTCCleared":
		response=str(WarmsupSinceDTCCleared)
	elif command=="ControlModuleVoltage":
		response=str(ControlModuleVoltage)
	elif command=="AirFlowRate":
		response=str(AirFlowRate)
	elif command=="IntakeManifoldPressure":
		response=str(IntakeManifoldPressure)

	return response.encode("utf-8")


def OBDIILoop():
	carConnection = obd.OBD() #Auto connect
	global updateDelay
	global updateCount

	global RPM
	global Speed

	global CoolantTemp
	global EngineOilTemp
	global AmbientAirTemp
	global IntakeAirTemp

	global FuelPressure
	global FuelLevelInput

	global EngineLoad
	global ThrottlePosition
	global EngineRunTime
	global WarmsupSinceDTCCleared
	global ControlModuleVoltage
	global AirFlowRate
	global IntakeManifoldPressure

	while 1:
		try:
			try:
				RPM=carConnection.query(obd.commands.RPM).value.magnitude
				sleep(updateDelay)
			except Exception,e:
				RPM="Unsupported"
				debugPrintOBDII("Error! "+str(e))
			try:
				Speed=carConnection.query(obd.commands.SPEED).value.to("mph").magnitude
				sleep(updateDelay)
			except Exception,e:
				Speed="Unsupported"
				debugPrintOBDII("Error! "+str(e))

			try:
				CoolantTemp=carConnection.query(obd.commands.COOLANT_TEMP).value.magnitude*1.8+32 # From Celsius > Fahrenheit
				sleep(updateDelay)
			except Exception,e:
				CoolantTemp="Unsupported"
				debugPrintOBDII("Error! "+str(e))
			# try:
			# 	EngineOilTemp=carConnection.query(obd.commands.OIL_TEMP).value.magnitude*1.8+32 # From Celsius > Fahrenheit
			# 	sleep(updateDelay)
			# except Exception,e:
			# 	EngineOilTemp="Unsupported"
			# 	debugPrintOBDII("Error! "+str(e))
			try:
				AmbientAirTemp=carConnection.query(obd.commands.AMBIANT_AIR_TEMP).value.magnitude*1.8+32 # From Celsius > Fahrenheit
				sleep(updateDelay)
			except Exception,e:
				AmbientAirTemp="Unsupported"
				debugPrintOBDII("Error! "+str(e))
			try:
				IntakeAirTemp=carConnection.query(obd.commands.INTAKE_TEMP).value.magnitude*1.8+32 # From Celsius > Fahrenheit
				sleep(updateDelay)
			except Exception,e:
				IntakeAirTemp="Unsupported"
				debugPrintOBDII("Error! "+str(e))

			try:
				FuelPressure=carConnection.query(obd.commands.COOLANT_TEMP).value.magnitude*.14503773773020923 #From kilopascal > psi
				sleep(updateDelay)
			except Exception,e:
				FuelPressure="Unsupported"
				debugPrintOBDII("Error! "+str(e))
			try:
				FuelLevelInput=carConnection.query(obd.commands.FUEL_LEVEL).value.magnitude
				sleep(updateDelay)
			except Exception,e:
				FuelLevelInput="Unsupported"
				debugPrintOBDII("Error! "+str(e))

			try:
				EngineLoad=carConnection.query(obd.commands.ENGINE_LOAD).value.magnitude
				sleep(updateDelay)
			except Exception,e:
				EngineLoad="Unsupported"
				debugPrintOBDII("Error! "+str(e))
			try:
				ThrottlePosition=carConnection.query(obd.commands.THROTTLE_POS).value.magnitude
				sleep(updateDelay)
			except Exception,e:
				ThrottlePosition="Unsupported"
				debugPrintOBDII("Error! "+str(e))
			try:
				# EngineRunTime=carConnection.query(obd.commands.RUN_TIME).value.magnitude
				sleep(updateDelay)
			except Exception,e:
				EngineRunTime="Unsupported"
				debugPrintOBDII("Error! "+str(e))
			try:
				# WarmsupSinceDTCCleared=carConnection.query(obd.commands.WARMUPS_SINCE_DTC_CLEAR).value.magnitude
				sleep(updateDelay)
			except Exception,e:
				WarmsupSinceDTCCleared="Unsupported"
				debugPrintOBDII("Error! "+str(e))
			try:
				ControlModuleVoltage=carConnection.query(obd.commands.CONTROL_MODULE_VOLTAGE).value.magnitude
				sleep(updateDelay)
			except Exception,e:
				ControlModuleVoltage="Unsupported"
				debugPrintOBDII("Error! "+str(e))
			try:
				# AirFlowRate=carConnection.query(obd.commands.MAF).value.magnitude*0.0022 # Grams per second > pounds per second
				sleep(updateDelay)
			except Exception,e:
				AirFlowRate="Unsupported"
				debugPrintOBDII("Error! "+str(e))
			try:
				# IntakeManifoldPressure=carConnection.query(obd.commands.INTAKE_PRESSURE).value.magnitude*.14503773773020923 #From kilopascal > psi
				sleep(updateDelay)
			except Exception,e:
				IntakeManifoldPressure="Unsupported"
				debugPrintOBDII("Error! "+str(e))

			updateCount=updateCount+1

		except Exception, e:
			debugPrintOBDII("Error!" +str(e))


# OBD-II Logger
def OBDIILogger():
	global updateDelay
	global updateCount

	global RPM
	global Speed

	global CoolantTemp
	global EngineOilTemp
	global AmbientAirTemp
	global IntakeAirTemp

	global FuelPressure
	global FuelLevelInput

	global EngineLoad
	global ThrottlePosition
	global EngineRunTime
	global WarmsupSinceDTCCleared
	global ControlModuleVoltage
	global AirFlowRate
	global IntakeManifoldPressure

	try:
		MySQLCur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'obd-ii';")
		returnVal = str(MySQLCur.fetchall())
		ourTableID = "Log" + returnVal[2:returnVal.index(")")-2]

		# Create our new table
		MySQLCur.execute("CREATE TABLE "+ourTableID+" LIKE Template;")
		debugPrint1("Table " + ourTableID + " created, starting log")

		# index=0
		while 1:
			try:
				# Insert our data
				MySQLCur.execute("""INSERT INTO """+ourTableID+""" VALUES ('"""+str(seconds_elapsed())+"""', '"""+str(updateCount)+"""', '"""+str(RPM)+"""', '"""+str(Speed)+"""', '"""+str(CoolantTemp)+"""', '"""+str(EngineOilTemp)+"""', '"""+str(AmbientAirTemp)+"""', '"""+str(IntakeAirTemp)+"""', '"""+str(AirFlowRate)+"""', '"""+str(IntakeManifoldPressure)+"""', '"""+str(EngineLoad)+"""', '"""+str(ThrottlePosition)+"""', '"""+str(ControlModuleVoltage)+"""', '"""+str(FuelPressure)+"""', 'Unsupported!', '"""+str(FuelLevelInput)+"""');""")

		 	except Exception, e:
		 		sqldb.rollback()
		 		debugPrint1("Error! "+str(e))
		 		debugPrint1(str(traceback.format_exc()))

			sqldb.commit() # Save the table into the database
		 	# debugPrint1("Saved! Table:" + ourTableID)
			sleep(updateDelay*15)
			debugPrint1("Rerun " + ourTableID)

	except Exception, e:
		debugPrint1("Logger error! Error: " + str(e))
		debugPrint1(str(traceback.format_exc()))

	debugPrint1("Logger error! " + ourTableID + " try loop ended!")


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
			command = self.sock.recv(1024).decode()
			if command:
				# response=handleCommand(command)
				response="Disabled"
				try:
					#debugPrint('\nCommand recieved: ' + command + '\nResponse: ' + response.decode('utf-8'))
					a=0
				except Exception:
					debugPrint('\nError printing response/command, probably has unicode in it')
				self.sock.sendto(response,self.addr)
			else:
				self.stop()


def main():
	try:
		try:
			OBDIIProcess=Thread(target=OBDIILoop)
			OBDIIProcess.start()
		except Exception, e:
			debugPrint("Error in OBDIILoop: " + str(e))
			debugPrint(str(traceback.format_exc()))

		try:
			OBDIILog=Thread(target=OBDIILogger)
			OBDIILog.start()
		except Exception, e:
			debugPrint1("Error in OBDIILogger: " + str(e))
			debugPrint1(str(traceback.format_exc()))

		try:
			CGISocket.listen(5)
			debugPrint('Listening.')
			while 1:
				conn,add=CGISocket.accept()
				client(conn, add)
		except Exception, e:
			debugPrint("Error in OBDII-Listener: " + str(e))
			debugPrint(str(traceback.format_exc()))

	except KeyboardInterrupt:
		debugPrint("\nGoodbye")
		carConnection.close()
		os._exit(0)
	except Exception, e:
		debugPrint("Error!" + str(e))
		debugPrint(str(traceback.format_exc()))

	carConnection.close()
	MySQLCur.close()
	sqldb.close()
	os._exit(0)

	debugPrint("Goodbye!\n\n\n")
	debugPrintOBDII("Goodbye!\n\n\n")
	debugPrint1("Goodbye!\n\n\n")

if __name__ == "__main__":
	main()