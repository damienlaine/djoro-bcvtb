# -*- coding: utf-8 -*-
"""
Created on Sun Jul 20 07:34:52 2014

@author: perez
"""

from temps_relance import *
from db_connection import *

import datetime

##
# Nom du fichier de sauvegarde des variables d'environnement (heure)
nom_fichier_environnement = "variablesEnvironnement.txt"
#
# Constantes pour l'algorithme
#

##
# Pas de simulation en minutes
pas_simulation = 10

class API_Environnement:
    """ Accès aux éléments liés à l'environnement (heure, météo) """
    
    def __init__(self):
        self.heure_actuelle = 0 # Initialise l'heure à 0 (au cas où le fichier d'environnement n'est pas encore créé)
        self.nom_fichier_environnement = nom_fichier_environnement
        self.pas_simulation = pas_simulation
        self.loadEnvironnement()    # Charge les variables depuis le fichier
        
    def loadEnvironnement(self):
        try:
            with open(self.nom_fichier_environnement, 'r') as f:
                data = pickle.load(f)
                self.heure_actuelle = data['heure_actuelle']
        except:
            print 'Premiere execution : fichier environnement inexistant'

    def getHeure(self):
        return self.heure_actuelle
    
    def saveEnvironnement(self):
        with open(self.nom_fichier_environnement, 'w') as f:
            data = {}
            data['heure_actuelle'] = self.heure_actuelle
            data_string = pickle.dumps(data)
            f.write(data_string)

    def incrementeHeure(self):
        self.heure_actuelle += pas_simulation
    
    def diffEnMinutes(h1, h2):
        return h1 - h2
        
class API_Mongo_Environnement(API_Environnement):
    """ Accès aux heures avec MongoDB (donc à l'heure système réelle) """
    
    def getHeure(self):
        return datetime.datetime.utcnow()
        
    def diffEnMinutes(h1, h2):
        diff = h1-h2        
        return diff.days * 86400 + diff.seconds
    

class API_Client:
    """ Accès aux données du client (matrice relance, schedule...) fictives """
    
    def __init__(self, environnement):
        # Crée l'objet contenant les données nécessaires au calculs du temps de relance
        self.schedule = API_Schedule(environnement)
        self.etat_relance = API_Etat_Relance(pas_simulation, environnement)

class API_Mongo_Etat_Relance(API_Etat_Relance):
    """ Hérite d'API_Etat_Relance qui contient les variables et méthodes nécessaires au calcul du temps de relance. Surcharge les méthodes loadData et saveData pour utiliser la BDD Mongo """

    def __init__(self, site_mongo_id, device_id, pas_simulation, environnement):
        # Initialisation des variables pour le temps de relance (seront remplacées par les données du fichier s'il existe)
        self.relance_en_cours = False
        self.Tconsigne_relance = 0.
        self.heure_debut_relance = 0
        self.Tint_initial_relance = 0.
        self.Text_initial_relance = 0.
        self.tIntSteps = tIntSteps
        self.tExtSteps = tExtSteps
        self.tempsRelanceMatrice = init_tempsRelanceMatrice
        self.nom_fichier_etat_relance = nom_fichier_etat_relance
        self.pas_simulation = pas_simulation
        self.environnement = environnement
        self.site_mongo_id = site_mongo_id
        self.device_id = device_id
        self.loadData() # Charge les données depuis le fichier s'il existe
        
    def loadData(self):  
        """ Charge les données depuis la bdd """
        data = MongoConnection.getMatriceData(self.site_mongo_id, self.device_id)
        if data:
            self.relance_en_cours = data['relance_en_cours']
            self.Tconsigne_relance = data['Tconsigne_relance']
            self.heure_debut_relance = data['heure_debut_relance']
            self.Tint_initial_relance = data['Tint_initial_relance']
            self.Text_initial_relance = data['Text_initial_relance']
            self.tempsRelanceMatrice = data['tempsRelanceMatrice']            
        else:
            print "Première exécution pour ce device, pas encore de données"

    def saveData(self):
        """ Sauve les données dans la bdd """
        data = {}
        data['relance_en_cours'] = self.relance_en_cours
        data['Tconsigne_relance'] = self.Tconsigne_relance
        data['heure_debut_relance'] = self.heure_debut_relance
        data['Tint_initial_relance'] = self.Tint_initial_relance
        data['Text_initial_relance'] = self.Text_initial_relance
        # Encode la matrice de temps de relance pour la rendre compatible avec mongo (si c'est nécessaire)
        try:
            tempsRelanceMatriceEncodee = []        
            for contenu in self.tempsRelanceMatrice:
                tempsRelanceMatriceEncodee.append(contenu.tolist())
        except:
            # Si la matrice contient déjà des éléments de type list
            tempsRelanceMatriceEncodee = self.tempsRelanceMatrice            
        data['tempsRelanceMatrice'] = tempsRelanceMatriceEncodee
        
        MongoConnection.saveMatriceData(self.site_mongo_id, self.device_id, data)
        
