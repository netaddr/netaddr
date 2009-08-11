#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
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

download_url = 'http://code.google.com/p/netaddr/downloads/list'

author = 'David P. D. Moss'

author_email = 'drkjam@gmail.com'

url = 'http://code.google.com/p/netaddr/'

#   Required by distutils only.
packages = [
    'netaddr',
    'netaddr.ip',
    'netaddr.eui',
    'netaddr.strategy',
    'netaddr.tests',
]

#   Required by distutils only.
package_data = {
    'netaddr.ip': [
        'ipv4-address-space',
        'ipv6-address-space',
        'multicast-addresses'
    ],
    'netaddr.eui': [
        '*.txt',
        '*.idx'
    ],
    'netaddr.tests': [
        'core/*.txt',
        'eui/*.txt',
        'ip/*.txt',
        'strategy/*.txt',
    ],
}

license = 'BSD License'

#   NB - keep this text around 74 characters wide so it is viewable
#        in various fixed window sizes.
long_description = """
A pure Python network address representation and manipulation library.

netaddr provides a Pythonic way to work with :-

- IPv4 and IPv6 addresses and subnet (including CIDR notation)
- MAC (Media Access Control) addresses in multiple formats
- IEEE EUI-64, OUI and IAB identifiers
- a user friendly IP glob-style format

Included are routines for :-

- generating, sorting and summarizing IP addresses
- converting IP addresses and ranges between various different formats
- arbitrary IP address range calculations and conversions
- querying IEEE OUI and IAB organisational information
- querying of IP standards related data from key IANA data sources

For examples please visit the example wiki pages :-

    http://code.google.com/p/netaddr/wiki/NetAddrExamples

Complete API documentation for the latest release is available online :-

    http://packages.python.org/netaddr/

For details on history changes and updates see the CHANGELOG :-

    http://code.google.com/p/netaddr/wiki/CHANGELOG
"""

platforms = 'OS Independent'

scripts = ['netaddr/tools/nash']

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Environment :: Plugins',
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
    'Topic :: Education :: Testing',
    'Topic :: Home Automation',
    'Topic :: Internet',
    'Topic :: Internet :: Log Analysis',
    'Topic :: Internet :: Name Service (DNS)',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: System :: Networking',
    'Topic :: System :: Networking :: Firewalls',
    'Topic :: System :: Networking :: Monitoring',
    'Topic :: System :: Operating System',
    'Topic :: System :: Shells',
    'Topic :: System :: Systems Administration',
    'Topic :: Utilities',
]
