@echo off
REM erase existing coverage data
c:\python25\python coverage.py -e

REM gather coverage information including line numbers that were omitted
c:\python25\python coverage.py -x -m run_all.py

REM generate a coverage report, omitting Python libraries
c:\python25\python coverage.py -m -i -r -o c:\python25,coverage > netaddr_coverage_report.txt

pause
