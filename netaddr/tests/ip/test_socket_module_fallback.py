import pytest

from netaddr.fbsocket import inet_ntop, inet_pton, inet_ntoa, AF_INET, AF_INET6


@pytest.mark.parametrize(
    ('actual', 'expected'),
    [
        ('0:0:0:0:0:0:0:0', '::'),
        ('0:0:0:0:0:0:0:A', '::a'),
        ('A:0:0:0:0:0:0:0', 'a::'),
        ('A:0:A:0:0:0:0:0', 'a:0:a::'),
        ('A:0:0:0:0:0:0:A', 'a::a'),
        ('0:A:0:0:0:0:0:A', '0:a::a'),
        ('A:0:A:0:0:0:0:A', 'a:0:a::a'),
        ('0:0:0:A:0:0:0:A', '::a:0:0:0:a'),
        ('0:0:0:0:A:0:0:A', '::a:0:0:a'),
        ('A:0:0:0:0:A:0:A', 'a::a:0:a'),
        ('A:0:0:A:0:0:A:0', 'a::a:0:0:a:0'),
        ('A:0:A:0:A:0:A:0', 'a:0:a:0:a:0:a:0'),
        ('0:A:0:A:0:A:0:A', '0:a:0:a:0:a:0:a'),
        ('1080:0:0:0:8:800:200C:417A', '1080::8:800:200c:417a'),
        ('FEDC:BA98:7654:3210:FEDC:BA98:7654:3210', 'fedc:ba98:7654:3210:fedc:ba98:7654:3210'),
    ],
)
def test_inet_ntop_and_inet_pton_ipv6_conversion(actual, expected):
    assert inet_ntop(AF_INET6, inet_pton(AF_INET6, actual)) == expected


def test_inet_ntoa_ipv4_exceptions():
    with pytest.raises(TypeError):
        inet_ntoa(1)

    # str is the wrong type on Python 3 (struct.unpack needs bytes), so it is a
    # TypeError rather than a length error. This used to pass '\x00', a 1-char
    # str, and expect ValueError - which only worked because the str check made
    # every call fail before the length was ever looked at.
    with pytest.raises(TypeError):
        inet_ntoa('\x00')

    with pytest.raises(ValueError):
        inet_ntoa(b'\x00')


def test_inet_ntoa_ipv4():
    assert inet_ntoa(b'\x01\x02\x03\x04') == '1.2.3.4'


@pytest.mark.parametrize(
    ('af', 'packed_ip', 'expected'),
    [
        (AF_INET, b'\x01\x02\x03\x04', '1.2.3.4'),
        (AF_INET6, bytes.fromhex('00000000000000000000ffff01020304'), '::ffff:1.2.3.4'),
        (AF_INET6, bytes.fromhex('20010db8000000000000000000000001'), '2001:db8::1'),
    ],
)
def test_inet_ntop_accepts_bytes(af, packed_ip, expected):
    assert inet_ntop(af, packed_ip) == expected


@pytest.mark.parametrize('af', [AF_INET, AF_INET6])
def test_inet_ntop_roundtrips_through_inet_pton(af):
    address = '1.2.3.4' if af == AF_INET else '::ffff:1.2.3.4'
    assert inet_ntop(af, inet_pton(af, address)) == address


def test_inet_pton_ipv4_exceptions():
    with pytest.raises(OSError):
        inet_pton(AF_INET, '::0x07f')

    with pytest.raises(TypeError):
        inet_pton(AF_INET, 1)


def test_inet_pton_ipv6_exceptions():
    with pytest.raises(OSError):
        inet_pton(AF_INET6, '::0x07f')

    with pytest.raises(TypeError):
        inet_pton(AF_INET6, 1)
