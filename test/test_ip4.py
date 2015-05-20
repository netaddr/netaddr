import types
import random

import pytest

from netaddr import IPAddress, IPNetwork


def test_ipaddress_v4():
    ip = IPAddress('192.0.2.1')
    assert ip.version == 4
    assert repr(ip) == "IPAddress('192.0.2.1')"
    assert str(ip) == '192.0.2.1'
    assert ip.format() == '192.0.2.1'
    assert int(ip) == 3221225985
    assert hex(ip) == '0xc0000201'
    assert ip.bin == '0b11000000000000000000001000000001'
    assert ip.bits() == '11000000.00000000.00000010.00000001'
    assert ip.words == (192, 0, 2, 1)


@pytest.mark.parametrize(
    ('value', 'ipaddr', 'network', 'cidr', 'broadcast', 'netmask', 'hostmask', 'size'), [
        (
            '192.0.2.1',
            IPAddress('192.0.2.1'),
            IPAddress('192.0.2.1'),
            IPNetwork('192.0.2.1/32'),
            IPAddress('192.0.2.1'),
            IPAddress('255.255.255.255'),
            IPAddress('0.0.0.0'),
            1,
        ),
        (
            '192.0.2.0/24',
            IPAddress('192.0.2.0'),
            IPAddress('192.0.2.0'),
            IPNetwork('192.0.2.0/24'),
            IPAddress('192.0.2.255'),
            IPAddress('255.255.255.0'),
            IPAddress('0.0.0.255'),
            256
        ),
        (
            '192.0.3.112/22',
            IPAddress('192.0.3.112'),
            IPAddress('192.0.0.0'),
            IPNetwork('192.0.0.0/22'),
            IPAddress('192.0.3.255'),
            IPAddress('255.255.252.0'),
            IPAddress('0.0.3.255'),
            1024
        ),
    ])
def test_ipnetwork_v4(value, ipaddr, network, cidr, broadcast, netmask, hostmask, size):
    net = IPNetwork(value)
    assert net.ip == ipaddr
    assert net.network == network
    assert net.cidr == cidr
    assert net.broadcast == broadcast
    assert net.netmask == netmask
    assert net.hostmask == hostmask
    assert net.size == size


def test_ipnetwork_list_operations_v4():
    ip = IPNetwork('192.0.2.16/29')
    assert len(ip) == 8

    ip_list = list(ip)
    assert len(ip_list) == 8

    assert ip_list == [
        IPAddress('192.0.2.16'),
        IPAddress('192.0.2.17'),
        IPAddress('192.0.2.18'),
        IPAddress('192.0.2.19'),
        IPAddress('192.0.2.20'),
        IPAddress('192.0.2.21'),
        IPAddress('192.0.2.22'),
        IPAddress('192.0.2.23'),
    ]


def test_ipnetwork_index_operations_v4():
    ip = IPNetwork('192.0.2.16/29')
    assert ip[0] == IPAddress('192.0.2.16')
    assert ip[1] == IPAddress('192.0.2.17')
    assert ip[-1] == IPAddress('192.0.2.23')


def test_ipnetwork_slice_operations_v4():
    ip = IPNetwork('192.0.2.16/29')

    assert isinstance(ip[0:4], types.GeneratorType)

    assert list(ip[0:4]) == [
        IPAddress('192.0.2.16'),
        IPAddress('192.0.2.17'),
        IPAddress('192.0.2.18'),
        IPAddress('192.0.2.19'),
    ]

    assert list(ip[0::2]) == [
        IPAddress('192.0.2.16'),
        IPAddress('192.0.2.18'),
        IPAddress('192.0.2.20'),
        IPAddress('192.0.2.22'),
    ]

    assert list(ip[-1::-1]) == [
        IPAddress('192.0.2.23'),
        IPAddress('192.0.2.22'),
        IPAddress('192.0.2.21'),
        IPAddress('192.0.2.20'),
        IPAddress('192.0.2.19'),
        IPAddress('192.0.2.18'),
        IPAddress('192.0.2.17'),
        IPAddress('192.0.2.16'),
]


def test_ipnetwork_sort_order():
    ip_list = list(IPNetwork('192.0.2.128/28'))
    random.shuffle(ip_list)
    assert sorted(ip_list) == [
        IPAddress('192.0.2.128'),
        IPAddress('192.0.2.129'),
        IPAddress('192.0.2.130'),
        IPAddress('192.0.2.131'),
        IPAddress('192.0.2.132'),
        IPAddress('192.0.2.133'),
        IPAddress('192.0.2.134'),
        IPAddress('192.0.2.135'),
        IPAddress('192.0.2.136'),
        IPAddress('192.0.2.137'),
        IPAddress('192.0.2.138'),
        IPAddress('192.0.2.139'),
        IPAddress('192.0.2.140'),
        IPAddress('192.0.2.141'),
        IPAddress('192.0.2.142'),
        IPAddress('192.0.2.143'),
    ]

def test_ipaddress_and_ipnetwork_canonical_sort_order_by_version():
    ip_list = [
        IPAddress('192.0.2.130'),
        IPNetwork('192.0.2.128/28'),
        IPAddress('::'),
        IPNetwork('192.0.3.0/24'),
        IPNetwork('192.0.2.0/24'),
        IPNetwork('fe80::/64'),
        IPNetwork('172.24/12'),
        IPAddress('10.0.0.1'),
    ]

    random.shuffle(ip_list)
    ip_list.sort()

    assert ip_list == [
        IPAddress('10.0.0.1'),
        IPNetwork('172.24.0.0/12'),
        IPNetwork('192.0.2.0/24'),
        IPNetwork('192.0.2.128/28'),
        IPAddress('192.0.2.130'),
        IPNetwork('192.0.3.0/24'),
        IPAddress('::'),
        IPNetwork('fe80::/64'),
    ]
