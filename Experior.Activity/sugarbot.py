#!/usr/bin/env python
# encoding: utf-8
"""
sugarbot.py

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
import gobject
import gtk
import logging
import os
import sblog
import socket
import sys

from xmlrpclib          import ServerProxy

from sugar.activity     import activity
#from sugar.activity    import registry
from jarabe.model.bundleregistry import get_registry

from sbrpcserver        import sbRpcServer, proxyString

# For reading GDK.Event's
from sbgui import sbGUI

class sugarbot(activity.Activity):
    def __dynamicImport(self, fullname, path=None):
        """
        Handles emulation of the target Activity.

        Dynamically modifies the module-search path, and imports an object from
        a module.  Some fancy work is done to get that to work properly.
        @param fullname: The module to import, example calculate.Calculate.
        @param path: If necessary, the path to the imported module.
        """
        module      = None
        module_name = ""
        class_name  = ""

        if fullname is None:
            return self.__parentClass

        try:
            # <hack>=========================================================
            # This could probably be cleaned up or refactored into separate
            # functions.  However, the code is short enough that it is not
            # likely worth it.
            if path != None:
                sys.path.append(path)

            splitted_module     = fullname.rsplit('.', 1)

            if len(splitted_module) >= 2:
                module_name         = splitted_module[0]
                class_name          = splitted_module[1]

            if module_name is not None and class_name is not None and \
                len(module_name) > 0 and len(class_name) > 0:
                module              = __import__(module_name)

                for comp in module_name.split('.')[1:]:
                    module = getattr(module, comp)
            # </hack>========================================================
        except ImportError:
            raise ImportError, \
                "Error in sugarbot._dynamicImport(%s,%s)" % (fullname,path)

        finally:
            if hasattr(module, class_name):
                self.__parentClass = getattr(module, class_name)
            else:   # Failsafe
                self.__parentClass = activity.Activity

        return self.__parentClass

    def __cloneActivity(self,sugarHandle):
        """
        Starts the cloned activity, where self.__parentClass is the activity
        class.  This is performed by [1] inheriting from the parentClass,
        and [2] calling parentClass.__init__.
        """
        if self.__parentClass is None:
            raise AttributeError, "self.__parentClass not defined properly."

        else:
            sugarbot.__bases__ = (self.__parentClass,)
            self.__parentClass.__init__(self,sugarHandle)

    def __getActivityList(self):
        """
        Gets a list of activities from the registry.  Stores this list in
        self.__activityList.
        """
        # Prevent looking up all of the activities multiple times.
        if not hasattr(self,"__activityList"):
            #self.__activityList = registry.get_registry().get_activities()
            self.__activityList = get_registry()._bundles
            return self.__activityList

        # If we didn't get any activities, something went wrong.
        if len(self.__activityList) < 1:
            raise "Activity list is empty.  Cannot get activity info!"

        return None

    def __selectActivity(self,name):
        """
        Selects an activity from the activityList by name.  This allows
        simpler access to the list of activities.
        (For example, one can specify only 'Calculate' instead of
        'org.laptop.Calculate' or 'calculate.Calculate').
        @param name: The name of the activity (e.g. 'Calculate')
        """
        # Get the list of activities if it does not already exist
        activityList = self.__getActivityList()

        # Initialization of some variables...
        self.__path             = None
        self.__importClass      = None
        self.__className        = None

        # Iterate through the activity list
        for activity in activityList:
            if activity.get_name() == name:
                self.__path         = activity.get_path()
                self.__importClass  = activity.get_command().split()[-1]
                self.__className    = self.__importClass.split(".")[-1]
                self.log.debug("Importing class %s" % name)
                return

        # If we ever get here, that means we didn't find anything...
        if (self.__path is None) and (self.__importClass is None) and \
            (self.__className is None):
            raise NameError, "Could not find '%s' in activity list." % name

    def __initializeScript(self):
        """
        Initialize the script on the XML-RPC server.
        Returns the name of the Activity that should be instantiated
        """
        rpc = self.__xmlRPC

        try:
            self.sessID = os.environ['SUGARBOT_ID']
        except KeyError:
            self.sessID = 0

        # Start the script
        if not rpc.startScript(self.sessID):
            rpc.fail("Could not start the script!", self.sessID)
            exit()

        # Get our activity name
        activityName    = rpc.getActivityName(self.sessID)
        if activityName is None:
            rpc.fail('Bad activity name provided', self.sessID)
            exit()

        self.log.info("Activity is %s" % activityName)
        return activityName


    def __init__(self, handle):
        """
        Performs setup, and runs the specified activity.
        """
        self.log = logging.getLogger('sugarbot')

        # Set up threading...
        gtk.gdk.threads_init()

        # Handle is set to 'None' for testing purposes via Nose.  Obviously,
        # if Sugar sets the handle to None, there are other problems...
        if handle is None:
            return

        try:
            # Create the RPC connection object
            self.__xmlRPC = ServerProxy(proxyString())

            # Set up the sbGUI object for automation
            self.__sbgui    = sbGUI(self, self.__xmlRPC)

            # Get our activity name
            activityName    = self.__initializeScript()

            # Actually clone the activity
            self.__selectActivity(activityName)
            self.__dynamicImport(self.__importClass,self.__path)
            self.__cloneActivity(handle)
        except socket.error:
            sys.log.error("====== COULD NOT CONNECT TO XML-RPC SERVER ======")
            sys.exit(-1)
