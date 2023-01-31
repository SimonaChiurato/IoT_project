import urllib
from MyMQTT import *
import time
import json
import datetime
import requests
import sys


class ThinkSpeak:
    def __init__(self, clientID, broker, port, think):
        self.client = MyMQTT(clientID, broker, port, self)
        self.status = None
        self.Studyroom = think["name"]
        self.channel = think["channel"]
        self.write_key = think["key"]
        self.ID = self.Studyroom+"_TS-Adaptor"
        self.type = "TS-Adaptor"
        self.broker_address = think["broker"]
        self.field1_data = None #Temperature 
        self.field2_data = None #humidity
        self.field3_data = None #CO2 
#qui cambio commento

    def start(self, topic):
        self.topic=topic
        self.client.start()
        self.client.mySubscribe(self.topic)

    def stop(self):
        self.client.stop()

    def notify(self, topic, msg):
        d1 = json.loads(msg.decode('utf8'))
        d=json.loads(d1)
        print(d)     #temp ed umidita si

        if d["e"][0]["type"]=="temperature":
            self.field1_data= d["e"][0]["value"]
        elif d["e"][0]["type"]=="humidity":
            self.field2_data= d["e"][0]["value"]
        elif d["e"][0]["type"]=="CO2":
            self.field3_data= d["e"][0]["value"]
        

def rooms_sensors(HomeCatalog_settings): #METHOD FOR RETRIVING INFORMATION ABOUT OWNERS AND RESOURCE CATALOGS (rooms)
        #sostituire ad ogni service_catalog_info HomeCatalog_settings
        HomeCatalog_settings=HomeCatalog_settings
        #ip_address_service sostituire con ip_address.

        #CONTROLLARE MANAGER HOME è il loro service_catalog!
        service_get_string="http://"+service_catalog_info["ip_address_service"]+":"+service_catalog_info["ip_port_service"]+"/res_cat"
        print("INFORMATION FROM SERVICE CATALOG RECEIVED!\n")
        #mconvers cambiava service_get_string in service_get
        rooms_all=json.loads(requests.get(service_get_string).text)
        rooms=[]

        for entry in rooms_all:  #richiesta fatta nel resource_catalog
            request_string="http://"+entry["ip_address"]+":"+entry["ip_port"]+"/alldevices"
            print("INFORMATION OF RESOURCE CATALOG (room) RECEIVED!\n")
            devices=json.loads(requests.get(request_string).text)
            sensors=[]

            room={"room_name":entry["base_topic"],
                "room_sensors":sensors
                }
            found=0
            for own in rooms:  #VEDERE CATERINA
                if own['owner']==entry['owner']:
                    own['rooms'].append(room)
                    found=1
            if found==0:
                #qui copiare il self.rooms.append
                rooms.append({'owner':entry['owner'],
                      'rooms':[room]
                    })
               
        print(f"Available owners and rooms: {rooms}\n")
        chosen_owner=input('Owner: ')
        chosen_room=input('\nRoom: ')
        #chosen_patient=input('Patient: ')
        for owner in rooms:
                if owner["owner"]==chosen_owner:
                    for room in owner["rooms"]:
                        if room["room_name"]==chosen_room:
                            return owner["owner"], room["room_name"]
                            #NOI DOBBIAMO FARE RETURN PATIENT

                    

if __name__ == "__main__":

    think=json.load(open(sys.argv[1])) #QUI VEDERE NEL VIDEO CHE CAZZO FANNO
    headers = {'Content-type': 'application/json', 'Accept': 'raw'}
    #cambiare nome
    service_catalog_info=json.load(open("service_catalog_info.json"))
    owner, room=rooms_sensors(service_catalog_info)
            
    topic_to_subscribe="study_room_politecnico/"+owner+'/'+room+"/#"   #SUBSCRIBING TO TOPIC AFTER OBTAINING THE NEEDED INFORMATION FROM rooms_sensors METHOD
    #qui anche avro solo patient. al post di study_room_ trovare topic in home catalog setting.
    tp = ThinkSpeak("SmartStudyRoom22714",think["broker"],1883, think)

    tp.start(topic_to_subscribe)
    count = 0
    t=0
    while t<80: 
        data_upload = json.dumps({
        "api_key": tp.write_key,
        "channel_id": tp.channel, 
        "created_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_id": count,
        "field1": tp.field1_data,
        "field2": tp.field2_data,
        "field3": tp.field3_data
    })
          
        requests.post(url=think["url"], data=data_upload, headers=headers)
        print("\nINFORMATION SENT TO THINGSPEAK!\n")
        time.sleep(30)
        count += 1
        t+=1

tp.stop()