#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
network address manipulation, done Pythonically
"""
from address import Addr, IP, EUI, AddrRange, CIDR, Wildcard, nrange

from strategy import BIG_ENDIAN_PLATFORM, AT_LINK, AT_EUI64, AT_INET, \
    AT_INET6, AT_UNSPEC, ST_EUI48, ST_EUI64, ST_IPV4, ST_IPV6

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    import unittest

    import os
    import sys

    #   Run all unit tests.
    path = os.path.abspath(os.path.join(os.path.dirname(__file__),
        '../tests/'))
    sys.path.insert(0, path)

    import ut_address
    import ut_strategy

    #   Endian tests.
    print 'Is this platform natively big-endian?',
    if BIG_ENDIAN_PLATFORM is True:
        print 'Yes'
    elif BIG_ENDIAN_PLATFORM is False:
        print 'No'
    else:
        print 'Undefined'
        print 'Error: Endianness not recognised - Danger, Will Robinson!'
        sys.exit(1)

    loader = unittest.TestLoader()
    unit_test_suite = unittest.TestSuite()

    unit_test_modules = (ut_address, ut_strategy)

    for ut_module in unit_test_modules:
        for test_case in loader.loadTestsFromModule(ut_module):
            unit_test_suite.addTest(test_case)

    unittest.TextTestRunner(verbosity=2).run(unit_test_suite)
