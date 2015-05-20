from netaddr import IPGlob, IPNetwork


def test_ipglob_basic():
    #TODO: do the same testing on IPGlob as IPRange.
    assert IPGlob('192.0.2.*') == IPNetwork('192.0.2.0/24')
