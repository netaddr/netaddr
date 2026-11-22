import pytest

from netaddr.contrib.subnet_splitter import SubnetSplitter
from netaddr.ip import IPNetwork


def test_ip_splitter():
    splitter = SubnetSplitter('172.24.0.0/16')
    assert splitter.available_subnets() == [IPNetwork('172.24.0.0/16')]

    assert splitter.extract_subnet(23, count=4) == [
        IPNetwork('172.24.0.0/23'),
        IPNetwork('172.24.2.0/23'),
        IPNetwork('172.24.4.0/23'),
        IPNetwork('172.24.6.0/23'),
    ]

    assert splitter.available_subnets() == [
        IPNetwork('172.24.8.0/21'),
        IPNetwork('172.24.16.0/20'),
        IPNetwork('172.24.32.0/19'),
        IPNetwork('172.24.64.0/18'),
        IPNetwork('172.24.128.0/17'),
    ]

    assert splitter.extract_subnet(28, count=10) == [
        IPNetwork('172.24.8.0/28'),
        IPNetwork('172.24.8.16/28'),
        IPNetwork('172.24.8.32/28'),
        IPNetwork('172.24.8.48/28'),
        IPNetwork('172.24.8.64/28'),
        IPNetwork('172.24.8.80/28'),
        IPNetwork('172.24.8.96/28'),
        IPNetwork('172.24.8.112/28'),
        IPNetwork('172.24.8.128/28'),
        IPNetwork('172.24.8.144/28'),
    ]

    assert splitter.available_subnets() == [
        IPNetwork('172.24.8.160/27'),
        IPNetwork('172.24.8.192/26'),
        IPNetwork('172.24.9.0/24'),
        IPNetwork('172.24.10.0/23'),
        IPNetwork('172.24.12.0/22'),
        IPNetwork('172.24.16.0/20'),
        IPNetwork('172.24.32.0/19'),
        IPNetwork('172.24.64.0/18'),
        IPNetwork('172.24.128.0/17'),
    ]


def test_ip_splitter_remove_same_input_range():
    s = SubnetSplitter('172.24.0.0/16')
    assert s.available_subnets() == [IPNetwork('172.24.0.0/16')]

    assert s.extract_subnet(16, count=1) == [
        IPNetwork('172.24.0.0/16'),
    ]

    assert s.available_subnets() == []


def test_ip_splitter_remove_more_than_input_range():
    s = SubnetSplitter('172.24.0.0/16')
    assert s.available_subnets() == [IPNetwork('172.24.0.0/16')]

    with pytest.raises(ValueError):
        s.extract_subnet(16, count=2)


def test_ip_splitter_remove_prefix_larger_than_input_range():
    s = SubnetSplitter('172.24.0.0/16')
    assert s.available_subnets() == [IPNetwork('172.24.0.0/16')]
    assert s.extract_subnet(15, count=1) == []
    assert s.available_subnets() == [IPNetwork('172.24.0.0/16')]


@pytest.mark.parametrize('first_prefix,second_prefix', [(24, 26), (26, 24)])
def test_non_power_of_two_allocations_do_not_overlap(first_prefix, second_prefix):
    from netaddr import IPSet

    splitter = SubnetSplitter('10.40.0.0/22')
    first = splitter.extract_subnet(first_prefix, count=3)
    second = splitter.extract_subnet(second_prefix, count=3)
    assert len(first) == len(second) == 3
    assert not (IPSet(first) & IPSet(second))
    used = IPSet(first + second)
    available = IPSet(splitter.available_subnets())
    assert not (used & available)
    assert used | available == IPSet(['10.40.0.0/22'])
    assert available.size == 64


def test_fragmented_allocation_is_atomic_on_failure():
    splitter = SubnetSplitter('10.40.0.0/22')
    splitter.extract_subnet(26, count=3)
    before = splitter.available_subnets()
    with pytest.raises(ValueError):
        splitter.extract_subnet(24, count=4)
    assert splitter.available_subnets() == before
    assert len(splitter.extract_subnet(24, count=3)) == 3


def test_ipv6_non_power_of_two_allocation():
    from netaddr import IPSet

    splitter = SubnetSplitter('2001:db8::/120')
    first = splitter.extract_subnet(124, count=3)
    second = splitter.extract_subnet(126, count=3)
    assert not (IPSet(first) & IPSet(second))
    available = IPSet(splitter.available_subnets())
    assert not (IPSet(first + second) & available)
    assert available.size == 256 - 3 * 16 - 3 * 4


def test_unspecified_count_uses_first_available_block():
    splitter = SubnetSplitter('10.0.0.0/24')
    splitter.extract_subnet(26, count=1)
    assert splitter.extract_subnet(27) == [IPNetwork('10.0.0.64/27'), IPNetwork('10.0.0.96/27')]
    assert splitter.available_subnets() == [IPNetwork('10.0.0.128/25')]
