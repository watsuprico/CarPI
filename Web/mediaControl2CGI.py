#!/usr/bin/python

import cgi
import cgitb
cgitb.enable()

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

data = cgi.FieldStorage()
command=data.getvalue("command")
print "Content-Type: text/html\n"

# Send commands to the python script (so I don't have to scrub dbus for every method just to pause the music (it's cpu intensive))
import socket
CGISocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Their end


try:
	CGISocket.connect(("localhost",8002))
	CGISocket.send(command)
	Response=""
	Response=CGISocket.recv(1024).decode('utf-8')
	CGISocket.close()
	print Response
except socket.error:
	raise SystemExit()
except Exception, e:
	print "sys_error - "+str(e)

raise SystemExit(0)