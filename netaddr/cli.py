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
    banner = r"""               __            __    __
   ____  ___  / /_____ _____/ /___/ /____
  / __ \/ _ \/ __/ __ `/ __  / __  / ___/
 / / / /  __/ /_/ /_/ / /_/ / /_/ / /
/_/ /_/\___/\__/\__,_/\__,_/\__,_/_/

netaddr shell %s - %s
""" % (netaddr.__version__, __doc__)
    exit_msg = '\nShare and enjoy!'

    try:
        from IPython.terminal.embed import InteractiveShellEmbed

        ipshell = InteractiveShellEmbed(banner1=banner, exit_msg=exit_msg, user_ns=globals())
    except ImportError:
        sys.stderr.write('IPython (http://ipython.scipy.org/) not found!\n')
        sys.exit(1)

    ipshell()


if __name__ == '__main__':
    main()
