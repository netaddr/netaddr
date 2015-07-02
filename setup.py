#!/usr/bin/env python
#   Copyright (c) 2008-2015, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
"""
A distutils Python setup file. For setuptools support see setup_egg.py.
"""
import os
import sys

from distutils.core import setup, Command

if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

import release


class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        import sys
        import os
        saved_cwd = os.getcwd()
        try:
            os.chdir(os.path.join(os.path.dirname(__file__), 'test'))
            errno = subprocess.call([sys.executable, '../runtests.py'])
        finally:
            os.chdir(saved_cwd)
        raise SystemExit(errno)


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
        cmdclass         = {'test': PyTest},
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
        options = {
            'build_scripts': {
                'executable': '/usr/bin/env python',
            },
        },
    )

    setup(**setup_options)

if __name__ == "__main__":
    main()
