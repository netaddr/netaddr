#!/usr/bin/env python
"""
An Python setup file specifically supporting setuptools.

To create a Python egg :-

>>> python setup_egg.py bdist_egg
"""
import sys

from setuptools import setup, find_packages

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
        package_data     = release.package_data,
        include_package_data = True,
        platforms        = release.platforms,
        url              = release.url,
        version          = release.version,
        zip_safe         = False,   #   Package should always be extracted.
    )

#-----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
