#! /usr/bin/env python
# -*- encoding: utf-8 -*-

#sbrpcserver.py

#This file is part of sugarbot.

#sugarbot is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#sugarbot is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with sugarbot.  If not, see <http://www.gnu.org/licenses/>.

import binascii
import logging
import optparse
import os
import random
import sblog
import sys
import time
import xmlrpclib

from SimpleXMLRPCServer import SimpleXMLRPCServer
try:
	from sbconfig import host, port
except ImportError:
	from sbconfig_sample import host, port

def proxyString():
	return "http://%s:%s/" %  (host, str(port))
	
def rebuildMarshalledObject(obj, dictionary):
	for key in dictionary:
		setattr(obj, key, dictionary[key])
	
class sugarbotSession():
	def __init__(self,ID=0):
		self.id 			= ID
		# self.responses 		= []
		self.responses		= {}
		self.currentScript 	= -1
		self.scriptName		= ""
		self.failureText	= {}
		# self.log = logging.getLogger("%s" % ID)
		
	def getSuccessValue(self):
		retval = 0
		
		failed = [self.responses[k] for k in self.responses if not self.responses[k]]
		if failed:
			retval = 1
		return retval
		
	log = property(lambda self: logging.getLogger(str(self.id)))
	
class sbRpcServer(SimpleXMLRPCServer):
	"""
	Sugarbot RPC Server
	
	Responsible for listening on the XML-RPC port (defined as
	sbconfig.port).  The object loads the scripts provided
	on the command-line as individual text lines.  It then provides those
	lines of text over XML-RPC to the XML-RPC client.  The client is
	responsible for parsing the lines into meaningful objects/functions.
	
	The list of files, as well as each file's contents, are kept entirely in
	memory.  This may lead to issues in the future with particularly large
	script files, but this is currently not a problem.
	"""
	sugarbotActivityVar = 'sugarActivityName'

	def __init__(self, scripts=[], xmlport=port, kill=False, restart=False):
		# Random port?
		if xmlport is None:
			xmlport = random.randint(1024,65000)
		self.port = xmlport
		
		# Create the RPC server		
		SimpleXMLRPCServer.__init__(self, (host, xmlport), 
									allow_none=True, logRequests=False)

		# Create the logger
		self.log = self.initializeLogging()
		self.log.info("Listening on port %i" % xmlport)

		# A listing of the filenames for each script
		self.listOfScripts = []
		
		# Keep list of all of the clients
		self.clients		= {0: sugarbotSession(0)}
		
		# Misc other stuffs...
		self.kill			= kill
		self.restart		= restart
		self.log.info("Kill: %s\tRestart: %s" % (kill,restart))

		for script in scripts:
			self.addScript(script)
		
		# Register all of the functions so that callers can use them
		self.registerFunctions()
		
		# Initialize the random seed for generating client ID's
		self.initRandomSeed()
	
	def testConnectivity(self):
		"""
		This function exists so that the client can test the connection to the
		XML-RPC server.  The xmlrpclib throws a socket.error if a function is
		called when the ServerProxy object is not connected.  
		This provides a simple method so that we don't have to worry 
		about screwing with the internal state of other stuff.
		"""
		pass
	
	def initRandomSeed(self):
		"""
		Initializes the random seed using os.urandom.
		"""
		# Initialize the random seed...
		seed = 0
		try:
			seed = long(binascii.hexlify(os.urandom(64)), 16)
		except NotImplementedError:
			seed = time.time()
		random.seed(seed)
		
	def generateSessionID(self):
		"""
		In the event a client does not specify an identifier, provide one.
		"""
		return random.randint(0, sys.maxint)
		
	def initializeLogging(self):
		"""
		Initialize logging for the sbRpcServer object.  This provides logging
		of INFO and above to the terminal, and all statements go to
		a file named sbRpcServer.log.
		"""
		if __name__ == '__main__':
			logging.basicConfig(level=logging.DEBUG,
			                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
			                    datefmt='%m-%d %H:%M',
			                    filename='sbRpcServer.log')
			
			# define a Handler which writes INFO messages or higher to the sys.stderr
			console = logging.StreamHandler()
			console.setLevel(logging.INFO)			
			# set a format which is simpler for console use
			formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
			# tell the handler to use this format
			console.setFormatter(formatter)
			# add the handler to the root logger
			logging.getLogger('').addHandler(console)

		return logging.getLogger('sbRpcServer')
		
	def registerFunctions(self):
		"""
		Register the functions for use with the XML server.
		Recommended internal use only.
		"""
		self.register_function(self.addScript)
		self.register_function(self.completionStatus)
		self.register_function(self.fail)
		self.register_function(self.generateSessionID)
		self.register_function(self.getActivityName)
		self.register_function(self.getKillFlag)
		self.register_function(self.getRestartFlag)
		self.register_function(self.getScript)
		self.register_function(self.numberOfScripts)
		self.register_function(self.resetClientState)		
		self.register_function(self.startScript)
		self.register_function(self.success)
		self.register_function(self.testConnectivity)

	def numberOfScripts(self):
		"""
		Returns the number of scripts for execution.
		"""
		return len(self.listOfScripts)
		
	def haveClient(self,ID):
		"""
		Determine whether or not we have a given client in tracking.
		"""
		return self.clients.has_key(ID)
		
	def getClient(self, ID):
		"""
		Returns the sugarbotSession object corresponding to the provided ID.
		
		If such a sugarbotSession object does not exist, it is created.
		"""
		if not self.haveClient(ID):
			self.clients[ID] = sugarbotSession(ID)
			
		return self.clients[ID]
		
	def completionStatus(self,ID=0):
		"""
		Returns the completion status of all of the scripts as a list.
		For example, if there were a total of three scripts, and the second
		script had a command that did not complete successfully, the return
		value would be:
		[True, False, True]
		
		If no failures were reported:
		[True, True, True]
		
		All values are initialized to False.  If a script is still running,
		then at least one of the result-values will be False.
		
		Removes the client from tracking.  When the client re-connects, it
		will effectively have a clean slate.
		"""
		retval = []
		if self.haveClient(ID):	
			retval = self.clients[ID]
			self.resetClientState(ID)
		else:
			retval = None	
		
		return retval
		
	def resetClientState(self, ID=0):
		"""
		Clears a client from tracking.  
		
		When the client re-connects, it will start with a clean slate.
		"""
		if self.haveClient(ID):
			client = self.getClient(ID)
			
			# Get a completed ratio
			r 			= client.responses
			successes	= len([r[k] for k in r if r[k] is True])
			completed 	= len(r)
			overall		= len(self.listOfScripts)
			self.clients[ID].log.info("Disconnected [%s\%s\%s]" % \
						(successes, completed, overall))
			del self.clients[ID]
		
	def scriptOutOfBounds(self,ID):	
		"""
		Checks to see if a client's script index is out-of-bounds.
		"""
		client = self.getClient(ID)
		
		if client.currentScript < 0:
			return True
		
		if client.currentScript >= len(self.listOfScripts):
			return True
				
	def success(self, ID=0):
		"""
		This method is called after the successful completion of a script
		"""
		client = self.getClient(ID)
		client.log.info("Success (%s)" % client.scriptName) 
		client.responses[client.scriptName] = True
		
	def modifyTraceBackText(self, text, ID=0):
		"""
		Replaces '<string>' with the script name in a backtrace report.
		
		This is useful in determining _which_ script failed execution.
		"""
		client = self.getClient(ID)
		
		if "File \"<string>\"" in text:
			# Get the text..
			replacementText = "Sugarbot Script: '%s'" % client.scriptName
			
			# Replace the string with the filename
			text = text.replace("<string>", replacementText)
		return text
					
	def fail(self, status="No status provided", ID=0):
		"""
		This method is called if, for some reason, the client needs to disconnect
		prematurely.  A status message/reason is required.
		"""
		client = self.getClient(ID)
		
		# If the client is sending us exception text, replace that select
		# portions of the text to be more useful.
		status = self.modifyTraceBackText(status, ID)
		
		# Print the error
		client.log.error("%s" % status)
		client.responses[client.scriptName] = False
		client.failureText[client.scriptName] = status
					
		return status
		
	def startScript(self,ID=0):
		"""
		Increments the internal script counter, looping back to the first
		script if necessary.  This should be the first method that a client
		calls.
		"""
		# Get the client.  This will create it if it does not exist.
		client = self.getClient(ID)
		
		# Next script! (Note that the value is initialized to be -1)
		client.currentScript += 1
	
		# Prevent overflows if, for some reason, we loop back to script 0
		if self.scriptOutOfBounds(ID):
			client.currentScript = 0
			
		# Update the client's script name
		client.scriptName = self.listOfScripts[client.currentScript]
		
		# Pretty status message...
		client.log.info("Starting %s" % client.scriptName)

		# Make room for another response (default to failure)
		client.responses[client.scriptName] = False
		
		return True
		
	def getScript(self,ID=0):
		"""
		Returns the script that the client should execute.
		"""
		client = self.getClient(ID)
		client.log.info("Getting Script: %s" % client.scriptName )
		
		f = open(self.listOfScripts[client.currentScript])
		listOfLines = f.readlines()
		longString	= ''
		for line in listOfLines:
			longString += line
		
		f.close()
			
		return longString
		
	def getActivityName(self, ID=0, which=None):
		"""
		Imports from the specified script file in order to 
		"""
		client = self.getClient(ID)
		if which is None:
			which = client.currentScript
			
		if which == -1:
			raise IndexError, "Invalid script index. If calling " + \
				"getActivityNameMake without arguments, make sure that " + \
				"startScript gets called first."
				
		try:
			moduleName 	= self.listOfScripts[which]
			index 		= moduleName.find(".py")
			if index is not -1:
				moduleName	= moduleName[:index]
			
			execStr = 'from %s import %s' %  \
					(moduleName, self.sugarbotActivityVar)
					
			evalStr = '%s' % self.sugarbotActivityVar
			
			exec execStr
			return eval(evalStr)
		except:
			raise
	
	def getKillFlag(self):
		return self.kill
	
	def getRestartFlag(self):
		return self.restart
		
	def addScript(self,scriptPath):
		"""
		Adds a script to the internal list of scripts.  This causes the parser
		to load the script contents into memory for fast/easy access.
		"""
		self.listOfScripts.append(scriptPath)
				
		activityName = self.getActivityName(which=len(self.listOfScripts)-1 )
		self.log.info("Added script %s [Activity %s]" \
					% (scriptPath, activityName) )

		
def main(argv=None):
	p = optparse.OptionParser()
	p.add_option('--no-restart', dest='restart', action='store_false',default=True,
					help='do NOT restart sugarbot after execution has completed')
	p.add_option('--no-kill', dest='kill', action='store_false',default=True,
					help='do NOT kill sugar after all sugarbot scripts have executed')
			
	(options,args) = p.parse_args()
	
	if len(args) < 1:
		p.print_help()
		return 1
		
	server = sbRpcServer(args, kill=options.kill, restart=options.restart)		
	
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print 'Ctrl+C pressed, exiting...'
    
if __name__ == '__main__':
	main()
