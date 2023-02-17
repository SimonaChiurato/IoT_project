import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
import sys
from MyMQTT import *




class EchoBot1:

    exposed = True

    def __init__(self, token, Home_catalog_settings, Manager_sensor_settings, infoPatients):


        self.tokenBot = token

        self.Home_catalog_settings = Home_catalog_settings
        self.Manager_sensor_settings = Manager_sensor_settings


        self.infoPatients = json.load(open(infoPatients))
        self.bot = telepot.Bot(self.tokenBot)
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                               'callback_query': self.on_callback_query}).run_as_thread()

        Home_get_string = "http://" + self.Home_catalog_settings["ip_address"] + ":" + str(
            self.Home_catalog_settings["ip_port"]) + "/resource_catalogs"
        rc_info = json.loads(requests.get(Home_get_string).text)
        self.rooms = []

        self.clientID = 'telegramsubscriber'

        self.client = MyMQTT(self.clientID, Manager_sensor_settings['broker'], Manager_sensor_settings['broker_port'],
                             self)

        request_string = "http://" + rc_info["ip_address"] + ":" + str(rc_info["ip_port"]) + "/all"
        patients = json.loads(requests.get(request_string).text)
        print(patients)
        for patient in patients.values():
            print(patient)
            sensors = []
            for dev in patient:
                if dev["ID_sensor"] == 'sensor_th_1':
                    for type in dev['sensortype']:
                        sensors.append(type)
                else:
                    sensors.append(dev['sensortype'])
            # Which sensors are in the room of patient X
            self.rooms.append({"room_name": dev["patient"], "room_sensors": sensors})


    def run(self):
        self.client.start()

    def end(self):
      self.client.stop()

    def follow(self, topic):
      self.client.mySubscribe(topic)


   
    def run(self):
        self.client.start()

    def end(self):
        self.client.stop()

    def follow(self, topic):
        self.client.mySubscribe(topic)

    def notify(self, topic, msg):
        payload = json.loads(msg)
        warning_dict = json.loads(payload)

        chatID_doc= []

        for p in self.infoPatients['patients'].values():
            if p == warning_dict['patient']:
                chat_ID = p["chatID"]


        for p in self.infoPatients['doctors'].values():
            chatID_doc.append(p["chatID"])

        if warning_dict['warning'] == 'min':
            self.bot.sendMessage(chat_ID,'The' + str(warning_dict['type']) +'value is too low : '+ str(warning_dict['value']) + str(warning_dict['unit']))
            for d in chatID_doc:
                self.bot.sendMessage(d,'Patient: ' + str(warning_dict['patient']) + 'The' + str(warning_dict['type']) +'value is too low : '+ str(warning_dict['value']) + str(warning_dict['unit']))
        if warning_dict['warning'] == 'max':
            self.bot.sendMessage(chat_ID,'The' + str(warning_dict['type']) +'value is too high : '+ str(warning_dict['value']) + str(warning_dict['unit']))
            for d in chatID_doc:
                self.bot.sendMessage(d,'Patient: ' + str(warning_dict['patient']) + 'The' + str(warning_dict['type']) +'value is too high : '+ str(warning_dict['value']) + str(warning_dict['unit']))
        if warning_dict['warning'] == 'max_good':
            self.bot.sendMessage(chat_ID,'The' + str(warning_dict['type']) +'value is near the high limit : '+ str(warning_dict['value']) + str(warning_dict['unit']))
            for d in chatID_doc:
                self.bot.sendMessage(d,'Patient: ' + str(warning_dict['patient']) + 'The' + str(warning_dict['type']) +'value is near the high limit : '+ str(warning_dict['value']) + str(warning_dict['unit']))


    # fare il controllo e salvataggio id
    def checkRegistration(self, chat_ID):
        for p in self.infoPatients['patients'].values():
            if chat_ID == p["chatID"]:
                return True
        for p in self.infoPatients['doctors'].values():
            if chat_ID == p["chatID"]:
                return True
        return False

    def checkDoctor(self, chat_ID):
        for p in self.infoPatients['doctors'].values():
            if chat_ID == p["chatID"]:
                return True
        return False

    def findPatient(self, chat_ID):
        for p in self.infoPatients['patients'].values():
            if chat_ID == p["chatID"]:
                return p["name"]
        return ""

    def registration(self, chat_ID, message):
        if message.startswith('/Doctor'):
            params = message.split()[1:]
            if len(params) != 3:
                self.bot.sendMessage(chat_ID,
                                     'Check that you have write your name + your surname and the hospital password')
            else:
                if params[2] == 'password':
                    k = len(self.infoPatients['doctors'].keys())
                    k = str(k + 1)
                    self.infoPatients['doctors'][k] = {}
                    self.infoPatients['doctors'][k]["name"] = params[0] + " " + params[1]
                    self.infoPatients['doctors'][k]["chatID"] = chat_ID
                    with open(infoPatients, "w") as f:
                        json.dump(self.infoPatients, f)
                    self.bot.sendMessage(chat_ID, 'Now you are registered. Click here /data for check your data')
                else:
                    self.bot.sendMessage(chat_ID, 'Insert correct password')
        elif message.startswith('/Patient'):
            params = message.split()[1:]
            if len(params) == 0:
                self.bot.sendMessage(chat_ID, 'Insert also your name and surname')
            else:

                found = False
                name = params[0] + " " + params[1]
                for p in self.infoPatients['patients'].values():
                    if name == p["name"]:
                        p["chatID"] = chat_ID
                        found = True
                        with open(infoPatients, "w") as f:
                            json.dump(self.infoPatients, f)
                        self.bot.sendMessage(chat_ID, 'Now you are registered. Click here /data for check your data')
                if not found:
                    self.bot.sendMessage(chat_ID, 'You are not a patient')

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']
        if self.checkRegistration(chat_ID) or message == "/data":

            if self.checkDoctor(chat_ID):
                buttons = []
                for room_name in self.rooms:
                    buttons.append(
                        [InlineKeyboardButton(text=room_name['room_name'],
                                              callback_data='Patient' + ' ' + room_name['room_name'])])
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID, text='Which patient are you interested in?',
                                     reply_markup=keyboard)
            else:
                print(self.rooms)
                for room in self.rooms:
                    print(self.findPatient(chat_ID))
                    print(room['room_name'])
                    if self.findPatient(chat_ID) == room['room_name']:
                        chosen_patient = room['room_name']
                        buttons = []
                        buttons.append([InlineKeyboardButton(text='All sensor', callback_data='all')])
                        for sensor in room["room_sensors"]:
                            buttons.append([InlineKeyboardButton(text=sensor, callback_data=sensor)])
                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.bot.sendMessage(chat_ID, text='Which sensor are you interested for patient ' + room[
                            'room_name'] + '?', reply_markup=keyboard)
        else:
            if message == "/start":
                self.bot.sendMessage(chat_ID,
                                     text=" Welcome! If you are a doctor use the command '/Doctor + your name + your surname + hospital password'.\n If you are a patient use the command '/Patient + your name'.")
                '''keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Doctor', callback_data='doctor'),
                     InlineKeyboardButton(text='Patient', callback_data='patient')]])
                self.bot.sendMessage(chat_ID, text=" Welcome! Are you the doctor or the patient?", reply_markup=keyboard)'''

            elif message.startswith("/Doctor"):
                self.registration(chat_ID, message)
            elif message.startswith("/Patient"):
                self.registration(chat_ID, message)

            elif message == "/Check_All":
                self.bot.sendMessage(chat_ID, text='Start monitoring your patients')
                self.stop = False
                while not self.stop:

                    for room in self.rooms:
                        for dev in room["room_sensors"]:
                            string = requests.get("http://" + str(self.Manager_sensor_settings['ip']) + ':' + str(
                                self.Manager_sensor_settings['port']) +
                                                  "/?room_name=" + room[
                                                      'room_name'] + "&sensor_type=" + dev + "&check=value").text
                            # GET REQUEST TO THE SENSOR SUBSCRIBER IN ORDER TO RECEIVE SENSOR DATA
                            value = int(string.split()[1])
                            for l in self.limits:
                                if dev == l["sensor_type"]:
                                    if value < l["min"]:
                                        self.bot.sendMessage(chat_ID,
                                                             text="WARNING! " + dev + " is low for patient: " + room[
                                                                 "room_name"])
                                        self.bot.sendMessage(chat_ID, text=string)
                                    elif value > l["max"]:
                                        self.bot.sendMessage(chat_ID,
                                                             text="WARNING! " + dev + " is very high for patient: " +
                                                                  room["room_name"])
                                        self.bot.sendMessage(chat_ID, text=string)
                                    elif value > l["max_good"]:
                                        self.bot.sendMessage(chat_ID,
                                                             text="WARNING! " + dev + " is  high for patient: " + room[
                                                                 "room_name"])
                                        self.bot.sendMessage(chat_ID, text=string)

                    button = InlineKeyboardButton(text='Stop', callback_data='stop')
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
                    self.bot.sendMessage(chat_ID, text='Press to stop monitoring your patients', reply_markup=keyboard)
                    time.sleep(10)
                self.bot.sendMessage(chat_ID, text='Stop monitoring')

            else:
                self.bot.sendMessage(chat_ID, text="Command not supported")

    def on_callback_query(self, msg):
        query_ID, chat_ID, query_data = telepot.glance(msg, flavor='callback_query')
        message = query_data

        if message == 'temperature' or message == 'humidity' or message == 'body_temperature' or message == 'heart_rate':
            value = requests.get(
                "http://" + str(self.Manager_sensor_settings['ip']) + ':' + str(self.Manager_sensor_settings['port']) +
                "/?room_name=" + self.chosen_patient + "&sensor_type=" + message + "&check=value")
            # GET REQUEST TO THE SENSOR SUBSCRIBER IN ORDER TO RECEIVE SENSOR DATA

            self.bot.sendMessage(chat_ID, text=value.text)
            self.bot.sendMessage(chat_ID, text='Write new command if you want to ask other data')

        if message == 'all':
            value = requests.get(
                "http://" + str(self.Manager_sensor_settings['ip']) + ':' + str(self.Manager_sensor_settings['port']) +
                "/?room_name=" + self.chosen_patient + "&check=all")
            # GET REQUEST TO THE SENSOR SUBSCRIBER IN ORDER TO RECEIVE SENSOR DATA

            self.bot.sendMessage(chat_ID, text=value.text)
            self.bot.sendMessage(chat_ID, text='Write new command if you want to ask other data')


        if message.startswith('Patient'):
            params = message.split()[1:]
            found = 0
            for room in self.rooms:
                if params[0] + ' ' + params[1] == room['room_name']:
                    self.chosen_patient = room['room_name']
                    found = 1
                    buttons = []
                    buttons.append([InlineKeyboardButton(text='All sensor', callback_data='all')])
                    for sensor in room["room_sensors"]:
                        buttons.append([InlineKeyboardButton(text=sensor, callback_data=sensor)])
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                    self.bot.sendMessage(chat_ID, text='Which sensor are you interested in?', reply_markup=keyboard)

            if found == 0:
                self.bot.sendMessage(chat_ID, 'Insert correct name and surname')


if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    Manager_sensor_settings = json.load(open("Subscriber.json"))
    token = conf["telegramToken"]
    Home_catalog_settings = json.load(open("HomeCatalog_settings.json"))
    infoPatients = "infoPatients.json"
    bot = EchoBot1(token, Home_catalog_settings, Manager_sensor_settings, infoPatients)

    bot.run()
    bot.client.unsubscribe()
    result = bot.follow(Home_catalog_settings["base_topic"] + '/emergency/#')
    # bot.end

    print("Bot started ...")
    while True:
        time.sleep(3)
