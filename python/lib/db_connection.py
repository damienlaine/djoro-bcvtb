# -*- coding: utf-8 -*-
"""
Created on Sat Aug 02 05:31:37 2014

@author: perez
"""

from datetime import datetime
from dateutil import tz

from pymongo import MongoClient

from config import *
from temp_dummy_data import *

import datetime
import pytz
from bson.objectid import ObjectId

class MongoConnection:
    """ Accès à la bdd mongo pour récupérer et insérer des données """
    
    ##
    # Insère la météo dans un site
    @staticmethod
    def insertMeteo(site_id, meteoData):
        client = MongoClient(config_mongoURI)
        db = client[config_db_name]
        sites_collection = db['sites']
        meteo = { 'meteo': meteoData }
        sites_collection.update({'id': site_id }, {"$push": meteo}, upsert=False)

    ##
    # Récupère un site selon son id
    @staticmethod
    def getSite(site_id):
        client = MongoClient(config_mongoURI)
        db = client[config_db_name]
        sites_collection = db['sites']
        site = sites_collection.find_one( { 'id': site_id })
        return site
        
    ##
    # Récupère la dernière prévi météo du site
    @staticmethod
    def getMeteo(site_id):
        client = MongoClient(config_mongoURI)
        db = client[config_db_name]
        sites_collection = db['sites']
        site = sites_collection.find_one( { 'id': site_id })
        meteo = site['meteo'].pop()        
        return meteo
        
    
    ##
    # Récupère les coordonnées (lat,lon) d'un site
    @staticmethod    
    def getLatLon(site_id):
        site = MongoConnection.getSite(site_id)
        return { 'lat': site['lat'], 'lon': site['lon']}
               
    ##
    # Récupère le device
    @staticmethod
    def getDevice(site_mongo_id, device_id):
        site = MongoConnection.getSite(site_mongo_id)
        # Récupère le device dont l'id corresopnd à device_id
        try:
            device = site['devices'][device_id]
            # device = next(x for x in site['devices'] if x['id'] == device_id)
        except:
            # Pas de device trouvé
            return None
        return device
        
    ##
    # Récupère les données nécessaires au calcul du temps de relance
    @staticmethod
    def getMatriceData(site_id, device_id):
        device = MongoConnection.getDevice(site_id, device_id)
        if device:
            # Récupère la liste des matrices de temps de relance
            relance_matrices = device['relance_matrices']
            if len(relance_matrices) > 0 :
                # Récupère la dernière donnée
                data = relance_matrices[len(relance_matrices)-1]
            else:
                data = None   # Envoie une valeur par défaut en cas d'absence d'historique dans la bdd.
        else:
            data = None # Envoie une valeur par défaut en cas d'absence de device dans la bdd. Ne devrait jamais arriver.
        return data
        
    ##
    # Ajoute les données nécessaires au calcul du temps de relance dans la bdd
    @staticmethod
    def saveMatriceData(site_id, device_id, data):
        client = MongoClient(config_mongoURI)
        db = client[config_db_name]
        sites_collection = db['sites']
        relance_matrice = { 'devices.' + str(device_id) + '.relance_matrices': data}
        sites_collection.update({'id': site_id}, {"$push": relance_matrice}, upsert=False)
    
        
    ##
    # Transforme une température stockée dans la bdd en température numérique
    # Ex: transforme tempAway en 14°C
    @staticmethod
    def transformTemp(temperature, thermpoints_array):
        # Récupère le dernier élément du tableau des thermpoints (dernier setting de l'utilisateur, le reste étant de l'historique)        
        thermpoints = thermpoints_array[len(thermpoints_array) - 1]
        if temperature in thermpoints:
            return thermpoints[temperature]
        else:
            return temperature
            
    ##
    # Update the money_saved in the database
    @staticmethod
    def updateMoneySaved(site_id, device_id, data):
        client = MongoClient(config_mongoURI)
        db = client[config_db_name]
        sites_collection = db['sites']
        money_saved = { 'devices.' + str(device_id) + '.money_saved': data}
        sites_collection.update({'id': site_id}, {"$set": money_saved}, upsert=False)        

#print MongoConnection.getSavings(ObjectId('53df14f0d1ceb40644bb90f9'), 1)

#client = MongoClient(config_mongoURI)
#db = client[config_db_name]
#sites_collection = db['sites']
#
#sites_collection.remove()
#insert_id = sites_collection.insert(site1)
#print insert_id

#print sites_collection.find_one({ '_id': ObjectId('53dd0cb0d1ceb4031c96eb56') })

# Conversion local to UTC
#madate = datetime.datetime(2014,8,27,10,20)
#print madate
#from_zone = pytz.utc
#to_zone = pytz.timezone('Europe/Paris')
#new_date = madate.replace(tzinfo=from_zone).astimezone(to_zone)
#print new_date

#madate = madate.replace(tzinfo = from_zone)
#print madate
#madate_locale = madate.astimezone(to_zone)

#print madate_locale

#print datetime.time(10,20)
#print time.tzname
#print datetime.datetime.utcnow()