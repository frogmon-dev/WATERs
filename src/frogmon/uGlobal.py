#uGlobal.py

import os
import re
import json
import subprocess
import socket

from unidecode       import unidecode
from datetime import datetime, timedelta

from frogmon.uCommon     import COM
from frogmon.uConfig     import CONF

class GLOB:
	def __init__(self):
		print('init')

    ## 파일명 검색
	def getJsonFile(dirname, word):
		filenames = os.listdir(dirname)
		rc = []

		for filename in filenames:
			full_filename = os.path.join(dirname, filename)
			if word in full_filename:
				if ('save' not in full_filename) :
					rc.append(full_filename)
		return rc	

	def loadJsonFile(fileName: str):
		f = open(fileName, 'r')
		data = ''.join(f.read().split())
		f.close()
		return data

	def setUpdateTime():
		COM.gNOW  = datetime.now()
		COM.gYYYY = COM.gNOW.strftime('%Y')
		COM.gMM   = COM.gNOW.strftime('%m')
		COM.gDD   = COM.gNOW.strftime('%d')
		COM.gHH   = COM.gNOW.strftime('%H')
		COM.gNN   = COM.gNOW.strftime('%M')
		COM.gSS   = COM.gNOW.strftime('%S')
		COM.gstrYMD = COM.gNOW.strftime('%Y%m%d')
		COM.gstrYMDHMS = COM.gNOW.strftime('%Y%m%d%H%M%S')
		COM.gstrDATE = COM.gNOW.strftime('%Y-%m-%d %H:%M:%S')
		

	def betweenNow(strTm: str):
		convert_date = datetime.strptime(strTm, '%Y%m%d%H%M%S')
		now = datetime.now()
		return (now - convert_date).seconds
		

	def remoteFileFind(path):    
		file_list = os.listdir(path)
		file_list_remote = [file for file in file_list if file.startswith("remote_")]
		return file_list_remote
		
	# Making CSV function
	def makeCSVFile(data, fileName):
		print('fileName ='+fileName)
		print(data)
		if os.path.isfile(fileName) :
			f = open(fileName,'a', newline='')
			wr = csv.writer(f)
			wr.writerow(data)
			f.close()
		else :
			f = open(fileName,'w', newline='')
			wr = csv.writer(f)
			aRow = 'hhnnss', 'temp', 'humi', 'light', 'outTemp'
			wr.writerow(aRow)
			wr.writerow(data)
			f.close()

	# Identifier cleanup
	def clean_identifier(name):
		clean = name.strip()
		for this, that in [[' ', '-'], ['ä', 'ae'], ['Ä', 'Ae'], ['ö', 'oe'], ['Ö', 'Oe'], ['ü', 'ue'], ['Ü', 'Ue'], ['ß', 'ss']]:
			clean = clean.replace(this, that)
		clean = unidecode(clean)
		return clean
		
	def isMacAddress(mac):
		return re.match("[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}", mac.lower())

	def saveJsonData(fileName, data: str):
		rc = -1
		try :
			if data:
				afterData = data.replace("'", "\"")
				dicts = json.loads(afterData)
				with open(fileName, 'w', encoding='utf-8') as make_file:
					json.dump(dicts, make_file, indent="\t")
				print("save json file : %s" % fileName)
				rc = 0
		except Exception as e :
			print("[ERROR]: %s" % e)
		return rc

	def appendControlInfo(fileNM, am_mode, group1, group2):
		rc = -1
		try :
			with open(fileNM, 'r') as f:
				json_data = json.load(f)
				'''
				strControl = '{ "remote" : "%s", "group1" : "%s", "group2" : "%s" }' % (am_mode, group1, group2)
				#strControl["am_movde"] = am_mode
				#strControl["group1"] = group1
				#strControl["group2"] = group2
				jsonControl =  json.loads(strControl)
				#json_data['CONTROL'] = strControl
				json_data['CONTROL'] = jsonControl
				'''
				json_data['REMOTE'] = am_mode
				json_data['GROUP1'] = group1
				json_data['GROUP2'] = group2
				
			with open(fileNM, 'w', encoding='utf-8') as make_file:
				json.dump(json_data, make_file, indent="\t")
			rc = 0
		except Exception as e :
			print("[appendControlInfo ERROR]: %s" % e)

		return rc
	
	def appendWATERsControlInfo(fileNM, am_mode, light, pump, fan, heater):
		rc = -1
		try :
			with open(fileNM, 'r') as f:
				json_data = json.load(f)
				
				json_data['REMOTE'] = am_mode
				json_data['LIGHT'] = light
				json_data['PUMP'] = pump
				json_data['FAN'] = fan
				json_data['HEATER'] = heater
				
			with open(fileNM, 'w', encoding='utf-8') as make_file:
				json.dump(json_data, make_file, indent="\t")
			rc = 0
		except Exception as e :
			print("[appendWATERsControlInfo ERROR]: %s" % e)

		return rc

	def getJsonVal(strJson, section, defVal):
		try:
			json_data = json.loads(strJson)
			return json_data[section]
		except Exception as e :
			#print("getJsonVal Error : '%s' [%s] : error[%s] " % (strJson, section, e))
			return defVal
	
	def escape_ansi(line):
		ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
		return ansi_escape.sub('', line)
			
	def loadTeamviewerID():
		try:
			file = open(COM.gHomeDir+'teamviewerID.txt', 'r')
			strData = file.read()
			strData = strData.replace('TeamViewer ID:', '').rstrip("\n")
			strData = strData.replace(' ', '')
			strData = GLOB.escape_ansi(strData)
			
			return strData
		except Exception as e:
			print("error : %s" % e)
			return "-"
			
	def readConfig(fileName, section, item, defult):
		if os.path.exists(fileName):
			try:
				config  = CONF(fileName)
				rc = config.readConfig(section, item, defult)
				return rc
			except Exception as e:
				print("readConfig error : %s" % e)
				return defult

	def writeConfig(fileName, section, item, value):
		rc = False
		if os.path.exists(fileName):
			try:
				config  = CONF(fileName)
				config.writeConfig(section, item, value)
				config.saveConfig()
				rc = True
			except Exception as e:
				print("writeConfig error : %s" % e)
				return rc
		return rc

	def iniSectionRemove(fileName, section):
		if os.path.exists(fileName):
			try:
				config  = CONF(fileName)
				config.itemRemove(section)
				config.saveConfig()
				return True
			except Exception as e:
				print("iniSectionRemove error : %s" % e)
				return False

	def iniSectionAdd(fileName, section):
		if os.path.exists(fileName):
			try:
				config  = CONF(fileName)
				config.sectionAdd(section)
				config.saveConfig()
				return True
			except Exception as e:
				print("iniSectionAdd error : %s" % e)
				return False

	def itemConfig(fileName, section):
		if os.path.exists(fileName):
			try:
				config  = CONF(fileName)
				return config.itemsConfig(section)
			except Exception as e:
				print("itemConfig error : %s" % e)
	
	def run_command(command):
		ret_code, output = subprocess.getstatusoutput(command)
		if ret_code == 1:
			print("FAILED: %s" % command)
		return output.splitlines() 
		
	def get_ip_address():
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		return s.getsockname()[0]