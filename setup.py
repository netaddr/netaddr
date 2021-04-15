#!/usr/bin/env python
#   Copyright (c) 2008 by David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
"""
A distutils Python setup file. For setuptools support see setup_egg.py.
"""
import os
import sys

from setuptools import setup

def main():
    if sys.version_info[:2] < (2, 5):
        sys.stderr.write("netaddr requires Python version 2.5 or higher.\n")
        sys.exit(1)

    if sys.argv[-1] == 'setup.py':
        sys.stdout.write("To install, run 'python setup.py install'\n\n")

    setup(
        version=(
            [
                ln for ln in open(os.path.join(os.path.dirname(__file__), 'netaddr', '__init__.py'))
                if '__version__' in ln
            ][0]
            .split('=')[-1]
            .strip()
            .strip('\'"')
        ),
    )

if __name__ == "__main__":
    main()
