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

from netaddr.strategy import *

#-----------------------------------------------------------------------------
#   Unit Tests.
#-----------------------------------------------------------------------------

class Test_AddrStrategy_IPv4(unittest.TestCase):
    """
    Test basic IP version 4 address support using AddrStrategy.
    """
    def testExpectedValues(self):
        strategy = AddrStrategy(addr_type=AT_INET,
            width=32,
            word_size=8,
            word_fmt='%d',
            delimiter='.',
            hex_words=False)

        #DEBUG: print strategy.description()

        b = '11000000.10101000.00000000.00000001'
        i = 3232235521
        t = (192, 168, 0, 1)
        s = '192.168.0.1'

        #DEBUG: print 'expected bits :', b
        #DEBUG: print 'expected int  :', i
        #DEBUG: print 'expected words:', t
        #DEBUG: print 'expected str  :', s

        #   bits to x
        self.failUnless(strategy.bits_to_int(b) == i)
        self.failUnless(strategy.bits_to_str(b) == s)
        self.failUnless(strategy.bits_to_words(b) == t)

        #   int to x
        self.failUnless(strategy.int_to_bits(i) == b)
        self.failUnless(strategy.int_to_str(i) == s)
        self.failUnless(strategy.int_to_words(i) == t)

        #   str to x
        self.failUnless(strategy.str_to_bits(s) == b)
        self.failUnless(strategy.str_to_int(s) == i)
        self.failUnless(strategy.str_to_words(s) == t)

        #   words to x
        self.failUnless(strategy.words_to_bits(t) == b)
        self.failUnless(strategy.words_to_int(t) == i)
        self.failUnless(strategy.words_to_str(t) == s)

        self.failUnless(strategy.words_to_bits(list(t)) == b)
        self.failUnless(strategy.words_to_int(list(t)) == i)
        self.failUnless(strategy.words_to_str(list(t)) == s)

#-----------------------------------------------------------------------------
class Test_AddrStrategy_IPv6(unittest.TestCase):
    """
    Test basic IP version 6 address support using AddrStrategy.

    NB - AddrStrategy does not support compact string representation of IPv6
    addresses.
    """
    def testExpectedValues(self):
        strategy = AddrStrategy(addr_type=AT_INET6,
            width=128,
            word_size=16,
            word_fmt='%x',
            delimiter=':')

        #DEBUG: print strategy.description()

        b = '0000000000000000:0000000000000000:0000000000000000:' \
            '0000000000000000:0000000000000000:0000000000000000:' \
            '1111111111111111:1111111111111110'
        i = 4294967294
        t = (0, 0, 0, 0, 0, 0, 0xffff, 0xfffe)
        s = '0:0:0:0:0:0:ffff:fffe'

        #DEBUG: print 'expected bits :', b
        #DEBUG: print 'expected int  :', i
        #DEBUG: print 'expected words:', t
        #DEBUG: print 'expected str  :', s

        #   bits to x
        self.failUnless(strategy.bits_to_int(b) == i)
        self.failUnless(strategy.bits_to_str(b) == s)
        self.failUnless(strategy.bits_to_words(b) == t)

        #   int to x
        self.failUnless(strategy.int_to_bits(i) == b)
        self.failUnless(strategy.int_to_str(i) == s)
        self.failUnless(strategy.int_to_words(i) == t)

        #   str to x
        self.failUnless(strategy.str_to_bits(s) == b)
        self.failUnless(strategy.str_to_int(s) == i)
        self.failUnless(strategy.str_to_words(s) == t)

        #   words to x
        self.failUnless(strategy.words_to_bits(t) == b)
        self.failUnless(strategy.words_to_int(t) == i)
        self.failUnless(strategy.words_to_str(t) == s)

        self.failUnless(strategy.words_to_bits(list(t)) == b)
        self.failUnless(strategy.words_to_int(list(t)) == i)
        self.failUnless(strategy.words_to_str(list(t)) == s)

