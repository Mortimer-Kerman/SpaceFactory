# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 16:01:06 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

#Dictionnaire contenant toutes les traductions
__localizations = {}

def Init():
    """
    Charge toutes les traductions du fichier
    """
    try:
        #Ouverture du fichier
        with open("./Assets/localization.txt", "r", encoding="utf-8") as f:
            #Pour chaque ligne du fichier
            for LocKey in f.readlines():
                LocKey = LocKey[:-1]#retrait du dernier caractère, celui de retour à la ligne
                #Si la ligne n'est pas vide et qu'elle ne commence pas par // (un commentaire)...
                if len(LocKey) != 0 and not LocKey.startswith("//"):
                    #On coupe en deux au niveau du double point pour avoir d'un côté le code de la traduction et de l'autre la traduction
                    KeyPair = LocKey.split(' : ', 1)
                    #On la stocke dans le dictionnaire
                    __localizations[KeyPair[0]] = KeyPair[1]
    except:
        pass

def GetLoc(LocKey:str, *args):
    """
    Permet d'obtenir une traduction formatée à partir de son code. Les paramètres en entrée remplaceront %$n, avec n de 1 à 9 inclus suivant l'ordre des paramètres.
    """
    try:
        #On tente de récupérer la clé et on remplace %$r par des retours à la ligne
        loc = __localizations[LocKey].replace("%$r", "\n")
        
        #Pour chaque paramètre supplémentaire...
        for i in range(1,len(args)+1):
            #On tente de le placer dans la traduction aux bons indices
            loc = loc.replace("%$" + str(i), str(args[i - 1]))
        #Renvoi de la traduction formatée
        return loc
    except:
        #Si quelque chose se passe mal on renvoie simplement le code
        return LocKey
