@echo off
Title=HoshinoBot console

:loop
call=:Reset_path
cls
python run.py
echo=����5����Զ�����
ping -n 6 ::1 >nul
goto=loop

::=====Functions=====::
:Reset_path
%~d0
cd %~dp0
goto=End

:End