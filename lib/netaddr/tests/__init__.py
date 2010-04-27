#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""Runs all netaddr unit tests."""

import os
import sys
import glob
import doctest
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../..')))

DEBUG = True

#-----------------------------------------------------------------------------
def test_suit_all():

    test_dirs = ['ip', 'eui', 'strategy', 'core']

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    if DEBUG:
        print
        print 'module base path:', base_path
        print

    #   Gather list of files containing tests.
    test_files = []
    for entry in test_dirs:
        test_path = os.path.join(base_path, "tests", entry, "*.txt")
        files = glob.glob(test_path)
        test_files.extend(files)

    #   Add anything to the skiplist that we want to leave out.
    skiplist = []

    #   Exclude any entries from the skip list.
    test_files = [t for t in test_files if os.path.basename(t) not in skiplist]

    if DEBUG:
        print "doctest files to be processed :-"
        print
        print "\n".join(test_files)

    #   Build and return a complete unittest test suite.
    suite = unittest.TestSuite()

    for test_file in test_files:
        doctest_suite = doctest.DocFileSuite(test_file,
            optionflags=doctest.ELLIPSIS, module_relative=False)
        suite.addTest(doctest_suite)

    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(test_suit_all())
