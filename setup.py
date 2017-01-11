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

if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

import netaddr

keywords = [
    'Networking', 'Systems Administration', 'IANA', 'IEEE', 'CIDR', 'IP',
    'IPv4', 'IPv6', 'CIDR', 'EUI', 'MAC', 'MAC-48', 'EUI-48', 'EUI-64'
]

#   Required by distutils only.
packages = [
    'netaddr',
    'netaddr.ip',
    'netaddr.eui',
    'netaddr.strategy',
    'netaddr.contrib',
]

#   Required by distutils only.
package_data = {
    'netaddr.ip': [
        '*.xml',
    ],
    'netaddr.eui': [
        '*.txt',
        '*.idx'
    ],
}

#------------------------------------------------------------------------
#   NB - keep this text around 74 characters wide so it is viewable
#        in various fixed window sizes.
long_description = """
        Provides support for:

        Layer 3 addresses
        -----------------

        - IPv4 and IPv6 addresses, subnets, masks, prefixes
        - iterating, slicing, sorting, summarizing and classifying IP networks
        - dealing with various ranges formats (CIDR, arbitrary ranges and globs, nmap)
        - set based operations (unions, intersections etc) over IP addresses and subnets
        - parsing a large variety of different formats and notations
        - looking up IANA IP block information
        - generating DNS reverse lookups
        - supernetting and subnetting

        Layer 2 addresses
        -----------------

        - representation and manipulation MAC addresses and EUI-64 identifiers
        - looking up IEEE organisational information (OUI, IAB)
        - generating derived IPv6 addresses

        Changes
        -------

        For details on the latest changes and updates, see :-

        http://netaddr.readthedocs.io/en/latest/changes.html

        Requirements
        ------------

        Supports Python version 2.5 through 3.5

        Share and enjoy!
"""

platforms = 'OS Independent'

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Science/Research',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Telecommunications Industry',
    'License :: OSI Approved :: BSD License',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.0',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Communications',
    'Topic :: Documentation',
    'Topic :: Education',
    'Topic :: Education :: Testing',
    'Topic :: Home Automation',
    'Topic :: Internet',
    'Topic :: Internet :: Log Analysis',
    'Topic :: Internet :: Name Service (DNS)',
    'Topic :: Internet :: Proxy Servers',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
    'Topic :: Internet :: WWW/HTTP :: Site Management',
    'Topic :: Security',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Quality Assurance',
    'Topic :: Software Development :: Testing',
    'Topic :: Software Development :: Testing :: Traffic Generation',
    'Topic :: System :: Benchmark',
    'Topic :: System :: Clustering',
    'Topic :: System :: Distributed Computing',
    'Topic :: System :: Installation/Setup',
    'Topic :: System :: Logging',
    'Topic :: System :: Monitoring',
    'Topic :: System :: Networking',
    'Topic :: System :: Networking :: Firewalls',
    'Topic :: System :: Networking :: Monitoring',
    'Topic :: System :: Networking :: Time Synchronization',
    'Topic :: System :: Recovery Tools',
    'Topic :: System :: Shells',
    'Topic :: System :: Software Distribution',
    'Topic :: System :: Systems Administration',
    'Topic :: System :: System Shells',
    'Topic :: Text Processing',
    'Topic :: Text Processing :: Filters',
    'Topic :: Utilities',
]


def main():
    if sys.version_info[:2] < (2, 5):
        sys.stderr.write("netaddr requires Python version 2.5 or higher.\n")
        sys.exit(1)

    if sys.argv[-1] == 'setup.py':
        sys.stdout.write("To install, run 'python setup.py install'\n\n")

    setup_options = dict(
        author='David P. D. Moss',
        author_email='drkjam@gmail.com',
        maintainer='Stefan Nordhausen',
        maintainer_email='stefan.nordhausen@immobilienscout24.de',
        classifiers=classifiers,
        description='A network address manipulation library for Python',
        download_url='https://pypi.python.org/pypi/netaddr/',
        keywords=keywords,
        license='BSD License',
        long_description=long_description,
        name='netaddr',
        package_data=package_data,
        packages=packages,
        platforms=platforms,
        scripts=['netaddr/tools/netaddr'],
        url='https://github.com/drkjam/netaddr/',
        version=netaddr.__version__,
        options={
            'build_scripts': {
                'executable': '/usr/bin/env python',
            },
        },
    )

    setup(**setup_options)

if __name__ == "__main__":
    main()
