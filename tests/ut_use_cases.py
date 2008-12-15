#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------

import unittest

import os
import sys
import pprint

#   Run all unit tests for all modules.
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path)

from netaddr import *
from netaddr.strategy import IPv4StrategyOpt

#-----------------------------------------------------------------------------
#   Unit Tests.
#-----------------------------------------------------------------------------
class Test_Interfaces(unittest.TestCase):
    """
    Interfaces checks ensure that external interface is always monitored for
    unwitting changes.
    """
    def testEUI(self):
        """
        EUI class interface tests.
        """
        obj = EUI('0-0-0-0-0-0')

        IF_PROPERTIES = (
            'EUI.ADDR_TYPES',
            'EUI.STRATEGIES',
            'EUI.addr_type',
            'EUI.strategy',
            'EUI.value'
        )

        IF_METHODS = (
            'EUI.bits',
            'EUI.ei',
            'EUI.eui64',
            'EUI.info',
            'EUI.ipv6_link_local',
            'EUI.oui',
        )

        IF_SPECIALS = (
            'EUI.__class__',
            'EUI.__delattr__',
            'EUI.__dict__',
            'EUI.__doc__',
            'EUI.__eq__',
            'EUI.__ge__',
            'EUI.__getattribute__',
            'EUI.__getitem__',
            'EUI.__gt__',
            'EUI.__hash__',
            'EUI.__hex__',
            'EUI.__iadd__',
            'EUI.__init__',
            'EUI.__int__',
            'EUI.__isub__',
            'EUI.__iter__',
            'EUI.__le__',
            'EUI.__len__',
            'EUI.__long__',
            'EUI.__lt__',
            'EUI.__module__',
            'EUI.__ne__',
            'EUI.__new__',
            'EUI.__reduce__',
            'EUI.__reduce_ex__',
            'EUI.__repr__',
            'EUI.__setattr__',
            'EUI.__setitem__',
            'EUI.__str__',
            'EUI.__weakref__'
        )

        methods = []
        properties = []
        specials = []

        for attr in dir(obj):
            stmt = '.'.join(['EUI', attr])
            if attr.startswith('__') and attr.endswith('__'):
                specials.append(stmt)
            elif callable(eval(stmt)):
                methods.append(stmt)
            else:
                properties.append(stmt)

        methods.sort()
        properties.sort()
        specials.sort()

#DEBUG:        print 'Specials:', pprint.pformat(list(specials))
#DEBUG:        print 'Properties:', pprint.pformat(list(properties))
#DEBUG:        print 'Methods:', pprint.pformat(list(methods))

#DEBUG:        print set(IF_SPECIALS) ^ set(specials)
        self.failUnless(IF_SPECIALS == tuple(specials))
#DEBUG:        print set(IF_METHODS) ^ set(methods)
        self.failUnless(set(IF_METHODS) == set(methods))
#DEBUG:        print set(IF_PROPERTIES) ^ set(properties)
        self.failUnless(IF_PROPERTIES == tuple(properties))


    def testIP(self):
        """
        IP class interface tests.
        """
        obj = IP('192.168.0.1')

        IF_PROPERTIES = (
            'IP.ADDR_TYPES',
            'IP.STRATEGIES',
            'IP.TRANSLATE_STR',
            'IP.addr_type',
            'IP.prefixlen',
            'IP.strategy',
            'IP.value'
        )

        IF_METHODS = (
            'IP.bits',
            'IP.cidr',
            'IP.hostname',
            'IP.info',
            'IP.ipv4',
            'IP.ipv6',
            'IP.is_hostmask',
            'IP.is_multicast',
            'IP.is_netmask',
            'IP.is_unicast',
            'IP.netmask_bits',
            'IP.reverse_dns'
        )

        IF_SPECIALS = (
            'IP.__class__',
            'IP.__delattr__',
            'IP.__dict__',
            'IP.__doc__',
            'IP.__eq__',
            'IP.__ge__',
            'IP.__getattribute__',
            'IP.__getitem__',
            'IP.__gt__',
            'IP.__hash__',
            'IP.__hex__',
            'IP.__iadd__',
            'IP.__init__',
            'IP.__int__',
            'IP.__isub__',
            'IP.__iter__',
            'IP.__le__',
            'IP.__len__',
            'IP.__long__',
            'IP.__lt__',
            'IP.__module__',
            'IP.__ne__',
            'IP.__new__',
            'IP.__reduce__',
            'IP.__reduce_ex__',
            'IP.__repr__',
            'IP.__setattr__',
            'IP.__setitem__',
            'IP.__str__',
            'IP.__weakref__'
        )

        methods = []
        properties = []
        specials = []

        for attr in dir(obj):
            stmt = '.'.join(['IP', attr])
            if attr.startswith('__') and attr.endswith('__'):
                specials.append(stmt)
            elif callable(eval(stmt)):
                methods.append(stmt)
            else:
                properties.append(stmt)

        methods.sort()
        properties.sort()
        specials.sort()

#DEBUG:        print 'Specials:', pprint.pformat(list(specials))
#DEBUG:        print 'Properties:', pprint.pformat(list(properties))
#DEBUG:        print 'Methods:', pprint.pformat(list(methods))

#DEBUG:        print set(IF_SPECIALS) ^ set(specials)
        self.failUnless(IF_SPECIALS == tuple(specials))
#DEBUG:        print set(IF_METHODS) ^ set(methods)
        self.failUnless(IF_METHODS == tuple(methods))
