# -*- coding: utf-8 -*-
"""
Réalise le lien entre BCVTB et le programme de définition de la stratégie de chauffe
Appelé à chaque pas de simulation en ligne de commande par BCVTB, avec comme paramètres Tout et Tint
"""
import sys
from lib.strategie import *

# Check the number of arguments
if (len(sys.argv) != 4):
	print("Erreur: le programme prend 3 arguments: Tout Tint HeatPower")
	exit(1)
	
# Récupère les paramètres de la ligne de commande
Tout = float(sys.argv[1])
Tint = float(sys.argv[2])
heatPower = float(sys.argv[3])

print "HeatPower = ", heatPower

# Met la clim à 26 (pas de stratégie de pilotage de la clim pour l'instant)
tc = 26

th = Strategie_Chauffage.calcule_consigne(Tout, Tint, heatPower)

print "th=", th, " tc=", tc, "Tint=", Tint, "Tout=", Tout


# Ecrit le resultat dans le fichier de sortie TH (Tconsigne chauffage)
Fichier = open('output_TH.txt','w')
chaine = ''.join([str(th), '\n'])
Fichier.write(chaine)
Fichier.close()

# Ecrit le resultat dans le fichier de sortie TC (Tconsigne clim)
Fichier = open('output_TC.txt','w')
chaine = ''.join([str(tc), '\n'])
Fichier.write(chaine)
Fichier.close()

exit(0)