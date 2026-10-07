import random

import pytest

from netaddr import (
    iprange_to_cidrs,
    IPAddress,
    IPNetwork,
    IPSet,
    cidr_merge,
    cidr_exclude,
    largest_matching_cidr,
    smallest_matching_cidr,
    all_matching_cidrs,
)


def test_iprange_to_cidrs_worst_case_v4():
    networks = iprange_to_cidrs('0.0.0.1', '255.255.255.254')
    assert networks == [
        IPNetwork('0.0.0.1/32'),
        IPNetwork('0.0.0.2/31'),
        IPNetwork('0.0.0.4/30'),
        IPNetwork('0.0.0.8/29'),
        IPNetwork('0.0.0.16/28'),
        IPNetwork('0.0.0.32/27'),
        IPNetwork('0.0.0.64/26'),
        IPNetwork('0.0.0.128/25'),
        IPNetwork('0.0.1.0/24'),
        IPNetwork('0.0.2.0/23'),
        IPNetwork('0.0.4.0/22'),
        IPNetwork('0.0.8.0/21'),
        IPNetwork('0.0.16.0/20'),
        IPNetwork('0.0.32.0/19'),
        IPNetwork('0.0.64.0/18'),
        IPNetwork('0.0.128.0/17'),
        IPNetwork('0.1.0.0/16'),
        IPNetwork('0.2.0.0/15'),
        IPNetwork('0.4.0.0/14'),
        IPNetwork('0.8.0.0/13'),
        IPNetwork('0.16.0.0/12'),
        IPNetwork('0.32.0.0/11'),
        IPNetwork('0.64.0.0/10'),
        IPNetwork('0.128.0.0/9'),
        IPNetwork('1.0.0.0/8'),
        IPNetwork('2.0.0.0/7'),
        IPNetwork('4.0.0.0/6'),
        IPNetwork('8.0.0.0/5'),
        IPNetwork('16.0.0.0/4'),
        IPNetwork('32.0.0.0/3'),
        IPNetwork('64.0.0.0/2'),
        IPNetwork('128.0.0.0/2'),
        IPNetwork('192.0.0.0/3'),
        IPNetwork('224.0.0.0/4'),
        IPNetwork('240.0.0.0/5'),
        IPNetwork('248.0.0.0/6'),
        IPNetwork('252.0.0.0/7'),
        IPNetwork('254.0.0.0/8'),
        IPNetwork('255.0.0.0/9'),
        IPNetwork('255.128.0.0/10'),
        IPNetwork('255.192.0.0/11'),
        IPNetwork('255.224.0.0/12'),
        IPNetwork('255.240.0.0/13'),
        IPNetwork('255.248.0.0/14'),
        IPNetwork('255.252.0.0/15'),
        IPNetwork('255.254.0.0/16'),
        IPNetwork('255.255.0.0/17'),
        IPNetwork('255.255.128.0/18'),
        IPNetwork('255.255.192.0/19'),
        IPNetwork('255.255.224.0/20'),
        IPNetwork('255.255.240.0/21'),
        IPNetwork('255.255.248.0/22'),
        IPNetwork('255.255.252.0/23'),
        IPNetwork('255.255.254.0/24'),
        IPNetwork('255.255.255.0/25'),
        IPNetwork('255.255.255.128/26'),
        IPNetwork('255.255.255.192/27'),
        IPNetwork('255.255.255.224/28'),
        IPNetwork('255.255.255.240/29'),
        IPNetwork('255.255.255.248/30'),
        IPNetwork('255.255.255.252/31'),
        IPNetwork('255.255.255.254/32'),
    ]


def test_cidr_exclude_v4():
    assert cidr_exclude('192.0.2.1/32', '192.0.2.1/32') == []
    assert cidr_exclude('192.0.2.0/31', '192.0.2.1/32') == [IPNetwork('192.0.2.0/32')]
    assert cidr_exclude('192.0.2.0/24', '192.0.2.128/25') == [IPNetwork('192.0.2.0/25')]
    assert cidr_exclude('192.0.2.0/24', '192.0.2.128/27') == [
        IPNetwork('192.0.2.0/25'),
        IPNetwork('192.0.2.160/27'),
        IPNetwork('192.0.2.192/26'),
    ]

    assert cidr_exclude('192.0.2.1/32', '192.0.2.0/24') == []
    assert cidr_exclude('192.0.2.0/28', '192.0.2.16/32') == [IPNetwork('192.0.2.0/28')]
    assert cidr_exclude('192.0.1.255/32', '192.0.2.0/28') == [IPNetwork('192.0.1.255/32')]


