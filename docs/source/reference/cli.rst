CLI tool
========

The netaddr package includes a ``netaddr`` CLI application.

.. note::

    The tool is meant to be used by humans. Its interface should not be considered stable.
    Exercise caution when using it in any kind of programmatic context (read: scripting).

    If you want a stable interface use the :doc:`programmatic API <../api>`.

Interactive shell
-----------------

Calling ``netaddr`` without any arguments will launch an interactive, `IPython`_-based shell.
As such `IPython`_ needs to be installed for the shell to work.

The shell comes with all parts of :doc:`the netaddr API <../api>` pre-imported so you can
interact with it right away, with minimal friction:

::

    % netaddr
                __            __    __
    ____  ___  / /_____ _____/ /___/ /____
    / __ \/ _ \/ __/ __ `/ __  / __  / ___/
    / / / /  __/ /_/ /_/ / /_/ / /_/ / /
    /_/ /_/\___/\__/\__,_/\__,_/\__,_/_/

    netaddr shell 1.0.0 - an interactive shell for the netaddr library

    In [1]: '10.0.0.2' in IPNetwork('10.0.0.0/24')
    Out[1]: True

    In [2]:

.. _IPython: https://pypi.org/project/ipython/
