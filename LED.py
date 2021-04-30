#!/usr/bin/python

from termcolor import colored # Only for debugging
debug = True
def debugPrint(message):
    if debug:
        print colored("[DEBUG] " + str(message), "yellow")

# LEDs
from time import sleep
import pigpio
from random import randint
from multiprocessing import Process, Manager
pi = pigpio.pi()

Stop=False

redPIN=17
greenPIN=22
bluePIN=24

serviceColors={"red":0.0,"blue":0.0,"green":0.0}
stopService = False


brightness=1 # 0-1 (.5=half)

# RGB Led stuff
def colorToPin(color):
	if color=="red":
		return redPIN
	elif color=="green":
		return greenPIN
	else:
		return bluePIN

def current(color):
	current=0.0
	try:
		current=pi.get_PWM_dutycycle(colorToPin(color))
	except Exception:
		current=0
	return current

def setColor(color, val):
	val=round(abs(val)*brightness,5)
	if val>255:
		val=255
	elif val<0:
		val=0
	pi.set_PWM_dutycycle(colorToPin(color),val)

def fadeFromTo(color,Int,End,duration, isService=False, force=False):
	global stopService
	stopService = False
	if not isService:
		stopService = True
	if stopService and isService and not force:
		return ""
	Int=round(abs(Int),5)
	End=round(abs(End),5)
	if Int>255:
		Int=255
	elif Int<0:
		Int=0
	if End>255:
		End=255
	elif End<0:
		End=0

	if isService:
		serviceColors[color]=End

	#debugPrint(color+" is fading "+str(Int)+"->"+str(End)+" using duration: " + str(duration))
	if duration!=0 and Int-End!=0:
		duration=abs(duration)/abs(Int-End)
	if Int>End:
		while Int>=End and not Stop:
			setColor(color, Int)
			sleep(duration)
			Int=Int-1
	else:
		while Int<=End and not Stop:
			setColor(color, Int)
			sleep(duration)
			Int=Int+1

	if not isService and not force:
		fadeToRGB(serviceColors["red"],serviceColors["green"],serviceColors["blue"],0.5,True,True)

def fadeTo(color,to,duration,  isService=False, force=False):
	fadeFromTo(color,current(color),to,duration,isService, force)

def fadeIn(color, duration, isService=False, force=False):
	fadeTo(color,255,duration,isService, force)
def fadeOut(color,duration, isService=False, force=False):
	fadeTo(color,0,duration,isService, force)

def fadeRGBToRGB(redIntValue,greenIntValue,blueIntValue,redEndValue,greenEndValue,blueEndValue,duration, isService=False, force=False):
	redChange=redEndValue-redIntValue
	greenChange=greenEndValue-greenIntValue
	blueChange=blueEndValue-blueIntValue
	maxChange=max(abs(redChange),abs(greenChange),abs(blueChange),1)
	redInc=0.0
	greenInc=0.0
	blueInc=0.0
	if redChange==0:
		redInc=0
	else:
		redInc=round((redChange/maxChange),5)
	if greenChange==0:
		greenInc=0
	else:
		greenInc=round((greenChange/maxChange),5)
	if blueChange==0:
		blueInc=0
	else:
		blueInc=round((blueChange/maxChange),5)
	red=redIntValue
	green=greenIntValue
	blue=blueIntValue
	# debugPrint("maxChange: " + str(maxChange))
	# debugPrint("redChange: " + str(redChange))
	# debugPrint("greenChange: " + str(greenChange))
	# debugPrint("blueChange: " + str(blueChange))
	# debugPrint("red: " + str(red))
	# debugPrint("green: " + str(green))
	# debugPrint("blue: " + str(blue))
	# debugPrint("redInc: " + str(redInc))
	# debugPrint("greenInc: " + str(greenInc))
	# debugPrint("blueInc: " + str(blueInc))
	# debugPrint("redEndValue: " + str(redEndValue))
	# debugPrint("greenEndValue: " + str(greenEndValue))
	# debugPrint("blueEndValue: " + str(blueEndValue))
	# debugPrint("duration: " + str(duration))
	if duration!=0:
		duration=abs(duration)/maxChange
	i=0
	while i<maxChange:
		red=red+redInc
		green=green+greenInc
		blue=blue+blueInc
		fadeTo("red",red,duration/3,isService, force)
		fadeTo("green",green,duration/3,isService, force)
		fadeTo("blue",blue,duration/3,isService, force)
		sleep(duration)
		i=i+1

def fadeToRGB(redEndValue,greenEndValue,blueEndValue,duration, isService=False, force=False):
	fadeRGBToRGB(current("red"),current("green"),current("blue"),redEndValue,greenEndValue,blueEndValue,duration,isService, force)