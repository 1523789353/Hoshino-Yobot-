@echo off
cacls %systemroot%\system32\config\system||(
    cls
    echo=请以管理员身份运行|msg %username% /time 180
    exit
)
cls
Title Environment Setup
echo=正在尝试更新pip
pip install --upgrade pip
echo=正在安装依赖
@certutil -f -decode %0 %temp%\requirements.txt >nul
pip install -r "%temp%\requirements.txt"
del=/s=/f=/q="%temp%\requirements.txt"
(echo=依赖安装完成
echo=请使用RunHoshino.bat启动)|msg %username% /time 180
exit
::=====Based64 Data=====::
-----BEGIN CERTIFICATE-----
YWlvY3FodHRwPj0xLjINCmFpb2h0dHA+PTMuNi4xDQpBUFNjaGVkdWxlcn49My42DQphcnJvd349MC4xNA0KYmVhdXRpZnVsc291cDQ+PTQuOS4wDQpkYXRhY2xhc3Nlc349MC42DQpleHBpcmluZ2RpY3Q+PTEuMi4wDQpmZWVkcGFyc2Vyfj01LjINCmZpbGV0eXBlPT0xLjAuNw0KZnV6enl3dXp6eX49MC4xOC4wDQpqaW5qYTJ+PTIuMTANCmx4bWw+PTQuNC4xDQptYXRwbG90bGlifj0zLjIuMA0Kbm9uZWJvdFtzY2hlZHVsZXJdfj0xLjYuMA0KbnVtcHk+PTEuMTguMA0Kb3BlbmNjLXB5dGhvbi1yZWltcGxlbWVudGVkfj0wLjEuNQ0Kb3BlbmNjfj0xLjEuMQ0KcGVld2Vlfj0zLjEzDQpwaWxsb3d+PTcuMQ0KcHlndHJpZT49Mi4wDQpweXR6Pj0yMDE5LjMNCnF1YXJ0Pj0wLjYuMTUNCnJlcXVlc3Rzfj0yLjIyDQpzb2dvdV90cl9mcmVlPj0wLjAuNg0KdGlueWRiPj00LjANClR3aXR0ZXJBUEk+PTIuNS4xMA0KdWpzb25+PTMuMS4wDQp6aGNvbnY+PTEuNC4wDQo=
-----END CERTIFICATE-----
