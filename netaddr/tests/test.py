#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------

import os
import sys
import unittest
import doctest

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../..')))

tests = ['ip/tutorial.txt']

for test in tests:
    suite = doctest.DocFileSuite(test, optionflags=doctest.ELLIPSIS)
    test_runner = unittest.TextTestRunner()
    test_runner.run(suite)
