import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
import sys

        
class EchoBot1:
    def __init__(self, token, Home_catalog_settings, Manager_sensor_settings):
        
        self.tokenBot = token
        self.Home_catalog_settings = json.load(open(Home_catalog_settings))
        self.Manager_sensor_settings = json.load(open(Manager_sensor_settings))
        self.bot = telepot.Bot(self.tokenBot)
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                               'callback_query': self.on_callback_query}).run_as_thread()

        Home_get_string = "http://"+self.Home_catalog_settings["ip_address"]+":"+str(self.Home_catalog_settings["ip_port"])+"/resource_catalogs"
        rooms_all = json.loads(requests.get(Home_get_string).text)
        self.rooms = []

        for entry in rooms_all:
            request_string="http://"+entry["ip_address"]+":"+str(entry["ip_port"])+"/all"
            devices=json.loads(requests.get(request_string).text)
            sensors=[]
            for dev in devices:
                if dev["ID_sensor"] == 'sensor_th_1':
                    for type in dev['sensortype']:
                        sensors.append(type)
                else:
                    sensors.append(dev['sensortype'])
            self.rooms.append({"room_name":entry["patient"],
                "room_sensors":sensors
                })
        
    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']
        
        if message == "/start":
            self.bot.sendMessage(chat_ID, text=" Welcome! If you are a doctor use the command '/doctor + hospital_password'. If you are a patient use the command '/patient + your name'?")
            '''keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Doctor', callback_data='doctor'),
                 InlineKeyboardButton(text='Patient', callback_data='patient')]])
            self.bot.sendMessage(chat_ID, text=" Welcome! Are you the doctor or the patient?", reply_markup=keyboard)'''

        elif message.startswith('/doctor'):
            params = message.split()[1:]
            if len(params) == 0:
                self.bot.sendMessage(chat_ID, 'Insert also your password')
            else:
                if params[0] == 'albero':
                    buttons = []
                    for room_name in self.rooms:
                        print(room_name['room_name'])
                        buttons.append(
                            [InlineKeyboardButton(text=room_name['room_name'], callback_data=room_name['room_name'])])
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                    self.bot.sendMessage(chat_ID, text='Which patient are you interested in?', reply_markup=keyboard)
                else:
                    self.bot.sendMessage(chat_ID, 'Insert correct password')

        elif message.startswith('/patient'):
            params = message.split()[1:]
            if len(params) == 0:
                self.bot.sendMessage(chat_ID, 'Insert also your name and surname')
            else:
                found = 0
                for room in self.rooms:
                    if params[0] + ' ' + params[1] == room['room_name']:
                        self.chosen_patient = room['room_name']
                        found = 1
                        buttons = []
                        buttons.append([InlineKeyboardButton(text='All sensor', callback_data= 'all')])
                        for sensor in room["room_sensors"]:
                            buttons.append([InlineKeyboardButton(text= sensor, callback_data= sensor)])
                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.bot.sendMessage(chat_ID, text='Which sensor are you interested in?', reply_markup=keyboard)

                if found == 0:
                    self.bot.sendMessage(chat_ID, 'Insert correct name and surname')
        else:
            self.bot.sendMessage(chat_ID, text="Command not supported")


    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        message = query_data

        if message == 'temperature' or message == 'humidity' or message == 'body_temperature' or message == 'heart_rate':
            value = requests.get("http://"+str(self.Manager_sensor_settings['ip']) + ':' + str(self.Manager_sensor_settings['port']) +
                               "/?room_name="+self.chosen_patient+"&sensor_type="+message+"&check=value")
                 #GET REQUEST TO THE SENSOR SUBSCRIBER IN ORDER TO RECEIVE SENSOR DATA

            self.bot.sendMessage(chat_ID, text=value.text)
            self.bot.sendMessage(chat_ID, text='Write new command if you want to ask other data')

        if message == 'all':
            value = requests.get("http://"+str(self.Manager_sensor_settings['ip']) + ':' + str(self.Manager_sensor_settings['port']) +
                               "/?room_name="+self.chosen_patient+"&check=all")
                 #GET REQUEST TO THE SENSOR SUBSCRIBER IN ORDER TO RECEIVE SENSOR DATA

            self.bot.sendMessage(chat_ID, text=value.text)
            self.bot.sendMessage(chat_ID, text='Write new command if you want to ask other data')
        # if self.chosen_owner==0:
        #     self.chosen_owner=1    
        #     self.requested_owner=message
        #     buttons=[]
        #     for own in self.rooms:
        #         if own['owner']==self.requested_owner:
        #             for room in own['rooms']:
        #                 buttons.append ([InlineKeyboardButton(text=room["room_name"],callback_data=room["room_name"])])
        #     keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        #     print("Chosen owner: ", self.requested_owner, "\n") #PRINT FOR DEMO
        #     self.bot.sendMessage(chat_ID, text='Which room are you interested in?', reply_markup=keyboard) 

        # elif self.chosen_owner==1 and self.chosen_room==0:
        #     self.chosen_room=1
        #     self.requested_room=message
        #     print("Chosen room: ", self.requested_room, "\n") #PRINT FOR DEMO
        #     for own in self.rooms:
        #         if own['owner']==self.requested_owner:
        #             for room in own['rooms']:
                        
        #                 if room['room_name']==self.requested_room:
        #                     self.r=room
        #     buttons=[] 
        #     print(self.rooms) 
        #     for own in self.rooms:
        #         if own['owner']==self.requested_owner:
        #             for room in own['rooms']:
        #                 if room["room_name"]==message or self.requested_room==room["room_name"]:
        #                     for dev in room["room_sensors"]:
        #                         buttons.append ([InlineKeyboardButton(text=dev,callback_data=dev)])
                                
        #     keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        #     if len(buttons)>0:
        #         self.bot.sendMessage(chat_ID, text='Choose a sensor', reply_markup=keyboard)
        #     else:
        #         self.bot.sendMessage(chat_ID, text='No sensor available, write /operation to ask for data')

        # elif self.chosen_owner==1 and self.chosen_room==1:
        #     for dev in self.r["room_sensors"]:
        #         if message == dev:
                    
        #             value=requests.get("http://"+sys.argv[1]+"/?owner="+self.requested_owner+"&room_name="+self.requested_room+"&sensor_type="+message+"&check=all") 
        #             #GET REQUEST TO THE SENSOR SUBSCRIBER IN ORDER TO RECEIVE SENSOR DATA
                    
        #             self.chosen_room=0
        #             print(value.text, "\n", "\n")
        #             self.bot.sendMessage(chat_ID, text=value.text)
        #             self.bot.sendMessage(chat_ID, text='Write /operation to ask for data')

if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    conf_sensor = "Subscriber.json"
    token = conf["telegramToken"]
    Home_catalog_settings = "HomeCatalog_settings.json"
    bot = EchoBot1(token, Home_catalog_settings, conf_sensor)

    print("Bot started ...")
    while True:
        time.sleep(3)
