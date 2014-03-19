#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2014, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
A Python setup file for distribute - http://packages.python.org/distribute/
"""

from setuptools import setup
filename = 'setup.py'
exec(compile(open(filename).read(), filename, 'exec'))

