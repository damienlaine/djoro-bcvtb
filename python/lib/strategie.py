# -*- coding: utf-8 -*-
"""
Définit la stratégie de pilotage du thermostat
"""
from temps_relance import *
from api_bdd import *
from statistiques import *
from algo_predictif import *

from pylab import *

class Strategie_Chauffage:
    """ Contient les fonctions de calcul de la stratégie de chauffage à appliquer """
    def __init__(self):
        pass

    # Méthode appelée par bcvtb_link.py pour calculer la stratégie au pas de simulation actuel
    # Se base sur infos fictives
    @staticmethod    
    def calcule_consigne(tOut, tInt, heatPower):
        # Instancie les classes permettant d'accéder aux variables d'environnement, du client et de la météo
        environnement = API_Environnement()    
        client = API_Client(environnement)
        meteo = API_Meteo(tOut)        
        strategieObject = Strategie_Chauffage()

        # Instancie l'objet permettant de sauvegarder les statistiques, et charge le fichier de stats si on n'est pas au premier pas de simulation
        statistiques = Statistiques()
        
        strategie = strategieObject.calcul_strategie_chauffage(client, meteo, tInt, tOut, True)
        print "Strategie = ", strategie
        
        # Enregistre les données à des fins statistiques
        T_actuelle_souhaitee_par_client = client.schedule.get_schedule()[0][1]
        statistiques.enregistre_mesure(tInt, T_actuelle_souhaitee_par_client, tOut, heatPower)
        # Calcule et affiche les stats consolidées        
        statistiques.calcule_totaux()
    
        # Si la prochaine consigne doit être appliquée avant le prochain pas de simulation
        if (strategie[2] < pas_simulation):
            # Applique la prochaine température de consigne
            Tconsigne = strategie[1]
        else:
            # Applique la température de consigne actuelle
            Tconsigne = strategie[0]
        
        # Sauvegarde les paramètres du client
        client.etat_relance.saveData()
    
        # Incrémente l'heure et la sauvegarde
        environnement.incrementeHeure()
        environnement.saveEnvironnement()

        # Sauvegarde les statistiques
        statistiques.saveData()    

        # TEST du module prédictif
#        algo_predictif = Algo_predictif(statistiques)
#        p = algo_predictif.calcule_coefficients_p()
#        Estim_Ti_suivant_Puissance_nulle = algo_predictif.estimateur(p, )
#        print p
        
        return Tconsigne

    ##
    # Renvoie les prochaines consignes à appliquer pour le site
    @staticmethod
    def calcule_mambo_strategie(site_mambo_id, device_id):
        environnement = API_Mongo_Environnement()    
        client = API_Mongo_Client(site_mambo_id, device_id, environnement)
        meteo = API_Mongo_Meteo(site_mambo_id)        
        strategieObject = Strategie_Chauffage()

        # Instancie l'objet permettant de sauvegarder les statistiques, et charge le fichier de stats si on n'est pas au premier pas de simulation
#        statistiques = Statistiques()

        # Estime la température extérieure actuelle à partir de la prévision météo
        tOut = meteo.previ_meteo(0)

        # Récupère la température intérieure
        tInt = client.getTint()        
        
        strategie = strategieObject.calcul_strategie_chauffage(client, meteo, tInt, tOut, False)
        print "Strategie = ", strategie
        
        # Enregistre les données à des fins statistiques
#        T_actuelle_souhaitee_par_client = client.schedule.get_schedule()[0][1]
#        statistiques.enregistre_mesure(tInt, T_actuelle_souhaitee_par_client, tOut, heatPower)
        # Calcule et affiche les stats consolidées        
#        statistiques.calcule_totaux()
    
        # Si la prochaine consigne doit être appliquée avant le prochain pas de simulation
#        if (strategie[2] < pas_simulation):
            # Applique la prochaine température de consigne
#            Tconsigne = strategie[1]
#        else:
            # Applique la température de consigne actuelle
#            Tconsigne = strategie[0]
        
        # Sauvegarde les paramètres du client
        client.etat_relance.saveData()
    
        # Incrémente l'heure et la sauvegarde
#        environnement.incrementeHeure()
#        environnement.saveEnvironnement()

        # Sauvegarde les statistiques
