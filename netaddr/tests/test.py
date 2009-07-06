#!/usr/bin/env python

import unittest
import doctest

tests = ['ip/multicast.txt']

for test in tests:
    suite = doctest.DocFileSuite(test, optionflags=doctest.ELLIPSIS)
    test_runner = unittest.TextTestRunner()
    test_runner.run(suite)
