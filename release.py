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

license = 'BSD License'

#   NB - keep this text around 74 characters wide so it is viewable
#        in various fixed window sizes.
long_description = """
A Python library for representing and manipulating network addresses.

It takes the hassle out of dealing with a variety of common layer 2 and
layer 3 network addressing formats and operations performed on them,
presented in a consistent, easy to use and extensible Pythonic API.

The netaddr library allows you to work with :-

    - IPv4 and IPv6 addresses and subnets (including CIDR notation)

    - MAC (Media Access Control) addresses (and its many variant formats)

    - IEEE OUI, IAB, EUI-48 and EUI-64 identifiers

    - arbitary IP address ranges and user-friendly glob style IP ranges

Included are routines for :-

    - generating, sorting, summarizing and excluding IP addresses and
      ranges

    - converting IP addresses and ranges from one notation to another

    - querying OUI and IAB organisational information published by the
      IEEE

    - querying information on IP standards published by IANA


Online resources :-

    - Examples and tutorials

        http://code.google.com/p/netaddr/wiki/NetAddrExamples

    - API documentation

        http://packages.python.org/netaddr/

    - Changes and updates for all previous and current releases

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
