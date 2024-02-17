======================
How to install netaddr
======================

Various Linux distributions make it available via their package managers.

----------------------------------------
Installing from the Python Package Index
----------------------------------------

The easiest way to install netaddr is to use pip.

Download and install the latest version from PyPI -
https://pypi.org/project/pip and run the following command ::

    pip install netaddr

If you want better the :ref:`interactive-shell`  experience you can install the extra
IPython dependency like ::

    pip install 'netaddr[nicer-shell]'

or install IPython directly ::

    pip install ipython

--------------------------------------------------------
Installing using your Linux distribution package manager
--------------------------------------------------------

Various Linux distributions make netaddr available via their package managers.

.. note::

    The netaddr versions provided by Linux distributions may be outdated.

Refer to your distribution's documentation for installation instructions.

Example commands:

.. code-block:: shell

    # Debian, Ubuntu
    sudo apt install python3-netaddr

    # Fedora
    # Base installation
    sudo dnf install python3-netaddr
    # The CLI tool
    sudo dnf install python3-netaddr-shell

--------------------------------
Installing from a source package
--------------------------------

Download the latest release tarball/zip file and extract it to a temporary
directory or clone the repository into a local working directory.

Install the local package::

    pip install .

This automatically places the required files in the ``lib/site-packages``
directory of the Python version you used to run the setup script, may
also be part of a virtualenv or similar environment manager.
