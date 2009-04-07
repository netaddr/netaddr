#!/usr/bin/env python
"""
An Python setup file for distutils (see setup_egg.py) for setuptools support.

To install this release :-

>>> python setup.py install

"""
import os
import sys

from distutils.core import setup

if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

import release

#-----------------------------------------------------------------------------
def main():
    if sys.version_info[:2] < (2, 4):
        print "netaddr requires Python version 2.4.x or higher."
        sys.exit(1)

    if sys.argv[-1] == 'setup.py':
        print "To install, run 'python setup.py install'"
        print

    setup(
        name             = release.name,
        version          = release.version,
        description      = release.description,
        keywords         = release.keywords,
        download_url     = release.download_url,
        author           = release.author,
        author_email     = release.author_email,
        url              = release.url,
        packages         = release.packages,
        package_data     = release.package_data,
        license          = release.license,
        long_description = release.long_description,
        platforms        = release.platforms,
        classifiers      = release.classifiers,
    )

#-----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