class API_Mongo_Client:
    """ Accès aux données du device d'un client dans la BDD """
    # TODO supprimer environnement
    def __init__(self, site_mongo_id, device_id, environnement):
        self.schedule = API_Mongo_Schedule(site_mongo_id, device_id)
        # TODO etat_relance pour la BDD
        self.etat_relance = API_Mongo_Etat_Relance(site_mongo_id, device_id, pas_simulation, environnement)
        # TODO A optimiser (inutile de faire un accès à la bddd pour le schedule et un autre pour Tint)
        self.site_mongo_id = site_mongo_id
        self.device_id = device_id        
        
    def getTint(self):
        """ Récupère la température intérieure mesuré par le device """
        device = MongoConnection.getDevice(self.site_mongo_id, self.device_id)
        if device:
            # Récupère les savings
            history = device['history']
            if len(history) > 0 :
                dernier_status = history[len(history)-1]
                Tint = dernier_status['measuredTemp']
            else:
                Tint = 20   # Envoie une valeur par défaut en cas d'absence d'historique dans la bdd.
        else:
            Tint = 20   # Envoie une valeur par défaut en cas d'absence de device dans la bdd. Ne devrait jamais arriver.
        return Tint

class API_Schedule:
    """ Accès aux informations du calendrier de chauffe fictives pour la simulation """
    
    def __init__(self, environnement):
        # A besoin de connaître l'heure actuelle, donc de connaître l'environnement
        self.environnement = environnement
    
    # Fonction générant une matrice schedule fictive (pour les besoins du test)
    def get_schedule(self):
        # Récupère l'heure
        heure = self.environnement.getHeure()
        # Crée une liste avec le schedule suivant :
        # 21° à 7h
        # 12° à 9h
        # 21° à 18h
        # 18° à 23h
        liste = [( (420-heure) % 1440, 21), ( (560-heure) % 1440, 12), ( (1080-heure) % 1440, 21), ( (1380-heure) % 1440, 18)]
        liste.sort()
        # Si le premier élément n'est pas pour tout de suite, crée la consigne actuelle (dernier élément de la liste)
        if (liste[0][0] != 0):    
            dernier = liste[len(liste)-1][1]
            liste.insert(0, (0, dernier))
        next_schedule = np.array(liste)
        return next_schedule

