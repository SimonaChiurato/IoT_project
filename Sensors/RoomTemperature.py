from MyMQTT import *
import time
import json
import random
import requests
import sys


class SensorControl:

    def __init__(self, clientID, sensortype, sensorID, measure, broker, port, topic):
        self.clientID = clientID
        self.sensortype = sensortype
        self.sensorID = sensorID
        self.measure = measure
        self.topic = topic
        self.client = MyMQTT(self.sensorID, broker, port, None)

        self.__message = {
            'bn': self.topic,
            'e': [
                {
                    'type': self.sensortype,
                    'unit': self.measure,
                    'timestamp': '',
                    'value': ' ',
                    'room': ''
                }
            ]
        }

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()

    def publish(self, value, room):
        message = self.__message
        message['e'][0]['value'] = value
        message['e'][0]['timestamp'] = str(time.time())
        message['e'][0]['room'] = room
        self.client.myPublish(self.topic, json.dumps(message))
        print("Published!\n" + json.dumps(message) + "\n")


def registration(sensor_settings, home_settings):  # IN ORDER TO REGISTER ON THE RESOURCE CATALOG
    with open(sensor_settings, "r") as f1:
        conf_sensor = json.loads(f1.read())

    with open(home_settings, "r") as f2:
        conf_home = json.loads(f2.read())
    requeststring = 'http://' + conf_home['ip_address'] + ':' + conf_home[
        'ip_port'] + '/patients'    #ci siamo collegati al topic che ci restituisce la lista di nomi dei pazienti
    r = requests.get(requeststring)
    print("INFORMATION FROM SERVICE CATALOG RECEIVED!\n") #modifica
    print("List of patients:\n " + r.text + "\n")
    patient = input("Which patient do you want to control? ")

    requeststring = 'http://' + conf_home['ip_address'] + ':' + conf_home[
        'ip_port'] + '/info_room?patient=' + patient
    r = requests.get(requeststring)
    print("INFORMATION OF RESOURCE CATALOG (room) RECEIVED!\n")  # PRINT FOR DEMO #modifica string

    r_dict = json.loads(r.text)
    rc = r_dict['result']  # controllare perchè fa sta cosa
    if rc == 0:  #controllare cosa restituisce da manager home info_room
        return 'Patient not found'
    else:

        rc_ip = rc["ip_address"]
        rc_port = rc["ip_port"]
        poststring = 'http://' + rc_ip + ':' + rc_port + '/sensor'
        rc_basetopic = rc["base_topic"]
        rc_broker = rc["broker"]
        rc_port = rc["broker_port"]

        sensor_model = conf_sensor["sensor_model"]

        requeststring = 'http://' + conf_home['ip_address'] + ':' + conf_home[
            'ip_port'] + '/base_topic'
        sbt = requests.get(requeststring)

        service_b_t = json.loads(sbt.text)
        topic = []
        body = []
        index = 0
        for i in conf_sensor["sensor_type"]:
            print(i)
            topic.append(service_b_t + '/' + rc_basetopic + '/' + i + '/' + conf_sensor["ID_sensor"])
            body_dic = {
                "ID_sensor": conf_sensor['ID_sensor'],
                "sensor_type": conf_sensor['sensor_type'],
                "patient": rc["patient"],
                "measure": conf_sensor["measure"][index],
                "end-points": {
                    "basetopic": service_b_t + '/' + rc_basetopic,
                    "complete_topic": topic,
                    "broker": rc["broker"],
                    "port": rc["broker_port"]
                }
            }
            body.append(body_dic)
            requests.post(poststring, json.dumps(body[index]))
            print("REGISTRATION TO RESOURCE CATALOG (room) DONE!\n")  # PRINT FOR DEMO

            index = index + 1

        Result_Dict = {
            "clientID": rc_basetopic,
            "sensortype": conf_sensor["sensor_type"],
            "sensorID": conf_sensor["ID_sensor"],
            "topic": topic,
            "measure": conf_sensor["measure"],
            "broker": rc_broker,
            "port": rc_port,
            "sensor_model": sensor_model,
            "owner": rc["patient"]
        }

        return Result_Dict


if __name__ == "__main__":
    # creare variabili globali e modificare direttamente quelle in registrazion, evitare i NOT FOUND e usare solo flag 1 0 per dire
    #trovato o non trovato
    dict = registration(sys.argv[1], "HomeCatalog_settings.json")
    while dict == 'Patient not found':
        dict = registration(sys.argv[1], "HomeCatalog_settings.json")

    index = 0
    Sensor = []
    for i in dict['sensortype']:
        Sensor.append(SensorControl(dict['clientID'], i, dict['sensorID'], dict['measure'][index], dict['broker'], dict['port'], dict['topic'][index]))
        Sensor[index].start()
        index = index + 1

    Temperature = 20
    Humidity = 50
    while 1:
        Temperature = Temperature + random.randint(-5,10) #SIMULATED SENSOR
        print(Temperature)
        Sensor[0].publish(Temperature, dict['owner'])
        Humidity = Humidity + random.randint(-20,20) #SIMULATED SENSOR
        print(Humidity)
        Sensor[1].publish(Humidity, dict['owner'])
        time.sleep(15)