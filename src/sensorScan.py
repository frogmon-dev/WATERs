# -*- coding: utf-8 -*- 

#프로그램 시작
from frogmon.uCommon   import COM
from frogmon.uGlobal   import GLOB

from tendo import singleton
try:
	me = singleton.SingleInstance()
except :
	print("another process running!")
	exit()

print('')
print('--------------------------------------------------')
print('**  Welcome to FROGMON corp.')
print("**  Let's make it together")
print("**  Setup file (%s%s)" % (COM.gHomeDir,COM.gSetupFile))
print('--------------------------------------------------')
print('')

configFileNM = COM.gHomeDir+COM.gSetupFile

import struct
from bluepy.btle import Scanner, DefaultDelegate, UUID, Peripheral

#TARGET_UUID = "4d6fc88bbe756698da486866a36ec78e"
TARGET_UUID = "0000fe95-0000-1000-8000-00805f9b34fb"
target_dev = None    

#############################################
# Define scan callback
#############################################
class ScanDelegate(DefaultDelegate):
	def __init__(self):
		DefaultDelegate.__init__(self)

	def handleDiscovery(self, dev, isNewDev, isNewData):
		if isNewDev:
			print("Discovered device %s" % dev.addr)
		elif isNewData:
			print("Received new data from %s" % dev.addr)

#############################################
# Define notification callback
#############################################
class NotifyDelegate(DefaultDelegate):
	#Constructor (run once on startup)  
	def __init__(self, params):
		DefaultDelegate.__init__(self)

	#func is caled on notifications
	def handleNotification(self, cHandle, data):
		print("Notification : " + data.decode("utf-8"))

#############################################
# Main starts here
#############################################
scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(10.0)
cnt = 0
dev_str=''

if not GLOB.iniSectionRemove(configFileNM, 'DEVICE'):
	print('ini Section Delete Error ')

if not GLOB.iniSectionAdd(configFileNM, 'DEVICE'):
	print('ini Section Add Error ')

for dev in devices:
	#print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
	for (adtype, desc, value) in dev.getScanData():
		# Check iBeacon UUID
		# 255 is manufacturer data (1  is Flags, 9 is Name)
		#print("  (AD Type=%d) %s = %s" % (adtype, desc, value))
		if adtype is 2 and TARGET_UUID in value:
			cnt = cnt+1
			target_dev = dev
			print("%d) Device %s (%s), RSSI=%d dB" % (cnt, dev.addr, dev.addrType, dev.rssi))
			dev_str = "sensor%02d" % (cnt)
			# 센서 하나만 저장
			if cnt == 1:
				GLOB.writeConfig(configFileNM, 'DEVICE', dev_str, dev.addr)

GLOB.writeConfig(configFileNM, 'FLOWERCARE', 'sensor_cnt', "%d" %cnt)

if cnt > 0 :
	print('식물 정보 감지 센서 %d개를 찾았습니다. ' % cnt)
else :
	print('식물 정보 센서를 감지 하지 못하였습니다.')
	print('제어기와 너무 멀리 떨어지거나 건전지 교체 시기인지 확인하여 주세요')
