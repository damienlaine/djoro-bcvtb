# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext import restful

from controllers.sites import *

class DjoroRegulationServer(object):

    def __init__(self):
        self.app = Flask("DjoroRegulationServer")
        self.api = restful.Api(self.app)

        hw = HelloWorld.makeResource()
        self.api.add_resource(hw, '/site/<int:siteId>')
  
        um = FetchMeteo.makeResource()
        self.api.add_resource(um, '/site/<int:siteId>/meteo/fetch')      
        
        cc = CalculeConsigne.makeResource()
        self.api.add_resource(cc, '/site/<int:siteId>/device/<int:deviceId>/setpoints/calc') 
        
        cs = CostSavings.makeResource()
        self.api.add_resource(cs, '/site/<int:siteId>/device/<int:deviceId>/moneysaved/calc')

    def start(self, host, port):
        self.app.run(host = host, port = port, debug=True)
        