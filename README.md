# Rika_Firenet_AddOn

## Outdated (New here : https://github.com/antibill51/rika-firenet-custom-component)

File in /config/ :

rika_config.yaml

system:
  url_base: 'https://www.rika-firenet.com' # FIRENET Main page URL
  url_login: '/web/login' # FIRENET Login page partial URL
  url_stove: '/web/stove/' # FIRENET Stove page partial URL
  url_api: '/api/client/' # FIRENET API patirl URL
  json_path: '/yaml' # Local PATH to save JSON file
  verbose: 'False' # Dump the content of the JSON file once process is done - Value : True or False
  verbose_extended: 'False' # Dump extended content, including the Rika website page one logged : True of False

user:
  username: '' # FIRENET User Name
  password: '' # FIRENET Password

mqtt:
  server_address: '' # MQTT IP address
  topicreceiver: 'tele/rika/COMMAND'
  topicpublisher: 'tele/rika/SENSOR' # MQTT Topic (sample: tele/rika/SENSOR)
  client: 'rika' # MQTT Client Name (sample: rika)
  client_username: '' # MQTT Client Username (if applicable)
  client_password: '' # MQTT Client Password (if applicable)
  time_between_send: '300' # in seconds
  
  
  #---------------------------------End of file---------------------------------
  
  
Commands exemple: 

'onOff': True, 
'operatingMode': 0, 
'heatingPower': 30, 
'targetTemperature': '20', 
'ecoMode': False, 
'heatingTimesActiveForComfort': True, 
'setBackTemperature': '14', 
'convectionFan1Active': True, 
'convectionFan1Level': 0, 
'convectionFan1Area': 16, 
'convectionFan2Active': True, 
'convectionFan2Level': 0, 
'convectionFan2Area': -20, 
'frostProtectionActive': False, 
'frostProtectionTemperature': '10', 
'temperatureOffset': '0', 
'RoomPowerRequest': 0, 
'debug0': 0, 
'debug1': 0, 
'debug2': 0, 
'debug3': 0, 
'debug4': 0
  
  
  
Sensors exemple :

'sensors': {'inputRoomTemperature': '20', 'inputFlameTemperature': 332, 'statusError': 0, 'statusSubError': 0, 'statusWarning': 0, 'statusService': 0, 'outputDischargeMotor': 220, 'outputDischargeCurrent': 0, 'outputIDFan': 1002, 'outputIDFanTarget': 0, 'outputInsertionMotor': 0, 'outputInsertionCurrent': 0, 'outputAirFlaps': 0, 'outputAirFlapsTargetPosition': 0, 'outputBurnBackFlapMagnet': False, 'outputGridMotor': False, 'outputIgnition': False, 'inputUpperTemperatureLimiter': False, 'inputPressureSwitch': False, 'inputPressureSensor': 0, 'inputGridContact': False, 'inputDoor': False, 'inputCover': False, 'inputExternalRequest': True, 'inputBurnBackFlapSwitch': False, 'inputFlueGasFlapSwitch': False, 'inputBoardTemperature': '0', 'inputCurrentStage': 0, 'inputTargetStagePID': 0, 'inputCurrentStagePID': 0, 'statusMainState': 4, 'statusSubState': 3, 'statusWifiStrength': 0, 'parameterEcoModePossible': False, 'parameterFabricationNumber': 0, 'parameterStoveTypeNumber': 13, 'parameterLanguageNumber': 0, 'parameterVersionMainBoard': 225, 'parameterVersionTFT': 225, 'parameterVersionWiFi': 104, 'parameterVersionMainBoardBootLoader': 0, 'parameterVersionTFTBootLoader': 0, 'parameterVersionWiFiBootLoader': 0, 'parameterVersionMainBoardSub': 0, 'parameterVersionTFTSub': 0, 'parameterVersionWiFiSub': 0, 'parameterRuntimePellets': 533, 'parameterRuntimeLogs': 0, 'parameterFeedRateTotal': 592, 'parameterFeedRateService': 108, 'parameterServiceCountdownKg': 0, 'parameterServiceCountdownTime': 0, 'parameterIgnitionCount': 0, 'parameterOnOffCycleCount': 26, 'parameterFlameSensorOffset': 0, 'parameterPressureSensorOffset': 0, 'parameterErrorCount0': 0, 'parameterErrorCount1': 0, 'parameterErrorCount2': 0, 'parameterErrorCount3': 0, 'parameterErrorCount4': 0, 'parameterErrorCount5': 0, 'parameterErrorCount6': 0, 'parameterErrorCount7': 0, 'parameterErrorCount8': 0, 'parameterErrorCount9': 0, 'parameterErrorCount10': 0, 'parameterErrorCount11': 0, 'parameterErrorCount12': 0, 'parameterErrorCount13': 0, 'parameterErrorCount14': 0, 'parameterErrorCount15': 0, 'parameterErrorCount16': 0, 'parameterErrorCount17': 0, 'parameterErrorCount18': 0, 'parameterErrorCount19': 0, 'statusHeatingTimesNotProgrammed': False, 'statusFrostStarted': False, 'parameterSpiralMotorsTuning': 0, 'parameterIDFanTuning': 0, 'parameterCleanIntervalBig': 0, 'parameterKgTillCleaning': 0, 'parameterDebug0': 0, 'parameterDebug1': 0, 'parameterDebug2': 0, 'parameterDebug3': 0, 'parameterDebug4': 0}, 'stoveType': 'DOMO MultiAir', 'stoveFeatures': {'multiAir1': True, 'multiAir2': True, 'insertionMotor': False, 'airFlaps': False, 'logRuntime': False}, 'oem': 'RIKA'}
