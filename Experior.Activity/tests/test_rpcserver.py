#!/usr/bin/env python
# encoding: utf-8
"""
test_rpcserver.py

This file is part of sugarbot.

sugarbot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

sugarbot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with sugarbot.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import unittest
from sys import path
from random import randint

from xmlrpclib import ServerProxy

path.append("..")

try:
	import sbconfig
except ImportError:
	import sbconfig_sample
from sbrpcserver import *


class TestRPCServer(unittest.TestCase):
	
	files 			= ["fileOne.py", "fileTwo.py"]
	activityNames 	= ["activityOne", "activityTwo"]
	basicScript 	=  \
"""
def sugarbot_main(var):
	assert var

"""
	scripts 	= [basicScript + "sugarActivityName = '%s'" % activityNames[0],
					basicScript + "sugarActivityName = '%s'" % activityNames[1]]
	
	def __init__(self):
		self.is_setup = False
		
	def setUp(self):
		assert not self.is_setup
		
		# Generate a random ID
		self.clientID	= randint(1,1000)
		
		# Create the server object.
		self.server = sbRpcServer([], None)
		
		# Create the script file and add it...
		self.createScriptFiles()
		for file in self.files:
			self.server.addScript(file)
				
		self.is_setup = True

		
	def tearDown(self):
		assert self.is_setup
		
		self.server.server_close()
		self.deleteScriptFiles()
		
		self.is_setup = False
		
	def createScriptFiles(self):
		for i in range(0, len(self.scripts)):
			f = open(self.files[i],"w+")
			f.write(self.scripts[i])
			f.close()
	
	def deleteScriptFiles(self):
		for f in self.files:
			os.remove(f)
		
	def test_StartScript_Reset(self):
		self.server.startScript(self.clientID)
		
		client = self.server.clients[self.clientID]
		client.currentScript  = 999999
		
		self.server.startScript(self.clientID)
		
		assert client.currentScript == 0
		assert client.responses[client.scriptName] == False
	
	def test_StartScript_Bounds(self):
		# Check to see if we go beyond the bounds
		for count in range(0,1+len(self.server.listOfScripts)):
	 		self.server.startScript()
		assert self.server.clients[0].currentScript == 0

	def test_RegisteredFunctions(self):		
		expectedMethods 	= ['addScript',
								'completionStatus',
								'fail',
								'generateSessionID',
								'getActivityName',
								'getRestartFlag',
								'getScript',
								'numberOfScripts',
								'startScript',
								'success']
		listedMethods		= self.server.system_listMethods()
							
		for method in expectedMethods:
			if not method in listedMethods:
				print method
				assert 0		
			
		assert not 'NOTREGISTERED' in listedMethods
	
	def test_getActivityName_IndexError(self):
		try:
			self.server.startScript(self.clientID)
			self.server.getActivityName(self.clientID, 9999)
			assert 0
		except IndexError:
			pass
			
	def test_getActivityName_WithoutStartingScript(self):
		try:
			self.server.getActivityName(self.clientID)
			assert 0
		except IndexError:
			pass
			
	def test_getActivityName(self):
		for activity in self.activityNames:
			self.server.startScript()
			assert self.server.getActivityName() == activity
	
	def test_multipleCallsToGetScript(self):
		for script in self.scripts:
			self.server.startScript()
			assert self.server.getScript() == script

if __name__ == "__main__":
	unittest.main()
