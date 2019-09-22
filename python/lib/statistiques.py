# -*- coding: utf-8 -*-
"""
Created on Sun Jul 20 15:09:11 2014

@author: perez
"""

import cPickle as pickle

##
# Nom du fichier pour sauvegarder les statistiques
nom_fichier_statistiques = "variablesStatistiques.txt"
nom_fichier_csv_statistiques = "variablesCsvStatistiques.txt"

##
# Ecart entre température intérieure et température souhaitée à partir duquel on considère qu'il y a inconfort
delta_T_inconfort = 0.5

class Statistiques:
    """ Calcul et enregistrement de statistiques """
    
    def __init__(self):
        self.liste_mesures = []
        self.nom_fichier_statistiques = nom_fichier_statistiques
        self.nom_fichier_csv_statistiques = nom_fichier_csv_statistiques
        self.loadData()    # Charge les variables depuis le fichier
        
    def loadData(self):
        try:
            with open(self.nom_fichier_statistiques, 'r') as f:
                data = pickle.load(f)
                self.liste_mesures = data['liste_mesures']
        except:
            print 'Premiere execution : fichier statistiques inexistant'
    
    ##
    # Sauvegarde les mesures dans un fichier
    def saveData(self):
        # Sauvegarde la liste des mesures dans un fichier qui sera relu par python
        with open(self.nom_fichier_statistiques, 'w') as f:
            data = {}
            data['liste_mesures'] = self.liste_mesures
            data_string = pickle.dumps(data)
            f.write(data_string)
    
    ##
    # Ajoute une mesure dans la liste des mesures et l'enregistre dans un fichier csv 
    def enregistre_mesure(self, Tint, T_souhaitee_par_le_client, Tout, P_chauffage):
        mesure = {}
        mesure['Tint'] = Tint
        mesure['Tsouhaitee'] = T_souhaitee_par_le_client
        mesure['Tout'] = Tout
        mesure['P_chauffage'] = P_chauffage
        self.liste_mesures.append(mesure)
        # Sauvegarde la mesure dans un fichier csv
        with open(self.nom_fichier_csv_statistiques, 'a') as f:
            # Remplace les points par des virgules (pour Excel version française)
            Tint_str = str(Tint).replace(".",",")
            Tsouhaitee_str = str(T_souhaitee_par_le_client).replace(".",",")
            Tout_str = str(Tout).replace(".",",")
            P_chauffage_str = str(P_chauffage).replace(".",",")
            ligne = Tint_str + ";" + Tsouhaitee_str + ";" + Tout_str + ";" + P_chauffage_str + "\n"
            f.write(ligne)
    
    ##
    # Calcule des stats globales
    def calcule_totaux(self):
        nb_mesures_total = 0
        nb_mesures_inconfort = 0
        total_Tint = 0
        for mesure in self.liste_mesures:
            nb_mesures_total += 1
            total_Tint += mesure['Tint']
            if (mesure['Tint'] < (mesure['Tsouhaitee'] - delta_T_inconfort)):
                nb_mesures_inconfort += 1
        print "Inconfort = ", nb_mesures_inconfort, "/", nb_mesures_total , "(", (nb_mesures_inconfort*100/nb_mesures_total), "%)"
        print "Tint moyenne = ", total_Tint/nb_mesures_total
        
    ##
    # Renvoie les mesures sous forme d'un tuple contenant des vecteurs (listes)
    # Utilisé par la classe Algo_predictif
    # @ return (Vecteur Tint, Vecteur Puissance, Vecteur Text)
    def get_vecteurs(self):
        # Initialise les vecteurs        
        V_Ti = []
        V_P = []
        V_Te = []
        # Parcourt les mesures
        for mesure in self.liste_mesures:
            # Ajoute la mesure en cours aux vecteurs
            V_Ti.append(mesure['Tint'])
            V_P.append(mesure['P_chauffage'])
            V_Te.append(mesure['Tout'])
        return (V_Ti, V_P, V_Te)