class API_Mongo_Schedule:
    """ Accès aux informations du calendrier de chauffe programmé par le client """    

    def __init__(self, site_mongo_id, device_id):
        self.site_mongo_id = site_mongo_id
        self.device_id = device_id

    ##
    # Récupère la température applicable à la date de maintenant dans un programme de type WEEK
    # (retourne récursivement en arrière jusqu'à trouver une température applicable)
    @staticmethod
    def __get_last_week_temp(program, now, thermpoints, nb_recursions):
        # Récupère le jour de la semaine
        day_now = now.weekday()
        # Récupère la liste des changements de consigne du jour
        try:
            jour_type = next(x for x in program['week'] if x['day'] == day_now)
        except:
            # Aucun programme défini pour ce jour de la semaine
            jour_type = {}
            jour_type['list'] = []
        # Initialise le résultat
        resultat = {}
        resultat['heure'] = datetime.time(0,0)
        resultat['ok'] = False
        for elt in jour_type['list']:
            heure_consigne = datetime.time(elt['hour'], elt['minute'])            
            if (heure_consigne <= now.time()):
                # Si on a trouvé une consigne antérieure à l'instant présent
                if (resultat['heure'] <= heure_consigne):
                    # Si on a trouvé une consigne plus récente
                    resultat['ok'] = True
                    resultat['heure'] = heure_consigne
                    resultat['thermpoint'] = elt['temperature']
        if resultat['ok']:
            # Transforme le thermpoint en température
            temperature = MongoConnection.transformTemp(resultat['thermpoint'], thermpoints)
            return temperature
        else:
            # Incrémente le nombre de récursions et vérifie si on n'a pas déjà fait le tour de la semaine (ne devrait pas arriver, sauf en cas de programme WEEK vide dans la bdd)
            nb_recursions += 1
            if (nb_recursions > 8):
                return None
            else:
                # Passe au jour précédent
                now = now - datetime.timedelta(days=1)      # Retire un jour
                now = datetime.datetime.combine(now.date(), datetime.time(23, 59))    # Récupère la date et passe à 23h59
                # Lance la récursion
                return API_Mongo_Schedule.__get_last_week_temp(program, now, thermpoints, nb_recursions)

    ##
    # Récupère les prochaines températures applicables pour le jour en cours et le jour suivant
    # (récursif jour en cours puis jour suivant : jour_a_traiter = 0 pour le jour en cours, jour_a_traiter = 1 pour le jour suivant)
    # return [(temperature, date_application), ...]
    @staticmethod
    def __get_next_24h_change(program, mydate, thermpoints, jour_a_traiter):
        # Récupère le jour de la semaine
        day_now = mydate.weekday()
        # Récupère la liste des changements de consigne du jour
        try:
            jour_type = next(x for x in program['week'] if x['day'] == day_now)
        except:
            # Aucun programme défini pour ce jour de la semaine
            jour_type = {}
            jour_type['list'] = []
        # Initialise le résultat
        resultat = []
        # Parcourt la liste des changements de consigne du jour
        for elt in jour_type['list']:
            heure_consigne = datetime.time(elt['hour'], elt['minute'])            
            if ( (heure_consigne > mydate.time()) or (jour_a_traiter == 1) ):
                # Si on a trouvé une consigne postérieure à l'instant présent, ou si on est au jour suivant (jour entier à prendre en compte dans ce cas)
                # Transforme le thermpoint en température
                temperature = MongoConnection.transformTemp(elt['temperature'], thermpoints)  
                datetime_application = datetime.datetime.combine(mydate.date(), heure_consigne)
                resultat.append( (temperature, datetime_application) )

        if (jour_a_traiter == 1):
            # Si on est au deuxième jour, renvoie le résultat
            return resultat
        else:
            # Si on est au premier jour, poursuit récursivement vers le deuxième jour
            # Passe au jour suivant
            second_jour = mydate + datetime.timedelta(days=1)      # Ajoute un jour
            # Lance la récursion
            resultat = resultat + API_Mongo_Schedule.__get_next_24h_change(program, second_jour, thermpoints, 1)
            # Retourne le résultat
            return resultat

    ##
    # Récupère la matrice schedule dans la bdd mongo et la traite
    # Renvoie les températures de consigne à appliquer pour les 24 prochaines heures
    # (identique à get_schedule, mais travaille sur la bdd au lieu de renvoyer un dummy schedule)
    # @return programme sous la forme [(minutes à partir de maintenant, température souhaitée)]
    def get_schedule(self):
        # Récupère les savings depuis la bdd        
        device = MongoConnection.getDevice(self.site_mongo_id, self.device_id)
        if device:
            # Récupère les savings
            savings = device['savings']
            # Récupère l'heure actuelle
            now = datetime.datetime.now()   # TODO Gérer les problèmes de fuseaux horaires. Actuellement ça ne marche que pour le fuseau France          
