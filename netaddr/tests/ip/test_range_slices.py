import types

import pytest

from netaddr import IPAddress, IPNetwork, IPRange


@pytest.mark.parametrize(
    'addresses',
    [
        IPNetwork('192.0.2.0/29'),
        IPRange('192.0.2.0', '192.0.2.7'),
        IPNetwork('0.0.0.0/29'),
        IPNetwork('255.255.255.248/29'),
        IPNetwork('0.0.0.0/32'),
        IPNetwork('255.255.255.255/32'),
    ],
)
@pytest.mark.parametrize(
    'selection',
    [
        slice(0, 0),
        slice(1, 1),
        slice(100, 100),
        slice(None, None, -10),
        slice(3, 7, 20),
        slice(2, 5, 2),
        slice(1, 5, -1),
        slice(-100, -100),
        slice(5, 2),
        slice(100, None),
        slice(None, None),
        slice(None, None, -1),
    ],
)
def test_ipv4_slices_match_sequence_slicing(addresses, selection):
    result = addresses[selection]
    assert isinstance(result, types.GeneratorType)
    assert list(result) == list(addresses)[selection]


@pytest.mark.parametrize('addresses', [IPNetwork('::/128'), IPRange('::', '::1')])
def test_ipv6_slices_remain_unsupported(addresses):
    with pytest.raises(TypeError, match='IPv6 slices are not supported'):
        addresses[:0]


def test_zero_slice_step_remains_invalid():
    with pytest.raises(ValueError, match='slice step cannot be zero'):
        IPNetwork('0.0.0.0/32')[::0]


def test_large_ipv4_slice_is_lazy():
    result = IPNetwork('0.0.0.0/0')[1:]
    assert isinstance(result, types.GeneratorType)
    assert next(result) == IPAddress('0.0.0.1')
    assert next(result) == IPAddress('0.0.0.2')


def test_slice_keeps_original_addresses_after_network_changes():
    network = IPNetwork('192.0.2.0/29')
    result = network[1:3]
    network.value = int(IPAddress('198.51.100.0'))
    assert list(result) == [IPAddress('192.0.2.1'), IPAddress('192.0.2.2')]
