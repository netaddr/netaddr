@echo off
:
:   netaddr Windows binary package release script
:
python setup.py bdist_wininst --dist-dir=..\releases\
rmdir /S /Q .\build\
pause
