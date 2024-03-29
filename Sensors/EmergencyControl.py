import json
from MyMQTT import *
import time
import cherrypy
from datetime import datetime
import sys


class ManageSensor():
    exposed = True

    def __init__(self, baseTopic, broker, port, Limits):
        self.clientID = "emergency"
        topic = baseTopic.split("/")
        self.baseTopic = topic[0]
        self.client = MyMQTT(self.clientID, broker, port, self)
        self.register = []
        self.limits = json.load(open(Limits))
        self.__message = {  # topic --> bn   message--> e !!!!!!
            'bn': '',
            'e': [
                {
                    'type': '',
                    'unit': '',
                    'patient': '',
                    'value': '',
                    'time': '',
                    'warning': ''
                }
            ]
        }

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

    def GET(self, *uri, **parameters):  # METHOD FOR HANDLING THE REQUEST FROM APPLICATIONS
        if len(parameters) >= 1:
            print("TELEGRAM GET REQUEST RECEIVED!\n")
            print("\n\n")
            if parameters["check"] == "value":
                for entry in self.register:
                    if entry['e'][0]["patient"] == parameters["room_name"] and entry["e"][0]["type"] == parameters["sensor_type"]:  # modifica fatta per il telegram warning
                        output = (self.rightName(entry["e"][0]["type"]) +': ' + str(entry["e"][0]["value"]) + ' ' + entry["e"][0][
                                      "unit"])
                        print("MESSAGE SENT!\n")
                        return json.dumps(output)
                print("ERROR MESSAGE SENT!\n")
                return "NOT FOUND"
            elif parameters["check"] == "all":
                output = []
                for entry in self.register:
                    if entry['e'][0]["patient"] == parameters["room_name"]:
                        output.append(self.rightName(entry["e"][0]["type"]) + ': ' + str(entry["e"][0]["value"]) + ' ' +
                                      entry["e"][0][
                                          "unit"] + '. Time: ' + str(
                            datetime.utcfromtimestamp(int(round(float(entry["e"][0]["time"]), 0)))) + ' UTC\n')
                        print("MESSAGE SENT!\n")
                return output
            else:
                error_string = "incorrect URI" + str(len(uri))
                raise cherrypy.HTTPError(400, error_string)

    def run(self):
        self.client.start()

    def end(self):
        self.client.stop()

    def follow(self, topic):
        self.client.mySubscribe(topic)

    def notify(self, topic, msg):
        payload = json.loads(msg)
        result = payload
        result_dict = json.loads(result)

        flag = 0
        for entry in self.register:
            if entry["e"][0]['type'] == result_dict["e"][0]['type'] and entry["e"][0]["patient"] == result_dict["e"][0]['patient']:
                entry["e"][0]['value'] = result_dict["e"][0]['value']
                entry["e"][0]['time'] = result_dict["e"][0]['time']
                entry["e"][0]["patient"] = result_dict["e"][0]["patient"]
                flag = 1
        if flag == 0:
            self.register.append(result_dict)

        for l in self.limits:
            if result_dict["e"][0]['type'] == l["sensor_type"]:
                if result_dict["e"][0]['value'] < l["min"]:
                    self.emergencypublish(result_dict, 'min')

                elif result_dict["e"][0]['value'] > l["max"]:
                    self.emergencypublish(result_dict, 'max')

                elif result_dict["e"][0]['value'] > l["max_good"]:
                    self.emergencypublish(result_dict, 'max_good')

    def emergencypublish(self, result_dict, warning):
        message = self.__message
        message['e'][0]['patient'] = result_dict["e"][0]['patient']
        message['e'][0]['value'] = result_dict["e"][0]['value']
        message['e'][0]['time'] = result_dict["e"][0]['time']
        message['e'][0]['type'] = result_dict["e"][0]['type']
        message['e'][0]['unit'] = result_dict["e"][0]['unit']
        message['e'][0]['warning'] = warning
        message['bn'] = self.baseTopic + '/emergency/' + result_dict["e"][0]['type']
        self.client.myPublish(self.baseTopic + '/emergency/' + result_dict["e"][0]['type'],
                              json.dumps(message))  # TOPIC molinette/emergency/sensor_type
        print("Published!\n" + json.dumps(message) + "\n")


if __name__ == '__main__':
    config = json.load(open(sys.argv[1]))  #emergency control settings
    Home_info = json.load(open("HomeCatalog_settings.json"))
    Limits = "Limits.json"
    manager = ManageSensor(Home_info["base_topic"], config["broker"], config["broker_port"], Limits)

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(manager, '/', conf)
    cherrypy.config.update(conf)
    cherrypy.config.update({"server.socket_host": config["ip"]})
    cherrypy.config.update({"server.socket_port": config["port"]})
    cherrypy.engine.start()

    manager.run()
    manager.client.unsubscribe()
    manager.follow(Home_info["base_topic"] + '/#')   #molinette/patients/#'
    cherrypy.engine.block()
    manager.end()
