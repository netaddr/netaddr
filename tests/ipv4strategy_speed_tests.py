#!/usr/bin/env python
"""
A little script to prove the speed difference between a basic AddrStrategy
support IPv4 and a customised subclass of AddrStrategy that implements certain
methods using Python socket and struct modules.

Sample output on my rather slow and boring 1.7 GHz Pentium M Dell laptop :-

5000 iterations, repeated 3 time(s):-

AddrStrategy timings
--------------------
[0.40483804505879933, 0.40467070535501021, 0.40399436241198261]
avg: 0.404501037609

IPv4Strategy timings
--------------------
[0.17965970535361353, 0.17694008596064581, 0.17825254327016427]
avg: 0.178284111528

IPv4Strategy is 2.3x faster than AddrStrategy!
"""

import os
import sys
from timeit import Timer

#   Run all unit tests for all modules.
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path)

from netaddr.strategy import *

ST_IPV4_BASIC = AddrStrategy(addr_type=AT_INET, width=32, word_size=8,
                         word_fmt='%d', delimiter='.', hex_words=False)

#-----------------------------------------------------------------------------
print 'Bargain basement strategy setup :-'
print '-'*80
print ST_IPV4_BASIC.description()
print '-'*80

#-----------------------------------------------------------------------------
def ipv4_opt_speed_test():
    ST_IPV4.str_to_int('192.168.0.1')
    ST_IPV4.int_to_str(3232235521)
    ST_IPV4.int_to_words(3232235521)
    ST_IPV4.words_to_int((192, 168, 0, 1))

#-----------------------------------------------------------------------------
def ipv4_std_speed_test():
    ST_IPV4_BASIC.str_to_int('192.168.0.1')
    ST_IPV4_BASIC.int_to_str(3232235521)
    ST_IPV4_BASIC.int_to_words(3232235521)
    ST_IPV4_BASIC.words_to_int((192, 168, 0, 1))

#-----------------------------------------------------------------------------
def ipv4_speed_test():
    repeat = 3
    iterations = 5000
    t1 = Timer('ipv4_std_speed_test()',
               'from __main__ import ipv4_std_speed_test')
    results1 = t1.repeat(repeat, iterations)
    avg1 = sum(results1) / float(len(results1))

    t2 = Timer('ipv4_opt_speed_test()',
               'from __main__ import ipv4_opt_speed_test')
    results2 = t2.repeat(repeat, iterations)
    avg2 = sum(results2) / float(len(results2))

    print '%r iterations, repeated %r time(s)' % (iterations, repeat)
    print 'AddrStrategy timings:', results1, 'avg:', avg1
    print 'IPv4Strategy timings:', results2, 'avg:', avg2
    print 'IPv4Strategy is %.1fx faster than AddrStrategy!' \
        % (avg1 / avg2)

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    ipv4_speed_test()
