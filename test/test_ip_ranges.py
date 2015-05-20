from netaddr import iter_iprange, IPAddress, cidr_merge, IPNetwork, IPRange


def test_ip_range():
    ip_list = list(iter_iprange('192.0.2.1', '192.0.2.14'))

    assert len(ip_list) == 14

    assert ip_list == [
        IPAddress('192.0.2.1'),
        IPAddress('192.0.2.2'),
        IPAddress('192.0.2.3'),
        IPAddress('192.0.2.4'),
        IPAddress('192.0.2.5'),
        IPAddress('192.0.2.6'),
        IPAddress('192.0.2.7'),
        IPAddress('192.0.2.8'),
        IPAddress('192.0.2.9'),
        IPAddress('192.0.2.10'),
        IPAddress('192.0.2.11'),
        IPAddress('192.0.2.12'),
        IPAddress('192.0.2.13'),
        IPAddress('192.0.2.14'),
    ]

    assert cidr_merge(ip_list) == [
        IPNetwork('192.0.2.1/32'),
        IPNetwork('192.0.2.2/31'),
        IPNetwork('192.0.2.4/30'),
        IPNetwork('192.0.2.8/30'),
        IPNetwork('192.0.2.12/31'),
        IPNetwork('192.0.2.14/32'),
    ]

def test_iprange():
    range1 = IPRange('192.0.2.1', '192.0.2.15')
    assert range1 == IPRange('192.0.2.1', '192.0.2.15')

    assert range1.cidrs() == [
        IPNetwork('192.0.2.1/32'),
        IPNetwork('192.0.2.2/31'),
        IPNetwork('192.0.2.4/30'),
        IPNetwork('192.0.2.8/29'),
    ]

    assert IPRange('192.0.2.0', '192.0.2.255') == IPNetwork('192.0.2.0/24')

    range2 = IPRange('192.0.2.1', '192.0.2.15')
    addrs = list(range2)

    assert addrs ==  [
        IPAddress('192.0.2.1'),
        IPAddress('192.0.2.2'),
        IPAddress('192.0.2.3'),
        IPAddress('192.0.2.4'),
        IPAddress('192.0.2.5'),
        IPAddress('192.0.2.6'),
        IPAddress('192.0.2.7'),
        IPAddress('192.0.2.8'),
        IPAddress('192.0.2.9'),
        IPAddress('192.0.2.10'),
        IPAddress('192.0.2.11'),
        IPAddress('192.0.2.12'),
        IPAddress('192.0.2.13'),
        IPAddress('192.0.2.14'),
        IPAddress('192.0.2.15'),
    ]
    assert range2 != addrs

    assert list(range2) == addrs

    subnets = range2.cidrs()
    assert subnets == [
        IPNetwork('192.0.2.1/32'), IPNetwork('192.0.2.2/31'), IPNetwork('192.0.2.4/30'), IPNetwork('192.0.2.8/29')]

    assert range2 != subnets

    assert range2.cidrs() == subnets
