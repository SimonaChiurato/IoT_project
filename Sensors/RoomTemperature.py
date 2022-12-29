from MyMQTT import *
import time
import json
import random
import requests
import Adafruit_DHT
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
                    'owner': '',
                    'room': ''
                }
            ]
        }

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()

    def publish(self, value, owner, room):
        message = self.__message
        message['e'][0]['value'] = value
        message['e'][0]['timestamp'] = str(time.time())
        message['e'][0]['owner'] = owner
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
    if r_dict == None:  #controllare cosa restituisce da manager home info_room
        return 'NOT FOUND', 'NOT FOUND', 'NOT FOUND', 'NOT FOUND', 'NOT FOUND', 'NOT FOUND', 'NOT FOUND', 'NOT FOUND', 'NOT FOUND'  #modificare
    else:
        rc = r_dict['result'] #controllare perchè fa sta cosa
        rc_ip = rc["ip_address"]
        rc_port = rc["ip_port"]
        poststring = 'http://' + rc_ip + ':' + rc_port + '/sensor'
        rc_basetopic = rc["base_topic"]
        rc_broker = rc["broker"]
        rc_port = rc["broker_port"]
        rc_patient = rc["patient"]

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
            topic.append(service_b_t + '/' + rc_owner + '/' + rc_basetopic + "/" + i + "/" + conf_sensor["ID_sensor"])
            body_dic = {
                "ID_sensor": conf_sensor['ID_sensor'],
                "sensor_type": conf_sensor['sensor_type'],
                "patient": rc["patient"],
                "measure": conf_sensor["measure"][index],
                "end-points": {
                    "basetopic": service_b_t + '/' + rc_owner + '/' + rc_basetopic,
                    "complete_topic": topic,
                    "broker": rc["broker"],
                    "port": rc["broker_port"]
                }
            }
            body.append(body_dic)
            requests.post(poststring, json.dumps(body[index]))
            print("REGISTRATION TO RESOURCE CATALOG (room) DONE!\n")  # PRINT FOR DEMO

            index = index + 1

        return rc_basetopic, conf_sensor["sensor_type"], conf_sensor["ID_sensor"], topic, conf_sensor[
            "measure"], rc_broker, rc_port, sensor_model, rc["owner"]


if __name__ == "__main__":
    # creare variabili globali e modificare direttamente quelle in registrazion, evitare i NOT FOUND e usare solo flag 1 0 per dire
    #trovato o non trovato
    clientID, sensortype, sensorID, topic, measure, broker, port, sensor_model, owner = registration(sys.argv[1],
                                                                                                     "HomeCatalog_settings.json")
    while clientID == 'NOT FOUND' and sensortype == 'NOT FOUND' and sensorID == 'NOT FOUND' and topic == 'NOT FOUND' and measure == 'NOT FOUND' and broker == 'NOT FOUND' and port == 'NOT FOUND' and sensor_model == 'NOT FOUND' and owner == 'NOT FOUND':
        clientID, sensortype, sensorID, topic, measure, broker, port, sensor_model, owner = registration(sys.argv[1],
                                                                                                         "HomeCatalog_settings.json")
    index = 0
    Sensor = []
    for i in sensortype:
        Sensor.append(SensorControl(clientID, i, sensorID, measure[index], broker, port, topic[index]))
        Sensor[index].start()
        index = index + 1

    config = json.load(open(sys.argv[1]))
    while 1:

        pin = config["pin"]
        humidity, temperature = Adafruit_DHT.read_retry(11, pin)

        if humidity is not None and temperature is not None:
            print('\nTemp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
            Sensor[0].publish('{0:0.1f}'.format(temperature), owner, room)
            Sensor[1].publish('{0:0.1f}'.format(humidity), owner, room)
            time.sleep(3)
        else:
            print('Failed to get reading. Try again!')
