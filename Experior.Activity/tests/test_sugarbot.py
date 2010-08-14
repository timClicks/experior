#! /usr/bin/env python
# -*- encoding: utf-8 -*-

#test_sugarbot.py

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

from sugarbot import *

class rpcFailure(Exception):
	pass

class test_sugarbot:
	
	class cloneTest(activity.Activity):
		def __init__(self,x):
			self.clonedProperly = True
			
	class fakeXmlRpc:
		activity = "exampleActivity"
		def startScript(self, *args):
			return True
		def fail(self, reason, *args):
			raise rpcFailure
			
	class fakeXmlRpcGood(fakeXmlRpc):
		def getActivityName(self, *args):
			return self.activity
	
	class fakeXmlRpcBad(fakeXmlRpc):
		def getActivityName(self, *args):
			return None
					
	def __init__(self):
		self.is_setup = False

	def setUp(self):
		assert not self.is_setup

		self.sb = sugarbot(None)

		self.is_setup = True

	def tearDown(self):
		assert self.is_setup
		
		sugarbot.__bases__ = (activity.Activity, )
		
		self.is_setup = False
		
	def test_dynamicImport1(self):
		# Attempt to import a valid module
		assert gobject.GObject == \
				self.sb._sugarbot__dynamicImport("gobject.GObject")
				
	def test_dynamicImport2(self):
		# Attempt to import a module with a bad length or None
		assert activity.Activity == self.sb._sugarbot__dynamicImport("")
		assert activity.Activity == self.sb._sugarbot__dynamicImport(None)
				
	def test_dynamicImport3(self):
		# Attempt to import a module that does not exist
		try:
			assert activity.Activity == \
				self.sb._sugarbot__dynamicImport("asdf.1231231.##fw")
			assert 0
		except ImportError:
			pass
			
	def test_cloneActivity1(self):
		self.sb._sugarbot__parentClass = None
		try:
			self.sb._sugarbot__cloneActivity(None)
			assert 0
		except AttributeError:
			pass
		
	def test_cloneActivity2(self):
		self.sb._sugarbot__parentClass = self.cloneTest
		self.sb._sugarbot__cloneActivity(None)
		
		assert self.cloneTest in sugarbot.__bases__
		assert self.sb.clonedProperly
		
	def test_cloneActivity3(self):
		assert not self.cloneTest in sugarbot.__bases__
	
	def test_initializeScript1(self):
		fake 						= self.fakeXmlRpcGood()
		self.sb._sugarbot__xmlRPC 	= fake
		
		assert fake.activity == self.sb._sugarbot__initializeScript()
		
	def test_initializeScript2(self):
		fake 						= self.fakeXmlRpcBad()
		self.sb._sugarbot__xmlRPC 	= fake

		try:
			self.sb._sugarbot__initializeScript()
			assert 0
		except rpcFailure:
			pass
			
		

