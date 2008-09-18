#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------

import unittest

import os
import sys

#   Run all unit tests for all modules.
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path)

from netaddr.address import *

#-----------------------------------------------------------------------------
#   Unit Tests.
#-----------------------------------------------------------------------------
class Test_Addr_IPv4(unittest.TestCase):
    """
    IP version 4 Addr() class functionality tests.
    """
    def setUp(self):
        #   Basic address.
        self.size = 32
        self.ip_addr = Addr('192.168.0.1')
        self.octets = (192, 168, 0, 1)
        self.int_value = 3232235521
        self.hex_value = '0xc0a80001'
        self.bit_value = '11000000.10101000.00000000.00000001'

        #   Boundaries.
        self.ip_addr_min = Addr('0.0.0.0')
        self.ip_addr_max = Addr('255.255.255.255')
        self.int_min = 0
        self.int_max = 4294967295
        self.hex_max = '0xffffffff'
        self.bit_min = '.'.join(['0'*8 for i in range(4)])
        self.bit_max = '.'.join(['1'*8 for i in range(4)])
        self.octet_min = (0, 0, 0, 0)
        self.octet_max = (255, 255, 255, 255)

    def testAssignments(self):
        """
        Checks a list of addresses expected to be valid.
        """
        addr = Addr('0.0.0.0')
        self.failUnless(addr.value == 0)
        self.failUnless(addr.addr_type == AT_INET)
        self.failUnless(addr.strategy == ST_IPV4)

        #   Test addr_type assignment.
        addr.addr_type = AT_INET6
        self.failUnless(addr.addr_type == AT_INET6)
        self.failUnless(addr.strategy == ST_IPV6)

        #   Test strategy assignment.
        addr.strategy = ST_EUI48
        self.failUnless(addr.addr_type == AT_LINK)
        self.failUnless(addr.strategy == ST_EUI48)

        addr.strategy = ST_EUI64
        self.failUnless(addr.addr_type == AT_EUI64)
        self.failUnless(addr.strategy == ST_EUI64)

        #   Test value assignment.
        addr.addr_type = AT_INET
        addr.value = '192.168.0.1'
        self.failUnless(addr.value == 3232235521)
        self.failUnless(addr.addr_type == AT_INET)
        self.failUnless(addr.strategy == ST_IPV4)

    def testBasics(self):
        self.failUnless(len(self.ip_addr) == self.size)
        self.failUnless(self.ip_addr[0] == self.octets[0])
        self.failUnless(tuple(self.ip_addr) == self.octets)
        self.failUnless(int(self.ip_addr) == self.int_value)
        self.failUnless(long(self.ip_addr) == self.int_value)
        self.failUnless(hex(self.ip_addr) == self.hex_value)
        self.failUnless(self.ip_addr.bits() == self.bit_value)

    def testBoundaries(self):
        self.failUnless(int(self.ip_addr_min) == self.int_min)
        self.failUnless(int(self.ip_addr_max) == self.int_max)
        self.failUnless(hex(self.ip_addr_max) == self.hex_max)
        self.failUnless(self.ip_addr_min.bits() == self.bit_min)
        self.failUnless(self.ip_addr_max.bits() == self.bit_max)

        #   Addr indexing tests - addr[x].
        self.failUnless(tuple(self.ip_addr_min) == self.octet_min)
        self.failUnless(tuple(self.ip_addr_max) == self.octet_max)
        self.failUnless(list(self.ip_addr_min) == list(self.octet_min))
        self.failUnless(list(self.ip_addr_max) == list(self.octet_max))

    def testIteration(self):
        ip_addr = Addr('192.168.0.1')
        hex_octets = ['0xc0', '0xa8', '0x0', '0x1']
        self.failUnless([hex(i) for i in ip_addr] == hex_octets)

    def testIndexingAndSlicing(self):
        ip_addr = Addr('192.168.0.1')

        # using __getitem__()
        self.failUnless(ip_addr[0] == 192)
        self.failUnless(ip_addr[1] == 168)
        self.failUnless(ip_addr[2] == 0)
        self.failUnless(ip_addr[3] == 1)

        ip_addr[3] = 2                      # using __setitem__()
        self.failUnless(ip_addr[3] == 2)    # basic index
        self.failUnless(ip_addr[-4] == 192) # negative index

        #   Slicing, oh yeah!
        self.failUnless(ip_addr[0:2] == [192, 168])          # basic slice
        self.failUnless(ip_addr[0:4:2] == [192, 0])          # slice with step
        self.failUnless(ip_addr[-1::-1] == [2, 0, 168, 192]) # negative index

    def testBooleanAlgebra(self):
        self.failIf(self.ip_addr_min == self.ip_addr_max)
        self.failUnless(self.ip_addr_min != self.ip_addr_max)

        self.failUnless(self.ip_addr_min <  self.ip_addr_max)
        self.failUnless(self.ip_addr_min <= self.ip_addr_max)
        self.failUnless(self.ip_addr_min != self.ip_addr_max)
        self.failUnless(self.ip_addr_max >  self.ip_addr_min)
        self.failUnless(self.ip_addr_max >= self.ip_addr_min)

    def testEqualityOperations(self):
        #   Different object instance but same intrinsic value.
        self.failUnless(self.ip_addr_min == Addr('0.0.0.0'))
        self.failUnless(self.ip_addr_max == Addr('255.255.255.255'))

    def testIncrementAndDecrement(self):
        ip_addr_other = Addr('0.0.0.0')
        self.failUnless(int(ip_addr_other) == 0)
        ip_addr_other += 1
        self.failUnless(int(ip_addr_other) == 1)
        #   Increment it all the way up to the value of a 'real' address.
        ip_addr_other += 3232235520
        self.failUnless(str(ip_addr_other) == str(Addr('192.168.0.1')))

        #   Roll around boundaries.
        ip_addr_other = Addr('255.255.255.255')
        ip_addr_other += 1
        self.failUnless(int(ip_addr_other) == self.int_min)
        ip_addr_other -= 1
        self.failUnless(int(ip_addr_other) == self.int_max)

    def testExceptionRaising(self):
        """
        Check that exception are being raised for unexpected input.
        """
        for addr in ([], {}, '', None, 5.2, -1, 'abc.def.ghi.jkl', '::z'):
            self.failUnlessRaises(AddrFormatError, Addr, addr)

