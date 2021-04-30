#!/usr/bin/python

from termcolor import colored # Only for debugging
debug = True
def debugPrint(message):
    if debug:
        print colored("[DEBUG] " + str(message), "yellow")

import dbus
from xml.etree import ElementTree

bus=dbus.SystemBus()

# Returns an interface handle using your interface
def getInterface(path, interface):
    s=''
    if path!='' and path.startswith('/')!=True:
        s='/'
    # debugPrint("Path: " + path + " . S: " + s + " Startswith: " + str(path.startswith('/')) + " Empty: " + str(path==''))
    return dbus.Interface(bus.get_object('org.bluez', '/org/bluez' + s + path), interface)

# Returns a handle to change properties (fills in the interface part for you)
def getProperties(path):
    return getInterface(path,"org.freedesktop.DBus.Properties")

# Returns the introspect of a dbus address, kinda like a directory listing, but in xml
def renderSupport(path):
    iface = getInterface(path, 'org.freedesktop.DBus.Introspectable')
    return iface.Introspect()

# Internal use, please use renderPath or renderPathFull BUT renders your path maxDepth times. maxDepth = False; renders the path completely | maxDepth = True; renders the path with no depth
def _render(object_path, currentDepth=0, maxDepth=False):
    paths={}
    xml_string = renderSupport(object_path)
    for child in ElementTree.fromstring(xml_string):
        if child.tag == 'node':
            if maxDepth==False:
                new_path = '/'.join((object_path, child.attrib['name']))
                paths[child.attrib['name']]=_render(new_path,0,False)
            if maxDepth==True:
                paths[child.attrib['name']]={}
            elif currentDepth<=maxDepth:
                new_path = '/'.join((object_path, child.attrib['name']))
                paths[child.attrib['name']]=_render(new_path,currentDepth+1,maxDepth)
            else:
                paths[child.attrib['name']]={}
    return paths
## This just renders the top level path EX: {'hci0': {}, 'hci1': {}}
def render(object_path):
    return _render(object_path,0,True)

## This will render the and every sub path (so everything)
def renderAll(object_path):
    return _render(object_path, 0, False)