import pytest

from netaddr import EUI, OUI


@pytest.mark.parametrize(
    'address',
    [
        '00-1B-77-49-54-FD',
        '0-1b-77-49-54-fd',
        '00:1b:77:49:54:fd',
        '0:1b:77:49:54:fd',
        '001b.7749.54fd',
        '001b:7749:54fd',
        '001b-7749-54fd',
        '001b77:4954fd',
        '001b77-4954fd',
        '001b774954fd',
        '01b774954fd',
        '00-00-00-00-00-01',
        '0-0-0-0-0-1',
        '0000-0000-0001',
        '000000000001',
    ],
)
def test_oui_accepts_eui48_strings(address):
    expected = EUI(address).oui
    actual = OUI(address)
    assert actual == expected
    assert str(actual) == str(expected)
    assert actual.records == expected.records


@pytest.mark.parametrize('value', ['00-1B-77', '0-1b-77', '001b77', 0x001B77])
def test_oui_preserves_existing_oui_inputs(value):
    assert OUI(value) == OUI(0x001B77)


@pytest.mark.parametrize('value', [0x001B774954FD, -1, 0x1000000])
def test_oui_rejects_non_oui_integers(value):
    with pytest.raises(ValueError):
        OUI(value)


@pytest.mark.parametrize('value', ['00:1b:77:49:54:fd:12:34', 'not-a-mac'])
def test_oui_rejects_invalid_and_eui64_strings(value):
    with pytest.raises(ValueError):
        OUI(value)


@pytest.mark.parametrize('value', ['00-00-01', '0-0-1', '000001', 1])
def test_short_oui_with_leading_zeroes_remains_an_oui(value):
    assert int(OUI(value)) == 1


def test_full_mac_with_small_numeric_value_uses_its_oui_not_extension():
    assert int(OUI('000000000001')) == 0
    assert int(OUI(1)) == 1


def test_unregistered_full_mac_keeps_registration_error():
    from netaddr.core import NotRegisteredError

    with pytest.raises(NotRegisteredError):
        OUI('ff-ff-ff-12-34-56')
