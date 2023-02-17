import json
import requests
import time
import cherrypy
import sys
# un post al sensore che dice di aumentare/diminuire ossigeno

class TemperatureServer:
    exposed = True

    def POST(self):  # RECEIVING THE MESSAGE FROM SENSOR TEMPERATURE IN ORDER TO MAKE SOMETHING
        body = json.loads(cherrypy.request.body.read())
        patient = body['Patient']
        Temperature = body['Temperature']
        Humidity = body['Humidity']

        if Temperature < 18:
            #warning telegram
            print("Fa freddo dal paziente " + patient + ". Temperature: " + str(Temperature))
        elif Temperature > 25:
            print("Fa caldo dal paziente " + patient + ".Temperature: " + str(Temperature))

        if Humidity < 40:
            print("umidità troppo bassa dal paziente " + patient + ". Humidity: " + str(Humidity))
        elif Humidity > 60:
            print("umidità troppo alta dal paziente " + patient + ". Humidity: " + str(Humidity))
           # print("umidità troppo alta dal paziente " + patient + ". Humidity: " + str(Humidity))




if __name__ == "__main__":
    config = json.load(open(sys.argv[1]))
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(TemperatureServer(), '/', conf)
    cherrypy.config.update(conf)
    cherrypy.config.update({"server.socket_host": config["server_ip"]})
    cherrypy.config.update({"server.socket_port": config["server_port"]})
    cherrypy.engine.start()
