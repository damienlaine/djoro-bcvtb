# -*- coding: utf-8 -*-
"""
Created on Sun Jul 20 09:01:51 2014

@author: perez
"""

from pylab import *

# Coefficient d'apprentissage (plus il est élevé, plus le système apprend vite, mais plus il est nerveux et instable)
coeffApprentissage = 0.5
# Ecart de température entre Tint et Tconsigne à partir duquel on va faire l'apprentissage du temps de relance
relanceDeltaTint = 2.0


class FuzzyMethodes:
    """ Méthodes de calcul de logique floue """
    
    ##
    # Renvoie un vecteur indiquant quelle est l'appartenance en logique floue de l'élément
    # Exemple : tableau = ([1., 2., 3., 4.])
    # si element = 2.25, renvoie ([0., 0.75, 0.25, 0.])
    # car 2.25 est compris entre 2 et 3 et plus proche de 2 que de 3
    # si element = 4., renvoie ([0., 0., 0., 1.])
    @staticmethod
    def fuzzyAppartenance1D(element, tableau):
        taille = size(tableau)    
        resultat=zeros(taille)
    
        if element < tableau[0]:
            resultat[0] = 1.    
            return resultat
            
        for i in range(taille-1):
            if (tableau[i] <= element and element <= tableau[i+1]):
                distance1 = element - tableau[i]
                distance2 = tableau[i+1] - element
                distance_total = distance1 + distance2
                resultat[i] = distance2 / distance_total
                resultat[i+1] = distance1 / distance_total
                return resultat
                
        # Si on est arrivé ici, c'est que element est supérieur au dernier élément du tableau
        resultat[taille-1] = 1.
        return resultat
    
    # Même fonction que fuzzyAppartenance, mais en 2D (tableau 1 = lignes, tableau2 = colonnes)
    @staticmethod    
    def fuzzyMatriceVerite(element1, tableau1, element2, tableau2):
        # Calcule la matrice de vérité de Ti et Te
        verite1 = FuzzyMethodes.fuzzyAppartenance1D(element1, tableau1)
        verite1.shape = (1, size(verite1))    # Transformation 1D->2D
        verite2 = FuzzyMethodes.fuzzyAppartenance1D(element2, tableau2)    
        verite2.shape = (1, size(verite2))    # Transformation 1D->2D
        veriteMatrice = dot(verite1.T, verite2)
        return veriteMatrice
    
    # Corrige la matriceRegles après le constat d'un écart entre la valeur estimée et la valeur réelle
    @staticmethod
    def fuzzyCorrection(matriceRegles, matriceVerite, valeurEstimee, valeurReelle, coeffApprentissage):
        erreur = valeurReelle - valeurEstimee
        matriceCorrection = coeffApprentissage * erreur * matriceVerite
        matriceRegles += matriceCorrection
        return matriceRegles
    
    ##
    # Estime le temps de relance
    @staticmethod
    def estimeTempsRelance(tInt, tExt, tCible, tempsRelanceMatrice, tIntSteps, tExtSteps):
        # Translate le problème en fonction de t_a_atteindre    
        tIntPrime = tInt - (tCible - 20)
        tExtPrime = tExt - (tCible - 20)
        veriteMatrice = FuzzyMethodes.fuzzyMatriceVerite(tIntPrime, tIntSteps, tExtPrime, tExtSteps)
        tempsRelanceEstime = sum(veriteMatrice * tempsRelanceMatrice)
        return tempsRelanceEstime
    	
    ##
    # Corrige la matrice des temps de relance après avoir mesuré le temps de relance réel
    # @param tIntInitial Tint utilisé lors de l'estimation du temps de relance
    # @param tExtInitial Text utilisé lors de l'estimation du temps de relance
    # @param tempsRelanceReel Temps de relance réel mesuré
    # @param coeffApprentissage Coefficient d'apprentissage
    # @return tempsRelanceMatrice Nouvelle matrice de temps de relance
    @staticmethod
    def corrigeMatrice(tIntInitial, tExtInitial, tCible, tempsRelanceReel, coeffApprentissage, tempsRelanceMatrice, tIntSteps, tExtSteps):
        # Translate le problème en fonction de t_a_atteindre    
        tIntPrime = tIntInitial - (tCible - 20)
        tExtPrime = tExtInitial - (tCible - 20)
        veriteMatrice = FuzzyMethodes.fuzzyMatriceVerite(tIntPrime, tIntSteps, tExtPrime, tExtSteps)
        tempsRelanceEstime = sum(veriteMatrice * tempsRelanceMatrice)
        tempsRelanceMatrice = FuzzyMethodes.fuzzyCorrection(tempsRelanceMatrice, veriteMatrice, tempsRelanceEstime, tempsRelanceReel, coeffApprentissage)
        return tempsRelanceMatrice
