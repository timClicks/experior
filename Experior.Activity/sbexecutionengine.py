#! /usr/bin/env python
# -*- encoding: utf-8 -*-

#sbexecutionengine.py

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

import gobject
import logging
import os
import pygtk
import sys
import threading
import time
import traceback

pygtk.require('2.0')
import gtk

from sbpython import *

class sbExecutionEngine:
	"""
	Responsible for communications with the XML-RPC server regarding command
	retrieval, as well as parsing and execution of those commands.
	"""
	def __init__(self, sbGUI, xmlRpcServer):
		self.sbgui 		= sbGUI
		self.rpc		= xmlRpcServer
		self.widgets 	= sbwidgets
		
		self.delayedExecution 	= False
		self.executionComplete	= False
		self.lastCommand		= None
		
		self.log = logging.getLogger("ExecutionEngine")

		try:
			self.id	= os.environ['SUGARBOT_ID']
		except KeyError:
			self.log.error("Sugarbot ID is not set.  Using default 0. ")
			self.id	= 0

	def killSugarbot(self):
		"""
		Kills the sugarbot activity.
		"""
		self.log.info("Attempting to kill sugarbot")
		sys.exit(0)
		
	def executePy(self):
		"""
		Executes the Sugarbot p◊ython script.
		
		Executes the Sugarbot python script provided by the XML-RPC server.
		Regards any unhandled exceptions as fatal errors, and reports them
		to the server.  Also handles the termination of Sugarbot if the
		auto-restart flag has been set by the XML-RPC server.
		"""
		self.script 		= self.rpc.getScript(self.id)
		self.log.info("Executing Script:\n%s" % self.script)
		
		self.widgets.gui 	= self.sbgui
				
		# Execute the actual python script.
		try:		
			exec self.script
			
			# t = threading.Thread(args=(self.widgets,))
			# t.run = sugarbot_main
			# t.start()
			
			sugarbot_main(self.widgets)
			self.rpc.success(self.id)
		
		# Something bad happened.  Report it, and log it.
		except:
			text = "Execution failed:\n%s" % traceback.format_exc()
			text = self.rpc.fail(text, self.id)
			self.log.error( text )
		
		# Regarless of the success status, check to see if we need to restart
		# sugarbot or not.
		finally:
			restart = self.rpc.getRestartFlag()
			self.log.info("Got restart flag: " + str(restart))
			
			if restart:
				self.killSugarbot()

		
	def isComplete(self):
		"""
		Returns true if execution is complete.
		
		Returns true if execution is complete, i.e. there are no more
		commands that can be executed.
		"""
		return self.executionComplete
