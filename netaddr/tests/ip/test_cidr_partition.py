import pytest

from netaddr import IPNetwork, cidr_exclude
from netaddr.ip import cidr_partition


@pytest.mark.parametrize(
    'target,exclude',
    [
        ('0.0.0.0/0', '::/0'),
        ('192.0.2.1/24', '::/0'),
        ('0.0.0.0/24', '::1/128'),
        ('::/0', '0.0.0.0/0'),
        ('::192.0.2.0/120', '192.0.2.0/24'),
        ('2001:db8::1/64', '0.0.0.0/0'),
    ],
)
def test_cidr_partition_keeps_address_families_separate(target, exclude):
    network = IPNetwork(target).cidr
    if network.version == 4:
        expected = ([network], [], [])
    else:
        expected = ([], [], [network])

    assert cidr_partition(target, exclude) == expected
    assert cidr_exclude(target, exclude) == [network]
