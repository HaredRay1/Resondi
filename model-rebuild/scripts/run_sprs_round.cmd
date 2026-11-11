@echo off
rem ICBHI + SPRSound fusion round, harmonised (0.1-3.9 kHz, levelled) with per-source normalisation,
rem then the same harmonised setup on ICBHI alone for a fair comparison. Log: results\fusion-run-sprs2.log
cd /d %~dp0..
set PYTHONIOENCODING=utf-8
set PY=C:\Users\Hared\AppData\Local\Python\bin\python.exe
echo start %date% %time% >> results\fusion-run-sprs2.log
"%PY%" -u scripts\fusion.py features --bandlimit >> results\fusion-run-sprs2.log 2>&1
"%PY%" -u scripts\fusion.py run --data icbhi+sprs --bandlimit --srcnorm >> results\fusion-run-sprs2.log 2>&1
"%PY%" -u scripts\fusion.py run --data icbhi --bandlimit >> results\fusion-run-sprs2.log 2>&1
echo done %date% %time% >> results\fusion-run-sprs2.log
