#!/bin/bash
#-----------------------------------------------------------------------------
#   Copyright (c) 2008-2010, David P. D. Moss. All rights reserved.
#
#   Checks unit test code coverage for the netaddr project.
#-----------------------------------------------------------------------------

CWD=$(pwd)  #   Save caller's path for later.
BASE_DIR=$(cd $(dirname $0) && pwd)
TEST_DIR=$(cd $BASE_DIR/.. && pwd)

#   A bit of weirdness with coverage.py seem to require this...
cd $TEST_DIR

#   Whitelist globs for all of Python source files to be included in reports.
SOURCE_GLOBS='*.py ip/*.py eui/*.py strategy/*.py'

#   Erase existing coverage data
coverage -e

#   Gather coverage information including line numbers that were omitted
coverage -x -m tests/__init__.py

#   generate a coverage report, omitting Python libraries
coverage -r -m -i $SOURCE_GLOBS > tests/coverage_report.txt

#   Generate HTML output
coverage -b -d tests/coverage -i $SOURCE_GLOBS

#   Take us back to the user's original directory.
cd $CWD
