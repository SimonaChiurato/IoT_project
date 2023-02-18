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

        self.__message = {  #topic --> bn   message--> e !!!!!!
            'bn': self.topic,
            'e': [
                {
                    'type': self.sensortype,
                    'unit': self.sensormeasure,
                    'patient': '',
                    'value': '',
                    'time': ''
                }
            ]
        }

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()

    def publish(self, value, patient):
        message = self.__message
        message['e'][0]['patient'] = patient
        message['e'][0]['value'] = value
        message['e'][0]['time'] = str(time.time())
        self.client.myPublish(self.topic, json.dumps(message))
        print("Published!\n" + json.dumps(message) + "\n")


def RegisterSensor(sensor_settings, home_settings):  #how to register the sensor on the resource catalog
    with open(sensor_settings, "r") as file1:
        conf_sensor = json.loads(file1.read())

    with open(home_settings, "r") as file2:
        conf_home = json.loads(file2.read())
    request = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home[
        'ip_port']) + '/patients'    #ci siamo collegati al topic che ci restituisce la lista di nomi dei pazienti
    ListOfPatients = requests.get(request)
    print("Connection with home catalog: OK\n") #modifica
    names = ListOfPatients.json()
    check_name = False
    while check_name == False:
        print("List of patients:\n ")
        for i in range(len(names['names'])):
            print("Patient "+str(i+1)+" : "+names['names'][i]+"\n")
        index_patient = input("Which patient do you want to check? Insert the number please ")
        if isinstance(index_patient, str) and index_patient.isnumeric():
            int_index = int(index_patient)
            if (int_index-1) in range(len(names['names'])):
                patient = names['names'][int(index_patient) - 1]
                check_name = True
            else:
                print("Sorry, you have give the wrong input, try again!")
        else:
            print("Sorry, you have give the wrong input, you have to write only the number corresponding to the patient!")

    request = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home['ip_port']) + '/info_room?patient=' + patient
    ResourceCatalog = requests.get(request)
    rc = json.loads(ResourceCatalog.text)
    print("Information on patient " + rc['patient'] + " received (from resource catalog)\n")  # PRINT FOR DEMO #modifica string

    if rc == 0:
        print('No record for this patient')
        return 'Patient not found'
    else:
        post = 'http://' + str(rc["ip_address"]) + ':' + str(rc["ip_port"]) + '/sensor'
        request = 'http://' + str(conf_home['ip_address']) + ':' + str(conf_home['ip_port']) + '/base_topic'
        ServiceTopic = requests.get(request)
        ServiceTopic = json.loads(ServiceTopic.text)


        CompleteTopic = ServiceTopic + '/' +rc["base_topic"] + '/' + conf_sensor["sensor_type"][0] + '/' + conf_sensor["ID_sensor"]
        body_dic = {
            "sensortype": conf_sensor['sensor_type'][0],
            "ID_sensor": conf_sensor['ID_sensor'],
            "patient": rc["patient"],
            "measure": conf_sensor["measure"],
            "communication": {
                "basetopic": ServiceTopic + '/' + rc["base_topic"],
                "complete_topic": CompleteTopic,
                "broker": rc["broker"],
                "port": rc["broker_port"]
            }
        }
        requests.post(post, json.dumps(body_dic))
        print("the patient has been registered on the resource catalog\n")  # PRINT FOR DEMO

        Result_Dict = {
            "sensortype": conf_sensor["sensor_type"][0],
            "clientID": rc["base_topic"],
            "sensorID": conf_sensor["ID_sensor"],
            "topic": CompleteTopic,
            "measure": conf_sensor["measure"],
            "broker": rc["broker"],
            "port": int(rc["broker_port"]),
            "patient": rc["patient"]
        }

        return Result_Dict


if __name__ == "__main__":
    dict = RegisterSensor(sys.argv[1], "HomeCatalog_settings.json")
    while dict == 'Patient not found':
        dict = RegisterSensor(sys.argv[1], "HomeCatalog_settings.json")

    Sensor = (SensorComunication(dict['broker'], dict['clientID'], int(dict['port']), dict['sensorID'], dict['measure'], dict["sensortype"], dict['topic']))
    Sensor.start()
    """
        while 1:
            
        pin=config["pin"]
        Humidity, Temperature = Adafruit_DHT.read_retry(11, pin)
        
        if Humidity is not None and temperature is not None:
            print('\nTemp={0:0.1f}*C  Humidity={1:0.1f}%'.format(Temperature, Humidity))
            Sensor[0].publish('{0:0.1f}'.format(Temperature), dict['patient'])
            Sensor[1].publish('{0:0.1f}'.format(Humidity), dict['patient'])
            time.sleep(3)
        else:
            print('Failure. Try again!')
    """
    vect = [35 , 35.2, 35.4, 35.5, 35.5, 35.5, 35.5, 35.5, 35.5, 35.5, 35.5, 35.5, 35.5, 35.5, 35.5, 35.5, 35.5, 36.7, 36.7, 36.7, 36.7, 36.7, 36.7, 36.7, 36.7, 36.7, 36.7, 36.7, 36.7, 36.9, 37.2, 37.2, 37.2, 37.2, 37.2, 37.2, 37.2, 37.2, 37.2, 37.8, 37.8, 37.8, 37.8, 37.8, 37.8, 38.5, 38.5, 38.5, 38.5, 38.5, 38.5, 38.5, 37, 37, 37, 36.5, 36.5 ]
    while 1:
        for i in vect: 
            Body_Temperature = i

        #Body_Temperature = 35
        #Body_Temperature = Body_Temperature + random.randint(-1,1) #SIMULATED SENSOR
        print(Body_Temperature)
        Sensor.publish(Body_Temperature, dict['patient'])
        time.sleep(10)
        '''
        dict2={'Patient':dict['patient'], 'Temperature':Body_Temperature}
        poststring = 'http://' + sensor_settings["server_ip"] + ':' + str(sensor_settings["server_port"])
        requests.post(poststring, json.dumps(dict2))  #POSTING INFORMATION TO TEMPERATURE CONTROL SERVER
        '''