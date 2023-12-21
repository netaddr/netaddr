import pytest

from netaddr import IPAddress

# Excluding is_ipv4_compat as we'll likely be dropping it
unicast = 1 << 0
multicast = 1 << 1
loopback = 1 << 2
private = 1 << 3
link_local = 1 << 4
reserved = 1 << 5
ipv4_mapped = 1 << 6
hostmask = 1 << 7
netmask = 1 << 8

flags = {
    'unicast': unicast,
    'multicast': multicast,
    'loopback': loopback,
    'private': private,
    'link_local': link_local,
    'reserved': reserved,
    'ipv4_mapped': ipv4_mapped,
    'hostmask': hostmask,
    'netmask': netmask,
}


@pytest.mark.parametrize('text_address,categories', [
    # IPv4
    ['0.0.0.0', reserved | hostmask | netmask | unicast],
    ['0.0.1.255', hostmask | reserved | unicast | hostmask],
    ['0.255.255.255', reserved | hostmask | unicast],
    ['10.0.0.1', private | unicast],
    ['62.125.24.5', unicast],
    ['127.0.0.0', reserved | loopback | unicast | reserved],
    ['127.0.0.1', loopback | reserved | unicast],
    ['172.24.0.1', private | unicast],
    ['127.255.255.255', reserved | hostmask | loopback | unicast],
    ['192.0.2.0', reserved | unicast],
    ['192.0.2.1', reserved | unicast],
    ['192.0.2.255', reserved | unicast],
    ['192.88.99.0', reserved | unicast],
    ['192.88.99.255', reserved | unicast],
    ['192.168.0.1', private | unicast],
    ['198.18.0.0', private | unicast],
    ['198.19.255.255', private | unicast],
    ['233.252.0.0', reserved | multicast],
    ['233.252.0.255', reserved | multicast],
    ['239.192.0.1', private | multicast],
    ['253.0.0.1', reserved | unicast],
    ['255.255.254.0', netmask | reserved | unicast],
    # IPv6
    ['::1', loopback | hostmask | reserved | unicast],
    ['fc00::1', private | unicast],
    ['fe80::1', private | unicast | link_local],
    ['ff00::1', reserved | multicast],
])
def test_ip_categories(text_address, categories):
    address = IPAddress(text_address)
    methods = [
        getattr(address, name)
        for name in dir(address) if name.startswith('is_') and name != 'is_ipv4_compat'
    ]
    for method in methods:
        name = method.__name__.replace('is_', '')
        flag = flags[name]
        got_value = method()
        expected_value = bool(categories & flag)
        assert got_value == expected_value, 'Expected is_%s() value to be %s' % (name, expected_value)
        categories &= ~flag

    # Just one final check to make sure we haven't missed any flags
    assert categories == 0
