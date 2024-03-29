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
        self.chosen_patient = ""

        self.infoPatients = json.load(open(infoPatients))

        self.bot = telepot.Bot(self.tokenBot)


        Home_get_string = "http://" + self.Home_catalog_settings["ip_address"] + ":" + str(
            self.Home_catalog_settings["ip_port"]) + "/resource_catalogs"
        rc_info = json.loads(requests.get(Home_get_string).text)

        self.rooms = []
        self.clientID = 'telegramsubscriber'
        self.client = MyMQTT(self.clientID, Manager_sensor_settings['broker'], Manager_sensor_settings['broker_port'],
                             self)

        request_string = "http://" + rc_info["ip_address"] + ":" + str(rc_info["ip_port"]) + "/all"
        patients = json.loads(requests.get(request_string).text)
        for patient in patients.values():
            sensors = []
            for dev in patient:
                if dev["ID_sensor"] == 'sensor_th_1':
                    for type in dev['sensortype']:
                        sensors.append(type)
                else:
                    sensors.append(dev['sensortype'])
            # Which sensors are in the room of patient X
            self.rooms.append({"room_name": dev["patient"], "room_sensors": sensors})
        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()

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

    def rightName(self, type):
        if type == "body_temperature":
            return "Body temperature"
        elif type == "heart_rate":
            return "Heart rate"
        elif type == "oxygen":
            return "Oxygen"
        elif type == "temperature":
            return "Temperature"
        elif type == "humidity":
            return "Humidity"
        else:
            return type

    def notify(self, topic, msg):
        print("ehi")
        payload = json.loads(msg)
        warning_dict = json.loads((payload))
        warning_dict = warning_dict["e"][0]

        chatID_doc = []
        chat_ID = -1
        for p in self.infoPatients['patients'].values():
            if p["name"] == warning_dict['patient']:
                chat_ID = p["chatID"]

        for p in self.infoPatients['doctors'].values():
            if p["chatID"] != -1:
                chatID_doc.append(p["chatID"])

        if warning_dict['warning'] == 'min':
            if chat_ID != -1:
                self.bot.sendMessage(chat_ID,
                                     'Your ' + self.rightName(str(warning_dict['type'])) + ' value is too low: ' + str(
                                         warning_dict['value']) + " " + str(warning_dict['unit']))
            for d in chatID_doc:
                self.bot.sendMessage(d, 'Patient: ' + str(warning_dict['patient']) + '. The ' + self.rightName(str(
                    warning_dict['type'])) + ' value is too low: ' + str(warning_dict['value']) + " " + str(
                    warning_dict['unit']))
        if warning_dict['warning'] == 'max':
            if chat_ID != -1:
                self.bot.sendMessage(chat_ID,
                                     'Your ' + self.rightName(str(warning_dict['type'])) + ' value is too high: ' + str(
                                         warning_dict['value']) + " " + str(warning_dict['unit']))
            for d in chatID_doc:
                self.bot.sendMessage(d, 'Patient: ' + str(warning_dict['patient']) + '. The ' + self.rightName(str(
                    warning_dict['type'])) + ' value is too high: ' + str(warning_dict['value']) + " " + str(
                    warning_dict['unit']))
        if warning_dict['warning'] == 'max_good':
            if chat_ID != -1:
                self.bot.sendMessage(chat_ID, 'Your ' + self.rightName(
                    str(warning_dict['type'])) + ' value is near the high limit: ' + str(
                    warning_dict['value']) + " " + str(warning_dict['unit']))
            for d in chatID_doc:
                self.bot.sendMessage(d, 'Patient: ' + str(warning_dict['patient']) + '. The ' + self.rightName(str(
                    warning_dict['type'])) + ' value is near the high limit: ' + str(warning_dict['value']) + " " + str(
                    warning_dict['unit']))

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
                return p
        return ""

    def findPatientByName(self, name):
        for p in self.infoPatients['patients'].values():
            if name == p["name"]:
                return p
        return ""

    def findDoctor(self, chat_ID):
        for p in self.infoPatients['doctors'].values():
            if chat_ID == p["chatID"]:
                return p
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
                    self.bot.sendMessage(chat_ID, 'Now you are registered! Click here /data for check data')
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
                        self.bot.sendMessage(chat_ID, 'Now you are registered! Click here /data for check your data')
                if not found:
                    self.bot.sendMessage(chat_ID, 'You are not a patient')

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']
        if self.checkRegistration(chat_ID) and message == '/start':
            if self.checkDoctor(chat_ID):
                doc = self.findDoctor(chat_ID)
                if isinstance(doc, dict):
                    self.bot.sendMessage(chat_ID,
                                         text='Welcome back Dott. ' + doc[
                                             'name'] + '! Click /data to get a view of the current situation or '
                                                       '/thingspeak to see analysis of the last period',
                                         )
            else:
                patient = self.findPatient(chat_ID)
                if isinstance(patient, dict):
                    self.bot.sendMessage(chat_ID,
                                         text='Welcome back ' + patient[
                                             'name'] + '! Click /data to get a view of the current situation or '
                                                       '/thingspeak to see analysis of the last period',
                                         )
        elif self.checkRegistration(chat_ID) and message == "/data":
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
                # print(self.rooms)
                for room in self.rooms:
                    patient = self.findPatient(chat_ID)
                    if isinstance(patient, dict) and patient["name"] == room['room_name']:
                        self.chosen_patient = room['room_name']
                        buttons = []
                        buttons.append([InlineKeyboardButton(text='All sensor', callback_data='all')])
                        for sensor in room["room_sensors"]:
                            buttons.append([InlineKeyboardButton(text=self.rightName(sensor), callback_data=sensor)])
                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.bot.sendMessage(chat_ID, text='Which sensor are you interested in?', reply_markup=keyboard)
        elif self.checkRegistration(chat_ID) and message == "/thingspeak":
            if self.checkDoctor(chat_ID):
                buttons = []
                for room_name in self.rooms:
                    buttons.append(
                        [InlineKeyboardButton(text=room_name['room_name'],
                                              callback_data='Thingspeak' + ' ' + room_name['room_name'])])
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(chat_ID,
                                     text="Which patient's analysis do you want to select from the last period?",
                                     reply_markup=keyboard)
            else:
                patient = self.findPatient(chat_ID)
                # print(patient)
                self.bot.sendMessage(chat_ID,
                                     text='You can check your analytics on https://thingspeak.com/channels/' + str(
                                         patient[
                                             "channel"]))
                self.bot.sendMessage(chat_ID,
                                     text='Click /data if you want to ask other data or /thingspeak if you want to receive the analytics of the last period')


        elif message == "/start":
            self.bot.sendMessage(chat_ID,
                                 text=" Welcome! If you are a doctor use the command '/Doctor + your name + your surname + hospital password'.\n If you are a patient use the command '/Patient + your name'.")

        elif message.startswith("/Doctor"):
            self.registration(chat_ID, message)
        elif message.startswith("/Patient"):
            self.registration(chat_ID, message)
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
            self.bot.sendMessage(chat_ID,
                                 text='Click /data if you want to ask other data or /thingspeak if you want to receive the analytics of the last period')

        if message == 'all':
            value = requests.get(
                "http://" + str(self.Manager_sensor_settings['ip']) + ':' + str(self.Manager_sensor_settings['port']) +
                "/?room_name=" + self.chosen_patient + "&check=all")
            # GET REQUEST TO THE SENSOR SUBSCRIBER IN ORDER TO RECEIVE SENSOR DATA

            self.bot.sendMessage(chat_ID, text=value.text)
            self.bot.sendMessage(chat_ID,
                                 text='Click /data if you want to ask other data or /thingspeak if you want to receive the analytics of the last period')

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
                    self.bot.sendMessage(chat_ID,
                                         text='Which sensor are you interested in for patient ' + self.chosen_patient + "?",
                                         reply_markup=keyboard)

            if found == 0:
                self.bot.sendMessage(chat_ID, 'Insert correct name and surname')

        if message.startswith('Thingspeak'):
            params = message.split()[1:]
            for room in self.rooms:
                if params[0] + ' ' + params[1] == room['room_name']:
                    patient = self.findPatientByName(room['room_name'])
                    if isinstance(patient, dict):
                        self.bot.sendMessage(chat_ID,
                                             text='You can check the analytics of ' + patient[
                                                 "name"] + ' on https://thingspeak.com/channels/' + str(
                                                 patient[
                                                     "channel"]))
                        self.bot.sendMessage(chat_ID,
                                             text='Click /data if you want to ask other data or /thingspeak if you want to receive the analytics of the last period')


if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    Manager_sensor_settings = json.load(open("Subscriber.json"))
    token = conf["telegramToken"]
    Home_catalog_settings = json.load(open("HomeCatalog_settings.json"))
    infoPatients = "infoPatients.json"
    bot = EchoBot1(token, Home_catalog_settings, Manager_sensor_settings, infoPatients)

    bot.run()
    bot.client.unsubscribe()
    topic = Home_catalog_settings["base_topic"].split("/")
    print(topic[0] + '/emergency/#')
    bot.follow(topic[0] + '/emergency/#')
    # bot.end

    print("Bot started ...")
    while True:
        time.sleep(3)
