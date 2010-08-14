#! /usr/bin/env python
# -*- encoding: utf-8 -*-

#test_sbgui.py

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

import unittest
from sys import path
path.append('..')

import sbexecutionengine

from sbgui import *

class test_sbgui:
	class fakeExecutionEngine():
		def getCommand(self):
			pass
		def executeNextCommand(self):
			pass
		def isComplete(self):
			return False
	
	def __init__(self):
		self.is_setup = False
		
	def setUp(self):
		assert not self.is_setup
		
		self.gui  = sbGUI(None,None)
		self.gui.engine = self.fakeExecutionEngine()
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		
		self.is_setup = True
		
	def tearDown(self):
		assert self.is_setup
		
		self.is_setup = False

	def startTimer(self, timer):
		self.timer 	= time.time() + timer

	def timeout(self):
		if time.time() > self.timer:
			return True
		return False

	def test_CatchWidgetInstantiation(self):
		wlabel	= "testButton"
		widget 	= gtk.Button(label=wlabel)

		self.window.add(widget)
		widget.show()
		self.window.show()
		
		self.startTimer(3.0)
		while not self.timeout():
			gtk.main_iteration(False)
		
			if self.gui.getWidgetByName(wlabel) is widget:
				return
		assert 0

	def test_registerEventHandler(self):
		try:
			self.gui.registerEventHandler()
		except NotImplementedError:
			assert 0
			
	
if __name__ == "__main__":
    unittest.main()
