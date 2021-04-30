#!/usr/bin/python

# Enables pin auth mode...
# (IE you have to enter the correct SET pin on your phone to connect.)
# (( you MUST run hciconfig hci0 sspmode 0 to allow this to work ))


from __future__ import absolute_import, print_function, unicode_literals

from optparse import OptionParser
import dbus
import dbus.service
import dbus.mainloop.glib
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject
import bluezutils

BUS_NAME = 'org.bluez'
AGENT_INTERFACE = 'org.bluez.Agent1'
AGENT_PATH = "/CarPI/agent"

bus = None
device_obj = None
dev_path = None


def set_trusted(path):
	props = dbus.Interface(bus.get_object("org.bluez", path),
					"org.freedesktop.DBus.Properties")
	props.Set("org.bluez.Device1", "Trusted", True)

class Agent(dbus.service.Object):
	@dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
	def AuthorizeService(self, device, uuid):
		print("AuthorizeService (%s, %s)" % (device, uuid))
		return

	@dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
	def RequestPinCode(self, device):
		print("Validate pincode (RequestPinCode) for: (%s)" % (device))
		set_trusted(device)
		return "3211"

if __name__ == '__main__':
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bus = dbus.SystemBus()
	capability = "KeyboardOnly"

	parser = OptionParser()
	parser.add_option("-i", "--adapter", action="store", type="string", dest="adapter_pattern", default=None)
	parser.add_option("-c", "--capability", action="store", type="string", dest="capability")
	parser.add_option("-t", "--timeout", action="store", type="int", dest="timeout", default=60000)
	(options, args) = parser.parse_args()
	if options.capability:
		capability  = options.capability

	agent = Agent(bus, AGENT_PATH)
	mainloop = GObject.MainLoop()
	obj = bus.get_object(BUS_NAME, "/org/bluez");
	manager = dbus.Interface(obj, "org.bluez.AgentManager1")
	manager.RegisterAgent(AGENT_PATH, capability)

	print("Agent registered")

	# Fix-up old style invocation (BlueZ 4)
	if len(args) > 0 and args[0].startswith("hci"):
		options.adapter_pattern = args[0]
		del args[:1]

	if len(args) > 0:
		device = bluezutils.find_device(args[0],
						options.adapter_pattern)
		dev_path = device.object_path
		agent.set_exit_on_release(False)
		device.Pair(reply_handler=pair_reply, error_handler=pair_error,
								timeout=60000)
		device_obj = device
	else:
		manager.RequestDefaultAgent(AGENT_PATH)

	mainloop.run()