def test_cidr_merge_v4():
    assert cidr_merge(['192.0.128.0/24', '192.0.129.0/24']) == [IPNetwork('192.0.128.0/23')]
    assert cidr_merge(['192.0.129.0/24', '192.0.130.0/24']) == [
        IPNetwork('192.0.129.0/24'),
        IPNetwork('192.0.130.0/24'),
    ]
    assert cidr_merge(['192.0.2.112/30', '192.0.2.116/31', '192.0.2.118/31']) == [
        IPNetwork('192.0.2.112/29')
    ]
    assert cidr_merge(['192.0.2.112/30', '192.0.2.116/32', '192.0.2.118/31']) == [
        IPNetwork('192.0.2.112/30'),
        IPNetwork('192.0.2.116/32'),
        IPNetwork('192.0.2.118/31'),
    ]
    assert cidr_merge(['192.0.2.112/31', '192.0.2.116/31', '192.0.2.118/31']) == [
        IPNetwork('192.0.2.112/31'),
        IPNetwork('192.0.2.116/30'),
    ]

    assert cidr_merge(
        [
            '192.0.1.254/31',
            '192.0.2.0/28',
            '192.0.2.16/28',
            '192.0.2.32/28',
            '192.0.2.48/28',
            '192.0.2.64/28',
            '192.0.2.80/28',
            '192.0.2.96/28',
            '192.0.2.112/28',
            '192.0.2.128/28',
            '192.0.2.144/28',
            '192.0.2.160/28',
            '192.0.2.176/28',
            '192.0.2.192/28',
            '192.0.2.208/28',
            '192.0.2.224/28',
            '192.0.2.240/28',
            '192.0.3.0/28',
        ]
    ) == [
        IPNetwork('192.0.1.254/31'),
        IPNetwork('192.0.2.0/24'),
        IPNetwork('192.0.3.0/28'),
    ]


def test_extended_cidr_merge():
    orig_cidr_ipv4 = IPNetwork('192.0.2.0/23')
    orig_cidr_ipv6 = IPNetwork('::192.0.2.0/120')

    cidr_subnets = (
        [str(c) for c in orig_cidr_ipv4.subnet(28)]
        + list(orig_cidr_ipv4.subnet(28))
        + [str(c) for c in orig_cidr_ipv6.subnet(124)]
        + list(orig_cidr_ipv6.subnet(124))
        + ['192.0.2.1/32', '192.0.2.128/25', '::192.0.2.92/128']
    )

    random.shuffle(cidr_subnets)

    merged_cidrs = cidr_merge(cidr_subnets)

    assert merged_cidrs == [IPNetwork('192.0.2.0/23'), IPNetwork('::192.0.2.0/120')]
    assert merged_cidrs == [orig_cidr_ipv4, orig_cidr_ipv6]


@pytest.mark.parametrize(
    'networks, expected',
    [
        ([], []),
        (['192.0.2.1/32'], ['192.0.2.1/32']),
        (['2001:db8::1/128'], ['2001:db8::1/128']),
        (
            ['192.0.2.0/30', '192.0.2.4/31', '192.0.2.7/32'],
            ['192.0.2.0/30', '192.0.2.4/31', '192.0.2.7/32'],
        ),
        (
            ['2001:db8::/126', '2001:db8::4/127', '2001:db8::7/128'],
            ['2001:db8::/126', '2001:db8::4/127', '2001:db8::7/128'],
        ),
        (
            ['2001:db8::/126', '192.0.2.0/30'],
            ['192.0.2.0/30', '2001:db8::/126'],
        ),
        (['0.0.0.0/0', '::/0'], ['0.0.0.0/0', '::/0']),
    ],
)
def test_cidr_merge_ipset_does_not_expand_addresses(monkeypatch, networks, expected):
    ipset = IPSet(networks)

    def fail_iteration(self):
        pytest.fail('IPSet merging must not enumerate individual addresses')

    monkeypatch.setattr(IPSet, '__iter__', fail_iteration)
    monkeypatch.setattr(IPNetwork, '__iter__', fail_iteration)
    assert list(map(str, cidr_merge(ipset))) == expected


@pytest.mark.parametrize(
    'stored, expected',
    [
        ('192.0.2.42/24', '192.0.2.0/24'),
        ('2001:db8::42/120', '2001:db8::/120'),
        ('192.0.2.42/32', '192.0.2.42/32'),
        ('2001:db8::42/128', '2001:db8::42/128'),
    ],
)
def test_cidr_merge_ipset_returns_independent_canonical_networks(stored, expected):
    ipset = IPSet([stored])
    original = ipset.iter_cidrs()[0]
    merged = cidr_merge(ipset)
    assert list(map(str, merged)) == [expected]
    assert merged[0] is not original
    assert cidr_merge(ipset)[0] is not merged[0]
    merged[0].value = 0
    assert str(original) == stored
    assert str(ipset.iter_cidrs()[0]) == stored


def test_cidr_merge_ipset_subclass_preserves_iteration():
    class FilteredIPSet(IPSet):
        def __iter__(self):
            yield IPAddress('192.0.2.1')

        def iter_cidrs(self):
            pytest.fail('Custom IPSet iteration must not inspect CIDRs')

    assert cidr_merge(FilteredIPSet(['192.0.2.0/30'])) == [IPNetwork('192.0.2.1/32')]


