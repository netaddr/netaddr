======================
How to install netaddr
======================

netaddr is available in various formats :

- source code repository
- source distribution packages (tarball and zip formats)
- Python universal wheel packages

Various Linux distributions make it available via their package managers.

---------------------
Locating the software
---------------------

The netaddr project is hosted here on github

    https://github.com/drkjam/netaddr/

----------------------------------------
Installing from the Python Package Index
----------------------------------------

The easiest way to install netaddr is to use pip.

Download and install the latest version from PyPI -
https://pypi.org/project/pip and run the following command ::

    pip install netaddr

--------------------------------
Installing from a source package
--------------------------------

Download the latest release tarball/zip file and extract it to a temporary
directory or clone the repository into a local working directory.

Run the setup file from directory::

    python setup.py install

This automatically places the required files in the ``lib/site-packages``
directory of the Python version you used to run the setup script, may
also be part of a virtualenv or similar environment manager.