#-----------------------------------------------------------------------------
class Test_AddrStrategy_MAC(unittest.TestCase):
    """
    Test basic MAC (Media Access Control) address support using AddrStrategy.
    """
    def testExpectedValues(self):
        strategy = AddrStrategy(addr_type=AT_LINK,
            width=48,
            word_size=8,
            word_fmt='%02x',
            delimiter=':')

        #DEBUG: print strategy.description()

        #   A real address.
        #b = '00000000:00001111:00011111:00010010:11100111:00110011'
        #i = 64945841971
        #t = (0x0, 0x0F, 0x1F, 0x12, 0xE7, 0x33)
        #s = '00:0f:1f:12:e7:33'

        b = '00000000:00000000:11111111:11111111:11111111:11111110'
        i = 4294967294
        t = (0x0, 0x0, 0xff, 0xff, 0xff, 0xfe)
        s = '00:00:ff:ff:ff:fe'

        #DEBUG: print 'expected bits :', b
        #DEBUG: print 'expected int  :', i
        #DEBUG: print 'expected words:', t
        #DEBUG: print 'expected str  :', s

        #   bits to x
        self.failUnless(strategy.bits_to_int(b) == i)
        self.failUnless(strategy.bits_to_str(b) == s)
        self.failUnless(strategy.bits_to_words(b) == t)

        #   int to x
        self.failUnless(strategy.int_to_bits(i) == b)
        self.failUnless(strategy.int_to_str(i) == s)
        self.failUnless(strategy.int_to_words(i) == t)

        #   str to x
        self.failUnless(strategy.str_to_bits(s) == b)
        self.failUnless(strategy.str_to_int(s) == i)
        self.failUnless(strategy.str_to_words(s) == t)

        #   words to x
        self.failUnless(strategy.words_to_bits(t) == b)
        self.failUnless(strategy.words_to_int(t) == i)
        self.failUnless(strategy.words_to_str(t) == s)

        self.failUnless(strategy.words_to_bits(list(t)) == b)
        self.failUnless(strategy.words_to_int(list(t)) == i)
        self.failUnless(strategy.words_to_str(list(t)) == s)

#-----------------------------------------------------------------------------
class Test_AddrStrategy_Cisco_MAC(unittest.TestCase):
    """
    Test MAC (Media Access Control) address support using AddrStrategy for Cisco's own string format.
    """
    def testExpectedValues(self):
        strategy = AddrStrategy(addr_type=AT_LINK,
            width=48,
            word_size=16,
            word_fmt='%04x',
            delimiter='.')

        #DEBUG: print strategy.description()

        b = '0000000000000000.1111111111111111.1111111111111110'
        i = 4294967294
        t = (0x0, 0xffff, 0xfffe)
        s = '0000.ffff.fffe'


        #DEBUG: print 'expected bits :', b
        #DEBUG: print 'expected int  :', i
        #DEBUG: print 'expected words:', t
        #DEBUG: print 'expected str  :', s

        #   bits to x
        self.failUnless(strategy.bits_to_int(b) == i)
        self.failUnless(strategy.bits_to_str(b) == s)
        self.failUnless(strategy.bits_to_words(b) == t)

        #   int to x
        self.failUnless(strategy.int_to_bits(i) == b)
        self.failUnless(strategy.int_to_str(i) == s)
        self.failUnless(strategy.int_to_words(i) == t)

        #   str to x
        self.failUnless(strategy.str_to_bits(s) == b)
        self.failUnless(strategy.str_to_int(s) == i)
        self.failUnless(strategy.str_to_words(s) == t)

        #   words to x
        self.failUnless(strategy.words_to_bits(t) == b)
        self.failUnless(strategy.words_to_int(t) == i)
        self.failUnless(strategy.words_to_str(t) == s)

        self.failUnless(strategy.words_to_bits(list(t)) == b)
        self.failUnless(strategy.words_to_int(list(t)) == i)
        self.failUnless(strategy.words_to_str(list(t)) == s)

#-----------------------------------------------------------------------------
class Test_IPv4Strategy(unittest.TestCase):
    """
    Test IP version 4 address support using the optimised subclass of AddrStrategy - MUCH FASTER!
    """
    def testExpectedValues(self):
        strategy = IPv4Strategy()

        b = '11000000.10101000.00000000.00000001'
        i = 3232235521
        t = (192, 168, 0, 1)
        s = '192.168.0.1'

        #DEBUG: print 'expected bits :', b
        #DEBUG: print 'expected int  :', i
        #DEBUG: print 'expected words:', t
        #DEBUG: print 'expected str  :', s

        #   bits to x
        self.failUnless(strategy.bits_to_int(b) == i)
        self.failUnless(strategy.bits_to_str(b) == s)
        self.failUnless(strategy.bits_to_words(b) == t)

        #   int to x
        self.failUnless(strategy.int_to_bits(i) == b)
        self.failUnless(strategy.int_to_str(i) == s)
        self.failUnless(strategy.int_to_words(i) == t)

        #   str to x
        self.failUnless(strategy.str_to_bits(s) == b)
        self.failUnless(strategy.str_to_int(s) == i)
        self.failUnless(strategy.str_to_words(s) == t)

        #   words to x
        self.failUnless(strategy.words_to_bits(t) == b)
        self.failUnless(strategy.words_to_int(t) == i)
        self.failUnless(strategy.words_to_str(t) == s)

        self.failUnless(strategy.words_to_bits(list(t)) == b)
        self.failUnless(strategy.words_to_int(list(t)) == i)
        self.failUnless(strategy.words_to_str(list(t)) == s)

