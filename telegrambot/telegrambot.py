import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
import sys

        
class EchoBot1:
    def __init__(self, token, service_catalog_info):
        
        self.tokenBot = token
        self.service_catalog_info = json.load(open(service_catalog_info))

        self.bot = telepot.Bot(self.tokenBot)
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                               'callback_query': self.on_callback_query}).run_as_thread()
        poststring="http://"+self.service_catalog_info["ip_address"]
        
        service_get_string="http://"+self.service_catalog_info["ip_address"]+":"+str(self.service_catalog_info["ip_port"])+"/resource_catalogs"
        rooms_all=json.loads(requests.get(service_get_string).text)
        print(rooms_all)
        self.rooms=[]

        for entry in rooms_all:
            request_string="http://"+entry["ip_address"]+":"+str(entry["ip_port"])+"/all"
            print(entry['ip_port'])
            devices=json.loads(requests.get(request_string).text)
            sensors=[]
            for dev in devices:
                for type in dev["sensor_type"]:
                    sensors.append(type)
            self.rooms.append({"room_name":entry["patient"],
                "room_sensors":sensors
                })
           
        self.chosen_room=0
        self.requested_room=''
        self.r=''
        
    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        # print(content_type, chat_type, chat_ID)
        message = msg['text']
        
        if message == "/start":
            self.bot.sendMessage(chat_ID, text=" Benvenuto! Per leggere la temperatura chiedi /temperature, per leggere l'umidità chiedi /humidity")
        
        
        if message == "/temperature":
            self.chosen_room=0
            buttons=[]
            print(self.rooms)
            for room_name in self.rooms:
                print(room_name['room_name'])
                buttons.append ([InlineKeyboardButton(text=room_name['room_name'],callback_data=room_name['room_name'])])
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='Which owner are you interested in?', reply_markup=keyboard)   
            
        else:
                self.bot.sendMessage(chat_ID, text="Command not supported")

    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        message = query_data
        print(msg)
        
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
    token = conf["telegramToken"]
    service_catalog_info=("HomeCatalog_settings.json")
    bot=EchoBot1(token,service_catalog_info)

    print("Bot started ...")
    while True:
        time.sleep(3)
