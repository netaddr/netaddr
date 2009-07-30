#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------

import unittest
import doctest

tests = ['eui/eui64.txt']

for test in tests:
    suite = doctest.DocFileSuite(test, optionflags=doctest.ELLIPSIS)
    test_runner = unittest.TextTestRunner()
    test_runner.run(suite)
