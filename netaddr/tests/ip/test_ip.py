import weakref

from netaddr import IPAddress, IPNetwork, IPRange

def test_ip_classes_are_weak_referencable():
    weakref.ref(IPAddress('10.0.0.1'))
    weakref.ref(IPNetwork('10.0.0.1/8'))
    weakref.ref(IPRange('10.0.0.1', '10.0.0.10'))
