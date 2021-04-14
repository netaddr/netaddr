#!/usr/bin/env python
#   Copyright (c) 2008 by David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
"""
A distutils Python setup file. For setuptools support see setup_egg.py.
"""
import sys

from setuptools import setup

def main():
    if sys.version_info[:2] < (2, 5):
        sys.stderr.write("netaddr requires Python version 2.5 or higher.\n")
        sys.exit(1)

    if sys.argv[-1] == 'setup.py':
        sys.stdout.write("To install, run 'python setup.py install'\n\n")

    setup(
        use_scm_version={
            "write_to": "netaddr/version.py",
            "write_to_template": '__version__ = "{version}"\n',
        }
    )

if __name__ == "__main__":
    main()
