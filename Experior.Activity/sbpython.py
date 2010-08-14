#!/usr/bin/env python
# encoding: utf-8
"""
sbpython.py

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

import sys
import time
import gtk
import logging
from gtk import gdk
import gobject
from sbdecorators import *

import sugar
from sugar import graphics
from sugar.graphics.toolcombobox import ToolComboBox

class NotSupportedError(NotImplementedError):
	def __init__(self, widget=None, command=None):
		self.widget 	= widget
		self.command 	= command
	def __str__(self):
		return repr('The widget %s [%s] does not support the command(s) %s' \
		 				% (self.widget, self.widget.__class__, self.command))
		
class WidgetDoesNotExist(ValueError):
	def __init__(self, widget=None):
		self.widget 	= widget
	def __str__(self):
		return repr('The widget %s could not be identified.' % self.widget)
	

class wrappedWidget(object):
	raiseExceptions = True
	
	def __init__(self, widget, name):
		self.widget = widget
		self.name	= name
		self.log	= logging.getLogger('w(%s)' % name)
		
	def __getitem__(self, index):
		"""
		Returns the indexed item.  
		
		For ComboBox and similar items, this will effectively be the n'th object.
		Uses a helper function for each class type.
		"""
		indexMethods = \
		{ 
			gtk.ComboBox: self.getList_GtkComboBox,
		 	ToolComboBox: self.getList_SugarGraphicsCombo,
			# gtk.Container: self.getList_Container
		}

		for classType in indexMethods:
			if isinstance(self.widget, classType):
				return indexMethods[classType]()[index]

	def notSupportedError(self, args):
		"""
		Wrapper for raising NotSupportedError exceptions.
		"""
		if self.raiseExceptions:
			raise NotSupportedError, (self.widget, args)
		return None

	def supportsSignal(self, signalName):
		"""
		Checks to see if a GTK object supports a signal.
		
		Checks to see if a GTK object supports a signal, via the
		gobject.signal_lookup method.  Returns True if it is supported,
		false otherwise.
		"""
		return gobject.signal_lookup(signalName, self.widget.__class__) != 0
		
	def click(self):
		"""
		Simulates a user click.
		
		Simulates a user click by:
		 1) Emitting a 'clicked' signal
		 2) Calling the 'activate' method
		"""
		self.log.info("Clicking %s" % self.name)
		
		widgetClass	= self.widget.__class__
		
		clickedSignal	= 'clicked'
		activateMethod	= 'activate'
		
		# Attempt to emit the 'clicked' signal.
		if self.supportsSignal(clickedSignal):		
			self.widget.emit(clickedSignal)		
			return True
			
		# Attempt to simply 'activate' the widget.
		elif hasattr(self.widget, activateMethod):
			getattr(self.widget, activateMethod)()
			return True
			
		# Fail gracefully
		return self.notSupportedError((clickedSignal, activateMethod))
		
	
	def getText(self):
		"""
		Returns the text in the widget.
		
		Returns whatever text is being stored by the widget.  This function
		gives priority to Widget functions in the following order:
	 	 1) get_text method
		 2) label (same as getLabel)
		 3) title (same as getTitle)
 		"""
		self.log.info("Getting text for %s" % self.name)
		
		getText		= "get_text"

		# Get the text from the widget		
		# try:	return self.__simpleGetter(getText)
		# except NotSupportedError: 	pass
		if hasattr(self.widget, getText):
			return getattr(self.widget, getText)()
		
		# Special handling for sugar ToolComboBox
		if isinstance(self.widget, ToolComboBox):
			logging.fatal("YES!!!")
			return self.widget.combo.get_active_item()[0]
			
		# Try the label
		try: 	return self.label
		except NotSupportedError: 	pass
		
		# Try the title
		try:	return self.title
		except NotSupportedError:	pass
	
		# Fail
		return self.notSupportedError((getText,"label","title"))
		
	def typeText(self, val):
		"""
		Simulates user text entry.
		
		Simulates a user typing into a widget.  Inserts the text at the
		current insertion location, via:
		 1) Emits the 'insert-at-cursor' signal.
		"""
		self.log.info("Adding text for %s to %s" % (self.name, val))
		
		terminalMethod 	= "feed_child"
		insertAtCursor	= 'insert-at-cursor'
		
		if self.supportsSignal(insertAtCursor):
			self.widget.emit(insertAtCursor, val)
			return True
		
		# --- TERMINAL.ACTIVITY HACK ---	
		# vte.Terminal-specific typing
		if hasattr(self.widget, terminalMethod):
			self.widget.feed_child(val)
			return True

		return self.notSupportedError(insertAtCursor, terminalMethod)
		
	def setText(self, val):
		"""
		Sets the text for the widget.
		
		Sets the text for the widget to the user-provided string.
		Uses the following procedures to attempt to set the text:
		 1) Calls 'set_text' method
		 2) Set the 'label' property
		 3) Set the 'title' property
		 4) A Terminal-specific method, 'feed_child'
		 5) Set the text via 'typeText'
		"""
		self.log.info("Setting text for %s to %s" % (self.name, val))
		
		setText			= "set_text"
							
		# --- GENERAL APPROACH ---
		# Try simply setting the text...
		try:
			self.__simpleSetter(setText, val)
			return True
		except NotSupportedError: pass
		# if hasattr(self.widget, setText):
		# 	getattr(self.widget, setText)(val)
		# 	return True
			
		# Try setting the label
		try:
			self.label = val
			return True
		except NotSupportedError:	pass
		
		# Try setting the title
		try:	
			self.title = val
			return True
		except NotSupportedError: pass
				
		# --- TEXT APPENDING ---
		# Try to just insert the text at the given point...
		try:
			self.typeText(val)
			return True
		except NotSupportedError:
			pass

		# Fail
		return self.notSupportedError((setText,"label","title"))
					
	def delete(self, numberOfTimes, deleteType):
		"""
		Simulates user pressing the 'delete' key.
		
		Simulates user pressing the 'delete' key a given number of times,
		with a flexible deletion type (e.g. characters, words, lines)
		"""
		# Note that we must negate numberOfTimes here, because it is
		# re-negated inside of the 'backspace' call.
		return backspace(-numberOfTimes, deleteType)
			
	def backspace(self, numberOfTimes=1, deleteType=gtk.DELETE_CHARS):
		"""
		Simulates the backspace keypress.
		
		Simulates the backspace keypress. numberOfTimes times.
		If numberOfTimes is negative, simulate the 'delete' keypress.
		"""
		backspace 			= 'backspace'
		deleteFromCursor 	= 'delete-from-cursor'
		
		# Try the 'deleteFromCursor' approach, as it is very flexible in the
		# number of ways to delete content.
		if self.supportsSignal(deleteFromCursor):
			self.widget.emit(deleteFromCursor, deleteType, -numberOfTimes)
			
		# Try the standard 'backspace' command.  Note that this will not work
		# for negative quantities.
		elif self.supportsSignal(backspace) and numberOfTimes >= 0:
			for i in range(0, numberOfTimes):
				self.widget.emit(backspace)
			return True
			
		else:
			return self.notSupportedError((backspace, deleteFromCursor))
	
	def doFocus(self, setFocus=None):
		"""
		Either sets or gets the focus for the widget.
		"""
		if setFocus is None:
			return self.widget.flags() & gtk.HAS_FOCUS
		elif setFocus:
			self.widget.grab_focus()
			return True
	
	def getInfo(self):
		"""
		Returns a bunch of information about the widget.
		"""
		def getClasses(object):
			"""			
			Returns a list containing the class that the object is an instance of,
			and all of the classes that the instance inherits from.
			For example:
					>>> class A: pass
					>>> class B(A): pass
					>>> class C(B): pass
					>>> x = C()
					>>> list = getClasses(x)
					>>> list
					[<class __main__.C at 0x6a1e0>, <class __main__.B at 0x6a1b0>, 
						<class __main__.A at 0x6a180>]
					>>> for i in list:
					...   print "Is instance of " + str(i) + "? " + str(isinstance(x,i))
					... 
					Is instance of __main__.C? True
					Is instance of __main__.B? True
					Is instance of __main__.A? True
			"""
			# If the passed object is an instance of a class, it will have a
			# __class__ attribute.
			if hasattr(object,"__class__"):
				recursionData = [object.__class__]

				# Include the lowest-level class in the heirarchy tree
				# Iterate through all of the base classes
				for _class in object.__class__.__bases__:
					if not _class is object:
						recursionData.append(_class)
						recursionData.extend(getClasses(_class))
			# Otherwise, the object -is- a class, and it will have a __bases__
			# attribute.
			elif hasattr(object,"__bases__"):
				# Iterate through all of the base classes.   Note that we do NOT add
				# the class itself here, as that is only done above, on the first
				# call.
				for _class in object.__bases__:
					recursionData.append(_class)
					recursionData.extend(getClasses(_class))
			return recursionData
		
		# ------ BEGIN INFO() METHOD -------
		infoStr = "\n%s" % getClasses(self.widget)

		l = dir(self.widget)
		for i in l:
			infoStr+= "\n> %s" % i

		return infoStr
	
	def __simpleGetter(self, method):
		"""
		Wrapper for simple 'get' methods

		Wrapper for simple 'get' methods (like get_label), that fails gracefully
		if the method is not available for the widget object.
		"""
		self.log.info("Getting %s for %s" % (method, self.name))
		if hasattr(self.widget, method):
			return getattr(self.widget, method)
			
		return self.notSupportedError(method)

	def __simpleSetter(self, method, val):
		"""
		Wrapper for simple 'set' methods
		
		Wrapper for simple 'set' methods (like get_label), that fails
		gracefully if the method is not available for the widget object.
		"""
		self.log.info("Setting %s to %s for %s" % (method, val, self.name))
		if hasattr(self.widget, method):
			getattr(self.widget, method)(val)
			return True
			
		return self.notSupportedError(method)
				
	def getTitle(self):
		"""
		Returns the widget's title.
		"""
		return self.__simpleGetter('get_title')
		
	def setTitle(self, val):
		"""
		Sets the widget's title
		"""
		return self.__simpleSetter('set_title', val)
		
	def getLabel(self):
		"""
		Returns the widget's label.
		"""
		return self.__simpleGetter('get_label')
		
	def setLabel(self, val):
		"""
		Sets the widget's label
		"""
		return self.__simpleSetter('set_label', val)
	
	def getListFormat(self, item):
		"""
		Converts a ComboBox or ToolComboBox's entries into a list
		
		Converts a ComboBox or ToolComboBox's entries into a list.  This is
		useful in enumerating the entries in a ComboBox for selection.
		"""
		retVal = []
		
		if isinstance(item, ToolComboBox):
			retVal = self.getList_GtkComboBox(item)
		elif isinstance(item, gtk.ComboBox):
			retVal = self.getList_SugarGraphicsCombo()
						
		return retVal
				
	def getList_GtkComboBox(self, combo):
		"""
		getListFormat handler for gtk.ComboBo objects.
		"""
		index = combo.get_active()
		if index == -1:
			index = 0
		
		model = combo.get_model() 
		row = model.iter_nth_child(None, index)
		
		if not row:
			return None
		
		listOfValues = []
		
		for i in range(0, len(model)):
			try:
				item = model[i]
				listOfValues.append(item)
			except IndexError:
				break
		return listOfValues
		
	def getList_SugarGraphicsCombo(self):
		"""
		getListFormat handler for sugar.graphics.ComboBox objects.
		"""
		tempList = self.getList_GtkComboBox(self.widget.combo)
		
		returnList = []
		for entry in tempList:
			returnList.append(entry[1])
		
		return returnList 
	
	def getSelected_SugarGraphicsCombo(self):
		"""
		getSelected handler for sugar.graphics.combo* objects.
		"""
		active = self.getSelected_ComboBox(self.widget.combo)
		
		if len(active) > 1:
			return active[1]
		elif len(active) == 1:
			return active[0]
		return active

	def getSelected_ComboBox(self, combo=None):
		"""
		getSelected handler for gtk.ComboBox objects.
		"""
		if combo is None:
			combo = self.widget
			
		index = combo.get_active()
		if index == -1:
			index = 0

		row = combo.get_model().iter_nth_child(None, index)
		if not row:
			return None
		return combo.get_model()[row]

	def getSelected(self):
		"""
		Returns the item selected in a gtk.ComboBox or sugar.graphics.ToolComboBox
		"""
		self.log.info("Getting selected entry")
		# Handle for the ComboBox...
		if isinstance(self.widget, gtk.ComboBox):
			return self.getSelected_ComboBox(self.widget)
			
		# Special handling for sugar ToolComboBox
		if isinstance(self.widget, ToolComboBox):
			return self.getSelected_SugarGraphicsCombo()			

		try:	return self.__simpleGetter('get_active_text')
		except NotSupportedError: pass
		
		try:
			i 	= self.widget.get_active()
			mod	= self.widget.get_model()
			return mod[i]
		except:
			pass
			
		return self.notSupportedError('get_active_text', 'get_model')
	
	def setSelected(self, val):
		"""
		Sets the item selected in a gtk.ComboBox or sugar.graphics.ToolComboBox
		"""
		self.log.info("Setting selected entry")
		# If textual: Enumerate all of the selections
		# If numeric: set selected
		combo = self.widget
		
		# Special handling for ToolComboBox
		if isinstance(self.widget, ToolComboBox):
			combo = self.widget.combo
		
		if isinstance(combo, gtk.ComboBox):
			# If we were provided with a string, get the numerical offset of
			# the provided entry.
			if isinstance(val, str):
				l = self.getListFormat(combo)
				if val in l:
					val = l.index(val)
			
			# Use the index to set the active combobox item
			if isinstance(val, int):
				combo.set_active(val)
				return
				
		return self.notSupportedError('set_active')
			
	
	text 		= property(getText, setText)
	title		= property(getTitle, setTitle)
	label		= property(getLabel, setLabel)
	
	focus		= property(doFocus, doFocus)
	selected	= property(getSelected, setSelected)
	info		= property(getInfo)
	

class widgetRegistry():
	gui	= None
	
	def __init__(self):		
		self.widgets = {}
		self.log	= logging.getLogger('wrappedWidget')
		self.log.info("Instantiated widgetRegistry")

	def __getitem__(self, which):
		"""
		Allows us to select widgets like a dictionary.
		"""
		
		# If we do not already have the Widget wrapped in a wrappedWidget,
		# do so now.
		if which not in self.widgets:
			widget = self.gui.getWidgetByName(which)
			
			self.log.info("Fetched widget %s [%s]" % (which, which.__class__))
			
			if widget is None:
				raise WidgetDoesNotExist, which
			
			wrapped = wrappedWidget(widget, which)
			self.setWidget(which, wrapped)
		
		# Return the wrappedWidget object.
		return self.widgets[which]
		
	def setWidget(self, which, value):
		self.widgets[which]=value

# Create the 'sbwidgets' instance.
if not globals().has_key("sbwidgets"):
	sbwidgets = widgetRegistry()