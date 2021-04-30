from btadapter import BTAdapter
from time import sleep

adapter = BTAdapter('hci0')

if not adapter.ConnectedDevice:
	adapter.AutoConnect()

device = adapter.ConnectedDevice

if device:
	if not device.NConnected:
		print("Connecting...")
		device.NConnect("nap")
		print("Connected>>??")

	print("Checking...")
	sleep(3)

	if device.NConnected:
		print("Connected!")
		print("Interface: %s" % device.NInterface)
