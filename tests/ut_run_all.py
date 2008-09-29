#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------

import unittest

import os
import sys

#   Run all unit tests.

path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path)

from netaddr import BIG_ENDIAN_PLATFORM

#   What is our endianness?
print 'Is this platform natively big-endian?',
if BIG_ENDIAN_PLATFORM is True:
    print 'Yes'
elif BIG_ENDIAN_PLATFORM is False:
    print 'No'
else:
    print 'Undefined'
    print 'Error: Endianness not recognised - Danger, Will Robinson!'
    sys.exit(1)

#   Fixes ugly unit test output.
sys.stdout.flush()

import ut_address
import ut_strategy

loader = unittest.TestLoader()
unit_test_suite = unittest.TestSuite()

unit_test_modules = (ut_address, ut_strategy)

for ut_module in unit_test_modules:
    for test_case in loader.loadTestsFromModule(ut_module):
        unit_test_suite.addTest(test_case)

unittest.TextTestRunner(verbosity=2).run(unit_test_suite)
