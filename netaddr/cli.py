#!/usr/bin/env python
# -----------------------------------------------------------------------------
#   Copyright (c) 2008 by David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
# -----------------------------------------------------------------------------
"""an interactive shell for the netaddr library"""

import os
import sys
import netaddr
from netaddr import *

#   aliases to save some typing ...
from netaddr import IPAddress as IP, IPNetwork as CIDR
from netaddr import EUI as MAC


def main():
    argv = sys.argv[1:]

    banner = '\nnetaddr shell %s - %s\n' % (netaddr.__version__, __doc__)
    exit_msg = '\nShare and enjoy!'
    rc_override = None

    try:
        from IPython.terminal.embed import InteractiveShellEmbed

        ipshell = InteractiveShellEmbed(banner1=banner, exit_msg=exit_msg)
    except ImportError:
        sys.stderr.write('IPython (http://ipython.scipy.org/) not found!\n')
        sys.exit(1)

    ipshell()


if __name__ == '__main__':
    main()
