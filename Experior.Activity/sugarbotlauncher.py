#!/usr/bin/env python
# encoding: utf-8
"""
sugarbot-launcher.py

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
import logging
import os
import signal
import sys
import socket

from subprocess		import Popen
from time			import time,sleep
from xmlrpclib		import ServerProxy

# Set the Sugarbot path env var if it has not already been set
if not os.environ.has_key('SUGARBOT_PATH'):
	os.environ['SUGARBOT_PATH']=os.getcwd()
	
# Add the sugarbot path to the include-path
sys.path.append(os.environ['SUGARBOT_PATH'])

# Import sugar-specific stuff
from sbrpcserver	import proxyString, rebuildMarshalledObject, sugarbotSession
try:
	from sbconfig import clientName
except ImportError:
	from sbconfig_sample import clientName
	
class SugarProcessHandler():
	"""
	Handles launching and monitoring of the Sugar process.
	"""
	def __init__(self):
		# Set the environment variable to emulate, and the executed scripts.
		os.environ['SUGARBOT_EMULATOR']='1'

		# Get the connection to the XML-RPC server
		self.xml = self.connectToXMLRPC()
		logging.info("Connected to XML-RPC server %s" % proxyString())
		
		# Get our ID and reset the state
		self.ID	 = self.getSugarbotClientID()
		self.xml.resetClientState(self.ID)
		logging.info("Using session ID %s" % self.ID)

	def getSugarbotClientID(self):
		"""
		Retrieves whatever ID we should be using.  This is either set by the
		environment variables, the configuration file, or generated by the
		server.
		"""
		# If we have not specified a sugarbot ID, specify one now
		if not os.environ.has_key('SUGARBOT_ID'):
			if not clientName:
				os.environ['SUGARBOT_ID']=str(xml.generateSessionID())
			else:
				os.environ['SUGARBOT_ID']=clientName
				
		return os.environ['SUGARBOT_ID']
		
	def connectToXMLRPC(self):
		"""
		Connects to the ML-RPC server, tests connectivity.
		"""
		xml 		= ServerProxy(proxyString())
		try:
			xml.testConnectivity()
		except:
			logging.fatal('Could not connect to the XML-RPC server')
			sys.exit(1)
		
		return xml
	
	def launchSugar(self):
		"""
		Launches the sugar-emulator process and waits for it to finish.
		"""
		# Launch the process
		self.pid 	= Popen('sugar-emulator')
		self.waitForSugarbotExecution()

	def waitForSugarbotExecution(self):
		"""
		Waits a certain amount of time for Sugar to quit.
		
		If Sugar does not die in the alloted time, it is killed.
		"""
		# Wait five minutes for the tests to execute?  Why not.
		start 	= time()
		wait	= 60*5
		done	= start + wait
	
		# We've waited long enough. Kill it!
		while self.pid.poll() is None and done > time():
			sleep(0.1)
		if self.pid.poll() is None:
			logging.fatal("Had to send SIGTERM to Sugar process")
			os.kill(self.pid.pid, signal.SIGTERM)
		
	def getReturnValue(self):
		"""
		Determines whether all of the tests succeeded, or there was a failure.
		
		0 = All tests succeeded
		1 = At least one failure
		"""
		# Get the completion status...
		sessionDict	= self.xml.completionStatus(self.ID)
		if sessionDict is None:
			logging.error("Could not get completion status from XMLRPC server")
			return -1
		
		session		= sugarbotSession()
		rebuildMarshalledObject(session, sessionDict)
		
		# Get whatever the return value should be.
		retval 		= session.getSuccessValue()
	
		# Print out the completion statuses all pretty-like
		status = ""
		logging.info("Script completion statuses:")
		for script in session.responses:
			logging.info("\t%s: %s" % (session.responses[script], script)) 
			
			# if session.failureText.has_key(script) and \
			# 				not session.responses[script]:
			if not session.responses[script]:
				logging.info("================ [%s] ================", script)
				for line in session.failureText[script].split('\n'):
					if len(line) > 0:
						logging.info(line)
				logging.info("================ [%s] ================", script)
				
			
		# Check the number of scripts to make sure they all executed
		numScripts = self.xml.numberOfScripts()
		if( numScripts > len(session.responses) ):
			retval = False
			logging.warning("Only executed %i/%i scripts" %  \
							(numScripts,len(session.responses)) )
			
		return retval

def main():
	s = SugarProcessHandler()
	s.launchSugar()
	
	retval = s.getReturnValue()
	logging.info("Returning %s" % retval)
	
	return retval

if __name__ == "__main__":
	main()

else:
	import pygtk
	pygtk.require('2.0')
	import gtk
	import gobject
	import time

	from view.Shell 		import Shell
	from model.shellmodel 	import ShellModel
	from shellservice 		import ShellService

	from view.frame.activitiestray	import ActivitiesTray
	from view.frame.activitybutton 	import ActivityButton
	
	class SugarbotLauncher:
		"""
		Autmates the launching and re-launching of Sugarbot from the main Sugar
		GUI.  This automation is handled by simulating a click on the Sugarbot
		activity icon in the Sugar Pane.
		"""
		activityName = "sugarbot"

		def __init__(self, shell, shellModel):
			gtk.gdk.event_handler_set(self.eventHandler)
			self.model				= shellModel
			self.numberOfScripts	= 0
			self.shell 				= shell
			self.sugarbotIsRunning 	= False
			self.timesLaunched		= 0
			self.xml = ServerProxy(proxyString())
	
			home	= self.model.get_home()
			home.connect('activity-started', self._activity_started_cb)
			home.connect('activity-removed', self._activity_removed_cb)
			home.connect('active-activity-changed', self._activity_active_cb)	
			home.connect('pending-activity-changed', self._activity_pending_cb)		
		
		def isSugarbotActivity(self,activity):
			"""
			Checks to see if an 'Activity' object is the sugarbot activity.
			"""
			if activity._activity_info.name == self.activityName:
				if self.numberOfScripts <= 0:
					self.doSetup(activity)
				return True
			return False
	
		def doSetup(self, activity):
			"""
			Prepares for launching the activity, given its information.
			"""
			path = activity._activity_info.path
			sys.path.append(path)
	
			try:
				self.numberOfScripts = self.xml.numberOfScripts()
			except:
				logging.fatal("Could not connect to XMLRPC Server")
				sys.exit(-1)
		
		def _activity_started_cb(self, model, activity):
			if self.isSugarbotActivity(activity):
				self.sugarbotIsRunning = True
				self.timesLaunched += 1

		def _activity_removed_cb(self, model, activity):
			if self.isSugarbotActivity(activity):
				self.sugarbotIsRunning = False
		
				if self.xml.getKillFlag() and \
					1 <= self.numberOfScripts <= self.timesLaunched:
					logging.info("Sugarbot execution completed successfully")
					self.killSugar()		
	
		def _activity_active_cb(self, model, activity):
			pass
	
		def _activity_pending_cb(self, model, activity):
			pass
	
		def killSugar(self):
			"""
			Sends SIGTERM to the Sugar process.
			"""
			try:
				if os.environ.has_key('SUGAR_EMULATOR_PID'):
					pid = int(os.environ['SUGAR_EMULATOR_PID'])
					os.kill(pid, signal.SIGTERM)
			except:
				raise
	
		def tryToLaunchSugarbotActivity(self):	
			"""
			Attempts to launch sugarbot.
			"""
			if self.sugarbotIsRunning or not self.xml.getRestartFlag():
				# time.sleep(0.1)
				return
			
			frame 				= self.shell.get_frame()
			frameBottomPanel 	= frame._bottom_panel
			bottomPanelChildren = frameBottomPanel._bg.get_children()
			tray = [k for k in bottomPanelChildren if isinstance(k,ActivitiesTray)]
	
			if tray:
				trayIcons = tray[0]._tray.get_children()
			else:
				return
	
			activities 	= [k for k in trayIcons if isinstance(k, ActivityButton)]
			sbList 		= [k for k in activities if \
			 						k._activity_info.name == self.activityName]
	
			if len(sbList) > 0:
				sbList[0].emit('clicked')
				self.sugarbotIsRunning = True
	
		def eventHandler(self, event):
			"""
			Intercepts GTK calls, to attempt to launch sugarbot.
			
			Attempts to launch sugarbot at every gdk.Event emitted.
			"""
			if event is not None:
				gtk.main_do_event(event)
			self.tryToLaunchSugarbotActivity()
	