# TEST
#            now = datetime.datetime(2014, 8, 30, 14)
            
            # Crée une liste qui contiendra tous les changements de Tconsigne programmés, quelque soit leur priorité
            changements = []
            # Itère sur les savings
            saving_i = 0
            for saving in savings:
                # Incrémente l'indice identifiant le saving
                saving_i = saving_i + 1
                # Récupère le programme contenu dans le saving
                program = saving['program']
                # Vérifie si le programme est applicable (ie déjà démarré ou démarre dans moins de 24h, pas encore terminé, et validé)
                if (saving['status'] == "APPLIED" and (program['startDate'] - datetime.timedelta(days=1)) <= now < program ['endDate']):
                    if program['type'] == "PERMANENT":
                        # Si le programme est de type "PERMANENT"
                                # Récupère la température de consigne
                                temperature = MongoConnection.transformTemp(program['temperature'], device['thermpoints'])
                                # Calcule le nombre de minutes avant le début du programme
                                if program['startDate'] < now:
                                    # Le programme est déjà démarré
                                    delta_minutes_debut = 0
                                else:
                                    # Le programme démarre plus tard. Calcule dans combien de minutes il démarre.
                                    timedelta_debut = program['startDate'] - now
                                    delta_minutes_debut = (timedelta_debut.days * 24 * 60) + (timedelta_debut.seconds / 60)
                                # Ajoute le programme sous la forme d'un unique point de consigne à appliquer immédiatement...
                                changements.append({ 'minutes': delta_minutes_debut, 'saving_i': saving_i, 'priority': saving['priority'], 'temperature': temperature })
                                # ... et d'une fin de programme à la fin de validité de celui-ci
                                timedelta = program['endDate'] - now
                                delta_minutes = (timedelta.days * 24 * 60) + (timedelta.seconds / 60)   # temps en minutes entre maintenant et la fin du programme
                                changements.append({ 'minutes': delta_minutes, 'saving_i': saving_i, 'priority': saving['priority'], 'temperature': None })                                
                    elif program['type'] == "WEEK":
                        # Si le programme est de type WEEK
                        
                        # Récupère la dernière température applicable à la date/heure de maintenant...
                        temp_now = API_Mongo_Schedule.__get_last_week_temp(program, now, device['thermpoints'], 0)
                        # ... et l'ajoute au programme
                        changements.append({ 'minutes': 0, 'saving_i': saving_i, 'priority': saving['priority'], 'temperature': temp_now })
                        # Récupère les prochaines températures applicables pour les 24 prochaines heures
                        liste_temp_suivantes = API_Mongo_Schedule.__get_next_24h_change(program, now, device['thermpoints'], 0)                        
                        # ... et les ajoute au programme
                        for elt in liste_temp_suivantes:
                            (temperature, date_application) = elt
                            timedelta = date_application - now
                            delta_minutes = (timedelta.days * 24 * 60) + (timedelta.seconds / 60)
                            changements.append({ 'minutes': delta_minutes, 'saving_i': saving_i, 'priority': saving['priority'], 'temperature': temperature })                         
        else:
            # Aucun device trouvé (ne devrait pas se produire)
            return None

        # Parcourt la liste des changements de consigne programmés dans l'ordre et en déduit la température applicable à chaque instant pour chaque saving       
        # Trie la liste des changements par ordre chronologique        
        changements = sorted(changements, key=lambda k: k['minutes']) 
        # Initialise un tableau contenant les consignes en cours pour chaque saving        
        en_cours_par_saving_i = {}
        # Initialise le saving en cours
        saving_en_cours = None
        # Initialise le résultat
        resultat_inter = {}
        # Parcourt la liste des changements dans l'ordre
        for changement in changements:
            saving_fini = False
            minutes_fini = 0
            if (changement['temperature'] == None):
                # Si le saving est fini, le retire de la liste en_cours, et mémorise l'heure à laquelle il s'est terminé
                try:
                    en_cours_par_saving_i.pop(changement['saving_i'])
                    if changement['saving_i'] == saving_en_cours['saving_i']:
                        minutes_fini = changement['minutes']                        
                        saving_fini = True
                        saving_en_cours = None
                except:
                    None
            else:
                # Si le saving n'est pas fini (Température valide), l'insère dans la liste en_cours
                en_cours_par_saving_i[changement['saving_i']] = changement

            # Récupère la consigne la plus prioritaire dans la liste en_cours
            for elt in en_cours_par_saving_i:
                mybool = False
                if (not saving_en_cours):
                    mybool = True                    
                elif  (en_cours_par_saving_i[elt]['priority'] >= saving_en_cours['priority'] ):
                    mybool = True
                if mybool:
                    saving_en_cours = en_cours_par_saving_i[elt]
            
            # On a fini de déterminer quel est le saving en cours à l'instant t       
            
            # Détermine l'instant t
            if saving_fini:
                # Si c'est la fin d'un saving
                minutes = minutes_fini
            else:
                # Sinon, c'est qu'on est au début d'un nouveau saving
                minutes = saving_en_cours['minutes']            
            
            # Stocke le résultat intermédiaire sous forme de dictionnaire
            resultat_inter[minutes] = saving_en_cours['temperature']
        
        # Transforme le résultat intermédiaire (dico) sous la forme finale (liste de tuples), en supprimant les doublons
        temperature_en_cours = None
        resultat = []
        for minutes in sorted(resultat_inter.iterkeys()):
            # Ne renvoie que les prochaines 24h
            if (minutes < 1440):
                if (resultat_inter[minutes] != temperature_en_cours):
                    temperature_en_cours = resultat_inter[minutes]
                    resultat.append( (minutes, temperature_en_cours) )
        
        # Renvoie le résultat
        return resultat

