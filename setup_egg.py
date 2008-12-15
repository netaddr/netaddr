#!/usr/bin/env python
"""
An Python setup file specifically supporting setuptools.

To create a Python egg :-

>>> python setup_egg.py bdist_egg

To run unit tests :-

>>> python setup_egg.py nosetests

"""
import sys

from setuptools import setup, find_packages
#from setup import *

import release

#-----------------------------------------------------------------------------
def main():
    if sys.version_info[:2] < (2, 3):
        print "netaddr requires Python version 2.3 or later."
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
        platforms        = release.platforms,
        url              = release.url,
        version          = release.version,

#        include_package_data = True,
#        package_data     = package_data,
#        data_files       = data,
#        install_requires=['setuptools'],
#        test_suite       = 'nose.collector',
#        tests_require    = ['nose >= 0.10.1','netaddr-nose-plugin>=0.1'] ,
        zip_safe = True,
    )

#-----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
