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

long_description = """
a library providing Pythonic manipulation, validation and classification of common networking address notations, including :-

* IPv4
* IPv6
* CIDR (Classless Inter-Domain Routing)
* IEEE MAC (Media Access Control)/EUI-48 and EUI-64

For examples see the project wiki :-

    http://code.google.com/p/netaddr/wiki/NetAddrExamples

Full API documentation is available on PyPI here :-

    http://packages.python.org/netaddr/
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