#        statistiques.saveData()    

        return strategie


    ##
    # Fonction donnant la durée d'anticipation en minutes pour la baisse du chauffage
    # Ex: en cas de baisse du chauffage, anticipe la baisse de x minutes, pour prendre en compte l'inertie du bâtiment
    # @param Tint Température intérieure
    # @param Text Température extérieure
    # @return Durée d'anticipation en minutes
    def delai_anticipation_arret_chauffe(self, Tint, Text, T_a_atteindre):
        resultat = 0
        if (Tint > (T_a_atteindre - 1) ):
            if ((Tint - Text) < 10):
                resultat = 20
            else:
                resultat = 5
        return resultat
 		
    ##
    # Fonction principale de calcul de la stratégie de chauffage à appliquer
    # @param simulation True si on est en simulation BCVTB, False si on est en réel
    # @return [Tconsigne_actuelle, Tconsigne_prochaine, délai avant application de la prochaine consigne]
    def calcul_strategie_chauffage(self, client, meteo, Tint, Tout, simulation):
        
        # Récupère le schedule
        next_schedule = client.schedule.get_schedule()  
        
        # Définit la consigne à appliquer maintenant
        Tconsigne_actuelle = next_schedule[0][1]
    
        #
        # Calcule dans combien de minutes il faut faire la prochaine relance ou la prochaine baisse
        
        delai_prochaine_hausse = None
        Tconsigne_prochaine_hausse = None
        delai_prochaine_baisse = None
        Tconsigne_prochaine_baisse = None
            
        for elt in next_schedule:
            T_a_atteindre = elt[1]
            temps_disponible = elt[0]
            # Estime la température extérieure moyenne entre maintenant et le moment souhaité pour le changement de température
            Text_maintenant = meteo.previ_meteo(0)
            Text_a_terme = meteo.previ_meteo(temps_disponible)
            Text_moyen = (Text_maintenant + Text_a_terme) / 2		
    
            # S'il est demandé une hausse de température de consigne
            if (T_a_atteindre > Tconsigne_actuelle):
                # estime le temps de relance
                temps_pour_atteindre = FuzzyMethodes.estimeTempsRelance(Tint, Text_moyen, T_a_atteindre, client.etat_relance.tempsRelanceMatrice, client.etat_relance.tIntSteps, client.etat_relance.tExtSteps)
                relance_dans_x_min = temps_disponible - temps_pour_atteindre
                # vérifie s'il s'agit de la prochaine relance à réaliser, si oui la mémorise
                if ( (delai_prochaine_hausse == None) or (relance_dans_x_min < delai_prochaine_hausse)):
                    delai_prochaine_hausse = relance_dans_x_min
                    Tconsigne_prochaine_hausse = T_a_atteindre
            # S'il est demandé une baisse de température de consigne
            elif (T_a_atteindre < Tconsigne_actuelle):
                # estime le temps d'anticipation de la baisse de consigne
                temps_anticipation = self.delai_anticipation_arret_chauffe(Tint, Text_moyen, T_a_atteindre)
                baisse_dans_x_min = temps_disponible - temps_anticipation
                # vérifie s'il s'agit de la prochaine baisse à réaliser, si oui la mémorise
                if ( (delai_prochaine_baisse == None) or (baisse_dans_x_min < delai_prochaine_baisse)):
                    delai_prochaine_baisse = baisse_dans_x_min
                    Tconsigne_prochaine_baisse = T_a_atteindre
        
        # Si les valeurs sont négatives, met à zéro
        if (delai_prochaine_hausse != None):    
            delai_prochaine_hausse = max(delai_prochaine_hausse, 0)
        if (delai_prochaine_baisse != None):    
            delai_prochaine_baisse = max(delai_prochaine_baisse, 0)
    
        # Vérifie si la prochaine action à effectuer est une hausse ou une baisse et définit la consigne
        if ( ((delai_prochaine_baisse != None and delai_prochaine_hausse != None) and (delai_prochaine_hausse > delai_prochaine_baisse) ) or (delai_prochaine_baisse != None and delai_prochaine_hausse == None)) :
            delai_avant_application = delai_prochaine_baisse
            Tconsigne_prochaine = Tconsigne_prochaine_baisse
        else:
            delai_avant_application = delai_prochaine_hausse
            Tconsigne_prochaine = Tconsigne_prochaine_hausse
    
        # Si on n'a pas trouvé de stratégie future, applique simplement le prochain changement de consigne demandé par le calendrier de l'utilisateur
    #    if (delai_avant_application == None):
    #        if (len(next_schedule) > 1):
    #            delai_avant_application = next_schedule[1][0]
    #            Tconsigne_prochaine = next_schedule[1][1]
        # Envoie les valeurs nécessaires à l'apprentissage du temps de relance
        client.etat_relance.apprentissage_temps_relance(Tint, Tout, Tconsigne_actuelle, Tconsigne_prochaine, delai_avant_application)
        # Renvoie le résultat (stratégie de chauffage à appliquer)
        return [Tconsigne_actuelle, Tconsigne_prochaine, delai_avant_application]

# Test
# print Strategie_Chauffage.calcule_consigne(20,20)

# Routine principale
#while(1):
#    loadVariablesGlobales()   # Charge les variables globales pour le calcul du temps de relance
#    tInt = input ("Temp int (q pour faire planter et quitter) : ")
#    resultat = calcul_strategie_chauffage(init_api_next_schedule, init_api_next_meteo, tInt)
#    print "Résultat : ", resultat
#    incrementeHeure()
#    saveVariablesGlobales()   # Enregistre les variables globales pour le calcul du temps de relance
