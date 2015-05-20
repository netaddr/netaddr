from netaddr import IPAddress, IPNetwork, IPRange, IPSet


def test_ipset_basic():
    range1 = IPRange('192.0.2.1', '192.0.2.15')

    ip_list = [
        IPAddress('192.0.2.1'),
        '192.0.2.2/31',
        IPNetwork('192.0.2.4/31'),
        IPAddress('192.0.2.6'),
        IPAddress('192.0.2.7'),
        '192.0.2.8',
        '192.0.2.9',
        IPAddress('192.0.2.10'),
        IPAddress('192.0.2.11'),
        IPNetwork('192.0.2.12/30'),
    ]

    set1 = IPSet(range1.cidrs())

    set2 = IPSet(ip_list)

    assert set2 == IPSet([
        '192.0.2.1/32',
        '192.0.2.2/31',
        '192.0.2.4/30',
        '192.0.2.8/29',
    ])

    assert set1 == set2

    assert set2.pop() == IPNetwork('192.0.2.4/30')

    assert set1 != set2