## TEST
#schedule = API_Mongo_Schedule(ObjectId('53e3544098f7400e50d36676'), 1)
#print schedule.get_schedule()
        
class API_Meteo:
    """ Accès aux informations de prévision météo (fictive) """
    
    def __init__(self, tOut):
        # Crée une matrice météo fictive
        self.tOut = tOut
        
    ##
    # Fonction renvoyant la prévi météo à l'instant t
    # (prévi météo fictive en attendant : on considère que la température constante et vaut toujours tOut)
    # @param t Temps en minutes
    # @return température prévue
    def previ_meteo(self, t):
        return self.tOut
        
    ##
    # TODO A supprimer (a priori inutile, à vérifier)
    # Fonction renvoyant la prévi météo à l'instant t
    # Récupérée dans mongo
    # @param t Temps en minutes
    # @param site_mongo_id id du site dans la bdd
    # @return température prévue
    def mongo_previ_meteo(self, t, site_mongo_id):
        meteo = MongoConnection.getMeteo(site_mongo_id)        
        print meteo        
        
class API_Mongo_Meteo:
    """ Accès aux informations de prévision météo (mongo) """
    
    def __init__(self, site_mongo_id):
        # Récupère la prévision météo dans la bdd
        self.meteo = MongoConnection.getMeteo(site_mongo_id)        
        
    ##
    # Fonction renvoyant la prévi météo à l'instant t
    # Récupérée dans mongo
    # @param t Temps en minutes
    # @param site_mongo_id id du site dans la bdd
    # @return température prévue (None si pas de prévision trouvée)
    def previ_meteo(self, t):
        # Initialise la température        
        temp = None
        # Récupère la date de maintenant
        now = datetime.datetime.utcnow()
        # Ajoute le nombre de minutes souhaité
        date_souhaitee = now + datetime.timedelta(0, t*60)
        for echeance in self.meteo['echeances']:
            if echeance['date'] < date_souhaitee :
                temp = echeance['T']
        # Renvoie le résultat
        return temp

# TEST
#mymeteo = API_Mongo_Meteo('53e3544098f7400e50d36676')
#print mymeteo.previ_meteo(0)
        
    
