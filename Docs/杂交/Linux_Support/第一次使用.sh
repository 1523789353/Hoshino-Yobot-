#!/bin/bash
echo 正在尝试更新pip
pip install --upgrade pip
echo 正在安装依赖
cd /tmp
cat<<DATA|base64 -d>requirements.txt
YWlvY3FodHRwPj0xLjINCmFpb2h0dHA+PTMuNi4xDQpBUFNjaGVkdWxlcn49My42DQphcnJvd349MC4xNA0KYmVhdXRpZnVsc291cDQ+PTQuOS4wDQpkYXRhY2xhc3Nlc349MC42DQpleHBpcmluZ2RpY3Q+PTEuMi4wDQpmZWVkcGFyc2Vyfj01LjINCmZ1enp5d3V6enl+PTAuMTguMA0KamluamEyfj0yLjEwDQpseG1sPj00LjQuMQ0KbWF0cGxvdGxpYn49My4yLjANCm5vbmVib3Rbc2NoZWR1bGVyXX49MS42LjANCm51bXB5Pj0xLjE4LjANCm9wZW5jYy1weXRob24tcmVpbXBsZW1lbnRlZH49MC4xLjUNCm9wZW5jY349MS4xLjENCnBlZXdlZX49My4xMw0KcGlsbG93fj03LjENCnB5Z3RyaWU+PTIuMA0KcHl0ej49MjAxOS4zDQpxdWFydD49MC42LjE1DQpyZXF1ZXN0c349Mi4yMg0Kc29nb3VfdHJfZnJlZT49MC4wLjYNCnRpbnlkYj49NC4wDQpUd2l0dGVyQVBJPj0yLjUuMTANCnVqc29ufj0zLjEuMA0Kemhjb252Pj0xLjQuMA0K
DATA
pip install -r requirements.txt
rm -rf requirements.txt
echo 依赖安装完成
echo 请使用RunHoshino.bat启动
exit