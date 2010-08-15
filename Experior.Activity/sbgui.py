#! /usr/bin/env python
# -*- encoding: utf-8 -*-

#sbgui.py

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
import os
import pygtk
import sys
import time
pygtk.require('2.0')
import gtk
import logging
import sugar

from gobject            import idle_add
from gtk                import gdk
from gtk.gdk            import event_handler_set
from sbexecutionengine  import sbExecutionEngine
from sugar              import graphics
from sugar.graphics.toolbutton import Palette
from widgetIdentifier   import *

class sbGUI(gobject.GObject):
    """
    Responsible for tracking all identifiable* widgets instantiated by GTK.

    *Identifiable widgets are widgets for which a valid identifier can be
    found, via any of the identifiers enumerated by widgetIdentifier.identifiers.
    """
    def __init__(self,sugarbotInstance,rpcServer):
        """
        Initialize internal variables, and register self as an event handler.
        """
        # Necessary, due to inheritance
        gobject.GObject.__init__(self)

        # Get the RPC server connection and the sugarbot instance, as well
        # as the execution engine.
        self.sugarbot   = sugarbotInstance
        self.rpc        = rpcServer
        self.engine     = sbExecutionEngine(self,self.rpc)
        self.log        = logging.getLogger('sbGUI')

        # Keep track of the amount of idle time...
        self.idletime   = 0
        self.idletimeout= 6

        # In order to keep track of all of the windows, we set up a
        # dict of Windows.  For each window, the key is its id (as provided
        # by id(theWindowObject).  The value of each dictionary entry is a
        # dictionary of Widgets, set up the same way -- the id() of the
        # widget is the key, and the
        self.trackedWidgets = {}    # Maps id(object) -> widget
        self.names = {}             # Maps identifier -> widget

        # Register one of our methods to intercept all GTK events
        self.registerEventHandler()


    def eventHandler(self,event=None):
        """ Intercepts all GDK events.  We then send them off to a separate
        handler method (to keep things clean), and then have GTK execute
        whatever the event is supposed to do.
        """
        if event is not None:
            gtk.main_do_event(event)
            self.handleEvent(event)

        if event.type is not gtk.gdk.EXPOSE:
            self.idletime = 0

        return True


    def getWidgetIdentifier(self,widget):
        """
        Returns the Widget's unique identifier (for example, a button's
        label, or a gkt.Entry's name), or None if it does not have one.
        Also, this function filters out many uninitialized identifiers,
        such as "GtkToolbar" or "GtkButton"
        @param widget - The widget whose identifier is to be retrieved.
        """
        if not isinstance(widget,gtk.Widget):
            raise "_getWidgetName must take a gtk.Widget object as its argument"

        # ---- GENERIC APPROACH ----
        # Assuming that the widget was named explicitly by the developers,
        # getting the name should be very straightforward, with no specialized
        # cases or special name-detecting.
        widId = WidgetIdentifier(widget)
        ident = widId.getIdentifier()

        if ident is not None:
            return ident

        # ---- SPECIALIZED APPROACH ----
        # Check to see if we have an identifier for the specific type
        # of widget before we iterate through all of the different identifiers
        # hoping to get a hit.
        if identifiers.has_key(widget.__class__):
            widId = identifiers[widget.__class__](widget)
            ident = widId.getIdentifier()

            if ident is not None:
                return ident

        # ---- BRUTE FORCE ----
        # The widget was not named explicitly by the developers, and we do
        # not have a case for the specific widget class.
        # Iterate through all of our potential identifiers, since we
        # very likely have a widget class that it inherits from.
        # This method is undesirable, since the identifiers in the dictionary
        # widgetIdentifiers may be in a different order each time the
        # program is run, due to the non-ordered nature of dictionaries.
        for identifier in identifiers:
            if isinstance(widget, identifier):
                widId = identifiers[identifier](widget)
                ident = widId.getIdentifier()

                if ident is not None:
                    break

        # At this point, we either have a valid widget identifier, or None.
        return ident


    def addWidget(self,widget):
        """
        Add a widget to be tracked internally.  Widgets are tracked by their
        id().  Additionally, add it to the names{} dictionary, so that we
        can quickly look up widgets by the name.
        """

        # Don't do anything if we already have this widget by ID
        if self.trackedWidgets.has_key(id(widget)):
            return

        # Make sure we are working on a widget
        if not isinstance(widget, gtk.Widget):
            return

        # Containers might have children.  Check them all.
        if isinstance(widget, gtk.Container):       # gtk.Container can have
            for child in widget.get_children():     # any number of children
                self.addWidget(child)

        if isinstance(widget, gtk.Bin):             # gtk.Bin can only have
            self.addWidget(widget.get_child())      # one child.

        if isinstance(widget, gtk.Notebook):        # gtk.Notebook can have
            numPages = widget.get_n_pages()         # many children.
            for count in range(0, numPages):
                page = widget.get_nth_page(count)
                self.addWidget(page)
            return


        # Get the widget's identifier & id.  If the widget cannot be reliably
        # identified, there is no use in tracking it.
        identifier  = self.getWidgetIdentifier(widget)
        _id         = id(widget)
        if identifier is None:
            return

        # Simply keep track of the widgets by ID
        self.trackedWidgets[_id]=widget

        # Keep track of the widgets by identifier.
        # Check to see if it's already being tracked.
        if self.names.has_key(identifier):
            raise KeyError, "Already tracking a widget by identifier %s" \
                                % identifier

        # Track the little bugger
        else:
            self.log.debug("Tracking widget id %i by identifier %s" % (_id, identifier))
            self.names[identifier] = widget


    def delWidget(self,widget):
        """
        Remove a widget from internal tracking.  Widgets can be removed by
        their id() or by the gtk.Widget object.

        TODO: I don't think this function ever gets called.
        """
        if not isinstance(widget, gtk.Widget):
            raise "Called delWidget on non-Widget object"
            return

        # Get id(widget)
        identifier  = self.getWidgetIdentifier(widget)
        _id         = id(widget)

        # Remove the widget from the trackedWidgets dict if it is tracked.
        if self.trackedWidgets.has_key(_id):
            del self.trackedWidgets[_id]
            del self.names[identifier]

        else:    # Tried to call delWidget on non-tracked Widget
            return

    def getWidgetByName(self,widgetName):
        """
        Checks to see if we are tracking a Widget with a given name.
        If so, return the Widget.  If not, return None.
        """
        if widgetName in self.names:
            return self.names[widgetName]
        return None

    def handleEvent_firehose(self,event):
        """
        For exploratory testing.  Don't bother trying to figure out what this
        does, it will change without notification.
        Pretty much just outputs a firehose of events.  Useful for exploratory
        testing, and that's pretty much it.
        """
        if not hasattr(self,'classes'):
            self.classes = []

        eventType = event.type
        print "----------------------------------------"
        print event.type
        if event.window:
            # print event.window
            try:
                widget = event.window.get_user_data()
                print widget.__class__
                self.classes[widget.__class__] = 1
            except:
                raise
        print "----------------------------------------"
        print ""
        print ""

    def handleEvent(self,event):
        """
        Handles all GDK events.  We first filter them so that we know
        they pertain to a window, and then we further drill down based on the
        type of action.  This method is used to achieve two goals:
        [1] Build a database of all windows and widgets
        [2] Allow us to see actions as they happen.  This could lead to
            recording functionality in the future.
        """
        try:
            # Does the event have a Window that it belongs to?
            if (not event.window):
                return

            # Get some information on the widget.  If it doesn't work, just
            # gracefully fail.  Exceptions happen with the following events:
            # (maybe more, but these are what I've observed):
            # - GDK_OWNER_CHANGE
            widget = event.window.get_user_data()
            eventType = event.type

            # -------- HANDLE WIDGET INSTANTIATION --------
            # MAP events are generated when a widget is initially displayed
            # on the screen.  In most cases, any naming or configuration that
            # is going to be performed *has been* performed.
            if eventType == gdk.MAP:
                self.addWidget(widget)

            # -------- HANDLE WIDGET DESTRUCTION --------
            # UNMAP events are generated when a widget
            # is being taken off the screen.  Generally, this will happen at
            # the end of an application's execution.  However, to maintain
            # flexibility (e.g. the possibility of dialog windows), handle
            # the UNMAP event here.
            elif eventType == gdk.UNMAP:
                self.delWidget(widget)
        except ValueError:
            pass
        except: # Oops!
            raise

    def idleHandler(self, event=None):

        if self.engine.isComplete():
            return False

        if self.idletime is 0:
            self.idletime = time.time()
            self.lasttime = self.idletime

        if self.lasttime + 1 < time.time():
            self.lasttime += 1

        if self.idletime + self.idletimeout < time.time():
            self.engine.executePy()
            self.idletime = 0

        return True

    def registerEventHandler(self):
        """
        Registers the method self.eventHandler as the function that
        will receive all GDK events.  This allows us to snoop on GDK.
        """
        if not event_handler_set:
            raise NotImplementedError
        else:
            gobject.idle_add(self.idleHandler)
            event_handler_set(self.eventHandler)
