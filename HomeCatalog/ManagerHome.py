#home catalog
import json
import cherrypy

#probabilmente 5.1 server
#controllare i json.dump
#Creare le funzioni da mettere nell'home catalog invece di tenere utto nel get
class ManagerHome(object):
    exposed = True
    # mqtt-info
    #Usa i settings
    broker = "test.mosquitto.org"
    port = 1883
    ip_address = "192.168.1.208"
    ip_port = "8095"
    res_cat = json.load(open("resource_catalog_info.json"))  # quale resource catalog dovrei aprire?

    def GET(self, *uri, **params):

        if len(uri) == 1:

            if uri[0] == 'resource_catalogs':           #restituisce tutti i res cat che ho
                return json.dumps(self.res_cat)

            elif uri[0] == 'patients':     #restituisce la lista dei nomi dei pazienti
                result = {"names": self.res_cat["patient"] + '\n' }
                return json.dumps(result)

            elif uri[0] == 'room_info':     #restituisce le informazione della singola camera
                results = [entry for entry in self.res_cat if (entry["patient"] == params["patient"])]   #verifica che funzioni scritto cosi
                return json.dumps(results)

            elif uri[0] == 'broker':
                temp = {'broker': self.broker, 'port': self.port}
                return json.dumps(temp)

            elif uri[0] == 'base_topic':
                return json.dumps(self.res_cat["base_topic"])
        else:
            error_string = "incorrect URI or PARAMETERS URI" + {len(uri)} + "PAR" + {len(params)}           #cambia stringa
            raise cherrypy.HTTPError(400, error_string)

    def POST(self, *uri):
        if len(uri) == 0:
            body = cherrypy.request.body.read()
            print("POST RECEIVED WITH BODY:", body)
            json_body = json.loads(body)
            already_existing = False
            for entry in self.res_cat:
                if entry["base_topic"] == json_body["base_topic"]:
                    already_existing = True
            if already_existing == False:
                self.res_cat.append(json_body)
                print(json_body)
                with open(self.res_cat, "w") as f:
                    json.dump(self.res_cat, f)
                return "Resource catalog inserted with success"
            else:
                return "Resource catalog already existing"
        else:
            error_string = "incorrect URI or PARAMETERS" + {len(uri)}
            raise cherrypy.HTTPError(400, error_string)


    def PUT(self, *uri):
        if len(uri) == 0:
            body = cherrypy.request.body.read()
            print("PUT RECEIVED WITH BODY:", body)
            json_body = json.loads(body)
            already_existing = False
            for entry in self.res_cat:      #controlla salvataggio e nome degli attributi
                if entry["base_topic"] == json_body["base_topic"]:
                    already_existing = True
                    entry["broker"] = json_body["broker"]
                    entry["broker_port"] = json_body["broker_port"]
                    entry["ip_address"] = json_body["ip_address"]
                    entry["ip_port"] = json_body["ip_port"]
                    print(json_body)
                with open(self.res_cat, "w") as f:
                    json.dump(self.res_cat, f)
            if already_existing == False:
                self.res_cat.append(json_body)
                print(json_body)
                with open(self.res_cat, "w") as f:
                    json.dump(self.res_cat, f)
                return "Resource catalog not found. New resource catalog inserted with success"
            else:
                return "Resource catalog modified with success"
        else:
            error_string = "incorrect URI or PARAMETERS" + {len(uri)}
            raise cherrypy.HTTPError(400, error_string)