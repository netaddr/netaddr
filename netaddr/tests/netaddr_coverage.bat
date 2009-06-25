@echo off
REM erase existing coverage data
c:\python25\python coverage -e

REM gather coverage information including line numbers that were omitted
c:\python25\python coverage -x -m run_all.py

REM generate a coverage report, omitting Python libraries
c:\python25\python coverage -m -i -r -o c:\python25 > netaddr_coverage_report.txt

pause
