# -*- coding: utf-8 -*-
"""
Created on Sat Aug 02 16:50:54 2014

@author: perez
"""

from config import *
from db_connection import *

import requests
import json
import datetime

class Meteo:
    """ Accès à l'API météo pour télécharger les données """
    
    ##
    # Télécharge la dernière prévision météo depuis le serveur
    @staticmethod
    def downloadForecast(lat, lon):
        url = "http://api.openweathermap.org/data/2.5/forecast/?lat=" + str(lat) + "&lon=" + str(lon) + "&mode=json&APPID=" + config_openWeatherMapAPIKey
        r = requests.get(url)
        if (r.status_code == 200):
            data = json.loads(r.content)
            list = data['list']
            echeances = []
            for echeance in list:
                # Récupère l'échéance de la prévision
                ech_ts_date = echeance['dt']    # Format timestamp
                ech_date = datetime.datetime.utcfromtimestamp(ech_ts_date) # Convertit le timestamp en date
                # Récupère la température en Kelvin et convertit en °C                
                ech_temp = echeance['main']['temp'] - 273.15
                # Construit l'élément                
                resultat_element = {
                    'date': ech_date,
                    'T': ech_temp,
                }
                # Ajoute l'élément à la liste
                echeances.append(resultat_element) 
            # Prépare l'objet résultat
            resultat = {
                "createdOn": datetime.datetime.utcnow(), # en heures UTC
                "echeances": echeances,        
            }
            return resultat
        else:
            return None

    ##
    # Update la météo pour un site_mongo_id donné
    # Télécharge la météo et met à jour la prévision dans la bdd
    @staticmethod
    def updateForecast(site_id):
        # Récupère la latitude et longitude du site
        latLon = MongoConnection.getLatLon(site_id)
        lat = latLon['lat']
        lon = latLon['lon']
        # Télécharge la météo
        meteo = Meteo.downloadForecast(lat, lon)
        if (meteo != None):
            # En cas de succès de la requête, met à jour la météo du site dans la bdd
            MongoConnection.insertMeteo(site_id, meteo)
            return 0
        else:
            # Echec
            return 1

#print Meteo.updateForecast("53e3544098f7400e50d36676")
#print Meteo.downloadForecast(35,1)