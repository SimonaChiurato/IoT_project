from MyMQTT import *
import json
import random
import requests
import sys
import time


class SensorComunication:

    def __init__(self, broker, clientID, port, sensorID, sensormeasure, sensortype, topic):
        self.clientID = clientID
        self.sensortype = sensortype
        self.sensorID = sensorID
        self.sensormeasure = sensormeasure
        self.topic = topic
        self.client = MyMQTT(self.sensorID, broker, port, None)

        self.__message = {
            'topic': self.topic,
            'message': [
                {
                    'type': self.sensortype,
                    'unit': self.sensormeasure,
                    'patient': '',
                    'value': ' ',
                    'time': ''
                }
            ]
        }

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()

    def publish(self, value, room):
        message = self.__message
        message['message'][0]['patient'] = room
        message['message'][0]['value'] = value
        message['message'][0]['time'] = str(time.time())
        self.client.myPublish(self.topic, json.dumps(message))
        print("Published!\n" + json.dumps(message) + "\n")


def SensorRegistry(sensor_settings, home_settings):  # IN ORDER TO REGISTER ON THE RESOURCE CATALOG
    with open(sensor_settings, "r") as file1:
        conf_sensor = json.loads(file1.read())

    with open(home_settings, "r") as file2:
        conf_home = json.loads(file2.read())
    request = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home[
        'ip_port']) + '/patients'    #ci siamo collegati al topic che ci restituisce la lista di nomi dei pazienti
    ListOfPatients = requests.get(request)
    print("LIST OF PATIENTS RECEIVED FROM SERVICE CATALOG RECEIVED!\n") #modifica
    names = ListOfPatients.json()
    print("List of patients:\n ")
    for i in range(len(names['names'])):
        print("Patient "+str(i+1)+" : "+names['names'][i]+"\n")
    index_patient = input("Which patient do you want to control? Insert the number please ")
    patient = names['names'][int(index_patient)-1]
    request = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home[
        'ip_port']) + '/info_room?patient=' + patient
    ResourceCatalog = requests.get(request)
    rc = json.loads(ResourceCatalog.text)
    print("RESOURCE CATALOG OF PATIENT " + rc['patient'] + "RECEIVED!\n")  # PRINT FOR DEMO #modifica string

    if rc == 0:
        print('Patient not found')
        return 'Patient not found'
    else:
        post = 'http://' + str(rc["ip_address"]) + ':' + str(rc["ip_port"]) + '/sensor'
        sensor_model = conf_sensor["sensor_model"]
        request = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home[
            'ip_port']) + '/base_topic'
        ServiceTopic = requests.get(request)
        ServiceTopic = json.loads(ServiceTopic.text)
        CompleteTopic = []
        BodyMessage = []
        model = 0
        for i in conf_sensor["sensor_type"]:
            print(i)
            CompleteTopic.append(ServiceTopic + '/' +rc["base_topic"] + '/' + i + '/' + conf_sensor["ID_sensor"])
            body_dic = {
                "ID_sensor": conf_sensor['ID_sensor'],
                "sensor_type": conf_sensor['sensor_type'],
                "patient": rc["patient"],
                "measure": conf_sensor["measure"][model],
                "comunication": {
                    "basetopic": ServiceTopic + '/' + rc["base_topic"],
                    "complete_topic": CompleteTopic,
                    "broker": rc["broker"],
                    "port": rc["broker_port"]
                }
            }
            BodyMessage.append(body_dic)
            requests.post(post, json.dumps(BodyMessage[model]))
            print("REGISTRATION TO RESOURCE CATALOG (room) DONE!\n")  # PRINT FOR DEMO

            model = model + 1

        Result_Dict = {
            "clientID": rc["base_topic"],
            "sensortype": conf_sensor["sensor_type"],
            "sensorID": conf_sensor["ID_sensor"],
            "topic": CompleteTopic,
            "measure": conf_sensor["measure"],
            "broker": rc["broker"],
            "port": int(rc["broker_port"]),
            "sensor_model": sensor_model,
            "owner": rc["patient"]
        }

        return Result_Dict


if __name__ == "__main__":

    dict = SensorRegistry(sys.argv[1], "HomeCatalog_settings.json")
    while dict == 'Patient not found':
        dict = SensorRegistry(sys.argv[1], "HomeCatalog_settings.json")

    model = 0
    Sensor = []
    for i in dict['sensortype']:
        Sensor.append(SensorComunication(dict['broker'], dict['clientID'], int(dict['port']), dict['sensorID'], dict['measure'][model], i, dict['topic'][model]))
        Sensor[model].start()
        model = model + 1

    sensor_settings=json.load(open(sys.argv[1]))

    while 1:
        Temperature = 20
        Humidity = 50
        Temperature = Temperature + random.randint(-5,10) #SIMULATED SENSOR
        print(Temperature)
        Sensor[0].publish(Temperature, dict['owner'])
        Humidity = Humidity + random.randint(-20,20) #SIMULATED SENSOR
        print(Humidity)
        Sensor[1].publish(Humidity, dict['owner'])
        time.sleep(5)


        #prova codice di controllo sensori
        if Temperature < 20:
            poststring = 'http://' + sensor_settings["server_ip"] + ':' + str(sensor_settings["server_port"])
            requests.post(poststring, json.dumps(Temperature))  # POSTING INFORMATION TO TEMPERATURE CONTROL SERVER
            time.sleep(2)