----------------------
How to release netaddr
----------------------

Here is how to go about releasing a new version of `netaddr`.

* Pull down the latest set of changes for the current branch (at present this is '0.7.x').

* Run the tests under Python 2.7.x and Python 3.4.x at a minimum, like so

    `make test`

* Update the CHANGELOG with details of all changes since the last release.
  Ensure that all references to various tickets and merge requests are included.

* Update the version numbers throughout the source code. At present they are in
  the following locations.

  - CHANGELOG
  - netaddr/__init__.py
  - docs/source/conf.py
  - docs/source/index.rst

* Commit all changes.

* Build the packages and documentation.

    `make dist`

* Upload all built packages to PyPI (currently, only drkjam can do this).

    - `dist/*.whl`
    - `dist/*.zip`
    - `dist/*.gz`

* Update documentation on PyPI (readthedocs will update itself).

    - `docs/build/netaddr.zip`

* Tag the release and sync it to remote repo.

    `git tag -a netaddr-0.7.xx -m 'netaddr release 0.7.xx'`
    `make push_tags`

* Create a `GitHub Release <https://github.com/netaddr/netaddr/releases/new>`_ based on
  the tag you just pushed.

  Put the new ``CHANGELOG`` contents there and add the "Full changelog" link at the
  end (copy and adapt from the previous release).