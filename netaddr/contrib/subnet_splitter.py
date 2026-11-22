# -----------------------------------------------------------------------------
#   Copyright (c) 2008 by David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
# -----------------------------------------------------------------------------
from netaddr.ip import IPNetwork
from netaddr.ip.sets import IPSet


class SubnetSplitter(object):
    """
    A handy utility class that takes a single (large) subnet and allows
    smaller subnet within its range to be extracted by CIDR prefix. Any
    leaving address space is available for subsequent extractions until
    all space is exhausted.
    """

    def __init__(self, base_cidr):
        """
        Constructor.

        :param base_cidr: an IPv4 or IPv6 address with a CIDR prefix.
            (see IPNetwork.__init__ for full details).
        """
        self._subnets = set([IPNetwork(base_cidr)])

    def extract_subnet(self, prefix, count=None):
        """Extract subnets of the specified CIDR prefix.

        An explicit count may span multiple available blocks. If there is
        insufficient space, raise ValueError without allocating any subnets.
        With count=None, subdivide the first suitable available block.
        """
        candidates = [cidr for cidr in self.available_subnets() if cidr.prefixlen <= prefix]
        if not candidates:
            return []
        if count is not None:
            capacity = sum(2 ** (prefix - cidr.prefixlen) for cidr in candidates)
            if not 1 <= count <= capacity:
                raise ValueError('count outside of available IP subnet boundaries!')

        subnets = []
        for cidr in candidates:
            remaining = (
                None if count is None else min(count - len(subnets), 2 ** (prefix - cidr.prefixlen))
            )
            subnets.extend(cidr.subnet(prefix, count=remaining))
            if count is None or len(subnets) == count:
                break

        available = IPSet(self._subnets) - IPSet(subnets)
        self._subnets = set(available.iter_cidrs())
        return subnets

    def available_subnets(self):
        """Returns a list of the currently available subnets."""
        return sorted(self._subnets, key=lambda x: x.prefixlen, reverse=True)

    def remove_subnet(self, ip_network):
        """Remove a specified IPNetwork from available address space."""
        self._subnets.remove(ip_network)