#-----------------------------------------------------------------------------
class Test_IP(unittest.TestCase):
    """
    Test IP specific address functionality in the IP() subclass of Addr().
    """
    def setUp(self):
        #   Basic address.
        self.size = 32
        self.ip_addr = IP('192.168.0.1')
        self.octets = (192, 168, 0, 1)
        self.int_value = 3232235521
        self.hex_value = '0xc0a80001'
        self.bit_value = '11000000.10101000.00000000.00000001'

    def testAssignmentsIPv4(self):
        """
        Checks assignments to managed attributes.
        """
        ip = IP('192.168.0.1')
        self.failUnless(ip.value == 3232235521)
        self.failUnless(ip.addr_type == AT_INET)
        self.failUnless(ip.strategy == ST_IPV4)
        self.failUnless(ip.prefixlen == 32)

        #   Prefix /32 for IPv4 addresses should be implicit.
        self.failUnless(repr(ip) == "netaddr.address.IP('192.168.0.1')")
        ip.prefixlen = 24
        self.failUnless(repr(ip) == "netaddr.address.IP('192.168.0.1/24')")

    def testAssignmentsIPv6(self):
        """
        Checks assignments to managed attributes.
        """
        ip = IP('fe80::4472:4b4a:616d')
        self.failUnless(ip.value == 338288524927261089654018972099027820909)
        self.failUnless(ip.addr_type == AT_INET6)
        self.failUnless(ip.strategy == ST_IPV6)
        self.failUnless(ip.prefixlen == 128)

        #   Prefix /128 for IPv6 addresses should be implicit.
        self.failUnless(repr(ip) == "netaddr.address.IP('fe80::4472:4b4a:616d')")
        ip.prefixlen = 64
        self.failUnless(repr(ip) == "netaddr.address.IP('fe80::4472:4b4a:616d/64')")

    def testNetmask(self):
        addr = IP('192.168.1.100')
        self.failIf(addr.is_netmask())

        netmask = IP('255.255.254.0')
        self.failUnless(netmask.is_netmask())

        #   Apply subnet mask
        network_id = Addr(int(addr) & int(netmask), AT_INET)
        self.failUnless(str(network_id) == '192.168.0.0')

    def testPrefixlenAssignments(self):
        self.failUnlessRaises(ValueError, IP, '0.0.0.0/-1')
        self.failUnlessRaises(ValueError, IP, '0.0.0.0/33')
        self.failUnlessRaises(ValueError, IP, '::/-1')
        self.failUnlessRaises(ValueError, IP, '::/129')

    def test_init_negatively(self):
        #   No arguments passed to constructor.
        self.failUnlessRaises(TypeError, IP)

        #   Various bad types for address values.
        for bad_addr in ('', None, [], {}, 4.2):
            self.failUnlessRaises(AddrFormatError, IP, bad_addr)

        #   Various bad types for addr_type values.
        for bad_addr_type in ('', None, [], {}, 4.2):
            self.failUnlessRaises(ValueError, IP, '0.0.0.0', bad_addr_type)

        #   Wrong explicit address type for a valid address.
        self.failUnlessRaises(Exception, IP, '0.0.0.0', 6)
        self.failUnlessRaises(Exception, IP, '::', 4)

#-----------------------------------------------------------------------------
class Test_EUI(unittest.TestCase):
    """
    Test functionality in the EUI subclass of Addr.
    """
    def testEUI48(self):
        mac = EUI('00:C0:29:C2:52:FF')
        self.failUnless(str(mac) == '00-C0-29-C2-52-FF')
        self.failUnless(mac.oui() == '00-C0-29')
        self.failUnless(mac.ei() == 'C2-52-FF')
        self.failUnless(mac.eui64() == EUI('00-C0-29-FF-FE-C2-52-FF'))

    def testEUI64(self):
        eui64 = EUI('00-C0-29-FF-FE-C2-52-FF')
        self.failUnless(str(eui64) == '00-C0-29-FF-FE-C2-52-FF')
        self.failUnless(eui64.oui() == '00-C0-29')
        self.failUnless(eui64.ei() == 'FF-FE-C2-52-FF')
        self.failUnless(eui64.eui64() == EUI('00-C0-29-FF-FE-C2-52-FF'))

    def testIPv6LinkLocal(self):
        expected = 'fe80::20f:1fff:fe12:e733'

        mac = EUI('00-0F-1F-12-E7-33')
        ip1 = mac.ipv6_link_local()
        self.failUnless(str(ip1) == expected)
        self.failUnless(ip1 == IP(expected))

        eui64 = EUI('00-0F-1F-FF-FE-12-E7-33')
        ip2 = eui64.ipv6_link_local()
        self.failUnless(str(ip2) == expected)
        self.failUnless(ip2 == IP(expected))


