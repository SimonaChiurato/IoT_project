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
        self.channel = think["channel"]
        self.write_key = think["key"]
        # self.ID = self.chosen_patient+"_TS-Adaptor"
        self.type = "TS-Adaptor"
        self.broker_address = think["broker"]
        self.field1_data = None  # Temperature
        self.field2_data = None  # humidity
        self.field3_data = None  # BodyTemperature
        self.field4_data = None  # HeartRate
        self.field5_data = None  # Oxygen


    def start(self, topic):
        self.topic = topic
        self.client.start()
        self.client.mySubscribe(self.topic)

    def stop(self):
        self.client.stop()

    def notify(self, topic, msg):
        d1 = json.loads(msg.decode('utf8'))
        d = json.loads(d1)
        if d["e"][0]["type"] == "temperature":
            self.field1_data = d["e"][0]["value"]
        elif d["e"][0]["type"] == "humidity":
            self.field2_data = d["e"][0]["value"]
        elif d["e"][0]["type"] == "body_temperature":
            self.field3_data = d["e"][0]["value"]
        elif d["e"][0]["type"] == "heart_rate":
            self.field4_data = d["e"][0]["value"]
        elif d["e"][0]["type"] == "oxygen":
            self.field5_data = d["e"][0]["value"]


def rooms_sensors(Home_catalog_settings,
                  chosen_patient):  # METHOD FOR RETRIVING INFORMATION ABOUT OWNERS AND RESOURCE CATALOGS (rooms)
    # sostituire ad ogni service_catalog_info HomeCatalog_settings
    # ip_address_service sostituire con ip_address.

    # CONTROLLARE MANAGER HOME è il loro service_catalog!
    Home_get_string = "http://" + Home_catalog_settings["ip_address"] + ":" + str(
        Home_catalog_settings["ip_port"]) + "/resource_catalogs"
    rc_info = json.loads(requests.get(Home_get_string).text)
    rooms = []
    request_string = "http://" + rc_info["ip_address"] + ":" + str(rc_info["ip_port"]) + "/all"
    patients = json.loads(requests.get(request_string).text)
    for patient in patients.values():
        sensors = []
        for dev in patient:
            for type in dev['sensortype']:
                sensors.append(type)

        rooms.append({"room_name": dev["patient"],
                      "room_sensors": sensors,
                      "room_topic": dev["communication"]["basetopic"]
                      })
    print(chosen_patient)
    for patient in rooms:
        if patient["room_name"] == chosen_patient:
            return patient["room_topic"]
            flag = True


if __name__ == "__main__":

    think = json.load(open(sys.argv[1]))  # config
    headers = {'Content-type': 'application/json', 'Accept': 'raw'}
    # cambiare nome
    Home_catalog_info = json.load(open("HomeCatalog_settings.json"))
    patient = rooms_sensors(Home_catalog_info, think["name"])

    topic_to_subscribe = patient + "/#"  # SUBSCRIBING TO TOPIC AFTER OBTAINING THE NEEDED INFORMATION FROM rooms_sensors METHOD
    # qui anche avro solo patient. al post di study_room_ trovare topic in home catalog setting.
    tp = ThinkSpeak("Molinette", think["broker"], 1883, think)

    tp.start(topic_to_subscribe)
    count = 0
    t = 0
    while t < 80:
        data_upload = json.dumps({
            "api_key": tp.write_key,
            "channel_id": tp.channel,
            "created_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_id": count,
            "field1": tp.field1_data,
            "field2": tp.field2_data,
            "field3": tp.field3_data,
            "field4": tp.field4_data,
            "field5": tp.field5_data

        })

        requests.post(url=think["url"], data=data_upload, headers=headers)
        print("\nINFORMATION SENT TO THINGSPEAK!\n")
        print("Temperature", tp.field1_data)
        print("Humidity", tp.field2_data)
        print("Body_Temperature", tp.field3_data)
        print("Heart_Rate", tp.field4_data)
        print("Oxygen", tp.field5_data)

        time.sleep(20)
        count += 1
        t += 1

tp.stop()
