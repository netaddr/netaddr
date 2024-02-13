#!/usr/bin/env python
# -----------------------------------------------------------------------------
#   Copyright (c) 2008 by David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
# -----------------------------------------------------------------------------
"""an interactive shell for the netaddr library"""

import argparse
import sys
import netaddr

SHELL_NAMESPACE = {
    name: getattr(netaddr, name) for name in dir(netaddr) if name in netaddr.__all__
} | {
    #   aliases to save some typing ...
    'IP': netaddr.IPAddress,
    'CIDR': netaddr.IPNetwork,
    'MAC': netaddr.EUI,
}

ASCII_ART_LOGO = r"""               __            __    __
   ____  ___  / /_____ _____/ /___/ /____
  / __ \/ _ \/ __/ __ `/ __  / __  / ___/
 / / / /  __/ /_/ /_/ / /_/ / /_/ / /
/_/ /_/\___/\__/\__,_/\__,_/\__,_/_/
"""


def main():
    print(ASCII_ART_LOGO)

    parser = argparse.ArgumentParser(
        prog='netaddr', description='The netaddr CLI tool', epilog='Share and enjoy!'
    )
    _args = parser.parse_args()

    banner = r"""netaddr shell %s - %s
""" % (netaddr.__version__, __doc__)
    exit_msg = '\nShare and enjoy!'

    try:
        from IPython.terminal.embed import InteractiveShellEmbed

        ipshell = InteractiveShellEmbed(banner1=banner, exit_msg=exit_msg, user_ns=SHELL_NAMESPACE)
    except ImportError:
        sys.stderr.write('IPython (http://ipython.scipy.org/) not found!\n')
        sys.exit(1)

    ipshell()


if __name__ == '__main__':
    main()
