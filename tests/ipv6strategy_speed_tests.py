#!/usr/bin/env python
"""
A little script to prove the speed difference between a basic AddrStrategy
support IPv6 and a customised subclass of AddrStrategy that implements certain
methods using Python socket and struct modules.

Sample output on my beastly 3GHz Intel Core 2 Quad Q9450!

5000 iterations, repeated 3 time(s)

AddrStrategy timings:
--------------------
[0.35877585411071777, 0.36030697822570801, 0.37746715545654297]
avg: 0.365516662598

IPv4Strategy timings:
--------------------
[0.31410598754882812, 0.28557991981506348, 0.2736968994140625]
avg: 0.291127602259

IPv6Strategy is 1.3x faster than AddrStrategy!
"""

import os
import sys
import pprint
from timeit import Timer

#   Run all unit tests for all modules.
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path)

from netaddr.strategy import *

ST_IPV6_BASIC = AddrStrategy(addr_type=AT_INET6, width=128, word_size=16,
                         word_fmt='%.4x', word_sep=':', word_base=16)

#-----------------------------------------------------------------------------
print 'Bargain basement strategy setup :-'
print '-'*80
pprint.pprint(ST_IPV6_BASIC.__dict__)
print '-'*80

#-----------------------------------------------------------------------------
def ipv6_opt_speed_test():
    ST_IPV6.str_to_int('ffff:fffe:ffff:fffe:ffff:fffe:ffff:fffe')
    ST_IPV6.int_to_str(340282366841710300930663525760219742206)
    ST_IPV6.int_to_words(340282366841710300930663525760219742206)
    ST_IPV6.words_to_int(
        (65535, 65534, 65535, 65534, 65535, 65534, 65535, 65534))

#-----------------------------------------------------------------------------
def ipv6_std_speed_test():
    ST_IPV6_BASIC.str_to_int('ffff:fffe:ffff:fffe:ffff:fffe:ffff:fffe')
    ST_IPV6_BASIC.int_to_str(340282366841710300930663525760219742206)
    ST_IPV6_BASIC.int_to_words(340282366841710300930663525760219742206)
    ST_IPV6_BASIC.words_to_int(
        (65535, 65534, 65535, 65534, 65535, 65534, 65535, 65534))

#-----------------------------------------------------------------------------
def ipv6_speed_test():
    repeat = 3
    iterations = 5000
    t1 = Timer('ipv6_std_speed_test()',
               'from __main__ import ipv6_std_speed_test')
    results1 = t1.repeat(repeat, iterations)
    avg1 = sum(results1) / float(len(results1))

    t2 = Timer('ipv6_opt_speed_test()',
               'from __main__ import ipv6_opt_speed_test')
    results2 = t2.repeat(repeat, iterations)
    avg2 = sum(results2) / float(len(results2))

    print '%r iterations, repeated %r time(s)' % (iterations, repeat)
    print 'AddrStrategy timings:', results1, 'avg:', avg1
    print 'IPv6Strategy timings:', results2, 'avg:', avg2
    print 'IPv6Strategy is %.1fx faster than AddrStrategy!' \
        % (avg1 / avg2)

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    ipv6_speed_test()
