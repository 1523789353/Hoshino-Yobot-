@echo off
Title=HoshinoBot console

:loop
call=:Reset_path
cls
python run.py
echo=将在3秒后自动重启
ping -n 4 ::1 >nul
goto=loop

::=====Functions=====::
:Reset_path
%~d0
cd %~dp0
goto=End

:End