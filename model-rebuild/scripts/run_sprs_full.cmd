@echo off
rem Option B (user, 11 Nov): full fusion round on ICBHI + rebalanced SPRSound, harmonised features,
rem per-source normalisation, 3 seeds per recipe. Every model is saved to models\fusion-icbhi-sprs-2026-11-11.
rem Log: results\fusion-run-sprs-full.log
cd /d %~dp0..
set PYTHONIOENCODING=utf-8
set PY=C:\Users\Hared\AppData\Local\Python\bin\python.exe
echo start %date% %time% >> results\fusion-run-sprs-full.log
"%PY%" -u scripts\fusion.py run --data icbhi+sprs --bandlimit --srcnorm --balance --save-dir models\fusion-icbhi-sprs-2026-11-11 >> results\fusion-run-sprs-full.log 2>&1
echo done %date% %time% >> results\fusion-run-sprs-full.log
