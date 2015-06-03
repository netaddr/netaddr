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


def test_iterhosts_v6():
    assert list(IPNetwork('::ffff:192.0.2.0/125').iter_hosts()) == [
        IPAddress('::ffff:192.0.2.1'),
        IPAddress('::ffff:192.0.2.2'),
        IPAddress('::ffff:192.0.2.3'),
        IPAddress('::ffff:192.0.2.4'),
        IPAddress('::ffff:192.0.2.5'),
        IPAddress('::ffff:192.0.2.6'),
        IPAddress('::ffff:192.0.2.7'),
    ]

def test_ipnetwork_boolean_evaluation_v6():
    assert bool(IPNetwork('::/0'))


def test_ipnetwork_slice_v6():
    ip = IPNetwork('fe80::/10')
    assert ip[0] == IPAddress('fe80::')
    assert ip[-1] == IPAddress('febf:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
    assert ip.size == 332306998946228968225951765070086144

    with pytest.raises(TypeError):
        list(ip[0:5:1])


def test_ip_network_membership_v6():
    assert IPAddress('ffff::1') in IPNetwork('ffff::/127')


def test_ip_network_equality_v6():
    assert IPNetwork('fe80::/10') == IPNetwork('fe80::/10')
    assert IPNetwork('fe80::/10') is not IPNetwork('fe80::/10')

    assert not IPNetwork('fe80::/10') != IPNetwork('fe80::/10')
    assert not IPNetwork('fe80::/10') is IPNetwork('fe80::/10')


def test_ipnetwork_constructor_v6():
    assert IPNetwork(IPNetwork('::192.0.2.0/120')) == IPNetwork('::192.0.2.0/120')
    assert IPNetwork('::192.0.2.0/120') == IPNetwork('::192.0.2.0/120')
    assert IPNetwork('::192.0.2.0/120', 6) == IPNetwork('::192.0.2.0/120')


def test_ipaddress_netmask_v6():
    assert IPAddress('::').netmask_bits() == 128


def test_objects_use_slots():
    assert not hasattr(IPNetwork("::/64"), "__dict__")
    assert not hasattr(IPAddress("::"), "__dict__")
