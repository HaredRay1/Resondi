@echo off
rem Option H (12 Nov): 5-fold patient cross-validation over all 126 ICBHI patients. Resumable: re-run to continue.
rem Log: results\cv-run.log ; results: results\cv-results.md
cd /d %~dp0..
set PYTHONIOENCODING=utf-8
set PY=C:\Users\Hared\AppData\Local\Python\bin\python.exe
echo start %date% %time% >> results\cv-run.log
"%PY%" -u scripts\cv.py run >> results\cv-run.log 2>&1
"%PY%" -u scripts\cv.py report >> results\cv-run.log 2>&1
echo done %date% %time% >> results\cv-run.log
