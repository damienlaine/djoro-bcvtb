# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext import restful

from lib.meteo import *
from lib.strategie import *
from lib.cost_savings import *

class HelloWorld(restful.Resource):

    @classmethod
    def makeResource(cls):
        return cls

    def get(self, siteId):
        return {'status': siteId}

class FetchMeteo(restful.Resource):

    @classmethod
    def makeResource(cls):
        return cls

    def get(self, siteId):
        status = Meteo.updateForecast(siteId)
        return {'status': status}
        
class CalculeConsigne(restful.Resource):
    
    @classmethod
    def makeResource(cls):
        return cls
   
    def get(self, siteId, deviceId):
        consignes = Strategie_Chauffage.calcule_mambo_strategie(siteId, deviceId)
        return {'strategie': consignes}             

class CostSavings(restful.Resource):
    
    @classmethod
    def makeResource(cls):
        return cls
   
    def get(self, siteId, deviceId):
        costsavings = Cost_Savings.real_money_saved_calc(siteId, deviceId)
        return {'costsavings': costsavings}

#um = UpdateMeteo()
#print um.get("53e3544098f7400e50d36676")

#cc = CalculeConsigne()
#print cc.get("53e3544098f7400e50d36676", 1)