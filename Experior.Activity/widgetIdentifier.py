#! /usr/bin/env python
# -*- encoding: utf-8 -*- 

#widgetIdentifier.py

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
import sys
import os
import time
import pygtk
pygtk.require('2.0')

import gtk
from gtk import gdk

import sugar
from sugar 							import graphics
from sugar.graphics.toolbutton 		import Palette
from sugar.graphics.icon			import Icon
from sugar.graphics.toolcombobox	import ToolComboBox

class widgetIdentifier:
	"""
	The widgetIdentifier class is used as a basis for classes to identify
	Widgets.  Ideally, all developers would call Widget.set_name() on all
	widgets created by their Activities.  Since this is not always
	practical or worthwhile, we must rely on other methods to identify
	widgets.
	
	This class provides some of the functionality for identifying widgets,
	such as a list of strings that are default Widget names (e.g. 'GtkButton').
	"""
	identifiers = { }
	
	def __init__(self, widget):
		self.widgetAttribute = "sugarbotWidgetIdentifier"
		
		self.dontWant = ["GtkToolbar", "GtkToggleButton","GtkButton",
					"GtkEventBox", "GtkNotebook", "GtkViewport",
					"HippoCanvas", "GtkTextView", "GtkInvisible",
					"GtkEntry", "GtkLabel", "GtkVBox", "GtkHBox",
					"SugarIcon","SugarToolButton","GtkAlignment",
					"GtkSeparatorToolItem","GtkTable","SugarToolbox",
					"GtkToggleToolButton","GtkScrolledWindow","GtkCellView",
					"GtkVSeparator","GtkArrow","GtkToolItem","GtkAccelLabel",
					"SugarComboBox","SugarToggleToolButton","GtkHSeparator",
					"GtkHButtonBox","GtkImageMenuItem","GtkSeparatorMenuItem",
					"GtkSpinButton","GtkDrawingArea","GtkFrame",
					"GtkColorButton", ""]
					
		self.dontWantPrefixes = ["Gtk", "sugar+graphics"]
		self.setWidget(widget)
		
	def setWidget(self, widget):
		self._widget		= widget
		# self.getIdentifier()
		
	def getIdentifierSub(self):
		"""
		Overridden by inheriting classes.
		"""
		return None
		
	def getIdentifier(self):
		"""
		Returns the Identifier of the Widget set with __init__, or None
		if we cannot find an identifier.  Do not override this function!
		"""
		# If we have already set the attribute for this widget, just
		# retrieve it quickly.
		if self.checkStoredIdentifier():
			return self.getStoredIdentifier()
			
		ident = None
		widget = self._widget
		
		if hasattr(widget, "get_name"):
			ident = widget.get_name()
			
		if not self.validateIdentifier(ident):
			ident = self.getIdentifierSub()
				
		return self.setIdentifier(ident)
		
	def checkStoredIdentifier(self):
		"""
		Checks to see if we have previously identified this same Widget.
		If we have, the Widget will have an attribute as defined by
		widgetIdentifier.widgetAttribute.
		"""
		if hasattr(self._widget, self.widgetAttribute) \
		 	and getattr(self._widget, self.widgetAttribute) is not None:
			return True
		return False
		
	def getStoredIdentifier(self):
		"""
		If the Widget has a stored identifier (see checkStoredIdentifier),
		then retrieve the stored identifier's value.
		
		If the Widget does not have a stored identifier, return None.
		"""
		if self.checkStoredIdentifier():
			return getattr(self._widget, self.widgetAttribute)
		else:
			return None
		
	def validateIdentifier(self,ident):
		"""
		Checks a proposed identifier against a series of criterium.  For
		example, empty strings, and blacklisted strings, as well as
		blacklisted prefixes, may rule out an identifier for use.
		"""
		if ident is None:
			return False
		elif not isinstance(ident, str):
			return False
		elif len(ident) < 1:
			return False
		elif ident in self.dontWant:
			return False
		else:
			for prefix in self.dontWantPrefixes:
				if ident.startswith(prefix):
					return False
		return True
		
	def setIdentifier(self, ident):
		"""
		Sets the stored identifier for the Widget assigned by __init__.
		"""
		if self.validateIdentifier(ident):
			setattr(self._widget, self.widgetAttribute, ident)
			return ident
		return None
widgetIdentifier.identifiers[gtk.Widget] = widgetIdentifier


class buttonIdentifier(widgetIdentifier):
	def getIdentifierSub(self):
		ident 	= None
		widget 	= self._widget
		
		if hasattr(widget, "get_label"):
			ident 	= widget.get_label()
			
		return ident
widgetIdentifier.identifiers[gtk.Button] = buttonIdentifier
		
# class toolButtonIdentifier(widgetIdentifier):
class toolButtonIdentifier(buttonIdentifier):
	def getIdentifierSub(self):
		ident 	= buttonIdentifier.getIdentifierSub(self)
		widget 	= self._widget
		
		# Get the identifier using the icon
		if not self.validateIdentifier(ident):
			ico = None
			ico = widget.get_icon_widget()
			if isinstance(ico, Icon):
				ident = ico.props.icon_name
				
		# Label did not give us a good ident, check the icon name
		if not self.validateIdentifier(ident):
			ident = widget.get_icon_name()
		
		# Icon did not give us a good ident, try the label
		if not self.validateIdentifier(ident):
			label = widget.get_label_widget()
			if hasattr(label,"get_text"):
				ident = label.get_text()			
		
		return ident
widgetIdentifier.identifiers[gtk.ToolButton] = toolButtonIdentifier

class comboBoxIdentifier(widgetIdentifier):
	def getIdentifierSub(self):
		ident	= None
		widget 	= self._widget
		
		if hasattr(widget, "get_title"):
			ident = self._widget.get_title()
			
		return ident
widgetIdentifier.identifiers[gtk.ComboBox] = comboBoxIdentifier


class entryIdentifier(widgetIdentifier):
	def getIdentifierSub(self):	
		ident 	= None
		widget	= self._widget
		
		if not self.validateIdentifier(ident):
			if hasattr(widget, "get_text"):
				ident = self._widget.get_text()
			
		return ident
widgetIdentifier.identifiers[gtk.Entry] = entryIdentifier

class paletteIdentifier(widgetIdentifier):
	def getIdentifierSub(self):		
		ident  = None
		widget = self._widget

		if hasattr(widget, "_primary_text"):
			ident = getattr(widget,  "_primary_text")
			
		elif not self.validateIdentifier(ident):
			if hasattr(widget, "props.primary_text"):
				ident = getattr(widget, "props.primary_text")

		return ident
widgetIdentifier.identifiers[Palette] = paletteIdentifier


class toolComboBoxIdentifier(widgetIdentifier):
	def getIdentifierSub(self):
		ident  = None
		widget = self._widget

		if hasattr(widget, "_label_text"):
			ident = getattr(widget, "_label_text")
			print ident

		# if not self.validateIdentifier(ident):
		# 	try:
		# 		print "@@@"
		# 		ident = widget.get_property("label-text")
		# 		print ident
		# 	except TypeError:
		# 		raise
		
		# <DEPRECATED>
		# if not self.validateIdentifier(ident):
		# 	if hasattr(widget, "_label_text"):
		# 		ident = getattr(widget, "_label_text")
		# 	
		# elif not self.validateIdentifier(ident):
		# 	if hasattr(widget, "label"):
		# 		label = widget.label
		# 		ident = label.get_text()
		# </DEPRECATED> 
				
		return ident
widgetIdentifier.identifiers[ToolComboBox] = toolComboBoxIdentifier
