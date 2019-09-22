# -*- coding: utf-8 -*-
"""
Created on Sat Aug 02 06:15:54 2014

@author: perez
"""

# Fuseaux horaires pour le stockage des dates et heures :
# - Heure locale pour les infos de programmation utilisateur (ex : mettre à 21° à 07h00 locales)
# - Heure UTC pour les infos mesurées et pour la météo (ex : mesure de température 20.3°C à 06h00 UTC)

import datetime

thermpoints1 = {
    "tempDay": 20,
    "tempNight": 18,
    "tempDayBoost": 22,
    "tempNightBoost": 20,
    "tempAway": 12,
}

status1 = {
    "date": datetime.datetime.utcnow(),          # Heure UTC
    "measuredTemp": 19.5,                # Température intérieure mesurée par le thermostat
    "setPointTemp": 21.0 ,                # Température de consigne
}

# Semaine type
saving1 = {
    "priority": 1,                      # Niveau de priorité (le schedule à priorité la plus basse écrase les autres)
    "status": "APPLIED",                 # DISMISSED, PROPOSED, APPLIED, EXPIRED
    "program": {
        "startDate": datetime.datetime(2010,1,1),  # Heure locale
        "endDate": datetime.datetime(2100,1,1),  # Heure locale
        "type": "WEEK",
        "week": [
            {
                "day": 0,               # 0=Lundi, 1=Mardi, 2=Mercredi, etc. (conforme à la convention datetime python)
                "list":
                [
                    { "hour": 7,  "minute": 0, "temperature": "tempDay"},     # Heures locales
                    { "hour": 9,  "minute": 0, "temperature": "tempAway"},
                    { "hour": 18, "minute": 0, "temperature": "tempDay"},
                    { "hour": 23, "minute": 0, "temperature": "tempNight"}
                ]
            },
            {
                "day": 1,
                "list":
                [
                    { "hour": 7,  "minute": 0, "temperature": "tempDay"},     # Heures locales
                    { "hour": 9,  "minute": 0, "temperature": "tempAway"},
                    { "hour": 18, "minute": 0, "temperature": "tempDay"},
                    { "hour": 23, "minute": 0, "temperature": "tempNight"}
                ]
            },
            {
                "day": 5,               # 0=Lundi, 1=Mardi, 2=Mercredi, etc. (conforme à la convention datetime python)
                "list":
                [
                    { "hour": 7,  "minute": 0, "temperature": "tempDay"},     # Heures locales
                    { "hour": 9,  "minute": 0, "temperature": "tempAway"},
                    { "hour": 18, "minute": 0, "temperature": "tempDay"},
                    { "hour": 23, "minute": 0, "temperature": "tempNight"}
                ]
            },
            {
                "day": 6,               # 0=Lundi, 1=Mardi, 2=Mercredi, etc. (conforme à la convention datetime python)
                "list":
                [
                    { "hour": 0,  "minute": 0, "temperature": "tempDay"},     # Heures locales
                    { "hour": 9,  "minute": 0, "temperature": "tempAway"},
                    { "hour": 18, "minute": 0, "temperature": "tempDay"},
                    { "hour": 23, "minute": 0, "temperature": "tempNight"}
                ]
            },# Etc. Jours fériés à ajouter ultérieurement            
        ]
    }
}

# Vacances
saving2 = {
    "priority": 5,                       # Niveau de priorité (le schedule à priorité la plus basse écrase les autres)
    "status": "APPLIED",                 # DISMISSED, PROPOSED, APPLIED, EXPIRED
    "program": {
        "startDate": datetime.datetime(2014,8,4,7,15),  # Heure locale
        "endDate": datetime.datetime(2014,8,30,14,30),  # Heure locale
        "type": "PERMANENT",
        "temperature": "tempAway"
    }
}

meteo_forecast1 = {
    "updatedOn": datetime.datetime.utcnow(), # en heures UTC
    "echeances":
    [
        { "date": datetime.datetime(2014,7,5,0), "T": 21.5 }, # en heures UTC
        { "date": datetime.datetime(2014,7,5,3), "T": 19.4 },
        { "date": datetime.datetime(2014,7,5,6), "T": 17.5 }
        # Etc.
    ]
}

device1 = {
    #"id" : 1,                            # id pour identifier le device dans le site
    "type": "NETATMO",
    "manufacturer_id": "13544685132",    # Numéro permettant la connection au thermostat
    "thermpoints": [thermpoints1],         # Objet contenant les températures par défaut pour chacun des modes (away, boost...)
    "history": [status1],                # Historique des mesures et des températures de consigne
    "savings": [saving1, saving2],       # Liste des programmes calendaires (semaine type, proposition d'économies)
    "relance_matrices": [],              # Liste des matrices de temps de relance
    "money_saved": [{"from": datetime.datetime.utcnow(), "last_calc_date": None, "amount": 0}],                   # Historique de l'argent économisé
    "base_temp": 20,                     # Temperature for cost savings calculation (we assume that if setpoint temperature is less that base_temp, we save)
    "dju_cost": 0.44,                    # Cost of a DJU in real money
}

site1 = {
    "id" : 12,
    "name": "Ma maison",
    "local_time": "Europe/Paris",        # Fuseau horaire du site
    "lat": 43.60,                        # Latitude du site
    "lon": 1.44,                         # Longitude du site
    "devices": [device1],                # Liste des thermostats présents sur le site
    "meteo": [meteo_forecast1],          # Prévisions météo pour le site
}                                        