#DEBUG:        print set(IF_PROPERTIES) ^ set(properties)
        self.failUnless(IF_PROPERTIES == tuple(properties))


    def testCIDR(self):
        """
        CIDR class interface tests.
        """
        obj = CIDR('192.168.0.0/16')

        IF_PROPERTIES = (
            'CIDR.ADDR_TYPES',
            'CIDR.STRATEGIES',
            'CIDR.addr_type',
            'CIDR.first',
            'CIDR.klass',
            'CIDR.last',
            'CIDR.prefixlen',
            'CIDR.strategy'
        )

        IF_METHODS = (
            'CIDR.abbrev_to_verbose',
            'CIDR.adjacent',
            'CIDR.cidr',
            'CIDR.data_flavour',
            'CIDR.hostmask',
            'CIDR.iprange',
            'CIDR.issubnet',
            'CIDR.issupernet',
            'CIDR.netmask',
            'CIDR.overlaps',
            'CIDR.size',
            'CIDR.supernet',
            'CIDR.wildcard',
        )

        IF_SPECIALS = (
            'CIDR.__add__',
            'CIDR.__class__',
            'CIDR.__contains__',
            'CIDR.__delattr__',
            'CIDR.__dict__',
            'CIDR.__doc__',
            'CIDR.__eq__',
            'CIDR.__ge__',
            'CIDR.__getattribute__',
            'CIDR.__getitem__',
            'CIDR.__gt__',
            'CIDR.__hash__',
            'CIDR.__iadd__',
            'CIDR.__init__',
            'CIDR.__isub__',
            'CIDR.__iter__',
            'CIDR.__le__',
            'CIDR.__len__',
            'CIDR.__lt__',
            'CIDR.__module__',
            'CIDR.__ne__',
            'CIDR.__new__',
            'CIDR.__reduce__',
            'CIDR.__reduce_ex__',
            'CIDR.__repr__',
            'CIDR.__setattr__',
            'CIDR.__str__',
            'CIDR.__sub__',
            'CIDR.__weakref__'
        )

        methods = []
        properties = []
        specials = []

        for attr in dir(obj):
            stmt = '.'.join(['CIDR', attr])
            if attr.startswith('__') and attr.endswith('__'):
                specials.append(stmt)
            elif callable(eval(stmt)):
                methods.append(stmt)
            else:
                properties.append(stmt)

        methods.sort()
        properties.sort()
        specials.sort()

#DEBUG:        print 'Specials:', pprint.pformat(list(specials))
#DEBUG:        print 'Properties:', pprint.pformat(list(properties))
#DEBUG:        print 'Methods:', pprint.pformat(list(methods))

#DEBUG:        print set(IF_SPECIALS) ^ set(specials)
        self.failUnless(IF_SPECIALS == tuple(specials))
#DEBUG:        print set(IF_METHODS) ^ set(methods)
        self.failUnless(IF_METHODS == tuple(methods))
#DEBUG:        print set(IF_PROPERTIES) ^ set(properties)
        self.failUnless(IF_PROPERTIES == tuple(properties))


    def testWildcard(self):
        """
        Wildcard class interface tests.
        """
        obj = Wildcard('192.168.0.*')

        IF_PROPERTIES = (
            'Wildcard.ADDR_TYPES',
            'Wildcard.STRATEGIES',
            'Wildcard.addr_type',
            'Wildcard.first',
            'Wildcard.klass',
            'Wildcard.last',
            'Wildcard.strategy'
        )

        IF_METHODS = (
            'Wildcard.adjacent',
            'Wildcard.cidr',
            'Wildcard.data_flavour',
            'Wildcard.iprange',
            'Wildcard.is_valid',
            'Wildcard.issubnet',
            'Wildcard.issupernet',
            'Wildcard.overlaps',
            'Wildcard.size',
            'Wildcard.wildcard',
        )

        IF_SPECIALS = (
            'Wildcard.__add__',
            'Wildcard.__class__',
            'Wildcard.__contains__',
            'Wildcard.__delattr__',
            'Wildcard.__dict__',
            'Wildcard.__doc__',
            'Wildcard.__eq__',
            'Wildcard.__ge__',
            'Wildcard.__getattribute__',
            'Wildcard.__getitem__',
            'Wildcard.__gt__',
            'Wildcard.__hash__',
            'Wildcard.__iadd__',
            'Wildcard.__init__',
            'Wildcard.__isub__',
            'Wildcard.__iter__',
            'Wildcard.__le__',
            'Wildcard.__len__',
            'Wildcard.__lt__',
            'Wildcard.__module__',
            'Wildcard.__ne__',
            'Wildcard.__new__',
            'Wildcard.__reduce__',
            'Wildcard.__reduce_ex__',
            'Wildcard.__repr__',
            'Wildcard.__setattr__',
            'Wildcard.__str__',
            'Wildcard.__sub__',
            'Wildcard.__weakref__'
        )

        methods = []
        properties = []
        specials = []

        for attr in dir(obj):
            stmt = '.'.join(['Wildcard', attr])
            if attr.startswith('__') and attr.endswith('__'):
                specials.append(stmt)
            elif callable(eval(stmt)):
                methods.append(stmt)
            else:
                properties.append(stmt)

        methods.sort()
        properties.sort()
        specials.sort()

#DEBUG:        print 'Specials:', pprint.pformat(list(specials))
#DEBUG:        print 'Properties:', pprint.pformat(list(properties))
#DEBUG:        print 'Methods:', pprint.pformat(list(methods))

#DEBUG:        print set(IF_SPECIALS) ^ set(specials)
        self.failUnless(IF_SPECIALS == tuple(specials))
#DEBUG:        print set(IF_METHODS) ^ set(methods)
        self.failUnless(IF_METHODS == tuple(methods))
#DEBUG:        print set(IF_PROPERTIES) ^ set(properties)
        self.failUnless(IF_PROPERTIES == tuple(properties))

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
