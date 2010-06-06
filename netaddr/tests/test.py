#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2010, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------

import os
import sys
import unittest
import doctest

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..')))

tests = [
#    'core/pubsub.txt',
#    'eui/eui.txt',
#    'eui/eui64.txt',
#    'eui/pubsub.txt',
#    'eui/tutorial.txt',
#    'ip/abbreviated.txt',
#    'ip/boundaries.txt',
#    'ip/cidr.txt',
#    'ip/constructor.txt',
#    'ip/functions.txt',
#    'ip/intset.txt',
#    'ip/ipglob.txt',
#    'ip/matches.txt',
#    'ip/multicast.txt',
#    'ip/nmap.txt',
#    'ip/rfc1924.txt',
#    'ip/sets.txt',
    'ip/socket_fallback.txt',
#    'ip/subnet.txt',
#    'ip/tutorial.txt',
#    'strategy/eui48.txt',
#    'strategy/ipv4.txt',
#    'strategy/ipv6.txt',
]

py_ver_dir = '2.x'
if sys.version_info[0] == 3:
    py_ver_dir = '3.x'

for test in tests:
    test = os.path.abspath(os.path.join(py_ver_dir, test))
    sys.stdout.write('%s\n' % test)
    suite = doctest.DocFileSuite(test, optionflags=doctest.ELLIPSIS)
    test_runner = unittest.TextTestRunner()
    test_runner.run(suite)
