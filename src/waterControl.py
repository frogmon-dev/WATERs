# -*- coding: utf-8 -*- 

# 중복 실행 방지
from tendo import singleton
try:
	me = singleton.SingleInstance()
except :
	print("another process running!")
	exit()

#프로그램 시작	
import sys
import RPi.GPIO as GPIO
import time
import datetime

from frogmon.uLogger     import LOG
from frogmon.uCommon     import COM
from frogmon.uGlobal     import GLOB

def revRelay(val):
	if val == 1 :
		return 0
	else :
		return 1


configFileNM = COM.gHomeDir+COM.gSetupFile
controlFileNM = COM.gHomeDir+COM.gControlFile

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

LIGHT  = 26 #21  #RELAY1,2 LIGHT
PUMP   = 19 #20  #RELAY1,2 PUMP
FAN    = 13 #16  #RELAY1,2 FAN
HEATER = 6  #12  #RELAY1,2 HEATER

GPIO.setup(LIGHT , GPIO.OUT) #LIGHT
GPIO.setup(PUMP  , GPIO.OUT) #PUMP
GPIO.setup(FAN   , GPIO.OUT) #FAN
GPIO.setup(HEATER, GPIO.OUT) #HEATER

STAT_LIGHT  = 0
STAT_PUMP   = 0
STAT_FAN    = 0
STAT_HEATER = 0

cntLoadError = 0

def clearControlFile():
	GLOB.writeConfig(controlFileNM, 'CONTROL', 'light' , '0')
	GLOB.writeConfig(controlFileNM, 'CONTROL', 'pump'  , '0')
	GLOB.writeConfig(controlFileNM, 'CONTROL', 'fan'   , '0')
	GLOB.writeConfig(controlFileNM, 'CONTROL', 'heater', '0')

try:
	GPIO.output(LIGHT, GPIO.HIGH)
	time.sleep(1)
	
	LOG.writeLn("[CONTROL] : h/w Control Start %s" % GLOB.readConfig(configFileNM, 'AGENT', 'id', '0'))
	
	while (True):	
		time.sleep(1)
		try:
			
			STAT_LIGHT  = int(GLOB.readConfig(controlFileNM, 'CONTROL', 'light' , '99')) #0:ON/OFF, 1: LED 켜기, 0: LED 끄기
			STAT_PUMP   = int(GLOB.readConfig(controlFileNM, 'CONTROL', 'pump'  , '99')) #0:ON/OFF, 1: PUMP 켜기, 0: PUMP 끄기
			STAT_FAN    = int(GLOB.readConfig(controlFileNM, 'CONTROL', 'fan'   , '99')) #0:ON/OFF, 1: FAN 켜기, 0: FAN 끄기
			STAT_HEATER = int(GLOB.readConfig(controlFileNM, 'CONTROL', 'heater', '99')) #0:ON/OFF, 1: HEATER 켜기, 0: HEATER 끄기
			
			if (max(STAT_LIGHT, STAT_PUMP, STAT_FAN, STAT_HEATER) == 99):
				LOG.writeLn("[CONTROL] : config load error then continues")
				cntLoadError = cntLoadError + 1
				if (cntLoadError > 10) :
					clearControlFile()
					LOG.writeLn("[CONTROL] : control.ini file clear")
				continue
			else:
				cntLoadError = 0

			
			# Warning 릴레이 타입에 따라 HIGH와 LOW를 뒤바꿔줘야 한다.
			STAT_LIGHT  = revRelay(STAT_LIGHT)
			STAT_PUMP   = revRelay(STAT_PUMP)
			STAT_FAN    = revRelay(STAT_FAN)
			STAT_HEATER = revRelay(STAT_HEATER)
			
			if STAT_LIGHT == 1 :
				GPIO.output(LIGHT, GPIO.HIGH)
			else :
				GPIO.output(LIGHT, GPIO.LOW)
			
			if STAT_PUMP == 1 :
				GPIO.output(PUMP, GPIO.HIGH)
			else :
				GPIO.output(PUMP, GPIO.LOW)
			
			if STAT_FAN == 1 :
				GPIO.output(FAN, GPIO.HIGH)
			else :
				GPIO.output(FAN, GPIO.LOW)
			
			if STAT_HEATER == 1 :
				GPIO.output(HEATER, GPIO.HIGH)
			else :
				GPIO.output(HEATER, GPIO.LOW)
		except Exception as e :
			LOG.writeLn("[CONTROL] : error : %s" % e)
			
except KeyboardInterrupt:
	GPIO.cleanup()    
	print("[CONTROL] : KeyboardInterrupt")
