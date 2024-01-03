----------------------
How to release netaddr
----------------------

Here is how to go about releasing a new version of `netaddr`.

* Make sure you have the necessary dependencies installed:

  ::

    pip install --upgrade wheel twine

* Pull down the latest set of changes for the ``master`` branch.

  The assumption is the ``master`` branch build is green and everything works correctly
  (we have a CI process in place).

* Update the top-most section in the CHANGELOG with details of all notable
  changes since the last release that aren't there already.

  Set the release date to the current day.

* Decide what the new version should be (depending on the changes that will be present
  in this release):

  * Fixes – patch version bump
  * New features – minor version bump
  * Substantial or breaking changes – major version bump

* Update the version numbers throughout the source code. That includes changing the currently
  version number in

  - netaddr/__init__.py
  - docs/source/conf.py

  and replacing all ``NEXT_NETADDR_VERSION`` instances with the new version (except for places
  like this file, of course).

* Commit all changes.

* Build the packages and documentation.

    `make dist`

* Upload all built packages to PyPI (currently drkjam and jstasiak can do this)::

    twine upload dist/*

* Tag the release and sync it to remote repo.

    `git tag -a x.y.z -m 'Release version x.y.z'`
    `make push_tags`

* Create a `GitHub Release <https://github.com/netaddr/netaddr/releases/new>`_ based on
  the tag you just pushed.

  Put the new ``CHANGELOG`` contents there and add the "Full changelog" link at the
  end (copy and adapt from the previous release).
