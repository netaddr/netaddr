#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
A Python setup file specifically to support setuptools.

Reference :-

    http://peak.telecommunity.com/DevCenter/setuptools
"""
import os
import sys

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

import release

#-----------------------------------------------------------------------------
def main():
    if sys.version_info[:2] < (2, 4):
        print "netaddr requires Python version 2.4.x or higher."
        sys.exit(1)

    setup(
        author           = release.author,
        author_email     = release.author_email,
        classifiers      = release.classifiers,
        description      = release.description,
        download_url     = release.download_url,
        keywords         = release.keywords,
        license          = release.license,
        long_description = release.long_description,
        name             = release.name,
        packages         = find_packages(),
        include_package_data = True,
        platforms        = release.platforms,
        url              = release.url,
        version          = release.version,
        zip_safe         = False,   #   Package should always be extracted.
        test_suite       = 'netaddr.tests.test_suit_all',
    )

#-----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
