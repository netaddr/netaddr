#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
Consolidated set of unit tests for the netaddr module.
"""
from unittest import TestCase, TestLoader, TestSuite, TextTestRunner
import os as _os
import sys as _sys

path = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), '..'))
_sys.path.insert(0, path)

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
    """Tests on AddrStrategy class objects with various configurations"""

    def testInterfaceWithIPv4(self):
        """AddrStrategy() - interface tests (IPv4 specific)"""
        strategy = netaddr.strategy.AddrStrategy(addr_type=AT_INET,
            width=32,
            word_size=8,
            word_fmt='%d',
            delimiter='.',
            hex_words=False)

        b = '11000000.10101000.00000000.00000001'
        i = 3232235521
        t = (192, 168, 0, 1)
        s = '192.168.0.1'

        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)
        self.assertEqual(strategy.bits_to_str(b), s)
        self.assertEqual(strategy.bits_to_words(b), t)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)

        #   str to x
        self.assertEqual(strategy.str_to_bits(s), b)
        self.assertEqual(strategy.str_to_int(s), i)
        self.assertEqual(strategy.str_to_words(s), t)

        #   words to x
        self.assertEqual(strategy.words_to_bits(t), b)
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_str(t), s)

        self.assertEqual(strategy.words_to_bits(list(t)), b)
        self.assertEqual(strategy.words_to_int(list(t)), i)
        self.assertEqual(strategy.words_to_str(list(t)), s)

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
            delimiter=':')

        b = '0000000000000000:0000000000000000:0000000000000000:' \
            '0000000000000000:0000000000000000:0000000000000000:' \
            '1111111111111111:1111111111111110'
        i = 4294967294
        t = (0, 0, 0, 0, 0, 0, 0xffff, 0xfffe)
        s = '0:0:0:0:0:0:ffff:fffe'

        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)
        self.assertEqual(strategy.bits_to_str(b), s)
        self.assertEqual(strategy.bits_to_words(b), t)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)

        #   str to x
        self.assertEqual(strategy.str_to_bits(s), b)
        self.assertEqual(strategy.str_to_int(s), i)
        self.assertEqual(strategy.str_to_words(s), t)

        #   words to x
        self.assertEqual(strategy.words_to_bits(t), b)
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_str(t), s)

        self.assertEqual(strategy.words_to_bits(list(t)), b)
        self.assertEqual(strategy.words_to_int(list(t)), i)
        self.assertEqual(strategy.words_to_str(list(t)), s)

    def testInterfaceWithBasicMAC(self):
        """AddrStrategy() - interface tests (Unix MAC address format)"""
        strategy = netaddr.strategy.AddrStrategy(addr_type=AT_LINK,
            width=48,
            word_size=8,
            word_fmt='%02x',
            delimiter=':')

        b = '00000000:00001111:00011111:00010010:11100111:00110011'
        i = 64945841971
        t = (0x0, 0x0f, 0x1f, 0x12, 0xe7, 0x33)
        s = '00:0f:1f:12:e7:33'

        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)
        self.assertEqual(strategy.bits_to_str(b), s)
        self.assertEqual(strategy.bits_to_words(b), t)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)

        #   str to x
        self.assertEqual(strategy.str_to_bits(s), b)
        self.assertEqual(strategy.str_to_int(s), i)
        self.assertEqual(strategy.str_to_words(s), t)

        #   words to x
        self.assertEqual(strategy.words_to_bits(t), b)
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_str(t), s)

        self.assertEqual(strategy.words_to_bits(list(t)), b)
        self.assertEqual(strategy.words_to_int(list(t)), i)
        self.assertEqual(strategy.words_to_str(list(t)), s)

    def testInterfaceWithCiscoMAC(self):
        """AddrStrategy() - interface tests (Cisco address format)"""
        strategy = netaddr.strategy.AddrStrategy(addr_type=AT_LINK,
            width=48,
            word_size=16,
            word_fmt='%04x',
            delimiter='.')

        b = '0000000000001111.0001111100010010.1110011100110011'
        i = 64945841971
        t = (0xf, 0x1f12, 0xe733)
        s = '000f.1f12.e733'

        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)
        self.assertEqual(strategy.bits_to_str(b), s)
        self.assertEqual(strategy.bits_to_words(b), t)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)

        #   str to x
        self.assertEqual(strategy.str_to_bits(s), b)
        self.assertEqual(strategy.str_to_int(s), i)
        self.assertEqual(strategy.str_to_words(s), t)

        #   words to x
        self.assertEqual(strategy.words_to_bits(t), b)
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_str(t), s)

        self.assertEqual(strategy.words_to_bits(list(t)), b)
        self.assertEqual(strategy.words_to_int(list(t)), i)
        self.assertEqual(strategy.words_to_str(list(t)), s)

#-----------------------------------------------------------------------------
class IPv4StrategyTests(TestCase):
    """Tests on IPv4Strategy class and subclass objects"""

    def testInterfaceStandard(self):
        """IPv4StrategyStd() - interface tests (non-optimised)"""
        strategy = netaddr.strategy.IPv4StrategyStd()

        b = '11000000.10101000.00000000.00000001'
        i = 3232235521
        t = (192, 168, 0, 1)
        s = '192.168.0.1'

        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)
        self.assertEqual(strategy.bits_to_str(b), s)
        self.assertEqual(strategy.bits_to_words(b), t)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)

        #   str to x
        self.assertEqual(strategy.str_to_bits(s), b)
        self.assertEqual(strategy.str_to_int(s), i)
        self.assertEqual(strategy.str_to_words(s), t)

        #   words to x
        self.assertEqual(strategy.words_to_bits(t), b)
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_str(t), s)

        self.assertEqual(strategy.words_to_bits(list(t)), b)
        self.assertEqual(strategy.words_to_int(list(t)), i)
        self.assertEqual(strategy.words_to_str(list(t)), s)

    def testInterfaceOptimised(self):
        """IPv4StrategyOpt() - interface tests (optimised)"""
        #   Skip this test if optimisations will cause failures.
        if not netaddr.strategy.USE_IPV4_OPT:
            return

        strategy = netaddr.strategy.IPv4StrategyOpt()

        b = '11000000.10101000.00000000.00000001'
        i = 3232235521
        t = (192, 168, 0, 1)
        s = '192.168.0.1'

        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)
        self.assertEqual(strategy.bits_to_str(b), s)
        self.assertEqual(strategy.bits_to_words(b), t)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)

        #   str to x
        self.assertEqual(strategy.str_to_bits(s), b)
        self.assertEqual(strategy.str_to_int(s), i)
        self.assertEqual(strategy.str_to_words(s), t)

        #   words to x
        self.assertEqual(strategy.words_to_bits(t), b)
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_str(t), s)

        self.assertEqual(strategy.words_to_bits(list(t)), b)
        self.assertEqual(strategy.words_to_int(list(t)), i)
        self.assertEqual(strategy.words_to_str(list(t)), s)

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

        #   bits to x
        self.assertEqual(strategy.bits_to_int(b), i)

        self.assertEqual(strategy.bits_to_str(b), s)

        self.assertEqual(strategy.bits_to_words(b), t)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)

        #   str to x
        self.assertEqual(strategy.str_to_bits(s), b)
        self.assertEqual(strategy.str_to_int(s), i)
        self.assertEqual(strategy.str_to_words(s), t)

        #   words to x
        self.assertEqual(strategy.words_to_bits(t), b)
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_str(t), s)

        self.assertEqual(strategy.words_to_bits(list(t)), b)
        self.assertEqual(strategy.words_to_int(list(t)), i)
        self.assertEqual(strategy.words_to_str(list(t)), s)

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
            '::192.168.0.1',
            '::ffff:192.168.0.1',
            '0:0:0:0:0:0:192.168.0.1',
            '0:0:0:0:0:FFFF:192.168.0.1',
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
#FIXME:            '::fffe:192.168.0.1',
        )

        strategy = netaddr.strategy.IPv6Strategy()

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

        strategy = netaddr.strategy.IPv6Strategy()

        for long_form, short_form in valid_addrs.items():
            int_val = strategy.str_to_int(long_form)
            calc_short_form = strategy.int_to_str(int_val)
            self.assertEqual(calc_short_form, short_form)

    def testStringPadding(self):
        """IPv6Strategy() - address string padding tests"""
        strategy = netaddr.strategy.IPv6Strategy()

        addr = 'ffff:ffff::ffff:ffff'
        expected_int = 340282366841710300949110269842519228415

        int_addr = strategy.str_to_int(addr)

        self.assertEqual(int_addr, expected_int)

        self.assertEqual(strategy.int_to_str(int_addr, False), 'ffff:ffff:0:0:0:0:ffff:ffff')

        self.assertEqual(strategy.int_to_str(int_addr), 'ffff:ffff::ffff:ffff')

        words = strategy.int_to_words(int_addr)

        self.assertEqual(words, (65535, 65535, 0, 0, 0, 0, 65535, 65535))
        self.assertEqual(strategy.words_to_int(words), expected_int)

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
        self.assertEqual(strategy.bits_to_str(b), s)
        self.assertEqual(strategy.bits_to_words(b), t)

        #   int to x
        self.assertEqual(strategy.int_to_bits(i), b)
        self.assertEqual(strategy.int_to_str(i), s)
        self.assertEqual(strategy.int_to_words(i), t)

        #   str to x
        self.assertEqual(strategy.str_to_bits(s), b)
        self.assertEqual(strategy.str_to_int(s), i)
        self.assertEqual(strategy.str_to_words(s), t)

        #   words to x
        self.assertEqual(strategy.words_to_bits(t), b)
        self.assertEqual(strategy.words_to_int(t), i)
        self.assertEqual(strategy.words_to_str(t), s)

        self.assertEqual(strategy.words_to_bits(list(t)), b)
        self.assertEqual(strategy.words_to_int(list(t)), i)
        self.assertEqual(strategy.words_to_str(list(t)), s)

    def testStrategyConfigSettings(self):
        """EUI48Strategy() - interface configuration tests"""
        eui48 = '00-C0-29-C2-52-FF'
        eui48_int = 825334321919

        unix_mac = netaddr.strategy.EUI48Strategy(delimiter=':',
            word_fmt='%x', to_upper=False)

        self.assertEqual(unix_mac.int_to_str(eui48_int), '0:c0:29:c2:52:ff')
        unix_mac.delimiter = '-'
        self.assertEqual(unix_mac.int_to_str(eui48_int), '0-c0-29-c2-52-ff')
        unix_mac.to_upper = True
        unix_mac.word_fmt = '%02x'
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
        self.assertTrue(isinstance(ST_IPV6, netaddr.strategy.IPv6Strategy))

        #   The test below covers both standard and optimised IPv4 strategies
        #   as the optimised one is a subclass of the standard one.
        self.assertTrue(isinstance(ST_IPV4, netaddr.strategy.IPv4StrategyStd))

    def testProperties(self):
        """ST_* objects interface check - properties"""
        expected_properties = (
            'addr_type',
            'delimiter',
            'hex_words',
            'max_int',
            'max_word',
            'min_int',
            'min_word',
            'name',
            'to_upper',
            'width',
            'word_base',
            'word_count',
            'word_fmt',
            'word_size',
        )

        for strategy in self.strategies:
            for attribute in expected_properties:
                self.assertTrue(hasattr(strategy, attribute))
                self.assertFalse(callable(eval('strategy.%s' % attribute)))


    def testMethods(self):
        """ST_* objects interface check - methods"""
        expected_methods = (
            'bits_to_int',
            'bits_to_str',
            'bits_to_words',
            'description',
            'int_to_bits',
            'int_to_str',
            'int_to_words',
            'str_to_bits',
            'str_to_int',
            'str_to_words',
            'valid_bits',
            'valid_int',
            'valid_str',
            'valid_words',
            'word_to_bits',
            'words_to_bits',
            'words_to_int',
            'words_to_str',
        )

        for strategy in self.strategies:
            for attribute in expected_methods:
                self.assertTrue(hasattr(strategy, attribute))
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
        for addr in ([], {}, '', None, 5.2, -1, 'abc.def.ghi.jkl', '::z'):
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
        addr.value = '192.168.0.1'
        self.assertEqual(addr.value, 3232235521)
        self.assertEqual(addr.addr_type, AT_INET)
        self.assertEqual(addr.strategy, ST_IPV4)

    #---------------------
    #   *** IPv4 tests ***
    #---------------------

    def testRepresentationsIPv4(self):
        """Addr() - address representation tests (IPv4)"""
        width = 32
        addr = netaddr.address.Addr('192.168.0.1')
        octets = (192, 168, 0, 1)
        int_val = 3232235521
        hex_val = '0xc0a80001'
        bin_val = '11000000.10101000.00000000.00000001'

        self.assertEqual(len(addr), width)
        self.assertEqual(addr[0], octets[0])
        self.assertEqual(tuple(addr), octets)
        self.assertEqual(int(addr), int_val)
        self.assertEqual(long(addr), int_val)
        self.assertEqual(hex(addr), hex_val)
        self.assertEqual(addr.bits(), bin_val)

    def testBoundariesIPv4(self):
        """Addr() - boundary tests (IPv4)"""
        addr_min = netaddr.address.Addr('0.0.0.0')
        addr_max = netaddr.address.Addr('255.255.255.255')
        min_val_int = 0
        max_val_int = 4294967295
        max_val_hex = '0xffffffff'
        min_val_bin = '.'.join(['0'*8 for i in range(4)])
        max_val_bin = '.'.join(['1'*8 for i in range(4)])
        min_val_octets = (0, 0, 0, 0)
        max_val_octets = (255, 255, 255, 255)

        self.assertEqual(int(addr_min), min_val_int)
        self.assertEqual(int(addr_max), max_val_int)
        self.assertEqual(hex(addr_max), max_val_hex)
        self.assertEqual(addr_min.bits(), min_val_bin)
        self.assertEqual(addr_max.bits(), max_val_bin)

        #   Addr indexing tests - addr[x].
        self.assertEqual(tuple(addr_min), min_val_octets)
        self.assertEqual(tuple(addr_max), max_val_octets)
        self.assertEqual(list(addr_min), list(min_val_octets))
        self.assertEqual(list(addr_max), list(max_val_octets))

    def testIterationIPv4(self):
        """Addr() - iteration tests (IPv4)"""
        addr = netaddr.address.Addr('192.168.0.1')
        hex_bytes = ['0xc0', '0xa8', '0x0', '0x1']
        self.assertEqual([hex(i) for i in addr], hex_bytes)

    def testIndexingAndSlicingIPv4(self):
        """Addr() - indexing and slicing tests (IPv4)"""
        addr = netaddr.address.Addr('192.168.0.1')

        # using __getitem__()
        self.assertEqual(addr[0], 192)
        self.assertEqual(addr[1], 168)
        self.assertEqual(addr[2], 0)
        self.assertEqual(addr[3], 1)

        addr[3] = 2                     # using __setitem__()
        self.assertEqual(addr[3], 2)    # basic index
        self.assertEqual(addr[-4], 192) # negative index

        #   Slicing, oh yeah!
        self.assertEqual(addr[0:2], [192, 168])          # basic slice
        self.assertEqual(addr[0:4:2], [192, 0])          # slice with step
        self.assertEqual(addr[-1::-1], [2, 0, 168, 192]) # negative index

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

    def testIncrementAndDecrementIPv4(self):
        """Addr() - increment and decrement tests (IPv4)"""
        addr = netaddr.address.Addr('0.0.0.0')
        self.assertEqual(int(addr), 0)
        addr += 1
        self.assertEqual(int(addr), 1)
        #   Increment it all the way up to the value of a 'real' address.
        addr += 3232235520
        self.assertEqual(str(addr), str(netaddr.address.Addr('192.168.0.1')))

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
        self.assertEqual(str(ip_addr), '::ffff:c0a8:1')

    def testIPv6AddressCompression(self):
        """Addr() - test IPv6 '::' compression algorithm"""
        self.assertEqual(str(netaddr.address.Addr('0:0:0:0:0:0:0:0')), '::')
        self.assertEqual(str(netaddr.address.Addr('0:0:0:0:0:0:0:A')), '::a')
        self.assertEqual(str(netaddr.address.Addr('A:0:0:0:0:0:0:0')), 'a::')
        self.assertEqual(str(netaddr.address.Addr('A:0:A:0:0:0:0:0')), 'a:0:a::')
        self.assertEqual(str(netaddr.address.Addr('A:0:0:0:0:0:0:A')), 'a::a')
        self.assertEqual(str(netaddr.address.Addr('0:A:0:0:0:0:0:A')), '0:a::a')
        self.assertEqual(str(netaddr.address.Addr('A:0:A:0:0:0:0:A')), 'a:0:a::a')
        self.assertEqual(str(netaddr.address.Addr('0:0:0:A:0:0:0:A')), '0:0:0:a::a')
        self.assertEqual(str(netaddr.address.Addr('0:0:0:0:A:0:0:A')), '::a:0:0:a')
        self.assertEqual(str(netaddr.address.Addr('A:0:0:0:0:A:0:A')), 'a::a:0:a')
        self.assertEqual(str(netaddr.address.Addr('A:0:0:A:0:0:A:0')), 'a:0:0:a::a:0')
        self.assertEqual(str(netaddr.address.Addr('A:0:A:0:A:0:A:0')), 'a:0:a:0:a:0:a::')
        self.assertEqual(str(netaddr.address.Addr('0:A:0:A:0:A:0:A')), '0:a:0:a:0:a::a')
        self.assertEqual(str(netaddr.address.Addr('0:0:0:0:0:0:0:1')), '::1')
        self.assertEqual(str(netaddr.address.Addr('1:0:0:0:0:0:0:1')), '1::1')
        self.assertEqual(str(netaddr.address.Addr('0:1:0:0:0:0:0:1')), '0:1::1')
        self.assertEqual(str(netaddr.address.Addr('1:0:1:0:0:0:0:1')), '1:0:1::1')
        self.assertEqual(str(netaddr.address.Addr('0:0:0:1:0:0:0:1')), '0:0:0:1::1')
        self.assertEqual(str(netaddr.address.Addr('0:0:0:0:1:0:0:1')), '::1:0:0:1')
        self.assertEqual(str(netaddr.address.Addr('1:0:0:0:0:1:0:1')), '1::1:0:1')
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
        bin_val = '0000000000000000:0000000000000000:0000000000000000:' \
                  '0000000000000000:0000000000000000:1111111111111111:' \
                  '1100000010101000:0000000000000001'

        self.assertEqual(len(addr), width)
        self.assertEqual(addr[0], words[0])
        self.assertEqual(tuple(addr), words)
        self.assertEqual(int(addr), int_val)
        self.assertEqual(long(addr), int_val)
        self.assertEqual(hex(addr), hex_val)
        self.assertEqual(addr.bits(), bin_val)

    def testBoundariesIPv6(self):
        """Addr() - boundary tests (IPv6)"""
        addr_min = netaddr.address.Addr('::')
        addr_max = netaddr.address.Addr('ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
        min_val_int = 0
        max_val_int = 340282366920938463463374607431768211455
        max_val_hex = '0xffffffffffffffffffffffffffffffff'
        min_val_bin = ':'.join(['0'*16 for i in range(8)])
        max_val_bin = ':'.join(['1'*16 for i in range(8)])
        min_val_words = (0, 0, 0, 0, 0, 0, 0, 0)
        max_val_words = (65535, 65535, 65535, 65535, 65535, 65535, 65535, 65535)

        self.assertEqual(int(addr_min), min_val_int)
        self.assertEqual(int(addr_max), max_val_int)
        self.assertEqual(hex(addr_max), max_val_hex)
        self.assertEqual(addr_min.bits(), min_val_bin)
        self.assertEqual(addr_max.bits(), max_val_bin)
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
        bin_val = '00000000-00010100-11000010-11000111-11011010-11010101'

        self.assertEqual(len(addr), width)
        self.assertEqual(int(addr), int_val)
        self.assertEqual(long(addr), int_val)
        self.assertEqual(hex(addr), hex_val)
        self.assertEqual(addr.bits(), bin_val)

    def testBoundariesEUI(self):
        """Addr() - boundary tests (EUI)"""
        addr_min = netaddr.address.Addr('0:0:0:0:0:0')
        addr_max = netaddr.address.Addr('ff-ff-ff-ff-ff-ff')
        min_val_int = 0
        max_val_int = 281474976710655
        max_val_hex = '0xffffffffffff'
        min_val_bin = '-'.join(['0'*8 for i in range(6)])
        max_val_bin = '-'.join(['1'*8 for i in range(6)])

        self.assertEqual(int(addr_min), min_val_int)
        self.assertEqual(int(addr_max), max_val_int)
        self.assertEqual(hex(addr_max), max_val_hex)
        self.assertEqual(addr_min.bits(), min_val_bin)
        self.assertEqual(addr_max.bits(), max_val_bin)

#-----------------------------------------------------------------------------
class AddrRangeTests(TestCase):
    """Tests on EUI() class objects"""

    def testSortability(self):
        """AddrRange() - sortability tests"""
        #   Address ranges now sort as expected based on magnitude.
        ranges = (
            netaddr.address.AddrRange(
                netaddr.address.Addr('0-0-0-0-0-0-0-0'),
                netaddr.address.Addr('0-0-0-0-0-0-0-0')),
            netaddr.address.AddrRange(
                netaddr.address.Addr('::'),
                netaddr.address.Addr('::')),
            netaddr.address.AddrRange(
                netaddr.address.Addr('0-0-0-0-0-0'),
                netaddr.address.Addr('0-0-0-0-0-0')),
            netaddr.address.AddrRange(
                netaddr.address.Addr('0.0.0.0'),
                netaddr.address.Addr('255.255.255.255')),
            netaddr.address.AddrRange(
                netaddr.address.Addr('0.0.0.0'),
                netaddr.address.Addr('0.0.0.0')),
        )

        expected = [
            '0.0.0.0;0.0.0.0',
            '0.0.0.0;255.255.255.255',
            '::;::',
            '00-00-00-00-00-00;00-00-00-00-00-00',
            '00-00-00-00-00-00-00-00;00-00-00-00-00-00-00-00',
        ]

        self.assertEqual([str(r) for r in sorted(ranges)], expected)

#-----------------------------------------------------------------------------
class EUITests(TestCase):
    """Tests on EUI() class objects"""

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
            'info',
            'ipv6_link_local',
            'oui',
        )

        for attribute in expected_methods:
            self.assertTrue(hasattr(EUI, attribute))
            self.assertTrue(callable(eval('EUI.%s' % attribute)))

    def testEUI48(self):
        """EUI() basic tests (MAC, EUI-48)"""
        mac = EUI('00:C0:29:C2:52:FF')
        self.assertEqual(str(mac), '00-C0-29-C2-52-FF')
        self.assertEqual(mac.oui(), '00-C0-29')
        self.assertEqual(mac.ei(), 'C2-52-FF')
        self.assertEqual(mac.eui64(), EUI('00-C0-29-FF-FE-C2-52-FF'))

    def testEUI64(self):
        """EUI() basic tests (EUI-64)"""
        eui64 = EUI('00-C0-29-FF-FE-C2-52-FF')
        self.assertEqual(str(eui64), '00-C0-29-FF-FE-C2-52-FF')
        self.assertEqual(eui64.oui(), '00-C0-29')
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


#-----------------------------------------------------------------------------
class IPTests(TestCase):
    """Tests on IP() objects"""

    def testProperties(self):
        """IP() - class interface check (properties)"""
        expected_properties = (
            'ADDR_TYPES',
            'STRATEGIES',
            'TRANSLATE_STR',
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
            'ipv4',
            'ipv6',
            'is_hostmask',
            'is_multicast',
            'is_netmask',
            'is_unicast',
            'netmask_bits',
            'reverse_dns',
        )

        for attribute in expected_methods:
            self.assertTrue(hasattr(IP, attribute))
            self.assertTrue(callable(eval('IP.%s' % attribute)))

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
        ip = IP('192.168.0.1')
        self.assertEqual(ip.value, 3232235521)
        self.assertEqual(ip.addr_type, AT_INET)
        self.assertEqual(ip.strategy, ST_IPV4)
        self.assertEqual(ip.prefixlen, 32)

        #   Prefix /32 for IPv4 addresses should be implicit.
        self.assertEqual(repr(ip), "netaddr.address.IP('192.168.0.1')")
        ip.prefixlen = 24
        self.assertEqual(repr(ip), "netaddr.address.IP('192.168.0.1/24')")

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
        self.assertEqual(repr(ip), "netaddr.address.IP('fe80::4472:4b4a:616d')")
        ip.prefixlen = 64
        self.assertEqual(repr(ip), "netaddr.address.IP('fe80::4472:4b4a:616d/64')")

        #   Check IPv4 mapped IPv6.
        self.assertEqual(hex(IP('::ffff:10.11.12.13')), '0xffff0a0b0c0d')
        self.assertEqual(hex(IP('::10.11.12.13')), hex(IP('10.11.12.13')))

        self.assertRaises(ValueError, IP, '::/-1')
        self.assertRaises(ValueError, IP, '::/129')

    def testNetmaskIPv4(self):
        """IP() - netmask tests (IPv4)"""
        addr = IP('192.168.1.100')
        self.assertFalse(addr.is_netmask())

        netmask = IP('255.255.254.0')
        self.assertTrue(netmask.is_netmask())

        #   Apply subnet mask
        network_id = IP(int(addr) & int(netmask), AT_INET)
        self.assertEqual(str(network_id), '192.168.0.0')

    def testConstructorExceptions(self):
        """IP() - constructor Exception tests"""

        #   No arguments passed to constructor.
        self.assertRaises(TypeError, IP)

        #   Various bad types for address values.
        for bad_addr in ('', None, [], {}, 4.2):
            self.assertRaises(AddrFormatError, IP, bad_addr)

        #   Various bad types for addr_type values.
        for bad_addr_type in ('', None, [], {}, 4.2):
            self.assertRaises(ValueError, IP, '0.0.0.0', bad_addr_type)

        #   Wrong explicit address type for a valid address.
        self.assertRaises(Exception, IP, '0.0.0.0', 6)
        self.assertRaises(Exception, IP, '::', 4)

    def testReverseLookupIPv4(self):
        """IP() - reverse DNS lookup test (IPv4)"""
        expected = '1.0.168.192.in-addr.arpa.'
        ip = IP('192.168.0.1')
        self.assertEqual(expected, ip.reverse_dns())

    def testReverseLookupIPv6(self):
        """IP() - reverse DNS lookup test (IPv6)"""
        expected = '1.0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.3.d.c.0.0.0.0.8.b.d.0.1.0.0.2' \
        '.ip6.arpa.'
        ip = IP('2001:0DB8::CD30:0:0:0:101')
        self.assertEqual(expected, ip.reverse_dns())

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
            'klass',
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
            'cidr',
            'data_flavour',
            'iprange',
            'issubnet',
            'issupernet',
            'overlaps',
            'size',
            'wildcard',
        )

        for attribute in expected_methods:
            self.assertTrue(hasattr(IPRange, attribute))
            self.assertTrue(callable(eval('IPRange.%s' % attribute)))

#-----------------------------------------------------------------------------
class CIDRTests(TestCase):
    """Tests on CIDR() class objects"""

    def testProperties(self):
        """CIDR() - class interface check (properties)"""
        expected_properties = (
            'ADDR_TYPES',
            'STRATEGIES',
            'addr_type',
            'first',
            'klass',
            'last',
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
            'cidr',
            'data_flavour',
            'hostmask',
            'iprange',
            'issubnet',
            'issupernet',
            'netmask',
            'overlaps',
            'summarize',
            'size',
            'span',
            'wildcard',
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
        cidr1 = CIDR('192.168.0.0/255.255.254.0')
        cidr2 = CIDR('192.168.0.0/23')
        self.assertEqual(cidr1, cidr2)

    def testNonStrictConstructorValidation(self):
        """CIDR() - less restrictive __init__() bitmask/netmask tests"""
        c = CIDR('192.168.1.65/255.255.254.0', strict_bitmask=False)
        c.klass=str
        self.assertEqual(str(c), '192.168.0.0/23')
        self.assertEqual(c[0], '192.168.0.0')
        self.assertEqual(c[-1], '192.168.1.255')

    def testStandardConstructorValidation(self):
        """CIDR() - standard __init__() bitmask/netmask tests"""
        self.assertRaises(ValueError, CIDR, '192.168.1.65/255.255.254.0')
        self.assertRaises(ValueError, CIDR, '192.168.1.65/23')

    def testSlicingIPv4(self):
        """CIDR() - slicing tests (IPv4)"""
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
        cidr = CIDR('192.168.0.0/23', klass=str)

        #   Handy methods.
        self.assertEqual(cidr.first, 3232235520)
        self.assertEqual(cidr.last, 3232236031)

        #   As above with indices.
        self.assertEqual(cidr[0], '192.168.0.0')
        self.assertEqual(cidr[-1], '192.168.1.255')

        expected_list = [ '192.168.0.0', '192.168.0.128', '192.168.1.0',
                          '192.168.1.128' ]

        self.assertEqual(list(cidr[::128]), expected_list)

#FIXME:    def testIndexingAndSlicingIPv6(self):
#FIXME:        """CIDR() - indexing and slicing tests (IPv6)"""
#FIXME:        cidr = CIDR('fe80::/10', klass=str)
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
        self.assertTrue('192.168.0.1' in CIDR('192.168.0.0/24'))
        self.assertTrue('192.168.0.255' in CIDR('192.168.0.0/24'))
        self.assertTrue(CIDR('192.168.0.0/24') in CIDR('192.168.0.0/23'))
        self.assertTrue(CIDR('192.168.0.0/24') in CIDR('192.168.0.0/24'))
        self.assertTrue('ffff::1' in CIDR('ffff::/127'))
        self.assertFalse(CIDR('192.168.0.0/23') in CIDR('192.168.0.0/24'))

    def testEquality(self):
        """CIDR() - equality (__eq__) tests (IPv4/IPv6)"""
        c1 = CIDR('192.168.0.0/24')
        c2 = CIDR('192.168.0.0/24')
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
            self.assertEqual(result, expected)
            if result is not None:
                cidr = CIDR(abbrev)
                self.assertEqual(str(cidr), result)

    def testCIDRToWildcardConversion(self):
        """CIDR() - CIDR -> Wildcard conversion tests (IPv4 only)"""
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
            self.assertEqual(c1.size(), size)
            self.assertEqual(str(c1), cidr)
            self.assertEqual(str(w1), wildcard)
            self.assertEqual(w1.size(), size)
            self.assertEqual(c1, c2)           #   Test __eq__()
            self.assertEqual(str(c1), str(c2)) #   Test __str__() values too.

    def testCIDRIncrements(self):
        """CIDR() - address range increment tests (IPv4)"""
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

        self.assertEqual(expected, actual)

    def testCIDRAddition(self):
        """CIDR() - addition tests (IPv4 + IPv6)"""
        result0 = CIDR('192.168.0.1/32') + CIDR('192.168.0.1/32')
        self.assertEqual(result0, CIDR('192.168.0.1/32'))

        result1 = CIDR('192.168.0.0/24', klass=str) + CIDR('192.168.1.0/24')
        self.assertEqual(result1, '192.168.0.0/23')

        result2 = CIDR('::/128', klass=str) + CIDR('::255.255.255.255/128')
        self.assertEqual(result2, '::/96')

        result3 = CIDR('192.168.0.0/24', klass=str) + CIDR('192.168.255.0/24')
        self.assertEqual(result3, '192.168.0.0/16')

    def testCIDRSubtraction(self):
        """CIDR() - subtraction tests (IPv4 + IPv6)"""
        result0 = CIDR('192.168.0.1/32') - CIDR('192.168.0.1/32')
        self.assertEqual(result0, [])

        result1 = CIDR('192.168.0.0/31', klass=str) - CIDR('192.168.0.1/32')
        self.assertEqual(result1, ['192.168.0.0/32'])

        result2 = CIDR('192.168.0.0/24', klass=str) - CIDR('192.168.0.128/25')
        self.assertEqual(result2, ['192.168.0.0/25'])

        result3 = CIDR('192.168.0.0/24', klass=str) - CIDR('192.168.0.128/27')
        self.assertEqual(result3, ['192.168.0.0/25', '192.168.0.160/27', '192.168.0.192/26'])

        #   Subtracting a larger range from a smaller one results in an empty
        #   list (rather than a negative CIDR - which would be rather odd)!
        result4 = CIDR('192.168.0.1/32') - CIDR('192.168.0.0/24')
        self.assertEqual(result4, [])

    def testCIDRToIPEquality(self):
        """CIDR() - equality tests with IP() objects"""
        #   IPs and CIDRs do not compare favourably (directly), regardless of
        #   the logical operation being performed.
        #
        #   Logically similar, but fundamentally different on a Python and
        #   netaddr level.
        ip = IP('192.168.0.1')
        cidr = CIDR('192.168.0.1/32')

        #   Direct object to object comparisons will always fail.
        self.assertFalse(ip == cidr)
        self.assertFalse(ip != cidr)
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

    def testNetmask(self):
        """CIDR() - netmask tests"""
        c1 = CIDR('192.168.0.0/24', klass=str)
        self.assertEqual(c1.netmask(), '255.255.255.0')
        self.assertEqual(c1.hostmask(), '0.0.0.255')

    def testPrefixlenAssignment(self):
        """CIDR() - prefixlen assignment tests"""

        #   Invalid without turning off strict bitmask checking.
        self.assertRaises(ValueError, CIDR, '192.168.0.1/24')

        c1 = CIDR('192.168.0.1/24', strict_bitmask=False)
        c1.klass = str

        self.assertEqual(c1[0], '192.168.0.0')
        self.assertEqual(c1[-1], '192.168.0.255')

        c1.prefixlen = 23

        self.assertEqual(c1[-1], '192.168.1.255')
        try:
            c1.prefixlen = 33 #   Bad assignment that should fail!
        except ValueError:
            pass
        except:
            self.fail('expected ValueError was not raised!')

        self.assertEqual(c1[-1], '192.168.1.255')
        self.assertEqual(c1.prefixlen, 23)

        c2 = CIDR('192.168.0.0/16', klass=str)

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

        self.assertRaises(ValueError, CIDR, '192.168.0.0/192.168.0.0')
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
        self.assertEqual(CIDR(u'192.168.0.0/24'), CIDR('192.168.0.0/24'))

    def testSupernetSpanning(self):
        """CIDR() - spanning supernet functionality tests (IPv4 / IPv6)"""
        expected = (
            (['192.168.0.0', '192.168.0.0'], '192.168.0.0/32'),
            (['192.168.0.0', '192.168.0.1'], '192.168.0.0/31'),
            (['192.168.0.1', '192.168.0.0'], '192.168.0.0/31'),
            (['192.168.0.0/24', '192.168.1.0/24'], '192.168.0.0/23'),
            (['192.168.3.1/24', '192.168.0.1/24', '192.168.1.1/24'], '192.168.0.0/22'),
            (['192.168.0.*', '192.168.1.0/24'], '192.168.0.0/23'),
            (['192.168.1-2.*', '192.168.3.0/24'], '192.168.0.0/22'),
            (['*.*.*.*', '192.168.0.0/24'], '0.0.0.0/0'),
            (['::', '::255.255.255.255'], '::/96'),
            (['192.168.5.27', '192.168.5.28'], '192.168.5.24/29')   #   Yes, this is correct.
        )

        for comparison in expected:
            (arg, result) = comparison
            cidr = str(CIDR.span(arg))
            self.assertEqual(cidr, result)

    def testSupernetSpanningFailureModes(self):
        """CIDR() - spanning supernet failure mode tests (IPv4)"""
        #   Mixing address types is not allowed!
        self.assertRaises(TypeError, CIDR.span, ['::ffff:192.168.0.0/24', '192.168.1.0/24', ])

    def testSupernetMembership(self):
        """CIDR() - supernet membership tests (IPv4)"""
        self.assertTrue(CIDR('192.168.0.0/24').issupernet(CIDR('192.168.0.0/24')))
        self.assertTrue(CIDR('192.168.0.0/23').issupernet(CIDR('192.168.0.0/24')))
        self.assertFalse(CIDR('192.168.0.0/25').issupernet(CIDR('192.168.0.0/24')))

        #   Mix it up with Wildcard and CIDR.
        self.assertTrue(CIDR('192.168.0.0/24').issupernet(Wildcard('192.168.0.*')))
        self.assertTrue(Wildcard('192.168.0-1.*').issupernet(CIDR('192.168.0.0/24')))
        self.assertTrue(Wildcard('192.168.0-1.*').issupernet(Wildcard('192.168.0.*')))
        self.assertFalse(CIDR('192.168.0.0/25').issupernet(CIDR('192.168.0.0/24')))
        self.assertFalse(Wildcard('192.168.0.0-127').issupernet(CIDR('192.168.0.0/24')))

    def testSubnetMembership(self):
        """CIDR() - subnet membership tests (IPv4)"""
        self.assertTrue(CIDR('192.168.0.0/24').issubnet(CIDR('192.168.0.0/24')))
        self.assertTrue(CIDR('192.168.0.0/25').issubnet(CIDR('192.168.0.0/24')))
        self.assertFalse(CIDR('192.168.0.0/23').issubnet(CIDR('192.168.0.0/24')))

    def testOverlaps(self):
        """CIDR() - overlapping CIDR() object tests (IPv4)"""
        #   A useful property of CIDRs is that they cannot overlap!
#TODO!
        pass

    def testAdjacency(self):
        """CIDR() - adjancent CIDR() object tests (IPv4)"""
        self.assertTrue(CIDR('192.168.0.0/24').adjacent(CIDR('192.168.1.0/24')))
        self.assertTrue(CIDR('192.168.1.0/24').adjacent(CIDR('192.168.0.0/24')))
        self.assertFalse(CIDR('192.168.0.0/24').adjacent(CIDR('192.168.2.0/24')))
        self.assertFalse(CIDR('192.168.2.0/24').adjacent(CIDR('192.168.0.0/24')))


#-----------------------------------------------------------------------------
class WildcardTests(TestCase):
    """Tests on Wildcard() class objects"""

    def testProperties(self):
        """Wildcard() - class interface check (properties)"""
        expected_properties = (
            'ADDR_TYPES',
            'STRATEGIES',
            'addr_type',
            'first',
            'last',
            'klass',
            'strategy',
        )

        for attribute in expected_properties:
            self.assertTrue(hasattr(Wildcard, attribute))
            self.assertFalse(callable(eval('Wildcard.%s' % attribute)))


    def testMethods(self):
        """Wildcard() - class interface check (methods)"""
        expected_methods = (
            'adjacent',
            'cidr',
            'data_flavour',
            'iprange',
            'is_valid',
            'issubnet',
            'issupernet',
            'overlaps',
            'size',
            'wildcard',
        )

        for attribute in expected_methods:
            self.assertTrue(hasattr(Wildcard, attribute))
            self.assertTrue(callable(eval('Wildcard.%s' % attribute)))

    def testWildcardPositiveValidity(self):
        """Wildcard() - positive validity tests"""
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
            self.assertEqual(wc.size(), expected_size)

    def testWildcardNegativeValidity(self):
        """Wildcard() - negative validity tests"""
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
            self.assertRaises(AddrFormatError, Wildcard, wildcard)

    def testWildcardToCIDRConversion(self):
        """Wildcard() - Wildcard -> CIDR coversion tests"""
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
            self.assertEqual(w1.size(), size)
            self.assertEqual(str(w1), wildcard)
            self.assertEqual(str(c1), cidr)
            self.assertEqual(c1.size(), size)
            self.assertEqual(w1, w2)           #   Test __eq__()
            self.assertEqual(str(w1), str(w2)) #   Test __str__() values too.

    def testWilcardWithNonCIDREquivalents(self):
        """Wildcard() - no CIDR equivalent tests"""
        w1 = Wildcard('10.0.0.5-6')
        self.assertRaises(AddrConversionError, w1.cidr)

    def testWildcardToCIDRComparisons(self):
        """Wildcard() - comparison against CIDR() object tests"""
        #   Basically CIDRs and Wildcards are subclassed from the same parent
        #   class so should compare favourably.
        cidr1 = CIDR('192.168.0.0/24')
        cidr2 = CIDR('192.168.1.0/24')
        wc1 = Wildcard('192.168.0.*')

        #   Positives.
        self.assertTrue(cidr1 == wc1)
        self.assertTrue(cidr1 >= wc1)
        self.assertTrue(cidr1 <= wc1)
        self.assertTrue(cidr2 > wc1)
        self.assertTrue(wc1 < cidr2)

        #   Negatives.
        self.assertFalse(cidr1 != wc1)
        self.assertFalse(cidr1 > wc1)
        self.assertFalse(cidr1 < wc1)
        self.assertFalse(cidr2 <= wc1)
        self.assertFalse(cidr2 < wc1)
        self.assertFalse(wc1 >= cidr2)
        self.assertFalse(wc1 > cidr2)

    def testWildcardToIPEquality(self):
        """Wildcard() - equality tests with IP() objects"""
        #   IPs and Wildcards current do not compare favourably, regardless
        #   of the operation.
        #
        #   Logically similar, but fundamentally different at a Python and
        #   netaddr level.
        ip = IP('192.168.0.1')
        wc = Wildcard('192.168.0.1')

        #   Direct object to object comparisons will always fail.
        self.assertFalse(ip == wc)
        self.assertFalse(ip != wc)
        self.assertFalse(ip > wc)
        self.assertFalse(ip >= wc)
        self.assertFalse(ip < wc)
        self.assertFalse(ip <= wc)

        #   Compare with Wildcard object lower boundary.
        self.assertTrue(ip == wc[0])
        self.assertTrue(ip >= wc[0])
        self.assertTrue(ip <= wc[0])
        self.assertFalse(ip != wc[0])
        self.assertFalse(ip > wc[0])
        self.assertFalse(ip < wc[0])

        #   Compare with Wildcard object upper boundary.
        self.assertTrue(ip == wc[-1])
        self.assertTrue(ip >= wc[-1])
        self.assertTrue(ip <= wc[-1])
        self.assertFalse(ip != wc[-1])
        self.assertFalse(ip > wc[-1])
        self.assertFalse(ip < wc[-1])

    def testWildcardIncrements(self):
        """Wildcard() - address range increment tests"""
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

        self.assertEqual(expected, actual)

    def testOverlaps(self):
        """Wildcard() - overlapping Wildcard() object tests"""
        self.assertTrue(Wildcard('192.168.0.0-31').overlaps(Wildcard('192.168.0.16-63')))
        self.assertFalse(Wildcard('192.168.0.0-7').overlaps(Wildcard('192.168.0.16-23')))

    def testAdjacency(self):
        """Wildcard() - adjancent Wildcard() object tests"""
        self.assertTrue(Wildcard('192.168.0.*').adjacent(Wildcard('192.168.1.*')))
        self.assertTrue(Wildcard('192.168.1.*').adjacent(Wildcard('192.168.0.*')))
        self.assertFalse(Wildcard('192.168.0.*').adjacent(Wildcard('192.168.2.*')))
        self.assertFalse(Wildcard('192.168.2.*').adjacent(Wildcard('192.168.0.*')))

#-----------------------------------------------------------------------------
class nrangeTests(TestCase):
    """Tests on the nrange() function"""
    def testAddrObjectIteration(self):
        """nrange() - yield Addr() object test (IPv4)"""
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

        start_addr = netaddr.address.Addr('192.168.0.0')
        stop_addr = netaddr.address.Addr('192.168.0.32')
        for i, addr in enumerate(nrange(start_addr, stop_addr, 4)):
            self.assertEqual(str(addr), expected[i])

    def testIntegerIteration(self):
        """nrange() - yield positive integer test (IPv6)"""
        expected_type = int
        expected_list = [0,4,8,12,16]

        saved_list = []
        #   IPv6 addresses auto-detected, as int.
        for addr in nrange('::', '::10', 4, klass=expected_type):
            self.assertEqual(type(addr), expected_type)
            saved_list.append(addr)

        self.assertEqual(saved_list, expected_list)

    def testNegativeIntegerIteration(self):
        """nrange() - yield negative integer test (IPv6)"""
        expected_type = int
        expected_list = [16,12,8,4,0]

        saved_list = []
        #   IPv6 addresses auto-detected, negative step as int.
        for addr in nrange('::10', '::', -4, klass=expected_type):
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
        for addr in nrange('ff00::10', 'ff00::', -4, klass=hex):
            self.assertEqual(type(addr), str)
            saved_list.append(addr.lower().rstrip('l'))

        self.assertEqual(saved_list, expected_list)

    def testIPObjectIteration(self):
        """nrange() - yield IP() object test (IPv4)"""
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
            self.assertTrue(isinstance(addr, IP))
            #   Save addresses as string values for comparison.
            saved_list.append(str(addr))

        self.assertEqual(saved_list, expected_list)

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    unit_test_suite = TestSuite()
    for test_case in TestLoader().loadTestsFromName(__name__):
        unit_test_suite.addTest(test_case)
    TextTestRunner(verbosity=2).run(unit_test_suite)