#-----------------------------------------------------------------------------
class Test_IPv6Strategy(unittest.TestCase):
    """
    Test IP version 6 address support using the subclass of AddrStrategy.

    This strategy supports all IPv6 address forms found in RFC 4291.
    """
    def setUp(self):
        self.strategy = IPv6Strategy()

        #   Minimum required methods.
        self.methods = set([
            #   Binary string form methods.
            'valid_bits', 'bits_to_int', 'bits_to_str', 'bits_to_words',
            #   Integer methods.
            'valid_int', 'int_to_bits', 'int_to_str', 'int_to_words',
            #   String form methods.
            'valid_str', 'str_to_words', 'str_to_bits', 'str_to_int',
            #   Word list methods.
            'valid_words', 'word_to_bits', 'words_to_bits', 'words_to_int',
            'words_to_str',
        ])

        #   Minimum required properties.
        self.properties = set(['addr_type', 'delimiter', 'hex_words',
            'min_int', 'max_int', 'max_word', 'min_word', 'name',
            'width', 'word_base', 'word_count', 'word_fmt', 'word_size'])


    def testInterface(self):
        """
        Check strategy instance for the supported interface methods
        and properties.
        """
        callables = set([attr for attr in dir(self.strategy)
                        if callable(eval('self.strategy.%s' % attr)) is True
                            and not attr.startswith('__')])

        non_callables = set([attr for attr in dir(self.strategy)
                        if callable(eval('self.strategy.%s' % attr)) is False
                            and not attr.startswith('__')])

        self.failUnless(self.methods.issubset(callables))
        self.failUnless(self.properties.issubset(non_callables))

    def testAddressStringValidity(self):
        """
        Check strategy instance for address parsing capabilities.
        """
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

        #strategy = IPv6
        strategy = IPv6Strategy()

        for addr in valid_addrs:
            self.failUnless(strategy.valid_str(addr),
                'Address %r is expected to be valid!' % addr)

        for addr in invalid_addrs:
            self.failIf(strategy.valid_str(addr),
                'Address %r is expected to be invalid!' % str(addr))

    def testStringVariants(self):
        """
        Tests several different string representations of the same address
        value.
        """
        strategy = IPv6Strategy()

        expected_int = 42540766411282592856903984951992014763

        all_the_same = (
            '2001:0db8:0000:0000:0000:0000:1428:57ab',
            '2001:0db8:0000:0000:0000::1428:57ab',
            '2001:0db8:0:0:0:0:1428:57ab',
            '2001:0db8:0:0::1428:57ab',
            '2001:0db8::1428:57ab',
            '2001:db8::1428:57ab',
        )

        for addr in all_the_same:
            self.failUnless(strategy.str_to_int(addr) == expected_int)

    def testAddressStringEquivalence(self):
        """
        Check compaction algorithm for errors.
        """
        #   Positive testing.
        valid_addrs = {
            #   RFC 4291
            'FEDC:BA98:7654:3210:FEDC:BA98:7654:3210' : 'fedc:ba98:7654:3210:fedc:ba98:7654:3210',
            '1080:0:0:0:8:800:200C:417A' : '1080::8:800:200c:417a', #   a unicast address
            'FF01:0:0:0:0:0:0:43' : 'ff01::43', #   a multicast address
            '0:0:0:0:0:0:0:1' : '::1',          #   the loopback address
            '0:0:0:0:0:0:0:0' : '::',           #   the unspecified addresses
        }

        strategy = IPv6Strategy()

        for long_form, short_form in valid_addrs.items():
            int_val = strategy.str_to_int(long_form)
            calc_short_form = strategy.int_to_str(int_val)
            self.failUnless(calc_short_form == short_form,
                'Expected %r but got %r!' % (short_form, calc_short_form))

    def test_StringConversions(self):
        strategy = IPv6Strategy()

        addr = 'ffff:ffff::ffff:ffff'
        expected_int = 340282366841710300949110269842519228415

        int_addr = strategy.str_to_int(addr)

        self.failUnless(int_addr == expected_int)

        self.failUnless(strategy.int_to_str(int_addr, False) == \
            'ffff:ffff:0:0:0:0:ffff:ffff')

        self.failUnless(strategy.int_to_str(int_addr) == \
            'ffff:ffff::ffff:ffff')

        words = strategy.int_to_words(int_addr)

        self.failUnless(words == (65535, 65535, 0, 0, 0, 0, 65535, 65535))
        self.failUnless(strategy.words_to_int(words) == expected_int)

#-----------------------------------------------------------------------------
#   MAC Tests
#    def testStrategyConfigSettings(self):
#        mac_addr = '00-C0-29-C2-52-FF'
#        mac_addr_int = 825334321919
#
#        mac48 = EUI48Strategy(
#            delimiter=':', zero_fill=False, is_lcase=True)
#
#        self.failUnless(mac48.int_to_str(825334321919) == '0:c0:29:c2:52:ff')
#        mac48.delimiter = '-'
#        mac48.zero_fill = True
#        self.failUnless(mac48.int_to_str(825334321919) == '00-c0-29-c2-52-ff')
#        mac48.is_lcase = False
#        self.failUnless(mac48.int_to_str(825334321919) == '00-C0-29-C2-52-FF')
#



#-----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
