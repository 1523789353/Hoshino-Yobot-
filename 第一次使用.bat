@echo off
cacls %systemroot%\system32\config\system||(
cls
echo=���Թ���Ա�������|msg %username% /time 180
exit
)
cls
Title Environment Setup
echo=���ڳ��Ը���pip
pip install --upgrade pip
echo=���ڰ�װ����
echo=���ṩrequirements.txt����Ϊ�����������廪Դ����
echo=���廪Դӵ�еĲ���ֲ�����...
@certutil -f -decode %0 %temp%\requirements.txt >nul
pip install -r "%temp%\requirements.txt"
del=/s=/f=/q="%temp%\requirements.txt"
(echo=������װ���
echo=��ʹ��RunHoshino.bat����)|msg %username% /time 180
exit
::=====Data=====::
-----BEGIN CERTIFICATE-----
YWlvY3FodHRwPj0xLjINCmFpb2h0dHA+PTMuNi4xDQpBUFNjaGVkdWxlcn49My42DQphcnJvd349MC4xNA0KYmVhdXRpZnVsc291cDQ+PTQuOS4wDQpleHBpcmluZ2RpY3Q+PTEuMi4wDQpmZWVkcGFyc2Vyfj01LjINCmppbmphMn49Mi4xMA0KbHhtbD49NC40LjENCm1hdHBsb3RsaWJ+PTMuMi4wDQpub25lYm90W3NjaGVkdWxlcl1+PTEuNi4wDQpudW1weT49MS4xOC4wDQpvcGVuY2MtcHl0aG9uLXJlaW1wbGVtZW50ZWR+PTAuMS41DQpwZWV3ZWV+PTMuMTMNCnBpbGxvd349Ny4xDQpweWd0cmllPj0yLjANCnB5dHo+PTIwMTkuMw0KcXVhcnQ+PTAuNi4xNQ0KcmVxdWVzdHN+PTIuMjINCnNvZ291X3RyX2ZyZWU+PTAuMC42DQp0aW55ZGI+PTQuMA0KVHdpdHRlckFQST49Mi41LjEwDQp6aGNvbnY+PTEuNC4wDQo=
-----END CERTIFICATE-----
