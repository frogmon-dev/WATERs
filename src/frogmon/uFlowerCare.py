# uFlowerCare.py

import json

from collections import OrderedDict
from time import time, sleep, localtime, strftime

from frogmon.uCommon   import COM
from frogmon.uGlobal   import GLOB
from frogmon.uLogger   import LOG
from frogmon.uRequest  import REQUEST

configFileNM = COM.gHomeDir+COM.gSetupFile
controlFileNM = COM.gHomeDir+COM.gControlFile

from miflora.miflora_poller import MiFloraPoller, MI_BATTERY, MI_CONDUCTIVITY, MI_LIGHT, MI_MOISTURE, MI_TEMPERATURE
from btlewrap import available_backends, BluepyBackend, GatttoolBackend, PygattBackend, BluetoothBackendException

mParameters = OrderedDict([
		(MI_LIGHT,        dict(name="LightIntensity"  , name_pretty='Sunlight Intensity'         , typeformat='%d'  , unit='lux'    , device_class="illuminance")),
		(MI_TEMPERATURE,  dict(name="AirTemperature"  , name_pretty='Air Temperature'            , typeformat='%.1f', unit='°C'     , device_class="temperature")),
		(MI_MOISTURE,     dict(name="SoilMoisture"    , name_pretty='Soil Moisture'              , typeformat='%d'  , unit='%'      , device_class="humidity")),
		(MI_CONDUCTIVITY, dict(name="SoilConductivity", name_pretty='Soil Conductivity/Fertility', typeformat='%d'  , unit='µS/cm')),
		(MI_BATTERY,      dict(name="Battery"         , name_pretty='Sensor Battery Level'       , typeformat='%d'  , unit='%'      , device_class="battery"))
	])

class pwinfo :
	e_pty = 0
	e_sky = 0
	e_wsd = 0.0
	e_t1h = 0
	e_reh = 0
	
