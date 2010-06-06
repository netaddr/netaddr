#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2010, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
A setuptools Python setup file. For distutils support see setup.py.

Reference :-

    http://peak.telecommunity.com/DevCenter/setuptools
"""
import os
import sys

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

#-----------------------------------------------------------------------------
#   *** find_packages() is not being used as its output differs slightly ***
#   *** from the disutils setup.py script and I'd them to stay in line.  ***
#-----------------------------------------------------------------------------
#DISABLED: from setuptools import find_packages


if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

import release

#-----------------------------------------------------------------------------
def main():
    if sys.version_info[:2] < (2, 4):
        sys.stderr.write("netaddr requires Python version 2.4 or higher.\n")
        sys.exit(1)

    if sys.argv[-1] == 'setup_egg.py':
        sys.stdout.write("To install, run 'python setup_egg.py install'\n\n")

    setup_options = dict(
        author           = release.author,
        author_email     = release.author_email,
        classifiers      = release.classifiers,
        description      = release.description,
        download_url     = release.download_url,
        keywords         = release.keywords,
        license          = release.license,
        long_description = release.long_description,
        name             = release.name,
#----------------------------------------------------------
#   *** packages configured to be distutils compatible ***
#DISABLED:         packages         = find_packages(),
#DISABLED:         include_package_data = True,
#----------------------------------------------------------
        packages         = release.packages,
        package_data     = release.package_data,
        platforms        = release.platforms,
        scripts          = release.scripts,
        test_suite       = 'netaddr.tests.test_suite_all',
        url              = release.url,
        version          = release.version,
        zip_safe         = False,   #   Package should always be extracted.
    )

    setup(**setup_options)

#-----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
