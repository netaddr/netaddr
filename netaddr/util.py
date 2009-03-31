#!/usr/bin/env python
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""netaddr utility functions"""

def num_bits(n):
    """Minimum number of bits needed to represent a given unsigned integer."""
    n = abs(n)
    numbits = 0
    while n:
         numbits += 1
         n >>= 1
    return numbits
