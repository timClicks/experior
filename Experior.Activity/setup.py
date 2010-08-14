#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

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

from sugar.activity import bundlebuilder
bundlebuilder.start()


#try:
    #if len(sys.argv) < 2 or sys.argv[1] == "install":
        #from sugar.activity import bundlebuilder
        #bundlebuilder.start("sugarbot")
    #elif sys.argv[1] == "test":
        ## nosetests
        #pass
#except ImportError:
    #import os
    #os.system("find ./ | sed 's,^./,sugarbot.activity/,g' > MANIFEST")
    #os.system('rm sugarbot.xo')
    #os.chdir('..')
    #os.system('zip -r sugarbot.xo sugarbot.activity')
    #os.system('mv sugarbot.xo ./sugarbot.activity')
    #os.chdir('sugarbot.activity')
