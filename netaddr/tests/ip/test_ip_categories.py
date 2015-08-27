from netaddr import IPAddress


def test_is_unicast():
    assert IPAddress('192.0.2.1').is_unicast()
    assert IPAddress('fe80::1').is_unicast()


def test_is_multicast():
    assert IPAddress('239.192.0.1').is_multicast()
    assert IPAddress('ff00::1').is_multicast()


def test_is_private():
    assert IPAddress('172.24.0.1').is_private()
    assert IPAddress('10.0.0.1').is_private()
    assert IPAddress('192.168.0.1').is_private()
    assert IPAddress('fc00::1').is_private()
    assert IPAddress('198.18.0.0').is_private()
    assert IPAddress('198.19.255.255').is_private()


def test_is_reserved():
    assert IPAddress('253.0.0.1').is_reserved()
    assert IPAddress('192.0.2.0').is_reserved()
    assert IPAddress('192.0.2.255').is_reserved()
    assert IPAddress('127.0.0.0').is_reserved()
    assert IPAddress('127.255.255.255').is_reserved()
    assert IPAddress('192.88.99.0').is_reserved()
    assert IPAddress('192.88.99.255').is_reserved()
    assert IPAddress('0.0.0.0').is_reserved()
    assert IPAddress('0.255.255.255').is_reserved()
    assert IPAddress('233.252.0.0').is_reserved()
    assert IPAddress('233.252.0.255').is_reserved()


def test_is_public():
    ip = IPAddress('62.125.24.5')
    assert ip.is_unicast() and not ip.is_private()


def test_is_netmask():
    assert IPAddress('255.255.254.0').is_netmask()


def test_is_hostmask():
    assert IPAddress('0.0.1.255').is_hostmask()


def test_is_loopback():
    assert IPAddress('127.0.0.1').is_loopback()
    assert IPAddress('::1').is_loopback()
