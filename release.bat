@echo off
:
:   netaddr Windows binary package release script
:
D:\python24\python setup.py bdist_wininst --dist-dir=..\builds\
rmdir /S /Q .\build\
pause
