#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
Consolidated set of unit tests for the netaddr module.

Uses TEST-NET references throughout, as described in RFC 3330.

References :-
- RFC3330 Special-Use IPv4 Addresses
"""
from unittest import TestCase, TestLoader, TestSuite, TextTestRunner
import os as _os
import sys as _sys
import platform as _platform
import random as _random

PATH = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), '..'))
_sys.path.insert(0, PATH)

from netaddr import *
import netaddr.strategy

#-----------------------------------------------------------------------------
class LibraryConstantTests(TestCase):
    """Tests on netaddr's constants"""

    def testTypeFlavour(self):
        """AT_* constant tests - types"""
        for constant in (AT_LINK, AT_EUI64, AT_INET, AT_INET6):
            self.assertFalse(callable(constant))        #   not callable.
            self.assertTrue(isinstance(constant, int))  #   are integers.

    def testAddressTypeConstants(self):
        """AT_* constant tests - values"""
        #   MAC/EUI - layer 2.
        self.assertEqual(AT_LINK , 48)
        self.assertEqual(AT_EUI64, 64)

        #   IP - layer 3.
        self.assertEqual(AT_INET , 4)
        self.assertEqual(AT_INET6, 6)

#-----------------------------------------------------------------------------
class AddrStrategyTests(TestCase):
    """Tests on AddrStrategy() objects with various configurations"""

    def testInterfaceWithIPv4(self):
        """AddrStrategy() - interface tests (IPv4 specific)"""
        strategy = netaddr.strategy.AddrStrategy(addr_type=AT_INET,
            width=32,
            word_size=8,
            word_fmt='%d',
            word_sep='.',
            word_base=10)

        b = '11000000.00000000.00000010.00000001'
        i = 3221225985
        t = (192, 0, 2, 1)
        s = '192.0.2.1'
        p = '\xc0\x00\x02\x01'

        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)
        self.assertEqual(strategy.int_to_packed(i), p)

        #   str to x
        self.assertEqual(strategy.str_to_int(s), i)

        #   words to x
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_int(list(t)), i)

        #   packed string to x
        self.assertEqual(strategy.packed_to_int(p), i)

    def testInterfaceWithIPv6(self):
        """AddrStrategy() - interface tests (IPv6 specific)"""
        #
        #   NB - AddrStrategy does not support the compact string
        #   representation of IPv6 addresses. See IPv6Strategy
        #   subclass for an alternative that does this.
        #
        strategy = netaddr.strategy.AddrStrategy(addr_type=AT_INET6,
            width=128,
            word_size=16,
            word_fmt='%x',
            word_sep=':')

        b = '0000000000000000:0000000000000000:0000000000000000:' \
            '0000000000000000:0000000000000000:0000000000000000:' \
            '1111111111111111:1111111111111110'
        i = 4294967294
        t = (0, 0, 0, 0, 0, 0, 0xffff, 0xfffe)
        s = '0:0:0:0:0:0:ffff:fffe'
        p = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xfe'

        self.assertEqual(strategy.int_to_packed(i), p)


        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)

        #   str to x
        self.assertEqual(strategy.str_to_int(s), i)

        #   words to x
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_int(list(t)), i)

        #   packed string to x
        self.assertEqual(strategy.packed_to_int(p), i)

    def testInterfaceWithBasicMAC(self):
        """AddrStrategy() - interface tests (Unix MAC address format)"""
        strategy = netaddr.strategy.AddrStrategy(addr_type=AT_LINK,
            width=48,
            word_size=8,
            word_fmt='%02x',
            word_sep=':')

        b = '00000000:00001111:00011111:00010010:11100111:00110011'
        i = 64945841971
        t = (0x0, 0x0f, 0x1f, 0x12, 0xe7, 0x33)
        s = '00:0f:1f:12:e7:33'
        p = '\x00\x0f\x1f\x12\xe7\x33'

        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)
        self.assertEqual(strategy.int_to_packed(i), p)

        #   str to x
        self.assertEqual(strategy.str_to_int(s), i)

        #   words to x
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_int(list(t)), i)

        #   packed string to x
        self.assertEqual(strategy.packed_to_int(p), i)

    def testInterfaceWithCiscoMAC(self):
        """AddrStrategy() - interface tests (Cisco address format)"""
        strategy = netaddr.strategy.AddrStrategy(addr_type=AT_LINK,
            width=48,
            word_size=16,
            word_fmt='%04x',
            word_sep='.')

        b = '0000000000001111.0001111100010010.1110011100110011'
        i = 64945841971
        t = (0xf, 0x1f12, 0xe733)
        s = '000f.1f12.e733'
        p = '\x00\x0f\x1f\x12\xe7\x33'

        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)
        self.assertEqual(strategy.int_to_packed(i), p)

        #   str to x
        self.assertEqual(strategy.str_to_int(s), i)

        #   words to x
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_int(list(t)), i)

        #   packed string to x
        self.assertEqual(strategy.packed_to_int(p), i)

#-----------------------------------------------------------------------------
class IPv4StrategyTests(TestCase):
    """Tests on IPv4Strategy() class and subclass objects"""

    def testInterface(self):
        """IPv4Strategy() - interface tests"""
        strategy = netaddr.strategy.IPv4Strategy()

        b = '11000000.00000000.00000010.00000001'
        i = 3221225985
        t = (192, 0, 2, 1)
        s = '192.0.2.1'
        p = '\xc0\x00\x02\x01'

        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)
        self.assertEqual(strategy.int_to_packed(i), p)

        #   str to x
        self.assertEqual(strategy.str_to_int(s), i)

        #   words to x
        self.assertEqual(strategy.words_to_int(t), i)

        self.assertEqual(strategy.words_to_int(list(t)), i)

        #   packed string to x
        self.assertEqual(strategy.packed_to_int(p), i)

#-----------------------------------------------------------------------------
class IPv6StrategyTests(TestCase):
    """Tests on IPv6Strategy() objects"""

    def testInterface(self):
        """IPv6Strategy() - interface tests"""
        strategy = netaddr.strategy.IPv6Strategy()

        b = '0010000000000001:0000110110111000:0000000000000000:' \
            '0000000000000000:0000000000000000:0000000000000000:' \
            '0001010000101000:0101011110101011'
        i = 42540766411282592856903984951992014763
        t = (8193, 3512, 0, 0, 0, 0, 5160, 22443)
        s = '2001:db8::1428:57ab'
        p = '\x20\x01\x0d\xb8\x00\x00\x00\x00\x00\x00\x00\x00\x14\x28\x57\xab'

        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)
        self.assertEqual(strategy.int_to_packed(i), p)

        #   str to x
        self.assertEqual(strategy.str_to_int(s), i)

        #   words to x
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_int(list(t)), i)

        #   packed string to x
        self.assertEqual(strategy.packed_to_int(p), i)

        #   IPv6 address variants that are all equivalent.
        ipv6_addr_equals = (
            '2001:0db8:0000:0000:0000:0000:1428:57ab',
            '2001:0db8:0000:0000:0000::1428:57ab',
            '2001:0db8:0:0:0:0:1428:57ab',
            '2001:0db8:0:0::1428:57ab',
            '2001:0db8::1428:57ab',
            #   Upper case.
            '2001:0DB8:0000:0000:0000:0000:1428:57AB',
            '2001:DB8::1428:57AB',
        )

        for ipv6_addr in ipv6_addr_equals:
            self.assertEqual(strategy.str_to_int(ipv6_addr), i)

    def testStringVariantParsing(self):
        """IPv6Strategy() - address variant parsing tests"""
        #   Positive testing.
        valid_addrs = (
            #   RFC 4291
            #   Long forms.
            'FEDC:BA98:7654:3210:FEDC:BA98:7654:3210',
            '1080:0:0:0:8:800:200C:417A',    #   a unicast address
            'FF01:0:0:0:0:0:0:43',      #   a multicast address
            '0:0:0:0:0:0:0:1',          #   the loopback address
            '0:0:0:0:0:0:0:0',          #   the unspecified addresses

            #   Short forms.
            '1080::8:800:200C:417A',    #   a unicast address
            'FF01::43',                 #   a multicast address
            '::1',                      #   the loopback address
            '::',                       #   the unspecified addresses

            #   IPv4 compatible forms.
            '::192.0.2.1',
            '::ffff:192.0.2.1',
            '0:0:0:0:0:0:192.0.2.1',
            '0:0:0:0:0:FFFF:192.0.2.1',
            '0:0:0:0:0:0:13.1.68.3',
            '0:0:0:0:0:FFFF:129.144.52.38',
            '::13.1.68.3',
            '::FFFF:129.144.52.38',

            #   Other tests.
            '1::',
            '::ffff',
            'ffff::',
            'ffff::ffff',
            '0:1:2:3:4:5:6:7',
            '8:9:a:b:c:d:e:f',
            '0:0:0:0:0:0:0:0',
            'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff',
        )

        #   Negative testing.
        invalid_addrs = (
            'g:h:i:j:k:l:m:n',      #   bad chars.
            '0:0:0:0:0:0:0:0:0'     #   too long,
            '',                     #   empty string
            #   Unexpected types.
            [],
            (),
            {},
            True,
            False,
            #   Almost but not quite valid.
#FIXME:            '::fffe:192.0.2.1',
        )

        strategy = netaddr.strategy.ST_IPV6

        for addr in valid_addrs:
            self.assertTrue(strategy.valid_str(addr),
                'Address %r is expected to be valid!' % addr)

        for addr in invalid_addrs:
            self.assertFalse(strategy.valid_str(addr),
                'Address %r is expected to be invalid!' % str(addr))

    def testStringEquivalence(self):
        """IPv6Strategy() - address string compaction tests"""
        #   Positive testing.
        valid_addrs = {
            #   RFC 4291
            'FEDC:BA98:7654:3210:FEDC:BA98:7654:3210' : 'fedc:ba98:7654:3210:fedc:ba98:7654:3210',
            '1080:0:0:0:8:800:200C:417A' : '1080::8:800:200c:417a', #   a unicast address
            'FF01:0:0:0:0:0:0:43' : 'ff01::43', #   a multicast address
            '0:0:0:0:0:0:0:1' : '::1',          #   the loopback address
            '0:0:0:0:0:0:0:0' : '::',           #   the unspecified addresses
        }

        strategy = netaddr.strategy.ST_IPV6

        for long_form, short_form in valid_addrs.items():
            int_val = strategy.str_to_int(long_form)
            calc_short_form = strategy.int_to_str(int_val)
            self.assertEqual(calc_short_form, short_form)

    def testStringPadding(self):
        """IPv6Strategy() - address string padding tests"""
        strategy = netaddr.strategy.ST_IPV6

        addr = 'ffff:ffff::ffff:ffff'
        expected_int = 340282366841710300949110269842519228415

        int_addr = strategy.str_to_int(addr)

        self.assertEqual(int_addr, expected_int)

        self.assertEqual(strategy.int_to_str(int_addr, False), 'ffff:ffff:0:0:0:0:ffff:ffff')

        self.assertEqual(strategy.int_to_str(int_addr), 'ffff:ffff::ffff:ffff')

        words = strategy.int_to_words(int_addr)

        self.assertEqual(words, (65535, 65535, 0, 0, 0, 0, 65535, 65535))
        self.assertEqual(strategy.words_to_int(words), expected_int)

    def testIntegerFormatting(self):
        """IPv6Strategy() - IPv4 integer to string formatting"""
        self.assertEqual(ST_IPV6.int_to_str(0xffff), '::ffff')
        self.assertEqual(ST_IPV6.int_to_str(0xffffff), '::0.255.255.255')
        self.assertEqual(ST_IPV6.int_to_str(0xffffffff),'::255.255.255.255')
        self.assertEqual(ST_IPV6.int_to_str(0x1ffffffff),'::1:ffff:ffff')

        self.assertEqual(
            ST_IPV6.int_to_str(0xffffffffffff), '::ffff:255.255.255.255')

        self.assertEqual(
            ST_IPV6.int_to_str(0xfffeffffffff), '::fffe:ffff:ffff')

        self.assertEqual(
            ST_IPV6.int_to_str(0xffffffffffff), '::ffff:255.255.255.255')

        self.assertEqual(
            ST_IPV6.int_to_str(0xfffffffffff1), '::ffff:255.255.255.241')

        self.assertEqual(
            ST_IPV6.int_to_str(0xfffffffffffe), '::ffff:255.255.255.254')

        self.assertEqual(
            ST_IPV6.int_to_str(0xffffffffff00), '::ffff:255.255.255.0')

        self.assertEqual(
            ST_IPV6.int_to_str(0xffffffff0000), '::ffff:255.255.0.0')

        self.assertEqual(
            ST_IPV6.int_to_str(0xffffff000000), '::ffff:255.0.0.0')

        self.assertEqual(
            ST_IPV6.int_to_str(0xffff000000), '::ff:ff00:0')

        self.assertEqual(
            ST_IPV6.int_to_str(0xffff00000000), '::ffff:0.0.0.0')

        self.assertEqual(
            ST_IPV6.int_to_str(0x1ffff00000000), '::1:ffff:0:0')

        self.assertEqual(
            ST_IPV6.int_to_str(0xffff00000000), '::ffff:0.0.0.0')

