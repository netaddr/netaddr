import weakref

import pytest

from netaddr import IPAddress, IPNetwork, group_supernets

def test_group_supernets():

    ip_list = [
        IPNetwork('192.0.2.0/24'),
        IPAddress('192.0.2.1'),
        '192.0.2.4/31',
        '192.0.2.6',
        '192.0.3.0/30',
        IPNetwork('192.0.3.0/24'),
        IPNetwork('::0/32'),
        IPNetwork('::0/0'),
        IPNetwork('::192.168.0.0/64'),
        IPAddress('::192.168.0.1'),
    ]

    assert group_supernets(ip_list) == [
        (IPNetwork('192.0.2.0/24'), [
            IPNetwork('192.0.2.0/24'),
            '192.0.2.6',
            '192.0.2.4/31',
            IPAddress('192.0.2.1'),
        ]),
        (IPNetwork('192.0.3.0/24'), [
            IPNetwork('192.0.3.0/24'),
            '192.0.3.0/30',
        ]),
        (IPNetwork('::/0'), [
            IPNetwork('::/0'),
            IPNetwork('::/32'),
            IPNetwork('::192.168.0.0/64'),
            IPAddress('::192.168.0.1')
        ])
    ]

def test_group_supernets_keyfunc():

    ip_list = [
        {'network': IPNetwork('192.0.2.0/24')},
        {'network': IPAddress('192.0.2.1')},
        {'network': '192.0.2.4/31'},
        {'network': '192.0.2.6'},
        {'network': '192.0.3.0/30'},
        {'network': IPNetwork('192.0.3.0/24')},
        {'network': IPNetwork('::0/32')},
        {'network': IPNetwork('::0/0')},
        {'network': IPNetwork('::192.168.0.0/64')},
        {'network': IPAddress('::192.168.0.1')},
    ]

    assert group_supernets(ip_list, key=lambda obj: obj['network']) == [
        (IPNetwork('192.0.2.0/24'), [
            {'network': IPNetwork('192.0.2.0/24')},
            {'network': '192.0.2.6'},
            {'network': '192.0.2.4/31'},
            {'network': IPAddress('192.0.2.1')},
        ]),
        (IPNetwork('192.0.3.0/24'), [
            {'network': IPNetwork('192.0.3.0/24')},
            {'network': '192.0.3.0/30'},
        ]),
        (IPNetwork('::/0'), [
            {'network': IPNetwork('::/0')},
            {'network': IPNetwork('::/32')},
            {'network': IPNetwork('::192.168.0.0/64')},
            {'network': IPAddress('::192.168.0.1')},
        ])
    ]
