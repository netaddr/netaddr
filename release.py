import netaddr

name = 'netaddr'

version = netaddr.__version__

description = 'Pythonic manipulation of IPv4, IPv6, CIDR, EUI and MAC network addresses'

keywords = [
    'Networking', 'Systems Administration', 'IANA', 'IEEE', 'CIDR',
    'IPv4', 'IPv6', 'CIDR', 'EUI', 'MAC', 'MAC-48', 'EUI-48', 'EUI-64'
]

download_url = 'http://code.google.com/p/netaddr/downloads/list'

author = 'David P. D. Moss'

author_email = 'drkjam@gmail.com'

url = 'http://code.google.com/p/netaddr/'

packages = [
    'netaddr',
    'netaddr.ip',
    'netaddr.eui',
]

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
}

license = 'BSD License',

#   NB - keep this text around 74 characters wide so it is viewable
#        in various fixed window sizes.
long_description = """netaddr is a Python library for the representation and manipulation
of various common network address formats and notations.

It takes the hassle out of fiddling with innumerable variations of
network addresses, presenting a consistent, extensible, easy-to-use
and above all Pythonic API.

With it you can represent, validate, convert, categorize, iterate,
generate, slice (and dice) :-

* IP version 4
* IP version 6
* CIDR (Classless Inter-Domain Routing) both IPv4 and IPv6
* MAC (Media Access Control) and IEEE EUI-48 and EUI-64
* Support for arbitrary IP address ranges with CIDR interoperability
* User friendly alternative IPv4 range syntax using netaddr's
  glob-style Wildcard addresses

For examples see the project wiki :-

    http://code.google.com/p/netaddr/wiki/NetAddrExamples

API documentation (auto-generated with epydoc) :-

    http://packages.python.org/netaddr/

For details on latest changes and updates in the current and previous
releases see the CHANGELOG :-

    http://code.google.com/p/netaddr/wiki/CHANGELOG
"""

platforms = 'OS Independent'

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Environment :: Plugins',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Science/Research',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Telecommunications Industry',
    'License :: OSI Approved :: BSD License',
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