class FLOWERCARE:

	def __init__(self):
		#LOG.writeLn('FLOWERCARE Sensor Collector Start!!')
		self.flores = OrderedDict([])
		self.confUpdate()
		
	def confUpdate(self):
		self.sleep_period          = int(GLOB.readConfig(configFileNM, 'FLOWERCARE', 'period', '300'))
		self.miflora_cache_timeout = self.sleep_period - 1
		self.used_adapter          = GLOB.readConfig(configFileNM, 'FLOWERCARE', 'adapter', 'hci0')
		self.reporting_mode        = 'json'
		self.daemon_enabled        = True
		self.user_id               = GLOB.readConfig(configFileNM, 'SETUP', 'user_id', '0')
		self.device_id             = GLOB.readConfig(configFileNM, 'AGENT', 'id', '0')
		self.default_base_topic = 'miflora'
		self.local_id              = GLOB.readConfig(configFileNM, 'WEATHER', 'location0', '')
			

		# Check configuration
		if self.reporting_mode not in ['mqtt-json', 'mqtt-homie', 'json', 'mqtt-smarthome', 'homeassistant-mqtt', 'thingsboard-json', 'wirenboard-mqtt']:
			LOG.writeLn('Configuration parameter reporting_mode set to an invalid value ')
			sys.exit(1)

		if (self.device_id == '0' or self.user_id == '0'):
			LOG.writeLn('setup.ini file load error')
			sys.exit(1)

		#LOG.writeLn('Configuration accepted')
		print('**  USER     = %s' % self.user_id)
		print('**  PRODUCT  = %s' % self.device_id)
		print('**  interval = %d' % self.sleep_period)
		print('**  location = %s' % self.local_id)
		print('--------------------------------------------------')
		print('')

	def chkSensor(self):
		for [name, mac] in GLOB.itemConfig(configFileNM, 'DEVICE'):
			if not GLOB.isMacAddress(mac):
				LOG.writeLn('The MAC address "{}" seems to be in the wrong format. Please check your configuration')
				sys.exit(1)

			if '@' in name:
				name_pretty, location_pretty = name.split('@')
			else:
				name_pretty, location_pretty = name, ''
				
			name_clean = GLOB.clean_identifier(name_pretty)
			location_clean = GLOB.clean_identifier(location_pretty)

			flora = dict()
			print('Adding sensor to device list and testing connection ...')
			print('Name:		  "{}"'.format(name_pretty))
			#print_line('Attempting initial connection to Mi Flora sensor "{}" ({})'.format(name_pretty, mac), console=False, sd_notify=True)

			flora_poller = MiFloraPoller(mac=mac, backend=GatttoolBackend, cache_timeout=self.miflora_cache_timeout, retries=3, adapter=self.used_adapter)
			flora['poller'] = flora_poller
			flora['name_pretty'] = name_pretty
			flora['mac'] = flora_poller._mac
			flora['refresh'] = self.sleep_period
			flora['location_clean'] = location_clean
			flora['location_pretty'] = location_pretty
			flora['stats'] = {"count": 0, "success": 0, "failure": 0}
			
			try:
				flora_poller.fill_cache()
				flora_poller.parameter_value(MI_LIGHT)
				flora['firmware'] = flora_poller.firmware_version()
			except (IOError, BluetoothBackendException):
				LOG.writeLn('Initial connection to Mi Flora sensor "{}" ({}) failed.')
			else:
				print('Internal name: "{}"'.format(name_clean))
				print('Device name:   "{}"'.format(flora_poller.name()))
				print('MAC address:   {}'.format(flora_poller._mac))
				print('Firmware:	  {}'.format(flora_poller.firmware_version()))
				#LOG.writeLn('Initial connection to Mi Flora sensor "{}" ({}) successful')
			print()
			self.flores[name_clean] = flora
		return self.flores
		
	def encodeStatJson(self, fileNM, data):
		rc = -1
		try:
			dict = json.loads('{}')
			dict['DEV_ID']    = data[0]
			dict['MODE']      = data[1]
			dict['ALARM']     = data[2]
			dict['TEMP']      = data[3]
			dict['HUMI']      = data[4]
			dict['MOIST']     = data[5]
			dict['COND']      = data[6]
			dict['CDS']       = data[7]
			dict['BATTERY']   = data[8]
			dict['REMOTE']    = data[9]
			dict['LIGHT']     = data[10]
			dict['PUMP']      = data[11]
			dict['FAN']       = data[12]
			dict['HEATER']    = data[13]
			dict['LASTUPDT']  = data[14]
			dict['TEAMVIEWER'] = data[15]
			dict['LOCAL_IP']   = GLOB.get_ip_address()
			
			print(json.dumps(dict, ensure_ascii=False, indent="\t"))
			#os.remove(fileNM)
			with open(fileNM, 'w', encoding='utf-8') as make_file:
				json.dump(dict, make_file, ensure_ascii=False, indent="\t")
			print("out values [%s,%s,%s,%s,%s]" % (data[9], data[10], data[11], data[12], data[13]))
			rc = 0
		except Exception as e :
			LOG.writeLn("[ERROR]: %s" % e)
		return rc
		
	def run(self):
		self.chkSensor()
		while True:
			GLOB.setUpdateTime()
			self.confUpdate()
			for [flora_name, flora] in self.flores.items():
				data = dict()
				attempts = 2
				flora['poller']._cache = None
				flora['poller']._last_read = None
				flora['stats']['count'] = flora['stats']['count'] + 1
				#print_line('Retrieving data from sensor "{}" ...'.format(flora['name_pretty']))
				while attempts != 0 and not flora['poller']._cache:
					try:
						flora['poller'].fill_cache()
						flora['poller'].parameter_value(MI_LIGHT)
					except (IOError, BluetoothBackendException):
						attempts = attempts - 1
						if attempts > 0:
							LOG.writeLn('Retrying ...')
						flora['poller']._cache = None
						flora['poller']._last_read = None

				if not flora['poller']._cache:
					flora['stats']['failure'] = flora['stats']['failure'] + 1
					LOG.writeLn('Failed to retrieve data from Mi Flora sensor "{}" ({}), success rate: {:.0%}'.format(
						flora['name_pretty'], flora['mac'], flora['stats']['success']/flora['stats']['count']
						))
					print()
					continue
				else:
					flora['stats']['success'] = flora['stats']['success'] + 1

				for param,_ in mParameters.items():
					data[param] = flora['poller'].parameter_value(param)
								
				rc = -1
				try:
					data['timestamp']   = COM.gstrDATE
					data['name']        = flora_name
					data['name_pretty'] = flora['name_pretty']
					data['mac']         = flora['mac']
					data['firmware']    = flora['firmware']
					
					#print('Data for "{}": {}'.format(flora_name, json.dumps(data)))
					with open(COM.gJsonDir+flora_name+'.json', 'w', encoding="utf-8") as make_file:
						json.dump(data, make_file, ensure_ascii=False, indent="\t")
						
					#to make device.json file
					datas = []
					datas.append(self.device_id)
					datas.append(GLOB.readConfig(configFileNM, 'SETUP', 'mod', ''))
					datas.append(GLOB.readConfig(controlFileNM, 'CONTROL', 'alarm', '0'))
					datas.append(str(data['temperature']))
					datas.append('0')
					datas.append(str(data['moisture']))
					datas.append(str(data['conductivity']))
					datas.append(str(data['light']))
					datas.append(str(data['battery']))
					datas.append(GLOB.readConfig(controlFileNM, 'CONTROL', 'active' , '0')) # active
					datas.append(GLOB.readConfig(controlFileNM, 'CONTROL', 'light' , '0')) # LED 조명
					datas.append(GLOB.readConfig(controlFileNM, 'CONTROL', 'pump'  , '0')) # 워터펌프
					datas.append(GLOB.readConfig(controlFileNM, 'CONTROL', 'fan'   , '0')) # 팬
					datas.append(GLOB.readConfig(controlFileNM, 'CONTROL', 'heater', '0')) # 히터
					datas.append(COM.gstrYMDHMS)
					datas.append(GLOB.loadTeamviewerID())
					
					rc = self.encodeStatJson(COM.gJsonDir+'device.json', datas)
					if rc == 0:
						LOG.writeLn('%s	[%s]	%s  %s  %s  %s  %s' % (data['name'], data['battery'], data['temperature'], data['moisture'], data['light'], data['conductivity'], data['mac']))
				except Exception as e :
					LOG.writeLn("[ERROR][FLOWERCARE] : %s" % e)

				if rc == 0:
					if GLOB.appendWATERsControlInfo(COM.gJsonDir+"device.json", GLOB.readConfig(controlFileNM, 'CONTROL', 'active', '0')
					, GLOB.readConfig(controlFileNM, 'CONTROL', 'light', '0')
					, GLOB.readConfig(controlFileNM, 'CONTROL', 'pump', '0')
					, GLOB.readConfig(controlFileNM, 'CONTROL', 'fan', '0')
					, GLOB.readConfig(controlFileNM, 'CONTROL', 'heater', '0')
					) == 0 :
						REQUEST.updateDIYs(self.user_id, self.device_id)
				
				
			if self.daemon_enabled:
				#print_line('Sleeping ({} seconds) ...'.format(sleep_period))
				sleep(self.sleep_period)
				#print()
			else:
				LOG.writeLn('Execution finished in non-daemon-mode')
				break

	
	def atOnce(self):
		self.chkSensor()
		GLOB.setUpdateTime()
		self.confUpdate()
		for [flora_name, flora] in self.flores.items():
			data = dict()
			attempts = 2
			flora['poller']._cache = None
			flora['poller']._last_read = None
			flora['stats']['count'] = flora['stats']['count'] + 1
			#print_line('Retrieving data from sensor "{}" ...'.format(flora['name_pretty']))
			while attempts != 0 and not flora['poller']._cache:
				try:
					flora['poller'].fill_cache()
					flora['poller'].parameter_value(MI_LIGHT)
				except (IOError, BluetoothBackendException):
					attempts = attempts - 1
					if attempts > 0:
						LOG.writeLn('Retrying ...')
					flora['poller']._cache = None
					flora['poller']._last_read = None

			if not flora['poller']._cache:
				flora['stats']['failure'] = flora['stats']['failure'] + 1
				LOG.writeLn('Failed to retrieve data from Mi Flora sensor "{}" ({}), success rate: {:.0%}'.format(
					flora['name_pretty'], flora['mac'], flora['stats']['success']/flora['stats']['count']
					))
				print()
				continue
			else:
				flora['stats']['success'] = flora['stats']['success'] + 1

			for param,_ in mParameters.items():
				data[param] = flora['poller'].parameter_value(param)
			
			rc = -1
			try:
				data['timestamp']   = COM.gstrDATE
				data['name']        = flora_name
				data['name_pretty'] = flora['name_pretty']
				data['mac']         = flora['mac']
				data['firmware']    = flora['firmware']
				
				#print('Data for "{}": {}'.format(flora_name, json.dumps(data)))
				with open(COM.gJsonDir+flora_name+'.json', 'w', encoding="utf-8") as make_file:
					json.dump(data, make_file, ensure_ascii=False, indent="\t")
					
				#to make device.json file
				datas = []
				datas.append(self.device_id)
				datas.append(GLOB.readConfig(configFileNM, 'SETUP', 'mod', ''))
				datas.append(GLOB.readConfig(configFileNM, 'AGENT', 'alarm', '0'))
				datas.append(str(data['temperature']))
				datas.append('0')
				datas.append(str(data['moisture']))
				datas.append(str(data['conductivity']))
				datas.append(str(data['light']))
				datas.append(str(data['battery']))
				datas.append(GLOB.readConfig(controlFileNM, 'CONTROL', 'active' , '0')) # active
				datas.append(GLOB.readConfig(controlFileNM, 'CONTROL', 'light' , '0')) # LED 조명
				datas.append(GLOB.readConfig(controlFileNM, 'CONTROL', 'pump'  , '0')) # 워터펌프
				datas.append(GLOB.readConfig(controlFileNM, 'CONTROL', 'fan'   , '0')) # 팬
				datas.append(GLOB.readConfig(controlFileNM, 'CONTROL', 'heater', '0')) # 히터
				datas.append(COM.gstrYMDHMS)
				datas.append(GLOB.loadTeamviewerID())
				
				rc = self.encodeStatJson(COM.gJsonDir+'device.json', datas)
				if rc == 0:
					LOG.writeLn('%s	[%s]	%s  %s  %s  %s  %s' % (data['name'], data['battery'], data['temperature'], data['moisture'], data['light'], data['conductivity'], data['mac']))
			except Exception as e :
				LOG.writeLn("[ERROR][FLOWERCARE] : %s" % e)

			if rc == 0:
				if GLOB.appendWATERsControlInfo(COM.gJsonDir+"device.json", GLOB.readConfig(controlFileNM, 'CONTROL', 'active', '0')
					, GLOB.readConfig(controlFileNM, 'CONTROL', 'light', '0')
					, GLOB.readConfig(controlFileNM, 'CONTROL', 'pump', '0')
					, GLOB.readConfig(controlFileNM, 'CONTROL', 'fan', '0')
					, GLOB.readConfig(controlFileNM, 'CONTROL', 'heater', '0')
					) == 0 :
					REQUEST.updateDIYs(self.user_id, self.device_id)