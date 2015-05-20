import pytest
from netaddr import IPAddress, IPNetwork


def test_ipaddress_v6():
    ip = IPAddress('fe80::dead:beef')
    assert ip.version == 6
    assert repr(ip) == "IPAddress('fe80::dead:beef')"
    assert str(ip) == 'fe80::dead:beef'
    assert ip.format() == 'fe80::dead:beef'
    assert int(ip) == 338288524927261089654018896845083623151
    assert hex(ip) == '0xfe8000000000000000000000deadbeef'
    assert ip.bin == '0b11111110100000000000000000000000000000000000000000000000000000000000000000000000000000000000000011011110101011011011111011101111'
    assert ip.bits() == '1111111010000000:0000000000000000:0000000000000000:0000000000000000:0000000000000000:0000000000000000:1101111010101101:1011111011101111'
    assert ip.words == (65152, 0, 0, 0, 0, 0, 57005, 48879)


@pytest.mark.parametrize(
    ('value', 'ipaddr', 'network', 'cidr', 'broadcast', 'netmask', 'hostmask', 'size'), [
        (
            'fe80::dead:beef/64',
            IPAddress('fe80::dead:beef'),
            IPAddress('fe80::'),
            IPNetwork('fe80::/64'),
            IPAddress('fe80::ffff:ffff:ffff:ffff'),
            IPAddress('ffff:ffff:ffff:ffff::'),
            IPAddress('::ffff:ffff:ffff:ffff'),
            18446744073709551616,
        ),
    ])
def test_ipnetwork_v6(value, ipaddr, network, cidr, broadcast, netmask, hostmask, size):
    net = IPNetwork(value)
    assert net.ip == ipaddr
    assert net.network == network
    assert net.cidr == cidr
    assert net.broadcast == broadcast
    assert net.netmask == netmask
    assert net.hostmask == hostmask
    assert net.size == size
