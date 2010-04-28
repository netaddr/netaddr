:-----------------------------------------------------------------------------
:   Copyright (c) 2008-2009, David P. D. Moss. All rights reserved.
:
:   Released under the BSD license. See the LICENSE file for details.
:-----------------------------------------------------------------------------
:@echo off
:
:   netaddr Windows binary and Python egg package release build
:
set DIST_DIR=..\builds\

:OLD C:\python25\python setup.py bdist_wininst --dist-dir=%DIST_DIR%
:OLD rmdir /S /Q .\build\

c:\Python26\python.exe setup.py --skip-build --target-version 2.4 --dist-dir=%DIST_DIR% bdist_wininst
rmdir /S /Q .\build\
c:\Python26\python.exe setup.py --skip-build --target-version 2.5 --dist-dir=%DIST_DIR% bdist_wininst
rmdir /S /Q .\build\
c:\Python26\python.exe setup.py --skip-build --target-version 2.6 --dist-dir=%DIST_DIR% bdist_wininst
rmdir /S /Q .\build\
c:\Python26\python.exe setup.py --skip-build --target-version 2.7 --dist-dir=%DIST_DIR% bdist_wininst
rmdir /S /Q .\build\
c:\Python31\python.exe setup.py --skip-build --target-version 3.0 --dist-dir=%DIST_DIR% bdist_wininst
rmdir /S /Q .\build\
c:\Python31\python.exe setup.py --skip-build --target-version 3.1 --dist-dir=%DIST_DIR% bdist_wininst 
rmdir /S /Q .\build\

Y:\virtualenv\py24_vanilla\Scripts\python.exe setup_egg.py bdist_egg --dist-dir=%DIST_DIR%
rmdir /S /Q netaddr.egg-info
rmdir /S /Q build

Y:\virtualenv\py25_vanilla\Scripts\python.exe setup_egg.py bdist_egg --dist-dir=%DIST_DIR%
rmdir /S /Q netaddr.egg-info
rmdir /S /Q build

Y:\virtualenv\py26_vanilla\Scripts\python.exe setup_egg.py bdist_egg --dist-dir=%DIST_DIR%
rmdir /S /Q netaddr.egg-info
rmdir /S /Q build

Y:\virtualenv\py27_vanilla\Scripts\python.exe setup_egg.py bdist_egg --dist-dir=%DIST_DIR%
rmdir /S /Q netaddr.egg-info
rmdir /S /Q build

pause
