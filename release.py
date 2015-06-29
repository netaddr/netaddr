#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2015, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------

import netaddr

name = 'netaddr'

version = netaddr.__version__

description = 'Pythonic manipulation of IPv4, IPv6, CIDR, EUI and MAC network addresses'

keywords = [
    'Networking', 'Systems Administration', 'IANA', 'IEEE', 'CIDR', 'IP',
    'IPv4', 'IPv6', 'CIDR', 'EUI', 'MAC', 'MAC-48', 'EUI-48', 'EUI-64'
]

download_url = 'https://pypi.python.org/pypi/netaddr/'

author = 'David P. D. Moss'

author_email = 'drkjam@gmail.com'

url = 'https://github.com/drkjam/netaddr/'

#   Required by distutils only.
packages = [
    'netaddr',
    'netaddr.ip',
    'netaddr.eui',
    'netaddr.strategy',
]

#   Required by distutils only.
package_data = {
    'netaddr.ip': [
        'ipv4-address-space.xml',
        'ipv6-address-space.xml',
        'multicast-addresses.xml'
    ],
    'netaddr.eui': [
        '*.txt',
        '*.idx'
    ],
}

scripts = ['netaddr/tools/netaddr']

license = 'BSD License'

#------------------------------------------------------------------------
#   NB - keep this text around 74 characters wide so it is viewable
#        in various fixed window sizes.
long_description = """
A Python library for representing and manipulating network addresses.

Provides support for:

Layer 3 addresses

    - IPv4 and IPv6 addresses, subnets, masks, prefixes
    - iterating, slicing, sorting, summarizing and classifying IP networks
    - dealing with various ranges formats (CIDR, arbitrary ranges and globs, nmap)
    - set based operations (unions, intersections etc) over IP addresses and subnets
    - parsing a large variety of different formats and notations
    - looking up IANA IP block information
    - generating DNS reverse lookups
    - supernetting and subnetting

Layer 2 addresses

    - representation and manipulation MAC addresses and EUI-64 identifiers
    - looking up IEEE organisational information (OUI, IAB)
    - generating derived IPv6 addresses

Changes
-------

For details on the latest updates and changes, see

    https://github.com/drkjam/netaddr/blob/rel-0.7.x/CHANGELOG

Documentation
-------------
    - https://pythonhosted.org/netaddr/
    - https://netaddr.readthedocs.org/en/latest/
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
    'Programming Language :: Python :: 2.4',
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
