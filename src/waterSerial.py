# -*- coding: utf-8 -*- 

# 중복 실행 방지
from tendo import singleton
try:
	me = singleton.SingleInstance()
except :
	print("another process running!")
	exit()

# 프로그램 시작	
from frogmon.uGlobal     import GLOB
from frogmon.uCommon     import COM
from frogmon.uLogger     import LOG
import serial
import time

fileNMPacket = 'packet.ini'

configFileNM = COM.gHomeDir+COM.gSetupFile
packetFileNM = COM.gHomeDir+fileNMPacket

#rtu = serial.Serial('/dev/ttyAMA0', 9600, timeout=0)
rtu = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)


mRecivePacket = []

def makePacket(strList):
	result = []
	try:
		result.append(0x16)
		result.append(0x7A)
		result.append(0x0E)		
		for b in strList:
			result.append(int(b))
		result.append(0x09)
		result.append(0x03)
		print(result)
		return result
	except Exception as e :
		LOG.writeLn("[Serial] : error : %s" % e)
		return None

def readPacket(packet):
	print(packet)
	result = []

	try:
		if packet[0] == 0x16:
			if packet[1] == 0x03:
				if packet[2] == 0x13:
					# SPA data
					result.append(packet[3])
					result.append(packet[4])
					result.append(packet[5])
					result.append(packet[6])
					result.append(packet[7])
					result.append(packet[8])					
					#Detox 1 data
					result.append(packet[9])
					result.append(packet[10])
					result.append(packet[11])
					result.append(packet[12])
					result.append(packet[13])
					
					#Detox 2 data
					result.append(packet[14])
					result.append(packet[15])
					result.append(packet[16])
					result.append(packet[17])
					result.append(packet[18])
					return result
		return None
	except Exception as e :
		LOG.writeLn("[Serial] : readPacket error ")

mCnt = 0
mC = 0
packetSend = ''
mLastSendPacket = ''
mLastBody = []

LOG.writeLn("[spaSerial] : Program Start!!")
while True:
	time.sleep(0.2)
	mCnt = mCnt + 1	
	
	if rtu.readable():
		try :
			#res = rtu.readline()
			packet = rtu.read()
			if packet:
				if packet[0] == 0x16:
					packet = rtu.read()
					if packet[0] == 0x03:
						packet = rtu.read()
						if packet[0] == 0x13:
							body = []
							for i in range(0, 16):
								packet = rtu.read()
								body.append(packet[0])
							
							mLastBody = body
							strBody = '%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d' % ( body[0], body[1], body[2], body[3], body[4], body[5], body[6], body[7], body[8], body[9], body[10], body[11], body[12], body[13], body[14], body[15])
							LOG.writeLn("[Serial] : recive : [%s]" % strBody)
							GLOB.writeConfig(packetFileNM, 'PACKET', 'recive', strBody)

		except Exception as e :
			LOG.writeLn("[Serial] : error : %s" % e)
	
	if mCnt > 5:
		mCnt = 0
		packetSend = GLOB.readConfig(packetFileNM, 'PACKET', 'send', '')
		if packetSend != '':
			mLastSendPacket = packetSend
			#todo make packet and send packet ex) "1,1,1,0,0,0,1,1,0,0"
			strBody = packetSend.split(',')
			packet = makePacket(strBody)
			if packet:
				rtu.write(packet)
				LOG.writeLn("[Serial] : send : %s" % packet)
			GLOB.writeConfig(packetFileNM, 'PACKET', 'send', '')

