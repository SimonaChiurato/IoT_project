#resource catalog
import json
import datetime
import requests
import cherrypy
from ResourceCatalog import *

class Manager(object):
    exposed = True
    # mqtt-info
    broker = "test.mosquitto.org"
    port = 1883
    # create a Catalog
    RM = ResourceCatalog()

    def GET(self, *uri, **params): #copiare da 5.1 server

    def POST(self, *uri, **params):


    def PUT(self, *uri, **params):




if __name__ == "__main__":
    service_info = json.load(open("service_catalog_info.json"))
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(ManagerHomeCatalog(), '/', conf)
    cherrypy.config.update(conf)
    cherrypy.config.update({'server.socket_host': service_info['ip_address_service']})
    cherrypy.config.update({"server.socket_port": ManagerHomeCatalog().getPort()})
    cherrypy.engine.start()
    cherrypy.engine.block()