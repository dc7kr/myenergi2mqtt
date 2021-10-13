import time

import json
import requests
from requests.auth import HTTPDigestAuth

class MyEnergiEntity:
    def __init__(self,hashmap):
        self.hashmap=hashmap

    def getSerialNumber(self):
        return self.hashmap["sno"]   
    def getJson(self):
        return json.dumps(self.hashmap)     

class Zappi(MyEnergiEntity):  
    pass

class Eddi(MyEnergiEntity):
    pass
class Harvi(MyEnergiEntity):
    pass
   

class MyenergiHub():
    def __init__(self,cfg):
        self.config=cfg
        self.retries=3

        self.hub_serial = self.config["myenergi"]["serial"]
        self.hub_password = self.config["myenergi"]["passwd"]  

        self.zappis = {}
        self.eddis = {}
        self.harvis = {}
        self.asn =""
        self.fw_version = ""
    
        self.myenergi_base_url = self.config["myenergi"]["director_url"]


    def checkMyEnergiServerURL(self, responseHeader):
        if 'X_MYENERGI-asn' in responseHeader:
            self.myenergi_base_url = 'https://' + responseHeader['X_MYENERGI-asn']
            print(self.myenergi_base_url)
        else:
            print('ERROR: MyEnergi ASN not found in Myenergi header')

    def addEddi(self,eddi):
        self.eddis[str(eddi.getSerialNumber())]=eddi
    def addZappi(self,zappi):
        self.zappis[str(zappi.getSerialNumber())]=zappi
    def addHarvi(self,harvi):
        self.harvis[str(harvi.getSerialNumber())]=harvi

    def getAsn(self):
        return self.asn

    def getStatus(self):
        h = {'User-Agent': 'Wget/1.14 (linux-gnu)'}

        success = False

        theURL = self.myenergi_base_url + '/cgi-jstatus-*'

        for retry in range(self.retries):
            try:
                response = requests.get(theURL, headers = h, auth=HTTPDigestAuth(self.hub_serial, self.hub_password), timeout=10)
            except:
                print(f"Myenergi overview request problem: {theURL}")
            else:
                self.checkMyEnergiServerURL(response.headers)
                if (response.status_code == 200):
                    self.overview_data = response.json()
                    success = True
                else:
                    print("Myenergi server call unsuccessful, returned code: " + str(response.status_code))

            if success == True:
                zappi_data = self.overview_data[1]["zappi"]
                eddi_data = self.overview_data[0]["eddi"]
                harvi_data = self.overview_data[2]["harvi"]
                asn_data = self.overview_data[3]

                self.asn=asn_data["asn"]
                self.fw_version = asn_data["fwv"]

                for zappi_hash in zappi_data: 
                    self.addZappi(Zappi(zappi_hash))

                for eddi_hash in eddi_data: 
                    self.addEddi(Eddi(eddi_hash))
                for harvi_hash in harvi_data: 
                    self.addHarvi(Harvi(harvi_hash))

                break
            else:
                time.sleep(1)

    def getZappis(self):
        return self.zappis

    def getEddis(self):
        return self.eddis

    def getHarvis(self):
        return self.harvis

    def getZappi(self,nr):
        return self.zappis[nr]

    def getEddi(self,nr):
        return self.eddis[nr]

    def getZappiCount(self):
        return len(self.zappis)

    def getEddiCount(self):
        return len(self.eddis)

    def updateZappis(self):
        h = {'User-Agent': 'Wget/1.14 (linux-gnu)'}

        success = False

        for i in range(self.retries):
            try:
                theURL = f"https://{self.getAsn()}/cgi-jstatus-Z"
                print(f"URL: {theURL}\n")
                response = requests.get(theURL, headers = h, auth=HTTPDigestAuth(self.hub_serial, self.hub_password), timeout=10)
            except:
                
                print("Myenergi server zappi request problem")
            else:
                self.checkMyEnergiServerURL(response.headers)
                if (response.status_code == 200):
                    pprint(response.json())
                    success = True
                else:
                    print("Myenergi server call unsuccessful, returned code: " + str(response.status_code))

            if success == True:
                break
            else:
                time.sleep(1)
