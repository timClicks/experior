#! /usr/bin/env python
# -*- encoding: utf-8 -*-

#test_sbexecutionengine.py

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

from sys import path
path.append('..')

from sbexecutionengine import *

logging.raiseExceptions = 0

class failException(Exception): pass
class successException(Exception): pass

class test_sbExecutionEngine:
		
	class fakeXmlRpc:
		def __init__(self):
			self.assertionValue = 1
			self.restart 	= False
			self.kill 		= False
			self.status		= False
			
		def success(self, clientID=None):
			# raise successException
			# We can't raise exceptions on success, because of the way
			# sbExecutionEngine works.  Any exceptions call fail()
			self.status = True
			
		def fail(self, reason=None, clientID=None):
			raise failException	
			
		def getRestartFlag(self):
			return self.restart
			
		def getKillFlag(self):
			return self.kill
			
		def getScript(self, dontCare):
			return \
"""
def sugarbot_main(param):
	assert param
"""	

	def __init__(self):
		self.is_setup = False
		
	def setUp(self):
		assert not self.is_setup
							
		self.xml 	= self.fakeXmlRpc()
		self.ee 	= sbExecutionEngine(None,self.xml)
				
		self.is_setup 	= True
		
	def tearDown(self):
		assert self.is_setup
		
		self.is_setup 	= False
			
	def test_setComplete(self):
		assert not self.ee.isComplete()
		self.ee.executionComplete = True
		assert self.ee.isComplete()
		
	def test_killSugarbot(self):
		try:
			self.ee.killSugarbot()
			assert 0
		except SystemExit:
			pass
			
	def test_executePy_Fail(self):
		try:
			self.ee.widgets.__nonzero__ = lambda: False
			self.ee.executePy()
			assert 0
		except failException:
			pass
			
	def test_executePy_Success(self):	
		# try:
		self.ee.widgets.__nonzero__ = lambda: True
		self.ee.executePy()

		assert self.xml.status == True

	def test_executePy_UnexpectedException(self):
		try:
			def raiseException():	raise ValueError
			
			self.ee.widgets.__nonzero__ = raiseException
			self.ee.executePy()
			assert 0
		except:
			pass
