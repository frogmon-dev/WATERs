#-*- coding:utf-8 -*-

# 중복 실행 방지
from tendo import singleton
try:
	me = singleton.SingleInstance()
except :
	print("another process running!")
	exit()

#프로그램 시작
import paho.mqtt.client as mqtt

from frogmon.uCommon  import COM
from frogmon.uGlobal  import GLOB
from frogmon.uRequest import REQUEST
from frogmon.uLogger  import LOG

#from frogmon.ulogger import LOG
configFileNM = COM.gHomeDir+COM.gSetupFile
controlFileNM = COM.gHomeDir+COM.gControlFile

mSvr_addr = GLOB.readConfig(configFileNM, 'MQTT', 'host_addr', 'frogmon.synology.me')
mSvr_port = GLOB.readConfig(configFileNM, 'MQTT', 'host_port', '8359')

user_id   = GLOB.readConfig(configFileNM, 'SETUP', 'user_id', '0')
dev_id    = GLOB.readConfig(configFileNM, 'AGENT', 'id', '0')

mSub_nm   = "DIYs/%s/%s" % (user_id, dev_id)
#mSub_nm   = "%s" % (user_id)

#서버로부터 CONNTACK 응답을 받을 때 호출되는 콜백
def on_connect(client, userdata, flags, rc):
	LOG.writeLn("[MQTT] Connected with result code "+str(rc))
	#client.subscribe("$SYS/#")
	client.subscribe("%s" % mSub_nm) #구독 "nodemcu"

#서버로부터 publish message를 받을 때 호출되는 콜백
def on_message(client, userdata, msg):
	strJson = msg.payload.decode()
	#print(msg.topic+" "+str(msg.payload)) #토픽과 메세지를 출력한다.
	LOG.writeLn("[MQTT] "+ msg.topic+" "+ strJson) #토픽과 메세지를 출력한다.
	try:
		if GLOB.saveJsonData(COM.gJsonDir+"action.json", strJson) == 0:
			remote = '0'
			grp1 = GLOB.getJsonVal(strJson, 'light', '99')
			if (grp1 != '99') :
				GLOB.writeConfig(controlFileNM, 'CONTROL', 'light', grp1)
				remote = '1'
			grp2 = GLOB.getJsonVal(strJson, 'heater', '99')
			if (grp2 != '99') :
				GLOB.writeConfig(controlFileNM, 'CONTROL', 'heater', grp2)
				remote = '1'
			grp3 = GLOB.getJsonVal(strJson, 'fan', '99')
			if (grp3 != '99') :
				GLOB.writeConfig(controlFileNM, 'CONTROL', 'fan', grp3)
				remote = '1'
			grp4 = GLOB.getJsonVal(strJson, 'pump', '99')
			if (grp4 != '99') :
				GLOB.writeConfig(controlFileNM, 'CONTROL', 'pump', grp4)
				remote = '1'
			
			active = GLOB.getJsonVal(strJson, 'active', '99')
			if (active != '99') :
				remote = active
			GLOB.writeConfig(controlFileNM, 'CONTROL', 'active', remote)
			 
			#print("grp data %s %s" % (grp1, grp2))
			if GLOB.appendWATERsControlInfo(COM.gJsonDir+"device.json", GLOB.readConfig(controlFileNM, 'CONTROL', 'active', '0')
			, GLOB.readConfig(controlFileNM, 'CONTROL', 'light', '0')
			, GLOB.readConfig(controlFileNM, 'CONTROL', 'pump', '0')
			, GLOB.readConfig(controlFileNM, 'CONTROL', 'fan', '0')
			, GLOB.readConfig(controlFileNM, 'CONTROL', 'heater', '0')
			) == 0 :
				REQUEST.updateDIYs(user_id, dev_id)
	except Exception as e :
		LOG.writeLn("[MQTT] : error : %s" % e)

print('')
print('--------------------------------------------------')
print('**  Welcome to FROGMON corp.')
print("**  Let's make it together")
print("**  ")
print('**  USER = %s' % user_id)
print('**  PRODUCT = %s' % dev_id)
print('**  CHNNEL_ID = %s' % mSub_nm)
print('--------------------------------------------------')
print('')

client = mqtt.Client() #client 오브젝트 생성
client.on_connect = on_connect #콜백설정
client.on_message = on_message #콜백설정

try:
	client.connect(mSvr_addr, int(mSvr_port), 60) #라즈베리파이3 MQTT 브로커에 연결
	client.loop_forever()
except Exception as e :
	LOG.writeLn("[MQTT] : error : %s" % e)
