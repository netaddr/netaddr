#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
This is the new proposal for internals of Addr and AddrRange base classes to
facilitate better policing of assignments and simpler logic and cleaner code
in sub classes.

This will make up part of netaddr release 0.5
"""
from netaddr import AddrFormatError, AT_UNSPEC, AT_INET, AT_INET6, AT_LINK, \
    AT_EUI64

from netaddr.strategy import ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64, \
    AddrStrategy

#   *** To be added to netaddr.__init__.py ***
AT_STRATEGIES = {
    #   Address Type : Strategy Object.
    AT_UNSPEC   : None,
    AT_INET     : ST_IPV4,
    AT_INET6    : ST_IPV6,
    AT_LINK     : ST_EUI48,
    AT_EUI64    : ST_EUI64,
}

#   *** To be added to netaddr.__init__.py ***
AT_NAMES = {
    #   Address Type : Strategy Object.
    AT_UNSPEC   : 'unspecified',
    AT_INET     : 'IPv4',
    AT_INET6    : 'IPv6',
    AT_LINK     : 'MAC',
    AT_EUI64    : 'EUI-64',
}

import unittest

#-----------------------------------------------------------------------------
class Addr(object):
    """
    Base class representing individual addresses.
    """
    #   Class properties.
    STRATEGIES = (ST_IPV4, ST_IPV6, ST_EUI48, ST_EUI64)
    ADDR_TYPES = (AT_INET, AT_INET6, AT_LINK, AT_EUI64)

    def __init__(self, addr, addr_type=AT_UNSPEC):
        #   NB - These should only be are accessed via property() methods.
        self.__strategy = None
        self.__value = None
        self.__addr_type = None

        self.addr_type = addr_type
        self.value = addr

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   START of accessor setup.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def _get_addr_type(self):
        return self.__addr_type

    def _set_addr_type(self, val):
        if val == AT_UNSPEC:
            pass
        else:
            #   Validate addr_type and keep in sync with strategy.
            if val not in self.__class__.ADDR_TYPES:
                raise ValueError('addr_type %r is invalid for objects of ' \
                    'the %s() class!' % (val, self.__class__.__name__))
            self.__strategy = AT_STRATEGIES[val]

        self.__addr_type = val

    def _get_value(self):
        return self.__value

    def _set_value(self, val):
        #   Select a strategy object for this address.
        if self.addr_type == AT_UNSPEC:
            for strategy in self.__class__.STRATEGIES:
                if strategy.valid_str(val):
                    self.strategy = strategy
                    break

        #   Make sure we picked up a strategy object.
        if self.__strategy is None:
            raise AddrFormatError('%r is not a recognised address ' \
                'format!' % val)

        #   Calculate and validate the value for this address.
        if isinstance(val, (str, unicode)):
            val = self.strategy.str_to_int(val)
        elif isinstance(val, (int, long)):
            if not self.strategy.valid_int(val):
                raise OverflowError('value %r cannot be represented ' \
                    'in %d bit(s)!' % (val, self.strategy.width))
        self.__value = val

    def _get_strategy(self):
        return self.__strategy

    def _set_strategy(self, val):
        #   Validate strategy and keep in sync with addr_type.
        if not issubclass(val.__class__, AddrStrategy):
            raise TypeError('%r is not an object of (sub)class of ' \
                'AddrStrategy!' % val)
        self.__addr_type = val.addr_type

        self.__strategy = val

    #   Initialise accessors and tidy the namespace.
    value = property(_get_value, _set_value, None,
        """
        The value of this address object (a network byte order integer).
        """)
    del _get_value, _set_value

    addr_type = property(_get_addr_type, _set_addr_type, None,
        """
        An integer value indicating the specific type of this address object.
        """)
    del _get_addr_type, _set_addr_type

    strategy = property(_get_strategy, _set_strategy, None,
        """
        An instance of the AddrStrategy (sub)class.
        """)
    del _get_strategy, _set_strategy

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   END of accessor setup.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def __int__(self):
        """
        @return: The value of this address as an network byte order integer.
        """
        return self.value

    def __long__(self):
        """
        @return: The value of this address as an network byte order integer.
        """
        return self.value

    def bits(self):
        """
        @return: A human-readable binary digit string for this address type.
        """
        return self.strategy.int_to_bits(self.value)

    def __len__(self):
        """
        @return: The size of this address (in bits).
        """
        return self.strategy.width

    def __str__(self):
        """
        @return: The common string representation for this address type.
        """
        return self.strategy.int_to_str(self.value)

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        return "netaddr.address.%s(%r)" % (self.__class__.__name__, str(self))

#-----------------------------------------------------------------------------
class IP(Addr):
    """
    Class representing individual IPv4 or IPv6 addresses.
    """
    #   Class properties.
    STRATEGIES = (ST_IPV4, ST_IPV6)
    ADDR_TYPES = (AT_INET, AT_INET6)

    def __init__(self, addr, addr_type=AT_UNSPEC):
        #   NB - This should only be are accessed via property() methods.
        self.__masklen = None

        #   Check for prefix and strip it out.
        masklen = None
        if isinstance(addr, (str, unicode)):
            if '/' in addr:
                (addr, masklen) = addr.split('/', 1)

        #   Call super class constructor before processing prefix to detect
        #   strategy, valid base address, etc.
        super(IP, self).__init__(addr, addr_type)

        #   Perform tests on netmask.
        if masklen is None:
            self.__masklen = self.strategy.width
        else:
            self.masklen = masklen

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   START of accessor setup.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def _get_masklen(self):
        return self.__masklen

    def _set_masklen(self, val):
        try:
            #   Basic integer subnet prefix.
            masklen = int(val)
        except ValueError:
            #   Convert possible subnet mask to integer subnet prefix.
            ip = IP(val)
            if self.addr_type != ip.addr_type:
                raise ValueError('address and netmask type mismatch!')
            if not ip.is_netmask():
                raise ValueError('%s is not a valid netmask!' % ip)
            masklen = ip.netmask_bits()

        #   Validate subnet prefix.
        if not 0 <= masklen <= self.strategy.width:
            raise ValueError('%d is an invalid CIDR prefix for %s!' \
                % (masklen, AT_NAMES[self.addr_type]))

        self.__masklen = masklen

    masklen = property(_get_masklen, _set_masklen, None,
        """The CIDR subnet prefix for this IP address.""")
    del _get_masklen, _set_masklen

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    #   END of accessor setup.
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    def is_netmask(self):
        """
        @return: C{True} if this addr is a mask that would return a host id,
        C{False} otherwise.
        """
        #   There is probably a better way to do this.
        #   Change at will, just don't break the unit tests :-)
        bits = self.strategy.int_to_bits(self.value).replace('.', '')

        if bits[0] != '1':
            #   Fail fast, if possible.
            return False

        #   Trim our search a bit.
        bits = bits.lstrip('1')

        seen_zero = False
        for i in bits:
            if i == '0' and seen_zero is False:
                seen_zero = True
            elif i == '1' and seen_zero is True:
                return False

        return True

    def netmask_bits(self):
        """
        @return: The number of bits set to one in this address if it is a
        valid netmask, otherwise the width (in bits) for the given address
        type is returned instead.
        """
        if not self.is_netmask():
            return self.strategy.width

        bits = self.strategy.int_to_bits(self.value)
        translate_str = ''.join([chr(_i) for _i in range(256)])
        mask_bits = bits.translate(translate_str, '.0')
        mask_length = len(mask_bits)

        if not 1 <= mask_length <= self.strategy.width:
            raise ValueError('Unexpected mask length %d for address type!' \
                % mask_length)

        return mask_length

    def __repr__(self):
        """
        @return: An executable Python statement that can recreate an object
            with an equivalent state.
        """
        if self.masklen == self.strategy.width:
            return "netaddr.address.%s('%s')" % (self.__class__.__name__,
                str(self))

        return "netaddr.address.%s('%s/%d')" % (self.__class__.__name__,
            str(self), self.masklen)

#-----------------------------------------------------------------------------
class EUI(Addr):
    """
    Class representing individual MAC, EUI-48 or EUI-64 addresses.
    """
    #   Class properties.
    STRATEGIES = (ST_EUI48, ST_EUI64)
    ADDR_TYPES = (AT_LINK, AT_EUI64)

#-----------------------------------------------------------------------------
#   Unit Tests.
#-----------------------------------------------------------------------------

class Test_Addr(unittest.TestCase):

    def test_assignments(self):
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

#-----------------------------------------------------------------------------
class Test_IP(unittest.TestCase):

    def test_assignments_IPv4(self):
        """
        Checks a list of addresses expected to be valid.
        """
        ip = IP('192.168.0.1')
        self.failUnless(ip.value == 3232235521)
        self.failUnless(ip.addr_type == AT_INET)
        self.failUnless(ip.strategy == ST_IPV4)
        self.failUnless(ip.masklen == 32)

        #   Prefix /32 for IPv4 addresses should be implicit.
        self.failUnless(repr(ip) == "netaddr.address.IP('192.168.0.1')")
        ip.masklen = 24
        self.failUnless(repr(ip) == "netaddr.address.IP('192.168.0.1/24')")

    def test_assignments_IPv6(self):
        """
        Checks a list of addresses expected to be valid.
        """
        ip = IP('fe80::4472:4b4a:616d')
        self.failUnless(ip.value == 338288524927261089654018972099027820909)
        self.failUnless(ip.addr_type == AT_INET6)
        self.failUnless(ip.strategy == ST_IPV6)
        self.failUnless(ip.masklen == 128)

        #   Prefix /128 for IPv6 addresses should be implicit.
        self.failUnless(repr(ip) == "netaddr.address.IP('fe80::4472:4b4a:616d')")
        ip.masklen = 64
        self.failUnless(repr(ip) == "netaddr.address.IP('fe80::4472:4b4a:616d/64')")

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
