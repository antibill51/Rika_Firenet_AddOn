global clientrika, url_base, url_api, stove, client

import sys
import time
import yaml
import requests
import json
import datetime
import paho.mqtt.client as mqtt
import os
from pathlib import Path
import colorama
from colorama import Fore, Back, Style
from threading import Thread

requests.packages.urllib3.disable_warnings()

import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup # parse page

web_response = ""
def load_config(config_file):
    with open(config_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
#RIKA connect
def connect(clientrika, url_base, url_login, url_stove, user, pwd) :
    data = {
        'email':user,
        'password':pwd}

    # retreive content of the web site in case of extended verbose
    global web_response

    r = clientrika.post(url_base+url_login, data)
    web_response = r.text

    if ('logout' in r.text) == True :
        print(Fore.GREEN + '               Connected to Rika !' + Fore.RESET)

        soup = BeautifulSoup(r.content, "html.parser")
        text = soup.find("ul", {"id": "stoveList"})
        if text is not None :
            stoveName = text.find('a').text
            a = text.find('a', href=True)
            stove = a['href'].replace(url_stove,'')
            return stove

    return ""
# Thread sent to stove
class send_to_stove(Thread):
    def __init__(set_stove_parameter, data):
        Thread.__init__(set_stove_parameter)
        set_stove_parameter.data = data

    def run(set_stove_parameter):
            r = clientrika.post(url_base+url_api+stove+'/controls', set_stove_parameter.data)
            senddata_to_mqtt()
            for counter in range (0,10) :
                if ('OK' in r.text) == True :
                    print(Fore.WHITE + "Send OK (" + current_time + ")")
                    #senddata_to_mqtt()
                    return True
                else :
                    print(Fore.WHITE + 'Send try.. ({}/10)'.format(counter + 1) + " (" + current_time + ")")
                    time.sleep(2)
# Get stove information
def get_stove_information(clientrika, url_base, url_api, stove) :
    r = ''
    while r == '':
        try:
            r = clientrika.get(url_base+url_api+stove+'/status?nocache=')
            return r.json()
        except:
            print("Connection refused by the server..")
            time.sleep(15)
            continue
# show all for debug mode
def show_stove_information(data) :

    print(Fore.CYAN + "Global :" + Fore.RESET)
    print(Fore.WHITE + "               Stove                  : " + Fore.YELLOW + "{0} [{1}]".format(data['name'],data['stoveID']))
    print(Fore.WHITE + "               Last seen              : " + Fore.YELLOW + "{} min ago".format(data['lastSeenMinutes']))
    lastConfirmedRevision = time.strftime('%d/%m/%Y %H:%M', time.localtime(data['lastConfirmedRevision']))
    print(Fore.WHITE + "               Last Revision          : " + Fore.YELLOW + "{}".format(lastConfirmedRevision))

    print(Fore.CYAN + "Control : ")
    revision = time.strftime('%d/%m/%Y %H:%M', time.localtime(data['controls']['revision']))
    print(Fore.WHITE + "               Last Revision          : " + Fore.YELLOW + "{}".format(revision))

    if data['controls']['onOff'] :
        print(Fore.WHITE + "               Stove                  : " + Fore.GREEN + "is online")
        jstovectl = "Online"
    else :
        print(Fore.WHITE + "               Stove                  : " + Fore.RED + "is offline")
        jstovectl = "Offline"

    if data['controls']['operatingMode'] == 0 :
        print(Fore.WHITE + "               Operating mode         : " + Fore.YELLOW + "Manual with {}% power".format(data['controls']['heatingPower']))
        jstovemode = "Manual"
    elif data['controls']['operatingMode'] == 1 :
        print(Fore.WHITE + "               Operating mode         : " + Fore.YELLOW + "Automatic with {}% power".format(data['controls']['heatingPower']))
        jstovemode = "Automatic"
    elif data['controls']['operatingMode'] == 2 :
        print(Fore.WHITE + "               Operating mode         : " + Fore.YELLOW + "Comfort with {}% power".format(data['controls']['heatingPower']))
        jstovemode = "Comfort"

    print(Fore.WHITE + "               Target Temperature     : " + Fore.YELLOW + "{} degC".format(data['controls']['targetTemperature']))
    print(Fore.WHITE + "               Protection Temperature : " + Fore.YELLOW + "{} degC".format(data['controls']['setBackTemperature']))

    print(Fore.CYAN + "Sensors : ")
    if data['sensors']['statusMainState'] == 1 :
        if data['sensors']['statusSubState'] == 0 :
            print(Fore.WHITE + "               Stove                  : " + Fore.YELLOW + "OFF")
            jstove = "Off"
        elif data['sensors']['statusSubState'] == 1 or data['sensors']['statusSubState'] == 3:
            print(Fore.WHITE + "               Stove                  : " + Fore.YELLOW + "Standby")
            jstove = "Standby"
        elif data['sensors']['statusSubState'] == 2 :
            print(Fore.WHITE + "               Stove                  : " + Fore.YELLOW + "External command")
            jstove = "External Command"
        else :
            print(Fore.WHITE + "               Stove                  : " + Fore.YELLOW + "Unknown State")
            jstove = "UnKnown State"
    elif data['sensors']['statusMainState'] == 2 :
        print(Fore.WHITE + "               Stove                  : " + Fore.YELLOW + "Waking up")
        jstove = "Waking Up"
    elif data['sensors']['statusMainState'] == 3 :
        print(Fore.WHITE + "               Stove                  : " + Fore.YELLOW + "Starting")
        jstove = "Starting"
    elif data['sensors']['statusMainState'] == 4 :
        print(Fore.WHITE + "               Stove                  : " + Fore.YELLOW + "Burning (control mode)")
        jstove = "Burning (control mode)"
    elif data['sensors']['statusMainState'] == 5 :
        if data['sensors']['statusSubState'] == 3 or data['sensors']['statusSubState'] == 4 :
            print(Fore.WHITE + "               Stove                  : " + Fore.YELLOW + "Deep Cleaning")
            jstove = "Deep Cleaning"
        else :
            print(Fore.WHITE + "               Stove                  : " + Fore.YELLOW + "Cleaning")
            jstove = "Cleaning"
    elif data['sensors']['statusMainState'] == 6 :
        print(Fore.WHITE + "               Stove                  : " + Fore.YELLOW + "Burn OFF")
        jstove = "Burn Off"
    else :
        print(Fore.WHITE + "               Stove                  : " + Fore.YELLOW + "Unknown state")
        jstove = "Unknown Stove State"

    print(Fore.WHITE + "               Room Temperature       : " + Fore.YELLOW + "{} degC".format(data['sensors']['inputRoomTemperature']))
    print(Fore.WHITE + "               Flame Temperature      : " + Fore.YELLOW + "{} degC".format(data['sensors']['inputFlameTemperature']))

    print(Fore.WHITE + "               Pellets consumption    : " + Fore.YELLOW + "{0} Kg ({1} h)".format(
        data['sensors']['parameterFeedRateTotal'],
        data['sensors']['parameterRuntimePellets']))

    pellets_bags = round((int(data["sensors"]["parameterFeedRateTotal"]) / 15), 2)
    print(Fore.WHITE + "               Pellets bags   : " + Fore.YELLOW + str(pellets_bags) + " bags")

    print(Fore.WHITE + "               Diag Motor             : " + Fore.YELLOW + "{} %".format(data['sensors']['outputDischargeMotor']))
    print(Fore.WHITE + "               Fan velocity           : " + Fore.YELLOW + "{} rps".format(data['sensors']['outputIDFan']))

    # json_data = {"SENSOR":{"check_time": current_time, "stove_status": jstove, "room_temp": int(data["sensors"]["inputRoomTemperature"]), "flame_temp": data["sensors"]["inputFlameTemperature"], "pellets_used": data["sensors"]["parameterFeedRateTotal"], "pellets_time": data["sensors"]["parameterRuntimePellets"], "diag_motor": data["sensors"]["outputDischargeMotor"],"fan_velocity": data["sensors"]["outputIDFan"]}, "STATE":{"stove_status": jstovectl, "revision_date": time.strftime("%d/%m/%Y"), "revision_time": time.strftime("%H:%M"), "operating_mode": jstovemode, "target_temp": int(data["controls"]["targetTemperature"]), "protection_temp": data["controls"]["setBackTemperature"]}}
    # #print(json.dumps(json_data, sort_keys=True, indent=2))
    # with open(json_path, 'w') as text_file:
    #     #print(json_data, file=text_file)
    #     print(json.dumps(json_data, sort_keys=True), file=text_file)
    # return json_data


def tosend_stove_information(data) :


    lastConfirmedRevision = time.strftime('%d/%m/%Y %H:%M', time.localtime(data['lastConfirmedRevision']))
    revision = time.strftime('%d/%m/%Y %H:%M', time.localtime(data['controls']['revision']))
    if data['controls']['onOff'] :
        jstovectl = "Online"
    else :
        jstovectl = "Offline"

    if data['controls']['operatingMode'] == 0 :
        jstovemode = "Manual"
    elif data['controls']['operatingMode'] == 1 :
        jstovemode = "Automatic"
    elif data['controls']['operatingMode'] == 2 :
        jstovemode = "Comfort"
    if data['sensors']['statusMainState'] == 1 :
        if data['sensors']['statusSubState'] == 0 :
            jstove = "Off"
        elif data['sensors']['statusSubState'] == 1 or data['sensors']['statusSubState'] == 3:
            jstove = "Standby"
        elif data['sensors']['statusSubState'] == 2 :
            jstove = "External Command"
        else :
            jstove = "UnKnown State"
    elif data['sensors']['statusMainState'] == 2 :
        jstove = "Waking Up"
    elif data['sensors']['statusMainState'] == 3 :
        jstove = "Starting"
    elif data['sensors']['statusMainState'] == 4 :
        jstove = "Burning (control mode)"
    elif data['sensors']['statusMainState'] == 5 :
        if data['sensors']['statusSubState'] == 3 or data['sensors']['statusSubState'] == 4 :
            jstove = "Deep Cleaning"
        else :
            jstove = "Cleaning"
    elif data['sensors']['statusMainState'] == 6 :
        jstove = "Burn Off"
    else :
        jstove = "Unknown Stove State"

    pellets_bags = round((int(data["sensors"]["parameterFeedRateTotal"]) / 15), 2)

    json_data = {"SENSOR":{"check_time": current_time, "stove_status": jstove, "heating_power": int(data["controls"]["heatingPower"]), "room_temp": int(data["sensors"]["inputRoomTemperature"]), "flame_temp": data["sensors"]["inputFlameTemperature"], "pellets_used": data["sensors"]["parameterFeedRateTotal"], "pellets_time": data["sensors"]["parameterRuntimePellets"], "pellets_before_service": data["sensors"]["parameterFeedRateService"], "diag_motor": data["sensors"]["outputDischargeMotor"],"fan_velocity": data["sensors"]["outputIDFan"]}, "STATE":{"fan1_active": data["controls"]["convectionFan1Active"], "fan1_level": data["controls"]["convectionFan1Level"], "fan1_area": data["controls"]["convectionFan1Area"], "fan2_active": data["controls"]["convectionFan2Active"], "fan2_level": data["controls"]["convectionFan2Level"], "fan2_area": data["controls"]["convectionFan2Area"], "frost_protection_active": data["controls"]["frostProtectionActive"], "front_protection_temp": data["controls"]["frostProtectionTemperature"], "stove_status": jstovectl, "revision_date": time.strftime("%d/%m/%Y"), "revision_time": time.strftime("%H:%M"), "operating_mode": jstovemode, "target_temp": int(data["controls"]["targetTemperature"]), "protection_temp": data["controls"]["setBackTemperature"]}}
    #print(json.dumps(json_data, sort_keys=True, indent=2))
    with open(json_path, 'w') as text_file:
        #print(json_data, file=text_file)
        print(json.dumps(json_data, sort_keys=True), file=text_file)
    return json_data    
# MQTT connect
def on_connect(client, userdata, flags, rc):
    if client.connected_flag == False :
        client.subscribe(topicreceiver)
        if rc==0:
            client.connected_flag=True #set flag
            print(Fore.WHITE + "                                      : " + Fore.GREEN + "Connected!" + Fore.RESET)
        else:
            print(Fore.RED + "               Bad connection Returned code=" + Fore.RESET,rc)
# On each MQTT message   
def senddata_to_mqtt():
        # Get information
    stove_infos = get_stove_information(clientrika, url_base, url_api, stove)
    data = tosend_stove_information(stove_infos)
    data_out = json.dumps(data, sort_keys=True)
    time.sleep(3)
    print("               Sending MQTT data      : Please wait...")
    client.publish(topicpublisher,data_out)
    print(Fore.WHITE + "                                      : " + Fore.GREEN + "MQTT Sent" + Fore.RESET)
    time.sleep(2)
    print(Fore.CYAN + "Process done !" + Fore.RESET)
    time.sleep(time_between_send) 
    
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    actual = get_stove_information(clientrika, url_base, url_api, stove)
    data = actual['controls']
    parameter = 0
    # #' revision': 1582916991
    # if "revision" in payload:
    #     parameter = "revision"
    #     value = payload[parameter]
    #     data[parameter] = str(value)    
    # 'onOff': True, 
    if "onOff" in payload:
        parameter = "onOff"
        value = payload[parameter]
        data[parameter] = bool(value)
    # 'operatingMode': 0, 
    if "operatingMode" in payload:
        parameter = "operatingMode"
        value = payload[parameter]
        data[parameter] = int(value)
    # 'heatingPower': 30, 
    if "heatingPower" in payload:
        parameter = "heatingPower"
        parameter = str(parameter)
        value = payload[parameter]
        data[parameter] = int(value)
    # 'targetTemperature': '20', 
    if "targetTemperature" in payload:
        parameter = "targetTemperature"
        value = payload[parameter]
        data[parameter] = int(value)       
    # # 'ecoMode': False, 
    # if "ecoMode" in payload:
    #     parameter = "ecoMode"
    #     value = payload[parameter]
    #     data[parameter] = bool(value)
    # # 'heatingTimeMon1': '00000000', 
    # if "heatingTimeMon1" in payload:
    #     parameter = "heatingTimeMon1"
    #     value = payload[parameter]
    #     data[parameter] = str(value)
    # # 'heatingTimeMon2': '00000000',
    # if "heatingTimeMon2" in payload:
    #     parameter = "heatingTimeMon2"
    #     value = payload[parameter]
    #     data[parameter] = str(value) 
    # # 'heatingTimeTue1': '00000000', 
    # if "heatingTimeTue1" in payload:
    #     parameter = "heatingTimeTue1"
    #     value = payload[parameter]
    #     data[parameter] = str(value)
    # # 'heatingTimeTue2': '00000000', 
    # if "heatingTimeTue2" in payload:
    #     parameter = "heatingTimeTue2"
    #     value = payload[parameter]
    #     data[parameter] = str(value)
    # # 'heatingTimeWed1': '00000000', 
    # if "heatingTimeWed1" in payload:
    #     parameter = "heatingTimeWed1"
    #     value = payload[parameter]
    #     data[parameter] = str(value)
    # # 'heatingTimeWed2': '00000000', 
    # if "heatingTimeWed2" in payload:
    #     parameter = "heatingTimeWed2"
    #     value = payload[parameter]
    #     data[parameter] = str(value)
    # # 'heatingTimeThu1': '00000000', 
    # if "heatingTimeThu1" in payload:
    #     parameter = "heatingTimeThu1"
    #     value = payload[parameter]
    #     data[parameter] = str(value)
    # # 'heatingTimeThu2': '00000000', 
    # if "heatingTimeThu2" in payload:
    #     parameter = "heatingTimeThu2"
    #     value = payload[parameter]
    #     data[parameter] = str(value)
    # # 'heatingTimeFri1': '00000000', 
    # if "heatingTimeFri1" in payload:
    #     parameter = "heatingTimeFri1"
    #     value = payload[parameter]
    #     data[parameter] = str(value)
    # # 'heatingTimeFri2': '00000000', 
    # if "heatingTimeFri2" in payload:
    #     parameter = "heatingTimeFri2"
    #     value = payload[parameter]
    #     data[parameter] = str(value)
    # # 'heatingTimeSat1': '00000000', 
    # if "heatingTimeSat1" in payload:
    #     parameter = "heatingTimeSat1"
    #     value = payload[parameter]
    #     data[parameter] = str(value)
    # # 'heatingTimeSat2': '00000000', 
    # if "heatingTimeSat2" in payload:
    #     parameter = "heatingTimeSat2"
    #     value = payload[parameter]
    #     data[parameter] = str(value)
    # # 'heatingTimeSun1': '00000000', 
    # if "heatingTimeSun1" in payload:
    #     parameter = "heatingTimeSun1"
    #     value = payload[parameter]
    #     data[parameter] = str(value)
    # # 'heatingTimeSun2': '00000000', 
    # if "heatingTimeSun2" in payload:
    #     parameter = "heatingTimeSun2"
    #     value = payload[parameter]
    #     data[parameter] = str(value)
    # # 'heatingTimesActiveForComfort': True, 
    if "heatingTimesActiveForComfort" in payload:
        parameter = "heatingTimesActiveForComfort"
        value = payload[parameter]
        data[parameter] = bool(value)
    # 'setBackTemperature': '14', 
    if "setBackTemperature" in payload:
        parameter = "setBackTemperature"
        value = payload[parameter]
        data[parameter] = int(value)
    # 'convectionFan1Active': True, 
    if "convectionFan1Active" in payload:
        parameter = "convectionFan1Active"
        value = payload[parameter]
        data[parameter] = bool(value)
    # 'convectionFan1Level': 0, 
    if "convectionFan1Level" in payload:
        parameter = "convectionFan1Level"
        value = payload[parameter]
        data[parameter] = int(value)
    # 'convectionFan1Area': 16,   
    if "convectionFan1Area" in payload:
        parameter = "convectionFan1Area"
        value = payload[parameter]
        data[parameter] = int(value)
    # 'convectionFan2Active': True, 
    if "convectionFan2Active" in payload:
        parameter = "convectionFan2Active"
        value = payload[parameter]
        data[parameter] = bool(value)
    # 'convectionFan2Level': 0, 
    if "convectionFan2Level" in payload:
        parameter = "convectionFan2Level"
        value = payload[parameter]
        data[parameter] = int(value)
    # 'convectionFan2Area': -20, 
    if "convectionFan2Area" in payload:
        parameter ="convectionFan2Area"
        value = payload[parameter]
        data[parameter] = int(value)
    # 'frostProtectionActive': False, 
    if "frostProtectionActive" in payload:
        parameter ="frostProtectionActive"
        value = payload[parameter]
        data[parameter] = bool(value)
    # 'frostProtectionTemperature': '10', 
    if "frostProtectionTemperature" in payload:
        parameter ="frostProtectionTemperature"
        value = payload[parameter]
        data[parameter] = int(value)
    # # 'temperatureOffset': '0', 
    # if "temperatureOffset" in payload:
    #     parameter ="temperatureOffset"
    #     value = payload[parameter]
    #     data[parameter] = int(value)
    # # 'RoomPowerRequest': 0, 
    # if "RoomPowerRequest" in payload:
    #     parameter ="RoomPowerRequest"
    #     value = payload[parameter]
    #     data[parameter] = int(value)
    # # 'debug0': 0, 
    # if "debug0" in payload:
    #     parameter ="debug0"
    #     value = payload[parameter]
    #     data[parameter] = int(value) 
    # # 'debug1': 0, 
    # if "debug1" in payload:
    #     parameter ="debug1"
    #     value = payload[parameter]
    #     data[parameter] = int(value)
    # # 'debug2': 0, 
    # if "debug2" in payload:
    #     parameter ="debug2"
    #     value = payload[parameter]
    #     data[parameter] = int(value)
    # # 'debug3': 0, 
    # if "debug3" in payload:
    #     parameter ="debug3"
    #     value = payload[parameter]
    #     data[parameter] = int(value)
    # # 'debug4': 0
    # if "debug4" in payload:
    #     parameter ="debug4"
    #     value = payload[parameter]
    #     data[parameter] = int(value)
    if parameter != 0:
        thread1 = send_to_stove(data)
        thread1.start()

if __name__ == "__main__":

    config_file = Path(os.path.dirname(__file__) + "/config/rika_config.yaml")
    #print('basename:    ', os.path.basename(__file__))
    #print('dirname:     ', os.path.dirname(__file__))

    if config_file.exists():
        config = load_config(config_file)

    else:
        error_text = """
        The configuration file is missing !
        Please create the following file:
        
        Name : rika_config.yaml
        Add the following items (and fill the missing data):
        system:
            url_base: 'https://www.rika-firenet.com'
            url_login: '/web/login'
            url_stove: '/web/stove/'
            url_api: '/api/client/'
            json_path: ''
            verbose: ''
            verbose_extended: ''
        user:
            username: ''
            password: ''
        mqtt:
            server_address: ''
            topicreceiver: ''
            topicpublisher: ''
            client: ''
            client_username: ''
            client_password: ''
            time_between_send: ''
        """
        print(error_text)
        exit()

    user = config['user']['username']
    pwd = config['user']['password']
    current_time = datetime.datetime.now().date().strftime("%d.%m.%y") + " " + datetime.datetime.now().time().strftime("%H:%M")
    url_base = config['system']['url_base']
    url_login = config['system']['url_login']
    url_stove = config['system']['url_stove']
    url_api = config['system']['url_api']
    json_path = config['system']['json_path']
    mqtt_server = config['mqtt']['server_address']
    topicpublisher = config['mqtt']['topicpublisher']
    topicreceiver = config['mqtt']['topicreceiver'] 
    time_between_send = int(config['mqtt']['time_between_send'])
    clientrika = requests.session()
    clientrika.verify = False

    print(Fore.CYAN + "Information : ")
    print(Fore.WHITE + "               Starting Rika Update (" + current_time + ")")
    print(Fore.WHITE + "               Connecting to Firenet...")
    stove = connect(clientrika, url_base, url_login, url_stove, user, pwd)

    if len(stove) == 0 :
        print(Fore.RED + "               No RIKA found (connection failed ?)" + Fore.RESET)
        sys.exit(1)

    # Create flag in class
    mqtt.Client.connected_flag=False
    client=mqtt.Client(config['mqtt']['client'])
    client.username_pw_set(username=config['mqtt']['client_username'],password=config['mqtt']['client_password'])
   # Bind call back function
    client.on_connect = on_connect
    client.on_message = on_message
    print(Fore.CYAN + "MQTT :")
    print(Fore.WHITE + "               Connecting to broker   :" + Fore.RESET, mqtt_server)
    client.connect(mqtt_server)
    client.loop_start()
    while 1:
        senddata_to_mqtt()


    # To display result of the API, uncomment following line
    if config['system']['verbose'] == "True":
        stove_json = show_stove_information(stove_infos)
        print("")
        print("JSON CONTENT (RESULT OF DATA RETRIEVAL)")
        print("----------------------------------------------------------------------------------------------")
        print(stove_infos)
        print("----------------------------------------------------------------------------------------------")
        if config['system']['verbose_extended'] == 'True':
            print("")
            print("HTML CONTENT FROM RIKA WEBSITE")
            print("----------------------------------------------------------------------------------------------")
            print(web_response)
            print("----------------------------------------------------------------------------------------------")
