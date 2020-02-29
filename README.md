# Rika_Firenet_AddOn


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
