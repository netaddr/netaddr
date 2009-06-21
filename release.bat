:@echo off
:
:   netaddr Windows binary and Python egg package release build
:
set DIST_DIR=..\builds\

C:\python25\python setup.py bdist_wininst --dist-dir=%DIST_DIR%
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

pause