#-----------------------------------------------------------------------------
class EUI48StrategyTests(TestCase):
    """Tests on EUI48Strategy() objects"""

    def testInterface(self):
        """EUI48Strategy() - interface tests"""
        strategy = netaddr.strategy.EUI48Strategy()

        b = '00000000-00001111-00011111-00010010-11100111-00110011'
        i = 64945841971
        t = (0x0, 0x0f, 0x1f, 0x12, 0xe7, 0x33)
        s = '00-0F-1F-12-E7-33'

        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)

        #   str to x
        self.assertEqual(strategy.str_to_int(s), i)

        #   words to x
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_int(list(t)), i)

    def testStrategyConfigSettings(self):
        """EUI48Strategy() - interface configuration tests"""
        eui48 = '00-C0-29-C2-52-FF'
        eui48_int = 825334321919

        unix_mac = netaddr.strategy.EUI48Strategy(word_sep=':', word_fmt='%x')

        self.assertEqual(
            unix_mac.int_to_str(eui48_int).lower(), '0:c0:29:c2:52:ff')
        unix_mac.word_sep = '-'
        self.assertEqual(
            unix_mac.int_to_str(eui48_int).lower(), '0-c0-29-c2-52-ff')
        unix_mac.word_fmt = '%.2X'
        self.assertEqual(unix_mac.int_to_str(eui48_int), '00-C0-29-C2-52-FF')

#-----------------------------------------------------------------------------
class PublicStrategyObjectTests(TestCase):
    """Tests on public netaddr Strategy objects"""

    def setUp(self):
        self.strategies = (ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64)

    def testStrategyConstants(self):
        """ST_* constant tests - class membership"""
        #   Are our exported strategy objects based on strategy base class?
        for strategy in self.strategies:
            self.assertTrue(isinstance(strategy, netaddr.strategy.AddrStrategy))

        #   Are our strategy objects customised as expected?
        self.assertTrue(isinstance(ST_EUI48, netaddr.strategy.EUI48Strategy))

        self.assertTrue(
            isinstance(ST_IPV4, netaddr.strategy.IPv4Strategy))

        self.assertTrue(
            isinstance(ST_IPV6, netaddr.strategy.IPv6Strategy))

    def testProperties(self):
        """ST_* objects interface check - properties"""
        expected_properties = (
            'addr_type',
            'max_int',
            'max_word',
            'name',
            'num_words',
            'width',
            'word_base',
            'word_fmt',
            'word_sep',
            'word_size',
        )

        for strategy in self.strategies:
            for attribute in expected_properties:
                self.assertTrue(hasattr(strategy, attribute),
                    '%r missing' % attribute)
                self.assertFalse(callable(eval('strategy.%s' % attribute)))

    def testMethods(self):
        """ST_* objects interface check - methods"""
        expected_methods = (
            'bits_to_int',
            #   'int_to_arpa',  #ST_IP* only.
            'int_to_bin',
            'int_to_bits',
            'int_to_packed',
            'int_to_str',
            'int_to_words',
            'packed_to_int',
            'str_to_int',
            'valid_bits',
            'valid_int',
            'valid_str',
            'valid_words',
            'words_to_int',
        )

        for strategy in self.strategies:
            for attribute in expected_methods:
                self.assertTrue(hasattr(strategy, attribute), '%r' % attribute)
                self.assertTrue(callable(eval('strategy.%s' % attribute)))

    def testIPInteface(self):
        """IP specific strategy interface checks"""
        for strategy in (ST_IPV4, ST_IPV6):
            self.assertTrue(hasattr(strategy, 'int_to_arpa'))

