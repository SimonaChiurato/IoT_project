#service catalog
import json

#metti tutte le funzioni e metti il main nel manager home
class HomeCatalog:
  #non so se questo init vada messo due volte o meno, oppure come farlo funzionare mettendolo una volta sola
  def __init__(self):
    self.settings = "HomeCatalog_settings.json"
    self.cat = json.load(open(self.settings))
    self.cat["resource_catalogs"]=[]
    with open(self.settings, "w") as myfile:
      myfile.write(json.dumps(self.cat))


  def returnAllPatients(self):
    result = { 'names':[] }
    for res in self.cat["resource_catalogs"]:
       result['names'].append(res['patient'])
    return result

  def searchPatient(self, params):
    found = 0
    for entry in self.cat["resource_catalogs"]:
      if (entry["patient"] == params["patient"]):
        found = 1
        return entry
    return found

  def newResCat(self, message):
    already_existing = False
    for entry in self.cat["resource_catalogs"]:
      if entry["base_topic"] == message["base_topic"]:
        already_existing = True
    if already_existing == False:
      self.cat["resource_catalogs"].append(message)
      print("Prova")
      print(self.cat)
      with open(self.settings, "w") as f:
        json.dump(self.cat, f)
      print ("Resource catalog inserted with success")
    else:
      print ("Resource catalog already existing")

  def updateResCat(self,message):
    already_existing = False
    for entry in self.cat["resource_catalogs"]:  # controlla salvataggio e nome degli attributi
      if entry["base_topic"] == message["base_topic"]:
        already_existing = True
        entry["broker"] = message["broker"]
        entry["broker_port"] = message["broker_port"]
        entry["ip_address"] = message["ip_address"]
        entry["ip_port"] = message["ip_port"]
        entry["patient"] = message["patient"]


    if already_existing == False:
      self.cat["resource_catalogs"].append(message)
      print ("Resource catalog not found. New resource catalog inserted with success")
    else:
      print ("Resource catalog modified with success")

    return self.cat

