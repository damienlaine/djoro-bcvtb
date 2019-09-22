# -*- coding: utf-8 -*-
"""
Classe contenant l'état de la relance
"""
from fuzzy_methodes import *
import cPickle as pickle

# Ecart de température entre Tint et Tconsigne à partir duquel on considère que la relance est terminée
finRelanceDeltaTint = 1.0
# Text en-dessous duquel on va faire l'apprentissage du temps de relance (au-dessus, on n'est pas sûr que le chauffage est effectivement allumé)
relanceText = 14.0

tInt = 5.
tExt = 20.
tempsRelanceReel = 120.

# "graduations" de la matrice des temps de relance
tIntSteps = array([ 5., 12., 17., 20.])
tExtSteps = array([ -15., -5., 5., 20.])

##
# matrice des temps de relance initiale
# données en minutes
# lignes = tInt (voir tIntSteps pour les "graduations")
# colonnes = tExt (voir tExtSteps pour les "graduations")
init_tempsRelanceMatrice = [[480, 480, 360, 240],
                             [360, 340, 240, 180],
                             [150, 120, 90, 70],
                             [0, 0, 0, 0]]
                             
##
# Nom du fichier de sauvegarde des données client relatives à l'algorithme du temps de relance
nom_fichier_etat_relance = "variablesRelance.txt"

class API_Etat_Relance:
    """ Contient les variables et méthodes nécessaires à l'algorithme du temps de relance """

    def __init__(self, pas_simulation, environnement):
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
        self.loadData() # Charge les données depuis le fichier s'il existe
        
    def loadData(self):  
        """ Charge les données depuis le fichier """
        try:
            with open(self.nom_fichier_etat_relance, 'r') as f:
                data = pickle.load(f)
                self.relance_en_cours = data['relance_en_cours']
                self.Tconsigne_relance = data['Tconsigne_relance']
                self.heure_debut_relance = data['heure_debut_relance']
                self.Tint_initial_relance = data['Tint_initial_relance']
                self.Text_initial_relance = data['Text_initial_relance']
                self.tempsRelanceMatrice = data['tempsRelanceMatrice']
        except:
            print "Premiere execution - fichier inexistant :", self.nom_fichier_etat_relance

    def saveData(self):
        """ Sauve les données dans le fichier """
        data = {}
        data['relance_en_cours'] = self.relance_en_cours
        data['Tconsigne_relance'] = self.Tconsigne_relance
        data['heure_debut_relance'] = self.heure_debut_relance
        data['Tint_initial_relance'] = self.Tint_initial_relance
        data['Text_initial_relance'] = self.Text_initial_relance
        data['tempsRelanceMatrice'] = self.tempsRelanceMatrice
        with open(self.nom_fichier_etat_relance, 'w') as f:
            data_string = pickle.dumps(data)
            f.write(data_string)

    ##
    # Fonction appelée par le gestionnaire de stratégie, permettant de connaître les paramètres
    # nécessaires à l'apprentissage du temps de relance
    # @param Tint Température intérieure actuelle
    # @param Text Température extérieure actuelle
    # @param Tconsigne_prochaine Prochaine température de consigne
    # @param delai_avant_application Temps en minutes avant application de la prochaine Tconsigne    
    def apprentissage_temps_relance(self, Tint, Text, Tconsigne_actuelle, Tconsigne_prochaine, delai_avant_application):
    
        # Détermine la température de consigne à appliquer maintenant
        if (delai_avant_application < self.pas_simulation):
            Tconsigne = Tconsigne_prochaine
        else:
            Tconsigne = Tconsigne_actuelle
    
        print "Relance en cours: ", self.relance_en_cours
    
        # S'il y a déjà une relance en cours
        if self.relance_en_cours:
            # Vérifie si la relance n'a pas été interrompue
            if (Tconsigne >= self.Tconsigne_relance):       # TODO Il y a un problème à résoudre ici : si la relance est lancée trop tôt, alors au moment où la température intérieure remonte, on se retrouve avec Tconsigne = Tconsigne antérieure, et donc cela génère une interruption de la relance alors qu'il ne faudrait pas.
                # Vérifie si la relance est terminée
                if (Tint > self.Tconsigne_relance - finRelanceDeltaTint):
                    # Arrête la relance
                    self.relance_en_cours = False
                    # Calcule le temps de relance réel
                    tempsRelanceReel = self.environnement.diffEnMinutes(self.environnement.getHeure(), self.heure_debut_relance)
                    # Lance la modification de la matrice de relance
                    self.tempsRelanceMatrice = FuzzyMethodes.corrigeMatrice(self.Tint_initial_relance, self.Text_initial_relance, self.Tconsigne_relance, tempsRelanceReel, coeffApprentissage, self.tempsRelanceMatrice, self.tIntSteps, self.tExtSteps)
                    print "Fin de la relance."
                    print "Temps de relance mesuré :", tempsRelanceReel
                    print "Text_initial:", self.Text_initial_relance
                    print "Tint_initial:", self.Tint_initial_relance
                    print "Tint final: ", Tint
                    print "Matrice temps relance : ", self.tempsRelanceMatrice
                    print "Heure: ", self.environnement.getHeure() % 1440
            else:
                # Interruption de la relance
                self.relance_en_cours = False
                print "Interruption de la relance"
                print "Tconsigne: ", Tconsigne, "Tconsigne_relance:", self.Tconsigne_relance
        else:
            # S'il n'y a pas de relance en cours            
            # Vérifie s'il faut lancer une relance
            if (Tconsigne > Tint + relanceDeltaTint):
                # Crée une nouvelle relance (mémorise les paramètres de la relance)
                self.relance_en_cours = True
                self.Tconsigne_relance = Tconsigne
                self.heure_debut_relance = self.environnement.getHeure()
                self.Tint_initial_relance = Tint
                self.Text_initial_relance = Text            
                print "Debut de relance. Tconsigne_relance:", self.Tconsigne_relance

