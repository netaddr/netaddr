@echo off
:
:   netaddr Windows binary package release script
:
C:\python25\python setup.py bdist_wininst --dist-dir=..\builds\
rmdir /S /Q .\build\
pause
