@echo off
rem 1) Save the ICBHI-only fusion models as a checkpoint (models\fusion-icbhi-only-2026-11-11).
rem 2) Gate check, one seed each: MFCC on ICBHI only vs ICBHI + rebalanced SPRSound, same harmonised features.
rem Log: results\fusion-gate.log
cd /d %~dp0..
set PYTHONIOENCODING=utf-8
set PY=C:\Users\Hared\AppData\Local\Python\bin\python.exe
echo start %date% %time% >> results\fusion-gate.log
"%PY%" -u scripts\fusion.py save >> results\fusion-gate.log 2>&1
"%PY%" -u scripts\fusion.py run single_mfcc --data icbhi --bandlimit --seeds 11 >> results\fusion-gate.log 2>&1
"%PY%" -u scripts\fusion.py run single_mfcc --data icbhi+sprs --bandlimit --srcnorm --balance --seeds 11 >> results\fusion-gate.log 2>&1
echo done %date% %time% >> results\fusion-gate.log
