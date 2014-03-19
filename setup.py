#!/usr/bin/env python
#   Copyright (c) 2008-2014, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
"""
A distutils Python setup file. For setuptools support see setup_egg.py.
"""
import os
import sys

from distutils.core import setup

if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

import release

def main():
    if sys.version_info[:2] < (2, 4):
        sys.stderr.write("netaddr requires Python version 2.4 or higher.\n")
        sys.exit(1)

    if sys.argv[-1] == 'setup.py':
        sys.stdout.write("To install, run 'python setup.py install'\n\n")

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
        package_data     = release.package_data,
        packages         = release.packages,
        platforms        = release.platforms,
        scripts          = release.scripts,
        url              = release.url,
        version          = release.version,
        install_requires = release.install_requires,
        setup_requires   = release.setup_requires,
    )

    setup(**setup_options)

if __name__ == "__main__":
    main()