#-----------------------------------------------------------------------------
class Test_Addr_IPv6(unittest.TestCase):
    """
    IP version 6 Addr() class functionality tests.
    """
    def setUp(self):
        #   Basic address.
        self.size = 128
        self.ip_addr = Addr('::ffff:c0a8:1')
        self.int_value = 281473913978881
        self.hex_value = '0xffffc0a80001'
        self.words = (0, 0, 0, 0, 0, 65535, 49320, 1)
        self.bit_value = '0000000000000000:0000000000000000:' \
                         '0000000000000000:0000000000000000:' \
                         '0000000000000000:1111111111111111:' \
                         '1100000010101000:0000000000000001'

        #   Boundaries.
        self.ip_addr_min = Addr('::')
        self.ip_addr_max = Addr('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
        self.int_min = 0
        self.int_max = 340282366920938463463374607431768211455
        self.hex_max = '0xffffffffffffffffffffffffffffffff'
        self.bit_min = ':'.join(['0'*16 for i in range(8)])
        self.bit_max = ':'.join(['1'*16 for i in range(8)])
        self.words_min = (0, 0, 0, 0, 0, 0, 0, 0)
        self.words_max = (65535, 65535, 65535, 65535, 65535, 65535,
                          65535, 65535)

    def testAssignment(self):
        ip_addr = Addr(0, AT_INET6)
        ip_addr.value = 0xffffc0a80001
        self.failUnless(str(ip_addr) == '::ffff:c0a8:1')

    def testCompaction(self):
        ipv6_compactions = {
            '0:0:0:0:0:0:0:0' : '::',
            '0:0:0:0:0:0:0:1' : '::1',
            '1:0:0:0:0:0:0:1' : '1::1',
            '1:0:1:0:0:0:0:1' : '1::1:0:0:0:0:1',
            '1:0:0:0:0:1:0:1' : '1::1:0:1',
            '1080:0:0:0:8:800:200C:417A' : '1080::8:800:200c:417a',
            'FEDC:BA98:7654:3210:FEDC:BA98:7654:3210' : \
                'fedc:ba98:7654:3210:fedc:ba98:7654:3210'
        }

        for init_val, expected_val in ipv6_compactions.items():
            self.failUnless(str(Addr(init_val)) == expected_val)

    def testValidityExamples(self):
        valid_ipv6_addrs = [
            '::',   #   unspecified address
            '1::',
            '::1',  #   IPv6 loopback address
            '::1:0',
            '2001:db8:31:1:20a:95ff:fef5:246e',
            '2001:db8:31:1:20a::fef5:246e',
            'ffff:ffff:ffff:ffff:ffff:ffff:ffff:fffe',
            'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff',
        ]

        for addr in valid_ipv6_addrs:
            self.failUnless(ST_IPV6.valid_str(addr))

    def testRunningIPv6_Chapter_01(self):
        """
        From "Running IPv6", Chapter 2.
        """
        addr1 = Addr('2001:db8:31:0:0:0:0:1')
        addr2 = Addr('2001:db8:31::1')

        self.failUnless(addr1 == addr2)

        self.failIf(ST_IPV6.valid_str('2001:db8:31::5900::1'))

    def testExceptions(self):
        for cidr in (None, [], {}):
            self.failUnlessRaises(TypeError, CIDR, cidr)

        for cidr in ('', 'foo'):
            self.failUnlessRaises(AddrFormatError, CIDR, cidr)

    def testBasics(self):
        self.failUnless(len(self.ip_addr) == self.size)
        self.failUnless(self.ip_addr[0] == self.words[0])
        self.failUnless(tuple(self.ip_addr) == self.words)
        self.failUnless(int(self.ip_addr) == self.int_value)
        self.failUnless(long(self.ip_addr) == self.int_value)
        self.failUnless(hex(self.ip_addr) == self.hex_value)
        self.failUnless(self.ip_addr.bits() == self.bit_value)

    def testBoundaries(self):
        self.failUnless(int(self.ip_addr_min) == self.int_min)
        self.failUnless(int(self.ip_addr_max) == self.int_max)
        self.failUnless(hex(self.ip_addr_max) == self.hex_max)
        self.failUnless(self.ip_addr_min.bits() == self.bit_min)
        self.failUnless(self.ip_addr_max.bits() == self.bit_max)
        #   Addr indexing tests - addr[x].
        self.failUnless(tuple(self.ip_addr_min) == self.words_min)
        self.failUnless(tuple(self.ip_addr_max) == self.words_max)
        self.failUnless(list(self.ip_addr_min) == list(self.words_min))
        self.failUnless(list(self.ip_addr_max) == list(self.words_max))

    def testBooleanAlgebra(self):
        self.failIf(self.ip_addr_min == self.ip_addr_max)
        self.failUnless(self.ip_addr_min != self.ip_addr_max)

        self.failUnless(self.ip_addr_min <  self.ip_addr_max)
        self.failUnless(self.ip_addr_min <= self.ip_addr_max)
        self.failUnless(self.ip_addr_min != self.ip_addr_max)
        self.failUnless(self.ip_addr_max >  self.ip_addr_min)
        self.failUnless(self.ip_addr_max >= self.ip_addr_min)

    def testEqualityOperations(self):
        #   Different object instance but same intrinsic value.
        self.failUnless(self.ip_addr_min == \
            Addr('::'))
        self.failUnless(self.ip_addr_max == \
            Addr('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'))

    def testIncrementAndDecrement(self):
        ip_addr_other = Addr('::')
        self.failUnless(int(ip_addr_other) == 0)
        ip_addr_other += 1
        self.failUnless(int(ip_addr_other) == 1)
        #   Increment it all the way up to the value of a 'real' address.
        ip_addr_other += 281473913978880
        self.failUnless(str(ip_addr_other) == \
            str(Addr('::ffff:c0a8:1')))

        #   Roll around boundaries.
        ip_addr_other = \
            Addr('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
        ip_addr_other += 1
        self.failUnless(int(ip_addr_other) == self.int_min)
        ip_addr_other -= 1
        self.failUnless(int(ip_addr_other) == self.int_max)


    def testSubnetPrefix_RFC4291(self):
        ip1 = IP('2001:0DB8:0000:CD30:0000:0000:0000:0000/60')
        ip2 = IP('2001:0DB8::CD30:0:0:0:0/60')
        ip3 = IP('2001:0DB8:0:CD30::/60')
        #FIXME: ip4 = IP('2001:0DB8:0:CD3/60')
        ip5 = IP('2001:0DB8::CD30/60')
        ip6 = IP('2001:0DB8::CD3/60')

        r1 = CIDR('2001:0DB8:0000:CD30:0000:0000:0000:0000/60')
        r2 = CIDR('2001:0DB8:0:CD30::/60')
        r3 = IP('2001:0DB8::CD3/60')

        self.failUnless(r1 == r2)
        #FIXME - this is an interesting case and we aren't handling it
        #        according to RFC4291 at the moment.
        #FIXME: self.failUnless(r1 == r3)

    def testPrefixlenAssignments(self):
        self.failUnlessRaises(ValueError, CIDR, '192.168.0.0/192.168.0.0')
        self.failUnlessRaises(ValueError, CIDR, '0.0.0.0/-1')
        self.failUnlessRaises(ValueError, CIDR, '0.0.0.0/33')
        self.failUnlessRaises(ValueError, CIDR, '::/-1')
        self.failUnlessRaises(ValueError, CIDR, '::/129')

#-----------------------------------------------------------------------------
class TestEUI48Strategy(unittest.TestCase):
    """
    48-bit EUI (MAC) Addr class functionality tests.
    """
    def setUp(self):
        #   Basic address.
        self.size = 48
        self.mac_addr = Addr('00-14-C2-C7-DA-D5')
        self.int_value = 89167223509
        self.hex_value = '0x14c2c7dad5'
        self.bit_value = '00000000-00010100-11000010-' \
                         '11000111-11011010-11010101'

        #   Boundaries.
        self.mac_addr_min = Addr('0:0:0:0:0:0')
        self.mac_addr_max = Addr('ff-ff-ff-ff-ff-ff')
        self.int_min = 0
        self.int_max = 281474976710655
        self.hex_max = '0xffffffffffff'
        self.bit_min = '-'.join(['0'*8 for i in range(6)])
        self.bit_max = '-'.join(['1'*8 for i in range(6)])

    def testBasics(self):
        self.failUnless(len(self.mac_addr) == self.size)
        self.failUnless(int(self.mac_addr) == self.int_value)
        self.failUnless(long(self.mac_addr) == self.int_value)
        self.failUnless(hex(self.mac_addr) == self.hex_value)
        self.failUnless(self.mac_addr.bits() == self.bit_value)

    def testBoundaries(self):
        self.failUnless(int(self.mac_addr_min) == self.int_min)
        self.failUnless(int(self.mac_addr_max) == self.int_max)
        self.failUnless(hex(self.mac_addr_max) == self.hex_max)
        self.failUnless(self.mac_addr_min.bits() == self.bit_min)
        self.failUnless(self.mac_addr_max.bits() == self.bit_max)

    def testBooleanAlgebra(self):
        self.failIf(self.mac_addr_min == self.mac_addr_max)
        self.failUnless(self.mac_addr_min != self.mac_addr_max)

        self.failUnless(self.mac_addr_min <  self.mac_addr_max)
        self.failUnless(self.mac_addr_min <= self.mac_addr_max)
        self.failUnless(self.mac_addr_min != self.mac_addr_max)
        self.failUnless(self.mac_addr_max >  self.mac_addr_min)
        self.failUnless(self.mac_addr_max >= self.mac_addr_min)

    def testEqualityOperations(self):
        #   Different object instance but same intrinsic value.
        self.failUnless(self.mac_addr_min == Addr('0:0:0:0:0:0'))
        self.failUnless(self.mac_addr_max == Addr('ff:ff:ff:ff:ff:ff'))

    def testIncAndDec(self):
        mac_addr_other = Addr('0:0:0:0:0:0')
        self.failUnless(int(mac_addr_other) == 0)
        mac_addr_other += 1
        self.failUnless(int(mac_addr_other) == 1)
        #   Increment it all the way up to the value of a 'real' address.
        mac_addr_other += 89167223508
        self.failUnless(str(mac_addr_other) == str(Addr('00:14:c2:c7:da:d5')))

        #   Roll around boundaries.
        mac_addr_other = Addr('ff:ff:ff:ff:ff:ff')
        mac_addr_other += 1
        self.failUnless(int(mac_addr_other) == self.int_min)
        mac_addr_other -= 1
        self.failUnless(int(mac_addr_other) == self.int_max)

#-----------------------------------------------------------------------------
class Test_Xrange_Generators(unittest.TestCase):

    def test_nrange(self):
        expected = [
            '192.168.0.0',
            '192.168.0.4',
            '192.168.0.8',
            '192.168.0.12',
            '192.168.0.16',
            '192.168.0.20',
            '192.168.0.24',
            '192.168.0.28',
            '192.168.0.32',
        ]

        start_addr = Addr('192.168.0.0')
        stop_addr = Addr('192.168.0.32')
        for i, addr in enumerate(nrange(start_addr, stop_addr, 4)):
            self.failUnless(str(addr) == expected[i])

    def test_xrange_int(self):
        """
        Get integer values back from xrange generator.
        """
        expected_type = int
        expected_list = [0,4,8,12,16]

        saved_list = []
        #   IPv6 addresses auto-detected, as int.
        for addr in nrange('::', '::10', 4, klass=expected_type):
            self.failUnless(type(addr) == expected_type)
            saved_list.append(addr)

        self.failUnless(saved_list == expected_list)

    def test_xrange_int_negative(self):
        """
        Get integer values back from xrange generator.
        """
        expected_type = int
        expected_list = [16,12,8,4,0]

        saved_list = []
        #   IPv6 addresses auto-detected, negative step as int.
        for addr in nrange('::10', '::', -4, klass=expected_type):
            self.failUnless(type(addr) == expected_type)
            saved_list.append(addr)

        self.failUnless(saved_list == expected_list)

    def test_xrange_hex(self):
        """
        Get hex address values back from xrange generator.
        """
        expected_list = [
            '0xff000000000000000000000000000010',
            '0xff00000000000000000000000000000c',
            '0xff000000000000000000000000000008',
            '0xff000000000000000000000000000004',
            '0xff000000000000000000000000000000',
        ]

        saved_list = []
        #   IPv6 addresses auto-detected multicast addresses,
        #   negative step as hex values.
        for addr in nrange('ff00::10', 'ff00::', -4, klass=hex):
            self.failUnless(type(addr) == str)
            saved_list.append(addr.lower().rstrip('l'))

        self.failUnless(saved_list == expected_list)

    def test_xrange_IP_implicit(self):
        """
        Get hex address values back from xrange generator.
        """
        expected_list = [
            '192.168.0.0',
            '192.168.0.128',
            '192.168.1.0',
            '192.168.1.128',
        ]

        saved_list = []
        #   IP class used to initialise generator with IPv4 addresses and a
        #   step of 128 addresses,
        for addr in nrange(IP('192.168.0.0'), IP('192.168.1.255'), 128):
            self.failUnless(isinstance(addr, IP))
            #   Save addresses as string values for comparison.
            saved_list.append(str(addr))

        self.failUnless(saved_list == expected_list)

#-----------------------------------------------------------------------------
class Test_AddrRange(unittest.TestCase):

    def testBasic(self):
        """
        Address ranges now sort as expected based on magnitude.
        """
        ranges = (
            AddrRange(Addr('0-0-0-0-0-0-0-0'), Addr('0-0-0-0-0-0-0-0')),
            AddrRange(Addr('::'), Addr('::')),
            AddrRange(Addr('0-0-0-0-0-0'), Addr('0-0-0-0-0-0')),
            AddrRange(Addr('0.0.0.0'), Addr('255.255.255.255')),
            AddrRange(Addr('0.0.0.0'), Addr('0.0.0.0')),
        )

        expected = [
            '0.0.0.0;0.0.0.0',
            '0.0.0.0;255.255.255.255',
            '::;::',
            '00-00-00-00-00-00;00-00-00-00-00-00',
            '00-00-00-00-00-00-00-00;00-00-00-00-00-00-00-00',
        ]

        self.failUnless([str(r) for r in sorted(ranges)] == expected)

#-----------------------------------------------------------------------------
class Test_CIDR(unittest.TestCase):
    """
    Tests for the CIDR aggregate class.
    """
    def test_IPv4_CIDR_Equality(self):
        cidr1 = CIDR('192.168.0.0/255.255.254.0')
        cidr2 = CIDR('192.168.0.0/23')
        self.failUnless(cidr1 == cidr2)

    def test_CIDR_Loose_Validation(self):
        c = CIDR('192.168.1.65/255.255.254.0', strict_bitmask=False)
        c.klass=str
        self.failUnless(str(c) == '192.168.0.0/23')
        self.failUnless(c[0] == '192.168.0.0')
        self.failUnless(c[-1] == '192.168.1.255')

    def test_CIDR_Strict_Validation(self):
        self.failUnlessRaises(ValueError, CIDR, '192.168.1.65/255.255.254.0')
        self.failUnlessRaises(ValueError, CIDR, '192.168.1.65/23')

    def test_IPv4_Slicing(self):
        expected = [
            ['10.0.0.0/28', '10.0.0.1', '10.0.0.14', 16],
            ['10.0.0.16/28', '10.0.0.17', '10.0.0.30', 16],
            ['10.0.0.32/28', '10.0.0.33', '10.0.0.46', 16],
            ['10.0.0.48/28', '10.0.0.49', '10.0.0.62', 16],
            ['10.0.0.64/28', '10.0.0.65', '10.0.0.78', 16],
            ['10.0.0.80/28', '10.0.0.81', '10.0.0.94', 16],
            ['10.0.0.96/28', '10.0.0.97', '10.0.0.110', 16],
            ['10.0.0.112/28', '10.0.0.113', '10.0.0.126', 16],
            ['10.0.0.128/28', '10.0.0.129', '10.0.0.142', 16],
            ['10.0.0.144/28', '10.0.0.145', '10.0.0.158', 16],
            ['10.0.0.160/28', '10.0.0.161', '10.0.0.174', 16],
            ['10.0.0.176/28', '10.0.0.177', '10.0.0.190', 16],
            ['10.0.0.192/28', '10.0.0.193', '10.0.0.206', 16],
            ['10.0.0.208/28', '10.0.0.209', '10.0.0.222', 16],
            ['10.0.0.224/28', '10.0.0.225', '10.0.0.238', 16],
            ['10.0.0.240/28', '10.0.0.241', '10.0.0.254', 16],
        ]

        supernet = CIDR('10.0.0.0/24')
        subnets = list(addr for addr in supernet)[::16]

        for i, subnet_addr in enumerate(subnets):
            subnet = CIDR("%s/28" % subnet_addr)
            subnet_addrs = list(subnet)
            calculated = [
                str(subnet),
                str(subnet_addrs[1]),
                str(subnet_addrs[-2]),
                len(subnet)
            ]

            self.failUnless(calculated == expected[i],
                "EXPECTED: %r, ACTUAL: %r" % (expected[i], calculated))

    def testIndexingAndSlicing(self):
        #   IPv4
        c1 = CIDR('192.168.0.0/23', klass=str)

        #   Handy methods.
        self.failUnless(c1.first == 3232235520)
        self.failUnless(c1.last == 3232236031)

        #   As above with indices.
        self.failUnless(c1[0] == '192.168.0.0')
        self.failUnless(c1[-1] == '192.168.1.255')

        expected_list = [ '192.168.0.0', '192.168.0.128', '192.168.1.0',
                          '192.168.1.128' ]

        self.failUnless(list(c1[::128]) == expected_list)

        #   IPv6
        c2 = CIDR('fe80::/10', klass=str)
        self.failUnless(c2[0] == 'fe80::')
        self.failUnless(c2[-1] == 'febf:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
        self.failUnless(c2.size() == 332306998946228968225951765070086144)

        #FIXME: IPv6 slicing is currently problematic.
        #FIXME: print list(c2[0:5:1])
        #FIXME: self.failUnless(list(c2[0:5:1]) == ['fe80::', 'fe80::1', 'fe80::2', 'fe80::3', 'fe80::4'])

    def testContains(self):
        self.failUnless('192.168.0.1' in CIDR('192.168.0.0/24'))
        self.failUnless('192.168.0.255' in CIDR('192.168.0.0/24'))
        self.failUnless(CIDR('192.168.0.0/24') in CIDR('192.168.0.0/23'))
        self.failUnless(CIDR('192.168.0.0/24') in CIDR('192.168.0.0/24'))
        self.failUnless('ffff::1' in CIDR('ffff::/127'))
        self.failIf(CIDR('192.168.0.0/23') in CIDR('192.168.0.0/24'))

    def testEquality(self):
        #   IPv4.
        c1 = CIDR('192.168.0.0/24')
        c2 = CIDR('192.168.0.0/24')
        self.failUnless(c1 == c2)
        self.failUnless(c1 is not c2)
        self.failIf(c1 != c2)
        self.failIf(c1 is c2)

        #   IPv6.
        c3 = CIDR('fe80::/10')
        c4 = CIDR('fe80::/10')
        self.failUnless(c1 == c2)
        self.failUnless(c1 is not c2)
        self.failIf(c1 != c2)
        self.failIf(c1 is c2)

    def test_CIDR_abbreviations(self):
        abbreviations = (
            #   Integer values.
            (-1, None),
            (0,   '0.0.0.0/8'),       #   Class A
            (10,  '10.0.0.0/8'),
            (127, '127.0.0.0/8'),
            (128, '128.0.0.0/16'),    #   Class B
            (191, '191.0.0.0/16'),
            (192, '192.0.0.0/24'),    #   Class C
            (223, '223.0.0.0/24'),
            (224, '224.0.0.0/4'),     #   Class D (multicast)
            (225, '225.0.0.0/8'),
            (239, '239.0.0.0/8'),
            (240, '240.0.0.0/32'),    #   Class E (reserved)
            (254, '254.0.0.0/32'),
            (255, '255.0.0.0/32'),
            (256, None),
            #   String values.
            ('-1', None),
            ('0',   '0.0.0.0/8'),       #   Class A
            ('10',  '10.0.0.0/8'),
            ('127', '127.0.0.0/8'),
            ('128', '128.0.0.0/16'),    #   Class B
            ('191', '191.0.0.0/16'),
            ('192', '192.0.0.0/24'),    #   Class C
            ('223', '223.0.0.0/24'),
            ('224', '224.0.0.0/4'),     #   Class D (multicast)
            ('225', '225.0.0.0/8'),
            ('239', '239.0.0.0/8'),
            ('240', '240.0.0.0/32'),    #   Class E (reserved)
            ('254', '254.0.0.0/32'),
            ('255', '255.0.0.0/32'),
            ('256', None),
            ('128/8',       '128.0.0.0/8'),
            ('128.0/8',     '128.0.0.0/8'),
            ('128.0.0.0/8', '128.0.0.0/8'),
            ('128.0.0/8',   '128.0.0.0/8'),
            ('192.168',     '192.168.0.0/24'),
#FIXME:     ('192.168/8',   '192.168.0.0/8'), # Invalid with strict checking!
            ('0.0.0.0',     '0.0.0.0/8'),
            ('::/128',      None),            #   Does not support IPv6.
            ('::10/128',    None),            #   Hmmm... IPv6 proper, not IPv4 mapped.
            ('::/128',      None),            #   Does not support IPv6.
#FIXME:            ('::192.168',   '::192.168.0.0/128'),
#FIXME:            ('::192.168',   '::192.168.0.0/128'),
#FIXME:            ('::ffff:192.168/120', '::ffff:192.168.0.0/120'),
            ('0.0.0.0.0', None),
            ('', None),
            (None, None),
            ([], None),
            ({}, None),
        )

        for (abbrev, expected) in abbreviations:
            result = CIDR.abbrev_to_verbose(abbrev)
            self.failUnless(result == expected, "expected %r, result %r" \
                % (expected, result))
            if result is not None:
                cidr = CIDR(abbrev)
                self.failUnless(str(cidr) == result, "expected %s, result %r" \
                    % (cidr, result))

    def test_CIDR_to_Wildcard(self):
        expected = (
            ('10.0.0.1/32', '10.0.0.1', 1),
            ('192.168.0.0/24', '192.168.0.*', 256),
            ('172.16.0.0/12', '172.16-31.*.*', 1048576),
            ('0.0.0.0/0', '*.*.*.*', 4294967296),
        )

        for cidr, wildcard, size in expected:
            c1 = CIDR(cidr)
            w1 = c1.wildcard()
            c2 = w1.cidr()
            self.failUnless(c1.size() == size)
            self.failUnless(str(c1) == cidr)
            self.failUnless(str(w1) == wildcard)
            self.failUnless(w1.size() == size)
            self.failUnless(c1 == c2)           #   Test __eq__()
            self.failUnless(str(c1) == str(c2)) #   Test __str__() values too.

    def test_cidr_increments(self):
        expected = [
            '192.168.0.0/28',
            '192.168.0.16/28',
            '192.168.0.32/28',
            '192.168.0.48/28',
            '192.168.0.64/28',
            '192.168.0.80/28',
            '192.168.0.96/28',
            '192.168.0.112/28',
            '192.168.0.128/28',
            '192.168.0.144/28',
            '192.168.0.160/28',
            '192.168.0.176/28',
            '192.168.0.192/28',
            '192.168.0.208/28',
            '192.168.0.224/28',
            '192.168.0.240/28',
        ]

        actual = []
        c = CIDR('192.168.0.0/28')
        for i in range(16):
            actual.append(str(c))
            c += 1

        self.failUnless(expected == actual)

    def test_cidr_subtraction(self):
        """
        Subtraction between CIDRs.
        """
        r0 = CIDR('192.168.0.1/32') - CIDR('192.168.0.1/32')
        self.failUnless(r0 == [])

        r1 = CIDR('192.168.0.0/31', klass=str) - CIDR('192.168.0.1/32')
        self.failUnless(r1 == ['192.168.0.0/32'])

        r2 = CIDR('192.168.0.0/24', klass=str) - CIDR('192.168.0.128/25')
        self.failUnless(r2 == ['192.168.0.0/25'])

        r3 = CIDR('192.168.0.0/24', klass=str) - CIDR('192.168.0.128/27')
        self.failUnless(r3 == ['192.168.0.0/25', '192.168.0.160/27', '192.168.0.192/26'])

        #   Subtracting a larger range from a smaller one results in an empty
        #   list (rather than a negative CIDR - which would be rather odd)!
        r4 = CIDR('192.168.0.1/32') - CIDR('192.168.0.0/24')
        self.failUnless(r4 == [])

    def test_CIDR_IP_comparisons(self):
        """
        IPs and CIDRs do not compare favourably (directly), regardless of the
        logical operation being performed.
        """
        #   Logically similar, but fundamentally different at a Python and
        #   netaddr level.
        ip = IP('192.168.0.1')
        cidr = CIDR('192.168.0.1/32')

        #   Direct object to object comparisons will always fail.
        self.failIf(ip == cidr)
        self.failIf(ip != cidr)
        self.failIf(ip > cidr)
        self.failIf(ip >= cidr)
        self.failIf(ip < cidr)
        self.failIf(ip <= cidr)

        #   Compare with CIDR object lower boundary.
        self.failUnless(ip == cidr[0])
        self.failUnless(ip >= cidr[0])
        self.failIf(ip != cidr[0])
        self.failIf(ip > cidr[0])
        self.failIf(ip < cidr[0])
        self.failUnless(ip <= cidr[0])

        #   Compare with CIDR object upper boundary.
        self.failUnless(ip == cidr[-1])
        self.failUnless(ip >= cidr[-1])
        self.failIf(ip != cidr[-1])
        self.failIf(ip > cidr[-1])
        self.failIf(ip < cidr[-1])
        self.failUnless(ip <= cidr[-1])

#-----------------------------------------------------------------------------
class Test_Wildcard(unittest.TestCase):
    """
    Tests for the Wildcard aggregate class.
    """
    def testValidWildcards(self):
        valid_wildcards = (
            ('192.168.0.1', 1),
            ('0.0.0.0', 1),
            ('255.255.255.255', 1),
            ('192.168.0.0-31', 32),
            ('192.168.0.*', 256),
            ('192.168.0-1.*', 512),
            ('192.168-169.*.*', 131072),
            ('*.*.*.*', 4294967296),
        )

        for wildcard, expected_size in valid_wildcards:
            wc = Wildcard(wildcard)
            self.failUnless(wc.size() == expected_size)

    def testInvalidWildcards(self):
        invalid_wildcards = (
            '*.*.*.*.*',
            '*.*.*',
            '*.*',
            '*',
            '192-193.*',
            '192-193.0-1.*.*',
            '192.168.*.0',
            'a.b.c.*',
            [],
            None,
            False,
            True,
        )
        for wildcard in invalid_wildcards:
            self.failUnlessRaises(AddrFormatError, Wildcard, wildcard)

    def test_Wildcard_to_CIDR(self):
        expected = (
            ('10.0.0.1', '10.0.0.1/32', 1),
            ('192.168.0.*', '192.168.0.0/24', 256),
            ('172.16-31.*.*', '172.16.0.0/12', 1048576),
            ('*.*.*.*', '0.0.0.0/0', 4294967296),
        )

        for wildcard, cidr, size in expected:
            w1 = Wildcard(wildcard)
            c1 = w1.cidr()
            w2 = c1.wildcard()
            self.failUnless(w1.size() == size)
            self.failUnless(str(w1) == wildcard)
            self.failUnless(str(c1) == cidr)
            self.failUnless(c1.size() == size)
            self.failUnless(w1 == w2)           #   Test __eq__()
            self.failUnless(str(w1) == str(w2)) #   Test __str__() values too.

    def test_Wilcard_without_CIDR_Equivalent(self):
        """
        Test valid wildcards that cannot be converted to CIDR.
        """
        w1 = Wildcard('10.0.0.5-6')
        self.failUnlessRaises(AddrConversionError, w1.cidr)

    def test_Wildcard_CIDR_comparisons(self):
        """
        Basically CIDRs and Wildcards are subclassed from the same parent so
        should compare favourably.
        """
        cidr1 = CIDR('192.168.0.0/24')
        cidr2 = CIDR('192.168.1.0/24')
        wc1 = Wildcard('192.168.0.*')

        #   Positives.
        self.failUnless(cidr1 == wc1)
        self.failUnless(cidr1 >= wc1)
        self.failUnless(cidr1 <= wc1)
        self.failUnless(cidr2 > wc1)
        self.failUnless(wc1 < cidr2)

        #   Negatives.
        self.failIf(cidr1 != wc1)
        self.failIf(cidr1 > wc1)
        self.failIf(cidr1 < wc1)
        self.failIf(cidr2 <= wc1)
        self.failIf(cidr2 < wc1)
        self.failIf(wc1 >= cidr2)
        self.failIf(wc1 > cidr2)

    def test_Wildcard_IP_comparisons(self):
        """
        IPs and Wildcards current do not compare favourably, regardless of the
        operation.
        """
        #   Logically similar, but fundamentally different at a Python and
        #   netaddr level.
        ip = IP('192.168.0.1')
        wc = Wildcard('192.168.0.1')

        #   Direct object to object comparisons will always fail.
        self.failIf(ip == wc)
        self.failIf(ip != wc)
        self.failIf(ip > wc)
        self.failIf(ip >= wc)
        self.failIf(ip < wc)
        self.failIf(ip <= wc)

        #   Compare with Wildcard object lower boundary.
        self.failUnless(ip == wc[0])
        self.failUnless(ip >= wc[0])
        self.failUnless(ip <= wc[0])
        self.failIf(ip != wc[0])
        self.failIf(ip > wc[0])
        self.failIf(ip < wc[0])

        #   Compare with Wildcard object upper boundary.
        self.failUnless(ip == wc[-1])
        self.failUnless(ip >= wc[-1])
        self.failUnless(ip <= wc[-1])
        self.failIf(ip != wc[-1])
        self.failIf(ip > wc[-1])
        self.failIf(ip < wc[-1])

    def test_wildcard_increments(self):
        expected = [
            '192.168.0.*',
            '192.168.1.*',
            '192.168.2.*',
            '192.168.3.*',
        ]

        actual = []
        wc = Wildcard('192.168.0.*')
        for i in range(4):
            actual.append(str(wc))
            wc += 1

        self.failUnless(expected == actual)

#-----------------------------------------------------------------------------
class Test_IP_DNS(unittest.TestCase):
    def testReverseLookup_IPv4(self):
        expected = '1.0.168.192.in-addr.arpa.'
        ip = IP('192.168.0.1')
        self.failUnless(expected == ip.reverse_dns())

    def testReverseLookup_IPv6(self):
        expected = '1.0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.3.d.c.0.0.0.0.8.b.d.0.1.0.0.2' \
        '.ip6.arpa.'
        ip = IP('2001:0DB8::CD30:0:0:0:101')
        self.failUnless(expected == ip.reverse_dns())

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