def test_cidr_merge_ipset_network_subclass_preserves_iteration():
    class FilteredIPNetwork(IPNetwork):
        def __iter__(self):
            yield IPAddress(self.first + 1, version=self.version)

        @property
        def cidr(self):
            pytest.fail('Custom network iteration must not be replaced with CIDR coverage')

    ipset = IPSet([FilteredIPNetwork('192.0.2.0/30'), IPNetwork('192.0.2.8/30')])
    assert cidr_merge(ipset) == [IPNetwork('192.0.2.1/32'), IPNetwork('192.0.2.8/30')]


def test_cidr_merge_ipset_network_subclass_is_not_sorted_twice():
    class ComparisonIPNetwork(IPNetwork):
        comparisons = 0

        def sort_key(self):
            type(self).comparisons += 1
            return super().sort_key()

        def __iter__(self):
            yield IPAddress(self.first + type(self).comparisons, version=self.version)

    ipset = IPSet([ComparisonIPNetwork('192.0.2.0/30'), IPNetwork('192.0.2.8/30')])
    ComparisonIPNetwork.comparisons = 0
    expected = cidr_merge(iter(ipset))
    ComparisonIPNetwork.comparisons = 0
    assert cidr_merge(ipset) == expected


def test_cidr_merge_ipset_noncompact_state():
    ipset = IPSet()
    ipset.__setstate__(((int(IPAddress('192.0.2.0')), 30, 4), (int(IPAddress('192.0.2.4')), 30, 4)))
    before = tuple(map(str, ipset.iter_cidrs()))
    assert cidr_merge(ipset) == [IPNetwork('192.0.2.0/29')]
    assert tuple(map(str, ipset.iter_cidrs())) == before


@pytest.mark.parametrize('container', [list, iter, dict.fromkeys])
def test_cidr_merge_generic_iterable_preserves_original_network(container):
    network = IPNetwork('192.0.2.42/24')
    merged = cidr_merge(container([network]))
    assert merged == [network]
    assert merged[0] is network
    assert str(merged[0]) == '192.0.2.42/24'


def test_whole_network_cidr_merge_v4():
    assert cidr_merge(['0.0.0.0/0', '0.0.0.0']) == [IPNetwork('0.0.0.0/0')]
    assert cidr_merge(['0.0.0.0/0', '255.255.255.255']) == [IPNetwork('0.0.0.0/0')]
    assert cidr_merge(['0.0.0.0/0', '192.0.2.0/24', '10.0.0.0/8']) == [IPNetwork('0.0.0.0/0')]


def test_largest_matching_cidr_v4():
    assert largest_matching_cidr('192.0.2.0', ['192.0.2.0']) == IPNetwork('192.0.2.0/32')
    assert largest_matching_cidr('192.0.2.0', ['10.0.0.1', '192.0.2.0']) == IPNetwork(
        '192.0.2.0/32'
    )
    assert largest_matching_cidr('192.0.2.0', ['10.0.0.1', '192.0.2.0', '224.0.0.1']) == IPNetwork(
        '192.0.2.0/32'
    )
    assert largest_matching_cidr('192.0.2.0', ['10.0.0.1', '224.0.0.1']) is None


def test_smallest_matching_cidr_v4():
    assert smallest_matching_cidr('192.0.2.0', ['10.0.0.1', '192.0.2.0', '224.0.0.1']) == IPNetwork(
        '192.0.2.0/32'
    )
    assert smallest_matching_cidr(
        '192.0.2.32',
        ['0.0.0.0/0', '10.0.0.0/8', '192.0.0.0/8', '192.0.1.0/24', '192.0.2.0/24', '192.0.3.0/24'],
    ) == IPNetwork('192.0.2.0/24')
    assert smallest_matching_cidr('192.0.2.0', ['10.0.0.1', '224.0.0.1']) is None


def test_all_matching_cidrs_v4():
    assert all_matching_cidrs(
        '192.0.2.32',
        ['0.0.0.0/0', '10.0.0.0/8', '192.0.0.0/8', '192.0.1.0/24', '192.0.2.0/24', '192.0.3.0/24'],
    ) == [
        IPNetwork('0.0.0.0/0'),
        IPNetwork('192.0.0.0/8'),
        IPNetwork('192.0.2.0/24'),
    ]


def test_cidr_matching_v4():
    networks = [str(c) for c in IPNetwork('192.0.2.128/27').supernet(22)]

    assert networks == [
        '192.0.0.0/22',
        '192.0.2.0/23',
        '192.0.2.0/24',
        '192.0.2.128/25',
        '192.0.2.128/26',
    ]

    assert all_matching_cidrs('192.0.2.0', networks) == [
        IPNetwork('192.0.0.0/22'),
        IPNetwork('192.0.2.0/23'),
        IPNetwork('192.0.2.0/24'),
    ]

    assert smallest_matching_cidr('192.0.2.0', networks) == IPNetwork('192.0.2.0/24')
    assert largest_matching_cidr('192.0.2.0', networks) == IPNetwork('192.0.0.0/22')


# {{{
# >>> all_matching_cidrs('192.0.2.0', ['192.0.2.0/24'])
# [IPNetwork('192.0.2.0/24')]
#
# >>> all_matching_cidrs('192.0.2.0', ['::/96'])
# []
#
#
# }}}
