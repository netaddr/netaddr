#!/usr/bin/env python
"""
An IPy compatible interface (facade) using netaddr internals.
"""
import netaddr
import re

#-----------------------------------------------------------------------------
def parseAddress(ipstr):
    #   Some workarounds here that netaddr does currently support.
    if isinstance(ipstr, (str, unicode)):
        #   Detect empty strings and raise ValueError.
        if ipstr == '':
            raise ValueError('%r is not a valid IP address!' % ipstr)

        #   Detect and convert string based hex address values.
        if len(re.findall('^0x[0-9a-fA-F]+$', ipstr)) > 0:
            int_val = int(ipstr, 16)
            for strategy in (netaddr.ST_IPV4, netaddr.ST_IPV6):
                if strategy.valid_int(int_val):
                   return int_val, strategy.addr_type

    #   Check all other forms of string addresses.
    for strategy in (netaddr.ST_IPV4, netaddr.ST_IPV6):
        if strategy.valid_str(ipstr):
           return strategy.str_to_int(ipstr), strategy.addr_type
    raise ValueError('%r is not a valid IP address!' % ipstr)

#-----------------------------------------------------------------------------
def intToIp(ip, version):
    if version == netaddr.AT_INET:
        return netaddr.ST_IPV4.int_to_str(ip)
    elif version == netaddr.AT_INET6:
        return netaddr.ST_IPV6.int_to_str(ip, compact=False, word_fmt='%04x')
    else:
        raise ValueError('unsupported version %r!' % version)

#-----------------------------------------------------------------------------
class IP(object):
    """
    A facade object implementing the same internals at IPy.IP but using
    netaddr's internals to perform all operations.
    """
    def __init__(self, data):#TODO:, ipversion=None, make_net=False):
        if isinstance(data, (str, unicode)) and '-' in data:
            first, last = data.split('-')
            iprange = netaddr.IPRange(first, last)
            if len(iprange.cidrs()) != 1:
                raise ValueError('IP range %r not on a network boundary.' \
                    % data)
            self._ip = iprange[0]
            self._cidr = iprange.cidrs()[0]
        elif isinstance(data, (int, long)):
            addr_type = netaddr.AT_INET
            if data > (2 ** 32 - 1):
                #   IPy assumes that an int above 2^32-1 is automatically an
                #   IPv6 address. netaddr requires a constant value as well.
                addr_type = netaddr.AT_INET6
            self._ip = netaddr.IP(data, addr_type)
            self._cidr = self._ip.cidr()
        else:
            self._ip = netaddr.IP(data)
            self._cidr = self._ip.cidr(strict=False)
        self._cidr.fmt=str

        #   If True omits prefixlen for /32 or /128 addresses, included
        #   otherwise.
        self.NoPrefixForSingleIp = True

        #   A numerical value controlling return values.
        self.WantPrefixLen = 0

    def broadcast(self):
        return IP(self._cidr[-1]).strCompressed()

    def int(self):
        return self._cidr.first

    def iptype(self):
        if self._ip.addr_type == netaddr.AT_INET:
            return self._ip.info()['IPv4'][0]['status'].upper()
        elif self._ip.addr_type == netaddr.AT_INET6:
            return self._ip.info()['IPv6'][0]['status'].upper()

    def len(self):
        return self._cidr.size()

    def make_net(self):
        return NotImplementedError('TODO')

    def net(self):
        return IP(self._cidr[0]).strCompressed()

    def netmask(self):
        return IP(self._cidr.netmask)

    def overlaps(self, other):
        if not isinstance(other, IP):
            other = IP(other)

        if other.ip >= self.ip and other.ip < self.ip + self.len():
            return 1
        elif self.ip >= other.ip and self.ip < other.ip + other.len():
            return -1
        else:
            return 0

    def prefixlen(self):
        return self._cidr.prefixlen

    def reverseName(self):
        return self._ip.reverse_dns()

    def reverseNames(self):

        return [netaddr.IP(ip).reverse_dns() for ip in self._cidr]

    def strBin(self):
        return self._ip.bin().replace('0b', '')

    def strCompressed(self):
        #   Display prefixlen as necessary.
        if self._ip.prefixlen != self._ip.strategy.width:
            return '%s/%d' % (str(self._ip), self._ip.prefixlen)
        return str(self._ip)

    def strDec(self, wantprefixlen=None):
        """
        TODO - add in 'wantprefixlen' logic.
        """
        return str(int(self._ip)).replace('L', '')

    def strFullsize(self, wantprefixlen=None):
        """
        TODO - add in 'wantprefixlen' logic.
        """
        if self._ip.addr_type == netaddr.AT_INET6:
            #   Expand IPv6 address to fullest extent.
            return netaddr.ST_IPV6.int_to_str(
                self._ip.value, compact=False, word_fmt='%04x')
        return str(self._ip)

    def strHex(self, wantprefixlen=None):
        """
        TODO - add in 'wantprefixlen' logic.
        """
        return hex(self._ip)

    def strNetmask(self):
        if self._ip.addr_type == netaddr.AT_INET:
            return self._cidr.netmask
        elif self._ip.addr_type == netaddr.AT_INET6:
            return '/%d' % self._cidr.prefixlen

    def strNormal(self, wantprefixlen=None):
        """
        TODO - add in 'wantprefixlen' logic.
        """
        if self._ip.addr_type == netaddr.AT_INET6:
            #   Turn off IPv6 compression.
            return self._ip.strategy.int_to_str(self._ip.value, compact=False)
        return str(self._ip)

    def ip(self):
        return self._ip.value

    ip = property(ip)

    def version(self):
        return self._ip.addr_type

    def __add__(self, other):
        raise NotImplementedError('TODO')

    def __hash__(self):
        thehash = int(-1)
        ip = self.ip
        while ip > 0:
            thehash = thehash ^ (ip & 0x7fffffff)
            ip = ip >> 32
        thehash = thehash ^ self.prefixlen()
        return int(thehash)

    def __cmp__(self, other):
        if not isinstance(other, IP):
            other = IP(other)

        if self.prefixlen() < other.prefixlen():
            return (other.prefixlen() - self.prefixlen())
        elif self.prefixlen() > other.prefixlen():
            return (self.prefixlen() - other.prefixlen()) * -1
        else:
            if self.ip < other.ip:
                return -1
            elif self.ip > other.ip:
                return 1
            else:
                return 0

    def __contains__(self, other):
        if not isinstance(other, IP):
            other = IP(other)

        if other.ip >= self.ip and \
            other.ip < self.ip + self.len() - other.len() + 1:
            return 1
        else:
            return 0

    def __getitem__(self, index):
        return IP(self._cidr[index])

    def __len__(self):
        return self._cidr.size()

    def __nonzero__(self):
        return 1

    def __str__(self):
        return str(self._cidr)

    def __repr__(self):
        return "IP('%s')" % self.strCompressed()

