#!/usr/bin/env python

import unittest
import doctest

tests = ['tutorial.txt', 'constructor.txt']

for test in tests:
    suite = doctest.DocFileSuite(test, optionflags=doctest.ELLIPSIS)
    test_runner = unittest.TextTestRunner()
    test_runner.run(suite)
