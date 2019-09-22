# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 18:30:13 2014

@author: perez
"""

from scipy.optimize import leastsq
from pylab import *

class Algo_predictif:
    """ Algorithme prédictif. Calcule une fonction d'estimation du comportement futur du bâtiment. """
    
    ##
    # Constructeur
    # @param statistiques Objet de type Statistiques, contenant les mesures
    def __init__(self, statistiques):
        self.statistiques = statistiques
        self.plsq = None    # Coefficients optimaux pour l'estimateur de Tint. Initialisé par la méthode calcule_coefficients_p
    
    ##
    # Calcule l'écart entre la mesure (Ti_k) et l'estimation de Ti à l'instant k
    # @param p Tuple contenant les paramètres (coefficients à déterminer pour l'estimateur)
    # @param Ti_k Tempé intérieure à l'instant k
    # @param Ti_k1 Tempé intérieure à l'instant k-1
    # @param Ti_k2 Tempé intérieure à l'instant k-2
    # @param P_k Puissance de chauffage à l'instant k
    # @param P_k1 Puissance de chauffage à l'instant k-1
    # @param Te_k1 Température extérieure à l'instant k-1
    # @param Te_k2 Température extérieure à l'instant k-2
    def residuals(self, p, Ti_k, Ti_k1, Ti_k2, P_k, P_k1, Te_k1, Te_k2):
        return (Ti_k - self.estimateur (p, Ti_k1, Ti_k2, P_k, P_k1, Te_k1, Te_k2))
    
    ##
    # Estimateur de la température à l'instant k
    def estimateur(self, p, Ti_k1, Ti_k2, P_k, P_k1, Te_k1, Te_k2):
        # Récupère les coefficients dans le tuple p
        (a, b, c, d, e, f) = p
        
        # Calcule et renvoie la fonction d'estimation
        return (a * Ti_k1) + (b * Ti_k2) + (c * P_k) + (d * P_k1) + (e* Te_k1) + (f * Te_k2)
              
    ##
    # Estimateur récursif renvoyant une liste contenant les températures prévues Tint pendant les n pas suivants
    # tenant compte d'une puissance injectée Vecteur_P_futurs = [P_0, P_1, ..., P_n-1]
    # et d'une météo Vecteur_Te_futurs = [Te_0, Te_1, ..., Te_n-1]
    def estim_Tint_futurs(self, Ti_k1, Ti_k2, P_k1, Te_k1, Te_k2, Vecteur_P_futurs, Vecteur_Te_futurs):
        # Si est arrivé au bout de la récurrence
        if (len(Vecteur_P_futurs) == 0):
            # Retourne une liste vide
            return []
        else:
            # Récupère le premier élément des vecteurs puissance et température extérieure et le supprime
            P_k = Vecteur_P_futurs.pop(0)
            Te_k = Vecteur_Te_futurs.pop(0)
            # Calcule la température intérieure estimée pour le pas actuel de la récurrence
            Tint_k = self.estimateur(self.plsq, Ti_k1, Ti_k2, P_k, P_k1, Te_k1, Te_k2)
            # Lance la récurrence pour le pas suivant
            Vecteur_Tint_futurs = self.estim_Tint_futurs(Tint_k, Ti_k1, P_k, Te_k, Te_k1, Vecteur_P_futurs, Vecteur_Te_futurs)
            # Renvoie le résultat
            return [Tint_k] + Vecteur_Tint_futurs
        
    def calcule_coefficients_p(self):
        # Coefficients initiaux pour l'optimisation
        p0 = (0,0,0,0,0,0)
                
        # Récupère les vecteurs contenant les données de mesures
        (V_Ti, V_P, V_Te) = self.statistiques.get_vecteurs()
        
        # Vérifie s'il y a suffisamment de données
        if len(V_Ti) > 50:
            # Décale les vecteurs dans le temps

            V_Ti_k = list(V_Ti)         # Crée une copie de la liste
            del V_Ti_k[0]               # Supprime le premier élément de la liste
            del V_Ti_k[0]            
            V_Ti_k = np.array(V_Ti_k)   # Convertit en numpy.array            
            
            V_Ti_k1 = list(V_Ti)
            del V_Ti_k1[-1]             # Supprime le dernier élément de la liste
            del V_Ti_k1[0]
            V_Ti_k1 = np.array(V_Ti_k1)

            V_Ti_k2 = list(V_Ti)
            del V_Ti_k2[-1]
            del V_Ti_k2[-1]
            V_Ti_k2 = np.array(V_Ti_k2)

            V_P_k = list(V_P)
            del V_P_k[0]
            del V_P_k[0]
            V_P_k = np.array(V_P_k)

            V_P_k1 = list(V_P)
            del V_P_k1[0]
            del V_P_k1[-1]
            V_P_k1 = np.array(V_P_k1)
            
            V_Te_k1 = list(V_Te)
            del V_Te_k1[-1]
            del V_Te_k1[0]
            V_Te_k1 = np.array(V_Te_k1)

            V_Te_k2 = list(V_Te)
            del V_Te_k2[-1]
            del V_Te_k2[-1]
            V_Te_k2 = np.array(V_Te_k2)
            
            # Met les données dans un tuple
            donnees = (V_Ti_k, V_Ti_k1, V_Ti_k2, V_P_k, V_P_k1, V_Te_k1, V_Te_k2)
            
            # Calcule les coefficients optimisés par la méthode des moindres carrés
            result_coeff_leastsq = leastsq(self.residuals, p0, args = donnees)
            
            # Stocke le résultat
            self.plsq = result_coeff_leastsq[0]
            
            # Renvoie le résultat
            return self.plsq
            
        else:
            # S'il n'y a pas suffisamment de données pour faire le calcul
            # Retourne une valeur par défaut            
            return p0
            
##
# TEST de l'estimation de la fonction de prédiction

#from statistiques import *
#
#stats = Statistiques()
#algo_predictif = Algo_predictif(stats)
#print algo_predictif.calcule_coefficients_p()
#print algo_predictif.estim_Tint_futurs(20, 20, 0, 2, 2, [0, 0, 0, 0, 0, 0, 3000, 3000, 3000], [2,2,2,2,2,2,2,2,2])