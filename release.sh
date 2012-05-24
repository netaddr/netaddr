#!/bin/bash
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2012, David P. D. Moss. All rights reserved.
#
#   Released under the BSD license. See the LICENSE file for details.
#-----------------------------------------------------------------------------
#
#   netaddr source release script
#
#   clean up
cd $(dirname $0)
rm docs/api/*
rm ./docs/netaddr.zip

#   build API documentation using epydoc
epydoc --config=docs/epydoc.cfg

#   Run code coverage tests.
./netaddr/tests/coverage.sh

#   build source releases
cd docs/api/
zip ../netaddr.zip *
cd ../..
#python2.4 setup_egg.py bdist_egg
#python2.5 setup_egg.py bdist_egg
#python2.6 setup_egg.py bdist_egg
#python2.7 setup_egg.py bdist_egg
python setup.py sdist --no-defaults --formats=gztar,zip --dist-dir=../builds/