#-----------------------------------------------------------------------------
class AddrTests(TestCase):
    """Tests on Addr() objects for all supported address types"""

    def testExceptionRaising(self):
        """Addr() - invalid constructor argument tests"""
        for addr in ('', [], {}, None, 5.2, -1, 'abc.def.ghi.jkl', '::z'):
            self.assertRaises(AddrFormatError, netaddr.address.Addr, addr)

    def testAssignments(self):
        """Addr() - strategy and address type assignment tests"""
        addr = netaddr.address.Addr('0.0.0.0')
        self.assertEqual(addr.value, 0)
        self.assertEqual(addr.addr_type, AT_INET)
        self.assertEqual(addr.strategy, ST_IPV4)

        #   Test addr_type assignment.
        addr.addr_type = AT_INET6
        self.assertEqual(addr.addr_type, AT_INET6)
        self.assertEqual(addr.strategy, ST_IPV6)

        #   Test strategy assignment.
        addr.strategy = ST_EUI48
        self.assertEqual(addr.addr_type, AT_LINK)
        self.assertEqual(addr.strategy, ST_EUI48)

        addr.strategy = ST_EUI64
        self.assertEqual(addr.addr_type, AT_EUI64)
        self.assertEqual(addr.strategy, ST_EUI64)

        #   Test value assignment.
        addr.addr_type = AT_INET
        addr.value = '192.0.2.1'
        self.assertEqual(addr.value, 3221225985)
        self.assertEqual(addr.addr_type, AT_INET)
        self.assertEqual(addr.strategy, ST_IPV4)

    #---------------------
    #   *** IPv4 tests ***
    #---------------------

    def testRepresentationsIPv4(self):
        """Addr() - address representation tests (IPv4)"""
        width = 32
        addr = netaddr.address.Addr('192.0.2.1')
        octets = (192, 0, 2, 1)
        int_val = 3221225985
        hex_val = '0xc0000201'
        bit_repr = '11000000.00000000.00000010.00000001'

        self.assertEqual(len(addr), width)
        self.assertEqual(addr[0], octets[0])
        self.assertEqual(tuple(addr), octets)
        self.assertEqual(int(addr), int_val)
        self.assertEqual(long(addr), int_val)
        self.assertEqual(hex(addr), hex_val)
        self.assertEqual(addr.bits(), bit_repr)

    def testBoundariesIPv4(self):
        """Addr() - boundary tests (IPv4)"""
        addr_min = netaddr.address.Addr('0.0.0.0')
        addr_max = netaddr.address.Addr('255.255.255.255')
        min_val_int = 0
        max_val_int = 4294967295
        max_val_hex = '0xffffffff'
        min_bit_repr = '.'.join(['0'*8 for i in range(4)])
        max_bit_repr = '.'.join(['1'*8 for i in range(4)])
        min_val_octets = (0, 0, 0, 0)
        max_val_octets = (255, 255, 255, 255)

        self.assertEqual(int(addr_min), min_val_int)
        self.assertEqual(int(addr_max), max_val_int)
        self.assertEqual(hex(addr_max), max_val_hex)
        self.assertEqual(addr_min.bits(), min_bit_repr)
        self.assertEqual(addr_max.bits(), max_bit_repr)

        #   Addr indexing tests - addr[x].
        self.assertEqual(tuple(addr_min), min_val_octets)
        self.assertEqual(tuple(addr_max), max_val_octets)
        self.assertEqual(list(addr_min), list(min_val_octets))
        self.assertEqual(list(addr_max), list(max_val_octets))

    def testIterationIPv4(self):
        """Addr() - iteration tests (IPv4)"""
        addr = netaddr.address.Addr('192.0.2.1')
        hex_bytes = ['0xc0', '0x0', '0x2', '0x1']
        self.assertEqual([hex(i) for i in addr], hex_bytes)

    def testIndexingAndSlicingIPv4(self):
        """Addr() - indexing and slicing tests (IPv4)"""
        addr = netaddr.address.Addr('192.0.2.1')

        # using __getitem__()
        self.assertEqual(addr[0], 192)
        self.assertEqual(addr[1], 0)
        self.assertEqual(addr[2], 2)
        self.assertEqual(addr[3], 1)

        addr[3] = 2                     # using __setitem__()
        self.assertEqual(addr[3], 2)    # basic index
        self.assertEqual(addr[-4], 192) # negative index

        #   Slicing, oh yeah!
        self.assertEqual(addr[0:2], [192, 0])          # basic slice
        self.assertEqual(addr[0:4:2], [192, 2])          # slice with step
        self.assertEqual(addr[-1::-1], [2, 2, 0, 192]) # negative index

    def testBooleanAlgebraIPv4(self):
        """Addr() - boolean operator tests (IPv4)"""
        addr_min = netaddr.address.Addr('0.0.0.0')
        addr_max = netaddr.address.Addr('255.255.255.255')

        self.assertFalse(addr_min == addr_max)
        self.assertTrue(addr_min != addr_max)
        self.assertTrue(addr_min <  addr_max)
        self.assertTrue(addr_min <= addr_max)
        self.assertTrue(addr_min != addr_max)
        self.assertTrue(addr_max >  addr_min)
        self.assertTrue(addr_max >= addr_min)

        self.assertTrue(IP('127.1') != 'foo')
        self.assertFalse(IP('127.1') != IP('127.1'))
        self.assertTrue(IP('127.1') == IP('127.1'))
        self.assertFalse(IP('127.1') == 2130706433)
        self.assertTrue(IP('127.1') == IP(2130706433))
        self.assertFalse(IP('127.1') == '127.1')

    def testIncrementAndDecrementIPv4(self):
        """Addr() - increment and decrement tests (IPv4)"""
        addr = netaddr.address.Addr('0.0.0.0')
        self.assertEqual(int(addr), 0)
        addr += 1
        self.assertEqual(int(addr), 1)
        #   Increment it all the way up to the value of a 'real' address.
        addr += 3221225984
        self.assertEqual(str(addr), str(netaddr.address.Addr('192.0.2.1')))

        #   Roll around boundaries.
        addr = netaddr.address.Addr('255.255.255.255')
        addr += 1
        self.assertEqual(int(addr), 0)
        addr -= 1
        self.assertEqual(int(addr), 0xffffffff)

    #---------------------
    #   *** IPv6 tests ***
    #---------------------

    def testAssignmentsIPv6(self):
        """Addr() - assignment tests (IPv6)"""
        ip_addr = netaddr.address.Addr(0, AT_INET6)
        ip_addr.value = 0xffffc0a80001
        self.assertEqual(str(ip_addr), '::ffff:192.168.0.1')

    def testIPv6AddressCompression(self):
        """Addr() - test IPv6 '::' compression algorithm"""
        #   Checked against socket.inet_ntop() on Linux (not available on Windows)
        self.assertEqual(str(netaddr.address.Addr('0:0:0:0:0:0:0:0')), '::')
        self.assertEqual(str(netaddr.address.Addr('0:0:0:0:0:0:0:A')), '::a')
        self.assertEqual(str(netaddr.address.Addr('A:0:0:0:0:0:0:0')), 'a::')
        self.assertEqual(str(netaddr.address.Addr('A:0:A:0:0:0:0:0')), 'a:0:a::')
        self.assertEqual(str(netaddr.address.Addr('A:0:0:0:0:0:0:A')), 'a::a')
        self.assertEqual(str(netaddr.address.Addr('0:A:0:0:0:0:0:A')), '0:a::a')
        self.assertEqual(str(netaddr.address.Addr('A:0:A:0:0:0:0:A')), 'a:0:a::a')
        self.assertEqual(str(netaddr.address.Addr('0:0:0:A:0:0:0:A')), '::a:0:0:0:a')
        self.assertEqual(str(netaddr.address.Addr('0:0:0:0:A:0:0:A')), '::a:0:0:a')
        self.assertEqual(str(netaddr.address.Addr('A:0:0:0:0:A:0:A')), 'a::a:0:a')
        self.assertEqual(str(netaddr.address.Addr('A:0:0:A:0:0:A:0')), 'a::a:0:0:a:0')
        self.assertEqual(str(netaddr.address.Addr('A:0:A:0:A:0:A:0')), 'a:0:a:0:a:0:a:0')
        self.assertEqual(str(netaddr.address.Addr('0:A:0:A:0:A:0:A')), '0:a:0:a:0:a:0:a')
        self.assertEqual(str(netaddr.address.Addr('1080:0:0:0:8:800:200C:417A')), '1080::8:800:200c:417a')
        self.assertEqual(str(netaddr.address.Addr('FEDC:BA98:7654:3210:FEDC:BA98:7654:3210')), 'fedc:ba98:7654:3210:fedc:ba98:7654:3210')


    def testValidityIPv6(self):
        """Addr() - basic validity tests (IPv6)"""
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
            self.assertTrue(ST_IPV6.valid_str(addr))

    def testRepresentationsIPv6(self):
        """Addr() - address representation tests (IPv6)"""
        width = 128
        addr = netaddr.address.Addr('::ffff:c0a8:1')
        int_val = 281473913978881
        hex_val = '0xffffc0a80001'
        words = (0, 0, 0, 0, 0, 65535, 49320, 1)
        bit_repr = '0000000000000000:0000000000000000:0000000000000000:' \
                   '0000000000000000:0000000000000000:1111111111111111:' \
                   '1100000010101000:0000000000000001'

        self.assertEqual(len(addr), width)
        self.assertEqual(addr[0], words[0])
        self.assertEqual(tuple(addr), words)
        self.assertEqual(int(addr), int_val)
        self.assertEqual(long(addr), int_val)
        self.assertEqual(hex(addr), hex_val)
        self.assertEqual(addr.bits(), bit_repr)

    def testBoundariesIPv6(self):
        """Addr() - boundary tests (IPv6)"""
        addr_min = netaddr.address.Addr('::')
        addr_max = netaddr.address.Addr('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
        min_val_int = 0
        max_val_int = 340282366920938463463374607431768211455
        max_val_hex = '0xffffffffffffffffffffffffffffffff'
        min_bit_repr = ':'.join(['0'*16 for i in range(8)])
        max_bit_repr = ':'.join(['1'*16 for i in range(8)])
        min_val_words = (0, 0, 0, 0, 0, 0, 0, 0)
        max_val_words = (65535, 65535, 65535, 65535, 65535, 65535, 65535, 65535)

        self.assertEqual(int(addr_min), min_val_int)
        self.assertEqual(int(addr_max), max_val_int)
        self.assertEqual(hex(addr_max), max_val_hex)
        self.assertEqual(addr_min.bits(), min_bit_repr)
        self.assertEqual(addr_max.bits(), max_bit_repr)
        #   Addr indexing tests - addr[x].
        self.assertEqual(tuple(addr_min), min_val_words)
        self.assertEqual(tuple(addr_max), max_val_words)
        self.assertEqual(list(addr_min), list(min_val_words))
        self.assertEqual(list(addr_max), list(max_val_words))

    def testIterationIPv6(self):
        """Addr() - iteration tests (IPv6)"""
        #TODO! - see method testIterationIPv4() for example.
        pass

    def testIndexingAndSlicingIPv6(self):
        """Addr() - indexing and slicing tests (IPv6)"""
        #TODO! - see method testIndexingAndSlicingIPv4() for example.
        pass

    def testBooleanAlgebraIPv6(self):
        """Addr() - boolean operator tests (IPv6)"""
        addr_min = netaddr.address.Addr('::')
        addr_max = netaddr.address.Addr('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')

        self.assertFalse(addr_min == addr_max)
        self.assertTrue(addr_min != addr_max)
        self.assertTrue(addr_min <  addr_max)
        self.assertTrue(addr_min <= addr_max)
        self.assertTrue(addr_min != addr_max)
        self.assertTrue(addr_max >  addr_min)
        self.assertTrue(addr_max >= addr_min)

    def testIncrementAndDecrementIPv6(self):
        """Addr() - increment and decrement tests (IPv6)"""
        addr = netaddr.address.Addr('::')
        self.assertEqual(int(addr), 0)
        addr += 1
        self.assertEqual(int(addr), 1)
        #   Increment it all the way up to the value of a 'real' address.
        addr += 281473913978880
        self.assertEqual(str(addr), str(netaddr.address.Addr('::ffff:c0a8:1')))

        #   Roll around boundaries.
        addr = netaddr.address.Addr('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
        addr += 1
        self.assertEqual(int(addr), 0)
        addr -= 1
        self.assertEqual(int(addr), 0xffffffffffffffffffffffffffffffff)

    #---------------------
    #   *** EUI tests ***
    #---------------------

    def testRepresentationsEUI(self):
        """Addr() - address representation tests (EUI)"""
        width = 48
        addr = netaddr.address.Addr('00-14-C2-C7-DA-D5')
        int_val = 89167223509
        hex_val = '0x14c2c7dad5'
        bit_repr = '00000000-00010100-11000010-11000111-11011010-11010101'

        self.assertEqual(len(addr), width)
        self.assertEqual(int(addr), int_val)
        self.assertEqual(long(addr), int_val)
        self.assertEqual(hex(addr), hex_val)
        self.assertEqual(addr.bits(), bit_repr)

    def testBoundariesEUI(self):
        """Addr() - boundary tests (EUI)"""
        addr_min = netaddr.address.Addr('0:0:0:0:0:0')
        addr_max = netaddr.address.Addr('ff-ff-ff-ff-ff-ff')
        min_val_int = 0
        max_val_int = 281474976710655
        max_val_hex = '0xffffffffffff'
        min_bit_repr = '-'.join(['0'*8 for i in range(6)])
        max_bit_repr = '-'.join(['1'*8 for i in range(6)])

        self.assertEqual(int(addr_min), min_val_int)
        self.assertEqual(int(addr_max), max_val_int)
        self.assertEqual(hex(addr_max), max_val_hex)
        self.assertEqual(addr_min.bits(), min_bit_repr)
        self.assertEqual(addr_max.bits(), max_bit_repr)

#-----------------------------------------------------------------------------
class EUITests(TestCase):
    """Tests on EUI() objects"""

    def testProperties(self):
        """EUI() - class interface check (properties)"""
        expected_properties = (
            'ADDR_TYPES',
            'STRATEGIES',
            'addr_type',
            'strategy',
            'value',
        )

        for attribute in expected_properties:
            self.assertTrue(hasattr(EUI, attribute))
            self.assertFalse(callable(eval('EUI.%s' % attribute)))


    def testMethods(self):
        """EUI() - class interface check (methods)"""
        expected_methods = (
            'bits',
            'ei',
            'eui64',
            'iab',
            'info',
            'ipv6_link_local',
            'isiab',
            'oui',
        )

        for attribute in expected_methods:
            self.assertTrue(hasattr(EUI, attribute))
            self.assertTrue(callable(eval('EUI.%s' % attribute)))

    def testEUI48(self):
        """EUI() basic tests (MAC, EUI-48)"""
        mac = EUI('00:C0:29:C2:52:FF')
        self.assertEqual(str(mac), '00-C0-29-C2-52-FF')
        self.assertEqual(mac.oui(str), '00-C0-29')
        self.assertEqual(mac.ei(), 'C2-52-FF')
        self.assertEqual(mac.eui64(), EUI('00-C0-29-FF-FE-C2-52-FF'))

    def testEUI64(self):
        """EUI() basic tests (EUI-64)"""
        eui64 = EUI('00-C0-29-FF-FE-C2-52-FF')
        self.assertEqual(str(eui64), '00-C0-29-FF-FE-C2-52-FF')
        self.assertEqual(eui64.oui(str), '00-C0-29')
        self.assertEqual(eui64.ei(), 'FF-FE-C2-52-FF')
        self.assertEqual(eui64.eui64(), EUI('00-C0-29-FF-FE-C2-52-FF'))

    def testIPv6LinkLocal(self):
        """EUI() IPv6 translation"""
        expected = 'fe80::20f:1fff:fe12:e733'

        mac = EUI('00-0F-1F-12-E7-33')
        ip1 = mac.ipv6_link_local()
        self.assertEqual(str(ip1), expected)
        self.assertEqual(ip1, IP(expected))

        eui64 = EUI('00-0F-1F-FF-FE-12-E7-33')
        ip2 = eui64.ipv6_link_local()
        self.assertEqual(str(ip2), expected)
        self.assertEqual(ip2, IP(expected))

    def testOUIFormatting(self):
        """EUI() OUI format tests"""
        mac = EUI('aa:bb:cc:dd:ee:ff')
        self.assertFalse(mac.isiab())
        self.assertEqual(mac.oui(str), 'AA-BB-CC')
        self.assertEqual(mac.iab(str), None)
        self.assertEqual(mac.ei(), 'DD-EE-FF')
        self.assertEqual(mac.oui(int), 0xaabbcc)
        self.assertEqual(mac.iab(int), None)

    def testIAB(self):
        """EUI() IAB tests"""
        lower_eui = EUI('00-50-C2-05-C0-00')
        upper_eui = EUI('00-50-C2-05-CF-FF')

        self.assertTrue(lower_eui.isiab())
        self.assertEqual(lower_eui.oui(str), '00-50-C2')
        self.assertEqual(lower_eui.iab(str), '00-50-C2-05-C0-00')
        self.assertEqual(lower_eui.ei(), '05-C0-00')
        self.assertEqual(lower_eui.oui(int), 0x0050c2)
        self.assertEqual(lower_eui.iab(int), 0x0050c205c)

        self.assertTrue(upper_eui.isiab())
        self.assertEqual(upper_eui.oui(str), '00-50-C2')
        self.assertEqual(upper_eui.iab(str), '00-50-C2-05-C0-00')
        self.assertEqual(upper_eui.ei(), '05-CF-FF')
        self.assertEqual(upper_eui.oui(int), 0x0050c2)
        self.assertEqual(upper_eui.iab(int), 0x0050c205c)

    def testMultipleMACFormats(self):
        """EUI() multi-format MAC constructor tests"""
        eui = EUI('00-90-96-AF-CC-39')
        self.assertEqual(eui, EUI('0-90-96-AF-CC-39'))
        self.assertEqual(eui, EUI('00-90-96-af-cc-39'))
        self.assertEqual(eui, EUI('00:90:96:AF:CC:39'))
        self.assertEqual(eui, EUI('00:90:96:af:cc:39'))
        self.assertEqual(eui, EUI('0090-96AF-CC39'))
        self.assertEqual(eui, EUI('0090:96af:cc39'))
        self.assertEqual(eui, EUI('009096-AFCC39'))
        self.assertEqual(eui, EUI('009096:AFCC39'))
        self.assertEqual(eui, EUI('009096AFCC39'))
        self.assertEqual(eui, EUI('009096afcc39'))

        self.assertEqual(EUI('01-00-00-00-00-00'), EUI('010000000000'))
        self.assertEqual(EUI('01-00-00-00-00-00'), EUI('10000000000'))

        self.assertEqual(EUI('01-00-00-01-00-00'), EUI('010000:010000'))
        self.assertEqual(EUI('01-00-00-01-00-00'), EUI('10000:10000'))

#-----------------------------------------------------------------------------
class OUITests(TestCase):
    """Tests on OUI() objects"""

    def testProperties(self):
        """OUI() - class interface check (properties)"""
        expected_properties = (
            #   None of interest (yet).
        )

        for attribute in expected_properties:
            self.assertTrue(hasattr(OUI, attribute))
            self.assertFalse(callable(eval('OUI.%s' % attribute)))


    def testMethods(self):
        """OUI() - class interface check (methods)"""
        expected_methods = (
            'address',
            'org',
            'org_count',
            'organisation',
            'registration',
        )

        for attribute in expected_methods:
            self.assertTrue(hasattr(OUI, attribute))
            self.assertTrue(callable(eval('OUI.%s' % attribute)))

#-----------------------------------------------------------------------------
class IABTests(TestCase):
    """Tests on IAB() objects"""

    def testProperties(self):
        """IAB() - class interface check (properties)"""
        expected_properties = (
            #   None of interest (yet).
        )

        for attribute in expected_properties:
            self.assertTrue(hasattr(IAB, attribute))
            self.assertFalse(callable(eval('IAB.%s' % attribute)))


    def testMethods(self):
        """IAB() - class interface check (methods)"""
        expected_methods = (
            'address',
            'org',
            'organisation',
            'registration',
            'split_iab_mac',
        )

        for attribute in expected_methods:
            self.assertTrue(hasattr(IAB, attribute))
            self.assertTrue(callable(eval('IAB.%s' % attribute)))

#-----------------------------------------------------------------------------
class IPTests(TestCase):
    """Tests on IP() objects"""

    def testProperties(self):
        """IP() - class interface check (properties)"""
        expected_properties = (
            'ADDR_TYPES',
            'STRATEGIES',
            'TRANSLATE_STR',    #   This must go in 0.7!
            'addr_type',
            'prefixlen',
            'strategy',
            'value',
        )

        for attribute in expected_properties:
            self.assertTrue(hasattr(IP, attribute))
            self.assertFalse(callable(eval('IP.%s' % attribute)))

    def testMethods(self):
        """IP() - class interface check (methods)"""
        expected_methods = (
            'bits',
            'cidr',
            'hostname',
            'info',
            'iprange',
            'ipv4',
            'ipv6',
            'is_hostmask',
            'is_ipv4_compat',
            'is_ipv4_mapped',
            'is_link_local',
            'is_loopback',
            'is_multicast',
            'is_netmask',
            'is_private',
            'is_reserved',
            'is_unicast',
            'netmask_bits',
            'reverse_dns',
            'ipglob',
        )

        for attribute in expected_methods:
            self.assertTrue(hasattr(IP, attribute))
            self.assertTrue(callable(eval('IP.%s' % attribute)))

    def testEdgeCases(self):
        """IP() - edge case string tests"""
        #   Turns out IPv4 has representation (string) formats that are both
        #   interesting and esoteric. We shall support them for completeness
        #   using socket.inet_aton where it is available.

        #   Mixture of hex and integer octet values...
        self.assertTrue(str(IP('127.1')), '127.0.0.1')
        self.assertTrue(str(IP('0x7f.1')), '127.0.0.1')
        self.assertTrue(str(IP('0x7f.0.0.1')), '127.0.0.1')
        self.assertTrue(str(IP('0x7f.0x0.0x0.0x1')), '127.0.0.1')

        #   Host count based addressing.
        self.assertTrue(str(IP('127')), '0.0.0.127')
        self.assertTrue(str(IP('127')), '0.0.0.127')

        if _platform.system() != 'Windows':
            #   We are on Windows that has a notorious bug. We aren't even
            #   going to attempt to test it.
            self.assertTrue(str(IP(str(0xffffffff))), '255.255.255.255')

    def testRFC4291WithIP(self):
        """IP() - RFC 4291 tests"""
        expected = '2001:db8:0:cd30::'

        actual = str(IP('2001:0DB8:0000:CD30:0000:0000:0000:0000/60'))
        self.assertEqual(actual, expected)

        actual = str(IP('2001:0DB8::CD30:0:0:0:0/60'))
        self.assertEqual(actual, expected)

        actual = str(IP('2001:0DB8:0:CD30::/60'))
        self.assertEqual(actual, expected)

    def testAssignmentsIPv4(self):
        """IP() - managed attribute assignment tests (IPv4)"""
        ip = IP('192.0.2.1')
        self.assertEqual(ip.value, 3221225985)
        self.assertEqual(ip.addr_type, AT_INET)
        self.assertEqual(ip.strategy, ST_IPV4)
        self.assertEqual(ip.prefixlen, 32)

        #   Disabled test below as there are seemingly too many variations of
        #   localhost across operating systems (wtf)?
        #DISABLED:   self.assertEqual(IP('127.0.0.1').hostname(), 'localhost')

        #   Prefix /32 for IPv4 addresses should be implicit.
        self.assertEqual(repr(ip), "IP('192.0.2.1')")
        ip.prefixlen = 24
        self.assertEqual(repr(ip), "IP('192.0.2.1/24')")

        self.assertRaises(ValueError, IP, '0.0.0.0/-1')
        self.assertRaises(ValueError, IP, '0.0.0.0/33')

    def testAssignmentsIPv6(self):
        """IP() - managed attribute assignment tests (IPv6)"""
        ip = IP('fe80::4472:4b4a:616d')
        self.assertEqual(ip.value, 338288524927261089654018972099027820909)
        self.assertEqual(ip.addr_type, AT_INET6)
        self.assertEqual(ip.strategy, ST_IPV6)
        self.assertEqual(ip.prefixlen, 128)

        #   Prefix /128 for IPv6 addresses should be implicit.
        self.assertEqual(repr(ip), "IP('fe80::4472:4b4a:616d')")
        ip.prefixlen = 64
        self.assertEqual(repr(ip), "IP('fe80::4472:4b4a:616d/64')")

        #   Check IPv4 mapped IPv6.
        self.assertEqual(hex(IP('::ffff:10.11.12.13')), '0xffff0a0b0c0d')
        self.assertEqual(hex(IP('::10.11.12.13')), hex(IP('10.11.12.13')))

        self.assertRaises(ValueError, IP, '::/-1')
        self.assertRaises(ValueError, IP, '::/129')

    def testIPv4CompatibleIP6(self):
        """IP() - IPv4 compatible IPv6 address conversions"""
        expected = {
            '::0.0.0.0' : '::',
            '::0.0.1.0' : '::100',
            '::0.0.1.1' : '::101',
            '::0.0.255.255' : '::ffff',
            '::0.1.0.0' : '::0.1.0.0',
            '::0.1.255.255' : '::0.1.255.255',
            '::255.255.255.255' : '::255.255.255.255',
        }

        for value, expected in expected.items():
            self.assertEqual(str(IP(value)), expected)

    def testIPv4MappedIP6(self):
        """IP() - IPv4 mapped IPv6 address conversions"""
        expected = {
            '::ffff:0.1.0.0' : '::ffff:0.1.0.0',
            '::ffff:0.0.0.0' : '::ffff:0.0.0.0',
            '::ffff:255.255.255.255' : '::ffff:255.255.255.255',
            '::ffff:0' : '::255.255.0.0',
            '::ffff:ffff' : '::255.255.255.255',
            '::ffff:ffff:ffff' : '::ffff:255.255.255.255',
            '::ffff:ffff' : '::255.255.255.255',
            '::ffff:ffff:ffff' : '::ffff:255.255.255.255',
            '::ffff:0:0' : '::ffff:0.0.0.0',
        }

        for value, expected in expected.items():
            self.assertEqual(str(IP(value)), expected)

    def testNetmaskIPv4(self):
        """IP() - netmask tests (IPv4)"""
        addr = IP('192.0.2.1')
        self.assertFalse(addr.is_netmask())

        netmask = IP('255.255.254.0')
        self.assertTrue(netmask.is_netmask())

        #   Apply subnet mask
        network_id = IP(int(addr) & int(netmask), AT_INET)
        self.assertEqual(str(network_id), '192.0.2.0')

    def testNetmaskAndPrefixlenIPv4(self):
        """IP() - netmask and CIDR prefix tests (IPv4)"""
        calculated = []

        #   Generate a bunch of addresses and see which ones are netmasks.
        for ip in nrange('255.255.255.255', '255.255.255.0',-1, fmt=IP):
            if ip.is_netmask():
                calculated.append((str(ip), ip.netmask_bits()))

        expected = [
            ('255.255.255.255', 32),
            ('255.255.255.254', 31),
            ('255.255.255.252', 30),
            ('255.255.255.248', 29),
            ('255.255.255.240', 28),
            ('255.255.255.224', 27),
            ('255.255.255.192', 26),
            ('255.255.255.128', 25),
            ('255.255.255.0', 24),
        ]

        self.assertEqual(calculated, expected)

    def testHostmaskIPv4(self):
        """IP() - hostmask tests (IPv4)"""
        calculated = []

        #   Generate a bunch of addresses and see which ones are hostmasks.
        for ip in nrange('0.0.0.0', '0.0.0.255', fmt=IP):
            if ip.is_hostmask():
                calculated.append(str(ip))

        expected = [
            '0.0.0.0',
            '0.0.0.1',
            '0.0.0.3',
            '0.0.0.7',
            '0.0.0.15',
            '0.0.0.31',
            '0.0.0.63',
            '0.0.0.127',
            '0.0.0.255',
        ]

        self.assertEqual(calculated, expected)

    def testNetmaskAndPrefixlenIPv6(self):
        """IP() - netmask and CIDR prefix tests (IPv6)"""
        calculated = []

        #   Generate a bunch of addresses and see which ones are netmasks.
        for ip in nrange('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff',
                         'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ff00',-1, fmt=IP):
            if ip.is_netmask():
                calculated.append((str(ip), ip.netmask_bits()))

        expected = [
            ('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff', 128),
            ('ffff:ffff:ffff:ffff:ffff:ffff:ffff:fffe', 127),
            ('ffff:ffff:ffff:ffff:ffff:ffff:ffff:fffc', 126),
            ('ffff:ffff:ffff:ffff:ffff:ffff:ffff:fff8', 125),
            ('ffff:ffff:ffff:ffff:ffff:ffff:ffff:fff0', 124),
            ('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffe0', 123),
            ('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffc0', 122),
            ('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ff80', 121),
            ('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ff00', 120),
        ]

        self.assertEqual(calculated, expected)

    def testHostmaskIPv6(self):
        """IP() - hostmask tests (IPv6)"""
        calculated = []

        #   Generate a bunch of addresses and see which ones are hostmasks.
        for ip in nrange('::', '::ff', fmt=IP):
            if ip.is_hostmask():
                calculated.append(str(ip))

        expected = [
            '::',
            '::1',
            '::3',
            '::7',
            '::f',
            '::1f',
            '::3f',
            '::7f',
            '::ff',
        ]

        self.assertEqual(calculated, expected)

    def testConstructorExceptions(self):
        """IP() - constructor Exception tests"""

        #   No arguments passed to constructor.
        self.assertRaises(TypeError, IP)

        #   Various bad types for address values.
        for bad_addr in (None, [], {}, 4.2):
            self.assertRaises(AddrFormatError, IP, bad_addr)

        #   Various bad types for addr_type values.
        for bad_addr_type in ('', None, [], {}, 4.2):
            self.assertRaises(ValueError, IP, '0.0.0.0', bad_addr_type)

        #   Wrong explicit address type for a valid address.
        self.assertRaises(Exception, IP, '0.0.0.0', 6)
        self.assertRaises(Exception, IP, '::', 4)

    def testFormattingIPv6(self):
        """IP() - formatting options for IPv6"""
        self.assertEqual(
            ST_IPV6.int_to_str(0, compact=False, word_fmt='%04x'),
            '0000:0000:0000:0000:0000:0000:0000:0000')
        self.assertEqual(ST_IPV6.int_to_str(0, compact=True), '::')
        self.assertEqual(ST_IPV6.int_to_arpa(0), '0.'*32 + 'ip6.arpa.')

    def testReverseLookupIPv4(self):
        """IP() - reverse DNS lookup test (IPv4)"""
        expected = '1.2.0.192.in-addr.arpa.'
        ip = IP('192.0.2.1')
        self.assertEqual(expected, ip.reverse_dns())

    def testReverseLookupIPv6(self):
        """IP() - reverse DNS lookup test (IPv6)"""
        expected = '1.0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.3.d.c.0.0.0.0.8.b.d.0.1.0.0.2' \
        '.ip6.arpa.'
        ip = IP('2001:0DB8::CD30:0:0:0:101')
        self.assertEqual(expected, ip.reverse_dns())

    def testMembership(self):
        """IP() - address class tests (IPv6)"""
        self.assertTrue(IP('::ffff:192.0.2.1').is_ipv4_mapped())
        self.assertFalse(IP('::192.0.2.1').is_ipv4_mapped())
        self.assertFalse(IP('192.0.2.1').is_ipv4_mapped())

        self.assertTrue(IP('::192.0.2.1').is_ipv4_compat())
        self.assertFalse(IP('::ffff:192.0.2.1').is_ipv4_compat())
        self.assertFalse(IP('192.0.2.1').is_ipv4_compat())

        self.assertFalse(IP('::').is_ipv4_mapped())

#-----------------------------------------------------------------------------
class IPRangeTests(TestCase):
    """Tests on IPRange() objects"""

    def testProperties(self):
        """IPRange() - class interface check (properties)"""
        expected_properties = (
            'ADDR_TYPES',
            'STRATEGIES',
            'addr_type',
            'first',
            'fmt',
            'last',
            'strategy',
        )

        for attribute in expected_properties:
            self.assertTrue(hasattr(IPRange, attribute))
            self.assertFalse(callable(eval('IPRange.%s' % attribute)))


    def testMethods(self):
        """IPRange() - class interface check (methods)"""
        expected_methods = (
            'adjacent',
            'cidrs',
            'format',
            'iprange',
            'issubnet',
            'issupernet',
            'overlaps',
            'size',
            'ipglob',
        )

        for attribute in expected_methods:
            self.assertTrue(hasattr(IPRange, attribute))
            self.assertTrue(callable(eval('IPRange.%s' % attribute)))

    def testSortability(self):
        """IPRange() - sortability tests"""
        #   Address ranges now sort as expected based on magnitude.
        ranges = (
            IPRange(IP('::'), IP('::')),
            IPRange(IP('0.0.0.0'), IP('255.255.255.255')),
            IPRange(IP('::'), IP('::FFFF')),
            IPRange(IP('0.0.0.0'), IP('0.0.0.0')),
        )

        expected = [
            '0.0.0.0-255.255.255.255',
            '0.0.0.0-0.0.0.0',
            '::-::ffff',
            '::-::',
        ]

        self.assertEqual([str(r) for r in sorted(ranges)], expected)

    def testIPRangeToMultipleCIDRConversion(self):
        """IPRange() - IPRange -> multiple CIDRs coversion tests"""
        #   IPv4 worst case scenario!
        self.assertEqual(IPRange('0.0.0.1', '255.255.255.254').cidrs(),
            [CIDR('0.0.0.1/32'), CIDR('0.0.0.2/31'), CIDR('0.0.0.4/30'),
            CIDR('0.0.0.8/29'), CIDR('0.0.0.16/28'), CIDR('0.0.0.32/27'),
            CIDR('0.0.0.64/26'), CIDR('0.0.0.128/25'), CIDR('0.0.1.0/24'),
            CIDR('0.0.2.0/23'), CIDR('0.0.4.0/22'), CIDR('0.0.8.0/21'),
            CIDR('0.0.16.0/20'), CIDR('0.0.32.0/19'), CIDR('0.0.64.0/18'),
            CIDR('0.0.128.0/17'), CIDR('0.1.0.0/16'), CIDR('0.2.0.0/15'),
            CIDR('0.4.0.0/14'), CIDR('0.8.0.0/13'), CIDR('0.16.0.0/12'),
            CIDR('0.32.0.0/11'), CIDR('0.64.0.0/10'), CIDR('0.128.0.0/9'),
            CIDR('1.0.0.0/8'), CIDR('2.0.0.0/7'), CIDR('4.0.0.0/6'),
            CIDR('8.0.0.0/5'), CIDR('16.0.0.0/4'), CIDR('32.0.0.0/3'),
            CIDR('64.0.0.0/2'), CIDR('128.0.0.0/2'), CIDR('192.0.0.0/3'),
            CIDR('224.0.0.0/4'), CIDR('240.0.0.0/5'), CIDR('248.0.0.0/6'),
            CIDR('252.0.0.0/7'), CIDR('254.0.0.0/8'), CIDR('255.0.0.0/9'),
            CIDR('255.128.0.0/10'), CIDR('255.192.0.0/11'),
            CIDR('255.224.0.0/12'), CIDR('255.240.0.0/13'),
            CIDR('255.248.0.0/14'), CIDR('255.252.0.0/15'),
            CIDR('255.254.0.0/16'), CIDR('255.255.0.0/17'),
            CIDR('255.255.128.0/18'), CIDR('255.255.192.0/19'),
            CIDR('255.255.224.0/20'), CIDR('255.255.240.0/21'),
            CIDR('255.255.248.0/22'), CIDR('255.255.252.0/23'),
            CIDR('255.255.254.0/24'), CIDR('255.255.255.0/25'),
            CIDR('255.255.255.128/26'), CIDR('255.255.255.192/27'),
            CIDR('255.255.255.224/28'), CIDR('255.255.255.240/29'),
            CIDR('255.255.255.248/30'), CIDR('255.255.255.252/31'),
            CIDR('255.255.255.254/32')])

        #   IPv4 compatible IPv6 test of worst case scenario.
        self.assertEqual(IPRange('::1', '::255.255.255.254', fmt=str).cidrs(),
            ['::1/128', '::2/127', '::4/126', '::8/125', '::10/124',
            '::20/123', '::40/122', '::80/121', '::100/120', '::200/119',
            '::400/118', '::800/117', '::1000/116', '::2000/115', '::4000/114',
            '::8000/113', '::0.1.0.0/112', '::0.2.0.0/111', '::0.4.0.0/110',
            '::0.8.0.0/109', '::0.16.0.0/108', '::0.32.0.0/107',
            '::0.64.0.0/106', '::0.128.0.0/105', '::1.0.0.0/104',
            '::2.0.0.0/103', '::4.0.0.0/102', '::8.0.0.0/101',
            '::16.0.0.0/100', '::32.0.0.0/99', '::64.0.0.0/98',
            '::128.0.0.0/98', '::192.0.0.0/99', '::224.0.0.0/100',
            '::240.0.0.0/101', '::248.0.0.0/102', '::252.0.0.0/103',
            '::254.0.0.0/104', '::255.0.0.0/105', '::255.128.0.0/106',
            '::255.192.0.0/107', '::255.224.0.0/108', '::255.240.0.0/109',
            '::255.248.0.0/110', '::255.252.0.0/111', '::255.254.0.0/112',
            '::255.255.0.0/113', '::255.255.128.0/114', '::255.255.192.0/115',
            '::255.255.224.0/116', '::255.255.240.0/117',
            '::255.255.248.0/118', '::255.255.252.0/119',
            '::255.255.254.0/120', '::255.255.255.0/121',
            '::255.255.255.128/122', '::255.255.255.192/123',
            '::255.255.255.224/124', '::255.255.255.240/125',
            '::255.255.255.248/126', '::255.255.255.252/127',
            '::255.255.255.254/128'])

        #   IPv4 mapped IPv6 test of worst case scenario.
        self.assertEqual(
            IPRange('::ffff:1', '::ffff:255.255.255.254', fmt=str).cidrs(),
            ['::255.255.0.1/128',  '::255.255.0.2/127',  '::255.255.0.4/126',
            '::255.255.0.8/125',  '::255.255.0.16/124',  '::255.255.0.32/123',
            '::255.255.0.64/122',  '::255.255.0.128/121',  '::255.255.1.0/120',
            '::255.255.2.0/119',  '::255.255.4.0/118',  '::255.255.8.0/117',
            '::255.255.16.0/116',  '::255.255.32.0/115',  '::255.255.64.0/114',
            '::255.255.128.0/113',  '::1:0:0/96',  '::2:0:0/95',  '::4:0:0/94',
            '::8:0:0/93',  '::10:0:0/92',  '::20:0:0/91',  '::40:0:0/90',
            '::80:0:0/89',  '::100:0:0/88',  '::200:0:0/87',  '::400:0:0/86',
            '::800:0:0/85',  '::1000:0:0/84',  '::2000:0:0/83',
            '::4000:0:0/82',  '::8000:0:0/82',  '::c000:0:0/83',
            '::e000:0:0/84',  '::f000:0:0/85',  '::f800:0:0/86',
            '::fc00:0:0/87',  '::fe00:0:0/88',  '::ff00:0:0/89',
            '::ff80:0:0/90',  '::ffc0:0:0/91',  '::ffe0:0:0/92',
            '::fff0:0:0/93',  '::fff8:0:0/94',  '::fffc:0:0/95',
            '::fffe:0:0/96',  '::ffff:0.0.0.0/97',  '::ffff:128.0.0.0/98',
            '::ffff:192.0.0.0/99',  '::ffff:224.0.0.0/100',
            '::ffff:240.0.0.0/101',  '::ffff:248.0.0.0/102',
            '::ffff:252.0.0.0/103',  '::ffff:254.0.0.0/104',
            '::ffff:255.0.0.0/105',  '::ffff:255.128.0.0/106',
            '::ffff:255.192.0.0/107',  '::ffff:255.224.0.0/108',
            '::ffff:255.240.0.0/109',  '::ffff:255.248.0.0/110',
            '::ffff:255.252.0.0/111',  '::ffff:255.254.0.0/112',
            '::ffff:255.255.0.0/113',  '::ffff:255.255.128.0/114',
            '::ffff:255.255.192.0/115',  '::ffff:255.255.224.0/116',
            '::ffff:255.255.240.0/117',  '::ffff:255.255.248.0/118',
            '::ffff:255.255.252.0/119',  '::ffff:255.255.254.0/120',
            '::ffff:255.255.255.0/121',  '::ffff:255.255.255.128/122',
            '::ffff:255.255.255.192/123',  '::ffff:255.255.255.224/124',
            '::ffff:255.255.255.240/125',  '::ffff:255.255.255.248/126',
            '::ffff:255.255.255.252/127',  '::ffff:255.255.255.254/128'])

#-----------------------------------------------------------------------------
class CIDRTests(TestCase):
    """Tests on CIDR() objects"""

    def testProperties(self):
        """CIDR() - class interface check (properties)"""
        expected_properties = (
            'ADDR_TYPES',
            'STRATEGIES',
            'addr_type',
            'broadcast',
            'first',
            'fmt',
            'hostmask',
            'last',
            'netmask',
            'network',
            'prefixlen',
            'strategy',
        )

        for attribute in expected_properties:
            self.assertTrue(hasattr(CIDR, attribute))
            self.assertFalse(callable(eval('CIDR.%s' % attribute)))


    def testMethods(self):
        """CIDR() - class interface check (methods)"""
        expected_methods = (
            'abbrev_to_verbose',
            'adjacent',
            'cidrs',
            'format',
            'iprange',
            'issubnet',
            'issupernet',
            'iter_host_addrs',
            'overlaps',
            'summarize',
            'size',
            'span_addrs',
            'span_size',
            'subnet',
            'ipglob',
        )

        for attribute in expected_methods:
            self.assertTrue(hasattr(CIDR, attribute))
            self.assertTrue(callable(eval('CIDR.%s' % attribute)))

    def testRFC4291WithCIDR(self):
        """CIDR() - RFC 4291 tests"""
        expected = '2001:db8:0:cd30::/60'

        actual = str(CIDR('2001:0DB8:0000:CD30:0000:0000:0000:0000/60'))
        self.assertEqual(actual, expected)

        actual = str(CIDR('2001:0DB8::CD30:0:0:0:0/60'))
        self.assertEqual(actual, expected)

        actual = str(CIDR('2001:0DB8:0:CD30::/60'))
        self.assertEqual(actual, expected)

    def testEquality(self):
        """CIDR() - equality tests (__eq__)"""
        cidr1 = CIDR('192.0.2.0/255.255.254.0')
        cidr2 = CIDR('192.0.2.0/23')
        self.assertEqual(cidr1, cidr2)

    def testNonStrictConstructorValidation(self):
        """CIDR() - less restrictive __init__() bitmask/netmask tests"""
        c = CIDR('192.0.2.65/255.255.254.0', strict=False)
        c.fmt=str
        self.assertEqual(str(c), '192.0.2.0/23')
        self.assertEqual(c[0], '192.0.2.0')
        self.assertEqual(c[-1], '192.0.3.255')

    def testStandardConstructorValidation(self):
        """CIDR() - standard __init__() bitmask/netmask tests"""
        self.assertRaises(ValueError, CIDR, '192.0.2.65/255.255.254.0')
        self.assertRaises(ValueError, CIDR, '192.0.2.65/23')

    def testSlicingIPv4(self):
        """CIDR() - slicing tests (IPv4)"""
        expected = [
            ['192.0.2.0/28', '192.0.2.1', '192.0.2.14', 16],
            ['192.0.2.16/28', '192.0.2.17', '192.0.2.30', 16],
            ['192.0.2.32/28', '192.0.2.33', '192.0.2.46', 16],
            ['192.0.2.48/28', '192.0.2.49', '192.0.2.62', 16],
            ['192.0.2.64/28', '192.0.2.65', '192.0.2.78', 16],
            ['192.0.2.80/28', '192.0.2.81', '192.0.2.94', 16],
            ['192.0.2.96/28', '192.0.2.97', '192.0.2.110', 16],
            ['192.0.2.112/28', '192.0.2.113', '192.0.2.126', 16],
            ['192.0.2.128/28', '192.0.2.129', '192.0.2.142', 16],
            ['192.0.2.144/28', '192.0.2.145', '192.0.2.158', 16],
            ['192.0.2.160/28', '192.0.2.161', '192.0.2.174', 16],
            ['192.0.2.176/28', '192.0.2.177', '192.0.2.190', 16],
            ['192.0.2.192/28', '192.0.2.193', '192.0.2.206', 16],
            ['192.0.2.208/28', '192.0.2.209', '192.0.2.222', 16],
            ['192.0.2.224/28', '192.0.2.225', '192.0.2.238', 16],
            ['192.0.2.240/28', '192.0.2.241', '192.0.2.254', 16],
        ]

        supernet = CIDR('192.0.2.0/24')
        subnets = list([addr for addr in supernet])[::16]

        for i, subnet_addr in enumerate(subnets):
            subnet = CIDR("%s/28" % subnet_addr)
            subnet_addrs = list(subnet)
            calculated = [str(subnet), str(subnet_addrs[1]),
                str(subnet_addrs[-2]), len(subnet)]
            self.assertEqual(calculated, expected[i])

    def testIndexingAndSlicingIPv4(self):
        """CIDR() - indexing and slicing tests (IPv4)"""
        #   IPv4
        cidr = CIDR('192.0.2.0/23', fmt=str)

        #   Handy methods.
        self.assertEqual(cidr.first, 3221225984)
        self.assertEqual(cidr.last, 3221226495)

        #   As above with indices.
        self.assertEqual(cidr[0], '192.0.2.0')
        self.assertEqual(cidr[-1], '192.0.3.255')

        expected_list = [ '192.0.2.0', '192.0.2.128', '192.0.3.0',
                          '192.0.3.128' ]

        self.assertEqual(list(cidr[::128]), expected_list)

#FIXME:    def testIndexingAndSlicingIPv6(self):
#FIXME:        """CIDR() - indexing and slicing tests (IPv6)"""
#FIXME:        cidr = CIDR('fe80::/10', fmt=str)
#FIXME:        self.assertEqual(cidr[0], 'fe80::')
#FIXME:        self.assertEqual(cidr[-1], 'febf:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
#FIXME:        self.assertEqual(cidr.size(), 332306998946228968225951765070086144)
#FIXME:
#FIXME:        try:
#FIXME:            self.assertEqual(list(cidr[0:5:1]),
#FIXME:                ['fe80::',
#FIXME:                'fe80::1',
#FIXME:                'fe80::2',
#FIXME:                'fe80::3',
#FIXME:                'fe80::4'])
#FIXME:        except OverflowError:
#FIXME:            self.fail('IPv6 slicing is currently problematic!')

    def testMembership(self):
        """CIDR() - membership (__contains__) tests (IPv4/IPv6)"""
        self.assertTrue('192.0.2.1' in CIDR('192.0.2.0/24'))
        self.assertTrue('192.0.2.255' in CIDR('192.0.2.0/24'))
        self.assertTrue(CIDR('192.0.2.0/24') in CIDR('192.0.2.0/23'))
        self.assertTrue(CIDR('192.0.2.0/24') in CIDR('192.0.2.0/24'))
        self.assertTrue('ffff::1' in CIDR('ffff::/127'))
        self.assertFalse(CIDR('192.0.2.0/23') in CIDR('192.0.2.0/24'))

    def testEquality(self):
        """CIDR() - equality (__eq__) tests (IPv4/IPv6)"""
        c1 = CIDR('192.0.2.0/24')
        c2 = CIDR('192.0.2.0/24')
        self.assertTrue(c1 == c2)
        self.assertTrue(c1 is not c2)
        self.assertFalse(c1 != c2)
        self.assertFalse(c1 is c2)

        c3 = CIDR('fe80::/10')
        c4 = CIDR('fe80::/10')
        self.assertTrue(c1 == c2)
        self.assertTrue(c1 is not c2)
        self.assertFalse(c1 != c2)
        self.assertFalse(c1 is c2)

    def testAbbreviatedCIDRs(self):
        """CIDR() - abbreviated CIDR tests (IPv4 only)"""
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
            ('192.0.2',     '192.0.2.0/24'),
            ('192.0.2.0',     '192.0.2.0/32'),
            ('0.0.0.0',     '0.0.0.0/32'),
            ('::/128',      None),            #   Does not support IPv6.
            ('::10/128',    None),            #   Hmmm... IPv6 proper, not IPv4 mapped.
            ('::/128',      None),            #   Does not support IPv6.
#TODO:            ('::192.0.2',     '::192.0.2.0/128'),
#TODO:            ('::192.0.2.0',     '::192.0.2.0/128'),
#TODO:            ('::ffff:192.0.2',     '::ffff:192.0.2.0/128'),
#TODO:            ('::ffff:192.0.2.0',     '::ffff:192.0.2.0/128'),
#TODO:            ('::192.168',   '::192.168.0.0/128'),
#TODO:            ('::192.168',   '::192.168.0.0/128'),
#TODO:            ('::ffff:192.168/120', '::ffff:192.168.0.0/120'),
            ('0.0.0.0.0', None),
            ('', None),
            (None, None),
            ([], None),
            ({}, None),
        )

        for (abbrev, expected) in abbreviations:
            result = CIDR.abbrev_to_verbose(abbrev)
            self.assertEqual(result, expected)
            if result is not None:
                cidr = CIDR(abbrev)
                self.assertEqual(str(cidr), result)

    def testCIDRToIPGlobConversion(self):
        """CIDR() - CIDR -> IPGlob conversion tests (IPv4 only)"""
        expected = (
            ('10.0.0.1/32', '10.0.0.1', 1),
            ('192.0.2.0/24', '192.0.2.*', 256),
            ('172.16.0.0/12', '172.16-31.*.*', 1048576),
            ('0.0.0.0/0', '*.*.*.*', 4294967296),
        )

        for cidr, ipglob, size in expected:
            c1 = CIDR(cidr)
            w1 = c1.ipglob()
            c2 = w1.cidrs()[0]
            self.assertEqual(c1.size(), size)
            self.assertEqual(str(c1), cidr)
            self.assertEqual(str(w1), ipglob)
            self.assertEqual(w1.size(), size)
            self.assertEqual(c1, c2)           #   Test __eq__()
            self.assertEqual(str(c1), str(c2)) #   Test __str__() values too.

    def testCIDRIncrements(self):
        """CIDR() - address range increment tests (IPv4)"""
        expected = [
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
        ]

        actual = []
        c = CIDR('192.0.2.0/28')
        for i in range(16):
            actual.append(str(c))
            c += 1

        self.assertEqual(expected, actual)

    def testCIDRAddition(self):
        """CIDR() - addition tests (IPv4 + IPv6)"""
        result0 = CIDR('192.0.2.1/32') + CIDR('192.0.2.1/32')
        self.assertEqual(result0, CIDR('192.0.2.1/32'))

        result1 = CIDR('192.0.2.0/24', fmt=str) + CIDR('192.0.3.0/24')
        self.assertEqual(result1, '192.0.2.0/23')

        result2 = CIDR('::/128', fmt=str) + CIDR('::255.255.255.255/128')
        self.assertEqual(result2, '::/96')

        result3 = CIDR('192.168.0.0/24', fmt=str) + CIDR('192.168.255.0/24')
        self.assertEqual(result3, '192.168.0.0/16')

    def testCIDRSubtraction(self):
        """CIDR() - subtraction tests (IPv4 + IPv6)"""
        result0 = CIDR('192.0.2.1/32') - CIDR('192.0.2.1/32')
        self.assertEqual(result0, [])

        result1 = CIDR('192.0.2.0/31', fmt=str) - CIDR('192.0.2.1/32')
        self.assertEqual(result1, ['192.0.2.0/32'])

        result2 = CIDR('192.0.2.0/24', fmt=str) - CIDR('192.0.2.128/25')
        self.assertEqual(result2, ['192.0.2.0/25'])

        result3 = CIDR('192.0.2.0/24', fmt=str) - CIDR('192.0.2.128/27')
        self.assertEqual(result3, ['192.0.2.0/25', '192.0.2.160/27', '192.0.2.192/26'])

        #   Subtracting a larger range from a smaller one results in an empty
        #   list (rather than a negative CIDR - which would be rather odd)!
        result4 = CIDR('192.0.2.1/32') - CIDR('192.0.2.0/24')
        self.assertEqual(result4, [])

    def testCIDRToIPEquality(self):
        """CIDR() - equality tests with IP() objects"""
        #   IPs and CIDRs do not compare favourably (directly), regardless of
        #   the logical operation being performed.
        #
        #   Logically similar, but fundamentally different on a Python and
        #   netaddr level.
        ip = IP('192.0.2.1')
        cidr = CIDR('192.0.2.1/32')

        #   Direct object to object comparisons will always fail.
        self.assertFalse(ip == cidr)
        self.assertTrue(ip != cidr)
        self.assertFalse(ip > cidr)
        self.assertFalse(ip >= cidr)
        self.assertFalse(ip < cidr)
        self.assertFalse(ip <= cidr)

        #   Compare with CIDR object lower boundary.
        self.assertTrue(ip == cidr[0])
        self.assertTrue(ip >= cidr[0])
        self.assertFalse(ip != cidr[0])
        self.assertFalse(ip > cidr[0])
        self.assertFalse(ip < cidr[0])
        self.assertTrue(ip <= cidr[0])

        #   Compare with CIDR object upper boundary.
        self.assertTrue(ip == cidr[-1])
        self.assertTrue(ip >= cidr[-1])
        self.assertFalse(ip != cidr[-1])
        self.assertFalse(ip > cidr[-1])
        self.assertFalse(ip < cidr[-1])
        self.assertTrue(ip <= cidr[-1])

    def testMasks(self):
        """CIDR() - netmask and hostmask method tests"""
        c1 = CIDR('192.0.2.0/24', fmt=str)
        self.assertEqual(c1.netmask, '255.255.255.0')
        self.assertEqual(c1.hostmask, '0.0.0.255')
        c1.prefixlen = 23
        self.assertEqual(c1.netmask, '255.255.254.0')
        self.assertEqual(c1.hostmask, '0.0.1.255')

    def testConstructorWithHostmaskACLPrefix(self):
        """CIDR() - ACL (hostmask) prefixlen constructor option tests"""
        c1 = CIDR('192.0.2.0/0.0.0.255', fmt=str)
        self.assertEqual(c1.netmask, '255.255.255.0')
        self.assertEqual(c1.hostmask, '0.0.0.255')
        self.assertEqual(c1.network, '192.0.2.0')
        self.assertEqual(c1.broadcast, '192.0.2.255')
        self.assertEqual(c1[0], '192.0.2.0')
        self.assertEqual(c1[-1], '192.0.2.255')

    def testConstructorWithNetmaskPrefix(self):
        """CIDR() - netmask prefixlen constructor option tests"""
        c1 = CIDR('192.0.2.0/255.255.255.0', fmt=str)
        self.assertEqual(c1.netmask, '255.255.255.0')
        self.assertEqual(c1.hostmask, '0.0.0.255')
        self.assertEqual(c1.network, '192.0.2.0')
        self.assertEqual(c1.broadcast, '192.0.2.255')
        self.assertEqual(c1[0], '192.0.2.0')
        self.assertEqual(c1[-1], '192.0.2.255')

    def testPrefixlenAssignment(self):
        """CIDR() - prefixlen assignment tests"""

        #   Invalid without turning off strict bitmask checking.
        self.assertRaises(ValueError, CIDR, '192.0.2.1/24')

        c1 = CIDR('192.0.2.1/24', strict=False)
        c1.fmt = str

        self.assertEqual(c1[0], '192.0.2.0')
        self.assertEqual(c1[-1], '192.0.2.255')

        c1.prefixlen = 23

        self.assertEqual(c1[-1], '192.0.3.255')
        try:
            c1.prefixlen = 33 #   Bad assignment that should fail!
        except ValueError:
            pass
        except:
            self.fail('expected ValueError was not raised!')

        self.assertEqual(c1[-1], '192.0.3.255')
        self.assertEqual(c1.prefixlen, 23)

        c2 = CIDR('192.168.0.0/16', fmt=str)

        self.assertEqual(str(c2), '192.168.0.0/16')
        self.assertEqual(c2.prefixlen, 16)
        self.assertEqual(c2[0],  '192.168.0.0')
        self.assertEqual(c2[-1], '192.168.255.255')
        self.assertEqual(len(c2), 65536)

        c2.prefixlen += 16

        self.assertEqual(str(c2),  '192.168.0.0/32')
        self.assertEqual(c2.prefixlen,  32)
        self.assertEqual(c2[0],  '192.168.0.0')
        self.assertEqual(c2[-1],  '192.168.0.0')
        self.assertEqual(len(c2),  1)

        c2.prefixlen -= 31

        self.assertEqual(str(c2),  '128.0.0.0/1')
        self.assertEqual(c2.prefixlen,  1)
        self.assertEqual(c2[0],  '128.0.0.0')
        self.assertEqual(c2[-1],  '255.255.255.255')
        self.assertEqual(c2.size(),  2147483648)

        c2.prefixlen = 0

        self.assertEqual(str(c2),  '0.0.0.0/0')
        self.assertEqual(c2.prefixlen,  0)
        self.assertEqual(c2[0],  '0.0.0.0')
        self.assertEqual(c2[-1],  '255.255.255.255')
        self.assertEqual(c2.size(),  4294967296)

    def testExceptions(self):
        """CIDR() - Exception generation tests"""

        self.assertRaises(ValueError, CIDR, '192.0.2.0/192.0.2.0')
        self.assertRaises(ValueError, CIDR, '0.0.0.0/-1')
        self.assertRaises(ValueError, CIDR, '0.0.0.0/33')
        self.assertRaises(ValueError, CIDR, '::/-1')
        self.assertRaises(ValueError, CIDR, '::/129')

        for cidr in (None, [], {}):
            self.assertRaises(TypeError, CIDR, cidr)

        for cidr in ('', 'foo'):
            self.assertRaises(AddrFormatError, CIDR, cidr)

    def testUnicodeStrings(self):
        """CIDR() - unicode string tests"""
        self.assertEqual(CIDR(u'192.0.2.0/24'), CIDR('192.0.2.0/24'))

    def testSupernetSpanning(self):
        """CIDR() - spanning supernet functionality tests (IPv4 / IPv6)"""
        expected = (
            (['192.0.2.0', '192.0.2.0'], '192.0.2.0/32'),
            (['192.0.2.0', '192.0.2.1'], '192.0.2.0/31'),
            (['192.0.2.1', '192.0.2.0'], '192.0.2.0/31'),
            (['192.0.2.0/24', '192.0.3.0/24'], '192.0.2.0/23'),
            (['192.0.2.*', '192.0.3.0/24'], '192.0.2.0/23'),
            (['*.*.*.*', '192.0.2.0/24'], '0.0.0.0/0'),
            (['192.168.3.1/24', '192.168.0.1/24', '192.168.1.1/24'], '192.168.0.0/22'),
            (['192.168.1-2.*', '192.168.3.0/24'], '192.168.0.0/22'),
            (['::', '::255.255.255.255'], '::/96'),
            (['192.0.2.27', '192.0.2.28'], '192.0.2.24/29')   #   Yes, this is correct.
        )

        for comparison in expected:
            (arg, result) = comparison
            cidr = str(CIDR.span_addrs(arg))
            self.assertEqual(cidr, result)

    def testSupernetSpanningFailureModes(self):
        """CIDR() - spanning supernet failure mode tests (IPv4)"""
        #   Mixing address types is not allowed!
        self.assertRaises(TypeError, CIDR.span_addrs, ['::ffff:192.0.2.0/24', '192.0.3.0/24', ])

    def testSupernetMembership(self):
        """CIDR() - supernet membership tests (IPv4)"""
        self.assertTrue(CIDR('192.0.2.0/24').issupernet(CIDR('192.0.2.0/24')))
        self.assertTrue(CIDR('192.0.2.0/23').issupernet(CIDR('192.0.2.0/24')))
        self.assertFalse(CIDR('192.0.2.0/25').issupernet(CIDR('192.0.2.0/24')))

        #   Mix it up with IPGlob and CIDR.
        self.assertTrue(CIDR('192.0.2.0/24').issupernet(IPGlob('192.0.2.*')))
        self.assertTrue(IPGlob('192.0.2-3.*').issupernet(CIDR('192.0.2.0/24')))
        self.assertTrue(IPGlob('192.0.2-3.*').issupernet(IPGlob('192.0.2.*')))
        self.assertFalse(CIDR('192.0.2.0/25').issupernet(CIDR('192.0.2.0/24')))
        self.assertFalse(IPGlob('192.0.2.0-127').issupernet(CIDR('192.0.2.0/24')))

    def testSubnetMembership(self):
        """CIDR() - subnet membership tests (IPv4)"""
        self.assertTrue(CIDR('192.0.2.0/24').issubnet(CIDR('192.0.2.0/24')))
        self.assertTrue(CIDR('192.0.2.0/25').issubnet(CIDR('192.0.2.0/24')))
        self.assertFalse(CIDR('192.0.2.0/23').issubnet(CIDR('192.0.2.0/24')))

    def testOverlaps(self):
        """CIDR() - overlapping CIDR() object tests (IPv4)"""
        #   A useful property of CIDRs is that they cannot overlap!
#TODO!
        pass

    def testAdjacency(self):
        """CIDR() - adjacent CIDR() object tests (IPv4)"""
        self.assertTrue(CIDR('192.0.2.0/24').adjacent(CIDR('192.0.3.0/24')))
        self.assertTrue(CIDR('192.0.3.0/24').adjacent(CIDR('192.0.2.0/24')))
        self.assertFalse(CIDR('192.0.2.0/24').adjacent(CIDR('192.0.4.0/24')))
        self.assertFalse(CIDR('192.0.4.0/24').adjacent(CIDR('192.0.2.0/24')))

    def testSupernetsIPv4(self):
        """CIDR() - supernet() method tests (IPv4)"""
        expected = [
            '0.0.0.0/0',
            '128.0.0.0/1',
            '192.0.0.0/2',
            '192.0.0.0/3',
            '192.0.0.0/4',
            '192.0.0.0/5',
            '192.0.0.0/6',
            '192.0.0.0/7',
            '192.0.0.0/8',
            '192.128.0.0/9',
            '192.128.0.0/10',
            '192.160.0.0/11',
            '192.160.0.0/12',
            '192.168.0.0/13',
            '192.168.0.0/14',
            '192.168.0.0/15',
            '192.168.0.0/16',
            '192.168.128.0/17',
            '192.168.192.0/18',
            '192.168.224.0/19',
            '192.168.240.0/20',
            '192.168.248.0/21',
            '192.168.252.0/22',
            '192.168.252.0/23',
            '192.168.252.0/24',
            '192.168.252.0/25',
            '192.168.252.64/26',
            '192.168.252.64/27',
            '192.168.252.64/28',
            '192.168.252.64/29',
            '192.168.252.64/30',
            '192.168.252.64/31',
        ]

        cidr = CIDR('192.168.252.65/32')
        calculated = cidr.supernet(fmt=str)

        self.assertEquals(expected, calculated)
        self.assertEquals(cidr.supernet(31, fmt=str), ['192.168.252.64/31'])
        self.assertEquals(cidr.supernet(24, fmt=str)[0], '192.168.252.0/24')

    def testSubnetsIPv4(self):
        """CIDR() - subnet iterator tests (IPv4)"""
        expected = [
            ('192.0.2.0/31', ('192.0.2.0', '192.0.2.1')),
            ('192.0.2.2/31', ('192.0.2.2', '192.0.2.3')),
            ('192.0.2.4/31', ('192.0.2.4', '192.0.2.5')),
            ('192.0.2.6/31', ('192.0.2.6', '192.0.2.7')),
            ('192.0.2.8/31', ('192.0.2.8', '192.0.2.9')),
            ('192.0.2.10/31', ('192.0.2.10', '192.0.2.11')),
            ('192.0.2.12/31', ('192.0.2.12', '192.0.2.13')),
            ('192.0.2.14/31', ('192.0.2.14', '192.0.2.15'))
        ]

        calculated = []
        cidr = CIDR('192.0.2.0/28')
        for subnet in cidr.subnet(prefixlen=31):
            subnet.fmt=str
            calculated.append((str(subnet), tuple(subnet)))

        self.assertEquals(expected, calculated)

        cidrs = ['192.0.2.0/30', '192.0.2.4/30',
                 '192.0.2.8/30', '192.0.2.12/30']

        #   external str() calls - returns CIDR() objects.
        self.assertEqual(cidrs,
            [str(c) for c in CIDR('192.0.2.0/28').subnet(30)])

        #   internal str() calls - returns CIDR string addresses.
        self.assertEqual(cidrs,
            list(CIDR('192.0.2.0/28').subnet(30, fmt=str)))

    def testAssignableIPv4(self):
        """CIDR() - assignable IP tests (IPv4)"""
        cidr = CIDR('192.0.2.0/28', fmt=str)
        cidrs = list(cidr.iter_host_addrs())
        self.assertTrue(('192.0.2.1' '192.0.2.14'), (cidrs[0], cidrs[-1]))

    def testSummarize(self):
        """CIDR() - summarization tests (IPv4)"""
        summaries = {
            ('192.0.128.0/24', '192.0.129.0/24') :
            ['192.0.128.0/23'],

            ('192.0.129.0/24', '192.0.130.0/24') :
            ['192.0.129.0/24', '192.0.130.0/24'],   #   bit boundary mismatch.

            ('192.0.2.112/30', '192.0.2.116/31', '192.0.2.118/31') :
            ['192.0.2.112/29'],

            ('192.0.2.112/30', '192.0.2.116/32', '192.0.2.118/31') :
            ['192.0.2.112/30', '192.0.2.116/32', '192.0.2.118/31'],

            ('192.0.2.112/31', '192.0.2.116/31', '192.0.2.118/31') :
            ['192.0.2.112/31', '192.0.2.116/30'],

            ('192.0.1.254/31', '192.0.2.0/28',
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
             '192.0.2.240/28', '192.0.3.0/28') : ['192.0.1.254/31', '192.0.2.0/24', '192.0.3.0/28'],
        }

        for actual, expected in summaries.items():
            calculated = CIDR.summarize(actual, fmt=str)
            self.assertEquals(expected, calculated)

    def testSummarizeExtended(self):
        """CIDR() - extended summarization tests (IPv4 and IPv6)"""
        #   Start with a single /23 CIDR.
        orig_cidr_ipv4 = CIDR('192.0.2.0/23')
        orig_cidr_ipv6 = CIDR('::192.0.2.0/120')

        #   Split it into /28 subnet CIDRs (mix CIDR objects and CIDR strings).
        cidr_subnets = []
        cidr_subnets.extend(list(orig_cidr_ipv4.subnet(28, fmt=str)))
        cidr_subnets.extend(list(orig_cidr_ipv4.subnet(28)))
        cidr_subnets.extend(list(orig_cidr_ipv6.subnet(124, fmt=str)))
        cidr_subnets.extend(list(orig_cidr_ipv6.subnet(124)))

        #   Add a couple of duplicates in to make sure summarization is working OK.
        cidr_subnets.append('192.0.2.1/32')
        cidr_subnets.append('192.0.2.128/25')
        cidr_subnets.append('::192.0.2.92/128')

        #   Randomize the order of subnets.
        _random.shuffle(cidr_subnets)

        #   Perform summarization operation.
        new_cidr = CIDR.summarize(cidr_subnets)

        self.assertEqual([orig_cidr_ipv4, orig_cidr_ipv6], new_cidr)

#-----------------------------------------------------------------------------
class IPGlobTests(TestCase):
    """Tests on IPGlob() objects"""

    def testProperties(self):
        """IPGlob() - class interface check (properties)"""
        expected_properties = (
            'ADDR_TYPES',
            'STRATEGIES',
            'addr_type',
            'first',
            'last',
            'fmt',
            'strategy',
        )

        for attribute in expected_properties:
            self.assertTrue(hasattr(IPGlob, attribute))
            self.assertFalse(callable(eval('IPGlob.%s' % attribute)))


    def testMethods(self):
        """IPGlob() - class interface check (methods)"""
        expected_methods = (
            'adjacent',
            'cidrs',
            'format',
            'iprange',
            'is_valid',
            'issubnet',
            'issupernet',
            'overlaps',
            'size',
            'ipglob',
        )

        for attribute in expected_methods:
            self.assertTrue(hasattr(IPGlob, attribute))
            self.assertTrue(callable(eval('IPGlob.%s' % attribute)))

    def testIPGlobPositiveValidity(self):
        """IPGlob() - positive validity tests"""
        valid_ipglobs = (
            ('192.0.2.1', 1),
            ('0.0.0.0', 1),
            ('255.255.255.255', 1),
            ('192.0.2.0-31', 32),
            ('192.0.2.*', 256),
            ('192.0.1-2.*', 512),
            ('192.0-1.*.*', 131072),
            ('*.*.*.*', 4294967296),
        )

        for ipglob, expected_size in valid_ipglobs:
            iglob = IPGlob(ipglob)
            self.assertEqual(iglob.size(), expected_size)

    def testIPGlobNegativeValidity(self):
        """IPGlob() - negative validity tests"""
        invalid_ipglobs = (
            '*.*.*.*.*',
            '*.*.*',
            '*.*',
            '*',
            '192-193.*',
            '192-193.0-1.*.*',
            '192.0.*.0',
            'a.b.c.*',
            [],
            None,
            False,
            True,
        )
        for ipglob in invalid_ipglobs:
            self.assertRaises(AddrFormatError, IPGlob, ipglob)

    def testIPGlobToCIDRConversion(self):
        """IPGlob() - IPGlob -> CIDR coversion tests"""
        expected = (
            ('10.0.0.1', '10.0.0.1/32', 1),
            ('192.0.2.*', '192.0.2.0/24', 256),
            ('172.16-31.*.*', '172.16.0.0/12', 1048576),
            ('*.*.*.*', '0.0.0.0/0', 4294967296),
        )

        for ipglob, cidr, size in expected:
            w1 = IPGlob(ipglob)
            c1 = w1.cidrs()[0]
            w2 = c1.ipglob()
            self.assertEqual(w1.size(), size)
            self.assertEqual(str(w1), ipglob)
            self.assertEqual(str(c1), cidr)
            self.assertEqual(c1.size(), size)
            self.assertEqual(w1, w2)           #   Test __eq__()
            self.assertEqual(str(w1), str(w2)) #   Test __str__() values too.

    def testIPGlobToMultipleCIDRConversion(self):
        """IPGlob() - IPGlob -> multiple CIDRs coversion tests"""
        #   Example from RFC3171 - IANA IPv4 Multicast Guidelines :-
        #   IANA reserved address space
        self.assertEqual(IPGlob('225-231.*.*.*').cidrs(),
            [CIDR('225.0.0.0/8'), CIDR('226.0.0.0/7'), CIDR('228.0.0.0/6')])

        self.assertEqual(IPGlob('225-231.*.*.*', fmt=str).cidrs(),
            ['225.0.0.0/8', '226.0.0.0/7', '228.0.0.0/6'])

        self.assertEqual(IPGlob('234-238.*.*.*').cidrs(),
            [CIDR('234.0.0.0/7'), CIDR('236.0.0.0/7'), CIDR('238.0.0.0/8')])

        self.assertEqual(IPGlob('234-238.*.*.*', fmt=str).cidrs(),
            ['234.0.0.0/7', '236.0.0.0/7', '238.0.0.0/8'])

        self.assertEqual(IPGlob('192.0.2.5-6').cidrs(),
            [CIDR('192.0.2.5/32'), CIDR('192.0.2.6/32')])

        self.assertEqual(IPGlob('192.0.2.5-6', fmt=str).cidrs(),
            ['192.0.2.5/32', '192.0.2.6/32'])

    def testIPGlobToCIDRComparisons(self):
        """IPGlob() - comparison against CIDR() object tests"""
        #   Basically CIDRs and IPGlobs are subclassed from the same parent
        #   class so should compare favourably.
        cidr1 = CIDR('192.0.2.0/24')
        cidr2 = CIDR('192.0.3.0/24')
        iglob1 = IPGlob('192.0.2.*')

        #   Positives.
        self.assertTrue(cidr1 == iglob1)
        self.assertTrue(cidr1 >= iglob1)
        self.assertTrue(cidr1 <= iglob1)
        self.assertTrue(cidr2 > iglob1)
        self.assertTrue(iglob1 < cidr2)

        #   Negatives.
        self.assertFalse(cidr1 != iglob1)
        self.assertFalse(cidr1 > iglob1)
        self.assertFalse(cidr1 < iglob1)
        self.assertFalse(cidr2 <= iglob1)
        self.assertFalse(cidr2 < iglob1)
        self.assertFalse(iglob1 >= cidr2)
        self.assertFalse(iglob1 > cidr2)

    def testIPGlobToIPEquality(self):
        """IPGlob() - equality tests with IP() objects"""
        #   IPs and IPGlobs current do not compare favourably, regardless
        #   of the operation.
        #
        #   Logically similar, but fundamentally different at a Python and
        #   netaddr level.
        ip = IP('192.0.2.1')
        iglob = IPGlob('192.0.2.1')

        #   Direct object to object comparisons will always fail.
        self.assertFalse(ip == iglob)
        self.assertTrue(ip != iglob)
        self.assertFalse(ip > iglob)
        self.assertFalse(ip >= iglob)
        self.assertFalse(ip < iglob)
        self.assertFalse(ip <= iglob)

        #   Compare with IPGlob object lower boundary.
        self.assertTrue(ip == iglob[0])
        self.assertTrue(ip >= iglob[0])
        self.assertTrue(ip <= iglob[0])
        self.assertFalse(ip != iglob[0])
        self.assertFalse(ip > iglob[0])
        self.assertFalse(ip < iglob[0])

        #   Compare with IPGlob object upper boundary.
        self.assertTrue(ip == iglob[-1])
        self.assertTrue(ip >= iglob[-1])
        self.assertTrue(ip <= iglob[-1])
        self.assertFalse(ip != iglob[-1])
        self.assertFalse(ip > iglob[-1])
        self.assertFalse(ip < iglob[-1])

    def testIPGlobIncrements(self):
        """IPGlob() - address range increment tests"""
        expected = [
            '192.0.0.*',
            '192.0.1.*',
            '192.0.2.*',
            '192.0.3.*',
        ]

        actual = []
        iglob = IPGlob('192.0.0.*')
        for i in range(4):
            actual.append(str(iglob))
            iglob += 1

        self.assertEqual(expected, actual)

    def testOverlaps(self):
        """IPGlob() - overlapping IPGlob() object tests"""
        self.assertTrue(IPGlob('192.0.2.0-31').overlaps(IPGlob('192.0.2.16-63')))
        self.assertFalse(IPGlob('192.0.2.0-7').overlaps(IPGlob('192.0.2.16-23')))

    def testAdjacency(self):
        """IPGlob() - adjacent IPGlob() object tests"""
        self.assertTrue(IPGlob('192.0.2.*').adjacent(IPGlob('192.0.3.*')))
        self.assertTrue(IPGlob('192.0.3.*').adjacent(IPGlob('192.0.2.*')))
        self.assertFalse(IPGlob('192.0.2.*').adjacent(IPGlob('192.0.4.*')))
        self.assertFalse(IPGlob('192.0.4.*').adjacent(IPGlob('192.0.2.*')))

#-----------------------------------------------------------------------------
class nrangeTests(TestCase):
    """Tests on the nrange() function"""
    def testIPObjectIteration(self):
        """nrange() - iterator yielding IP() object test (IPv4)"""
        expected = [
            '192.0.2.0',
            '192.0.2.4',
            '192.0.2.8',
            '192.0.2.12',
            '192.0.2.16',
            '192.0.2.20',
            '192.0.2.24',
            '192.0.2.28',
            '192.0.2.32',
        ]

        start_addr = IP('192.0.2.0')
        stop_addr = IP('192.0.2.32')
        for i, addr in enumerate(nrange(start_addr, stop_addr, 4)):
            self.assertEqual(str(addr), expected[i])

    def testIntegerIteration(self):
        """nrange() - yield positive integer test (IPv6)"""
        expected_type = int
        expected_list = [0,4,8,12,16]

        saved_list = []
        #   IPv6 addresses auto-detected, as int.
        for addr in nrange('::', '::10', 4, fmt=expected_type):
            self.assertEqual(type(addr), expected_type)
            saved_list.append(addr)

        self.assertEqual(saved_list, expected_list)

    def testNegativeIntegerIteration(self):
        """nrange() - yield negative integer test (IPv6)"""
        expected_type = int
        expected_list = [16,12,8,4,0]

        saved_list = []
        #   IPv6 addresses auto-detected, negative step as int.
        for addr in nrange('::10', '::', -4, fmt=expected_type):
            self.assertEqual(type(addr), expected_type)
            saved_list.append(addr)

        self.assertEqual(saved_list, expected_list)

    def testHexadecimalIteration(self):
        """nrange() - yield hexdecimal values test (IPv6)"""
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
        for addr in nrange('ff00::10', 'ff00::', -4, fmt=hex):
            self.assertEqual(type(addr), str)
            saved_list.append(addr.lower().rstrip('l'))

        self.assertEqual(saved_list, expected_list)

    def testIPObjectIteration(self):
        """nrange() - yield IP() object test (IPv4)"""
        expected_list = [
            '192.0.2.0',
            '192.0.2.128',
            '192.0.3.0',
            '192.0.3.128',
        ]

        saved_list = []
        #   IP class used to initialise generator with IPv4 addresses and a
        #   step of 128 addresses,
        for addr in nrange(IP('192.0.2.0'), IP('192.0.3.255'), 128):
            self.assertTrue(isinstance(addr, IP))
            #   Save addresses as string values for comparison.
            saved_list.append(str(addr))

        self.assertEqual(saved_list, expected_list)


#-----------------------------------------------------------------------------
class IPandCIDRDifferences(TestCase):
    """Tests on the nrange() function"""
    def testConstructor(self):
        """general - IP() versus CIDR() constructor parsing behaviour difference tests"""
        #!!!   The difference here are subtle and are *NOT* bugs!
        #!!!   IP() users inet_aton() whereas CIDR is employing customised
        #!!!   abbreviation completion rules based on old classful addressing
        #!!!   rules. Compatible with pgsql's cidr() function.
        self.assertEqual(IP('192.0.2/24'), IP('192.0.0.2/24'))
        self.assertEqual(CIDR('192.0.2/24'), CIDR('192.0.2.0/24'))

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    unit_test_suite = TestSuite()
    for test_case in TestLoader().loadTestsFromName(__name__):
        unit_test_suite.addTest(test_case)
    TextTestRunner(verbosity=2).run(unit_test_suite)
