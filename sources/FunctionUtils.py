# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 21:13:26 2023

@author: Thomas Sartre et François Patinec-Haxel
"""
import pygame
import pygame_menu

import math
import numpy as np

def clamp(val:float,minv:float,maxv:float)->float:
    """
    Bloque une valeur entre un minimum et un maximum
    """
    return max(min(val,maxv),minv)

def clamp01(val:float)->float:
    """
    Bloque une valeur entre 0 et 1
    """
    return clamp(val, 0, 1)

def lerp(a:float,b:float,t:float)->float:
    """
    Effectue une interpolation linéaire de a vers b par t
    """
    t = clamp01(t)
    return a * (1 - t) + (b * t)

def lerpcol(a:tuple,b:tuple,t:float)->tuple:
    """
    Effectue une interpolation linéaire d'un triple représentatif d'une couleur vers un autre par t
    """
    return (lerp(a[0],b[0],t),lerp(a[1],b[1],t),lerp(a[2],b[2],t))

def addcol(a:tuple,b:tuple)->tuple:
    """
    Additionne des triples représentatifs de couleurs RGB 0-1 en les gardant dans l'intervalle 0-1
    """
    return(clamp01(a[0] + b[0]), clamp01(a[1] + b[1]), clamp01(a[2] + b[2]))

def multiplycol(c:tuple,v:float)->tuple:
    """
    Multiplie un triple représentatif d'une couleur RGB 0-1 par un nombre en le gardant dans l'intervalle 0-1
    """
    return (clamp01(c[0] * v),clamp01(c[1] * v),clamp01(c[2] * v))

def ZeroOneToHexa(c:tuple)->tuple:
    """
    Convertit une couleurs RGB 0-1 en couleur 0-255
    """
    return (c[0] * 255, c[1] * 255, c[2] * 255)

def ReduceStr(message:str,lengthMax:int)->str:
    """
    S'assure qu'une chaine de caractères ne dépasse pas une certaine longueur, et si c'est le cas, retire la fin et ajoute trois points
    """
    return message[:lengthMax] + ("..." if len(message) > lengthMax else "")

def IsVowel(letter:str)->bool:
    """
    Permet de savoir si une lettre est une voyelle
    """
    return letter.lower() in "aeiouy"

def GetSign(n:float)->int:
    """
    renvoie le signe d'un nombre
    """
    if n > 0:
        return 1
    if n < 0:
        return -1
    return 0

def Distance(a:tuple,b:tuple):
    """
    Calcul de distance entre deux positions
    """
    if len(a) != 3 and len(b) != 3:
        return math.sqrt(((b[0]-a[0])**2) + ((b[1]-a[1])**2))
    
    return math.sqrt(((b[0]-a[0])**2) + ((b[1]-a[1])**2) + ((b[2]-a[2])**2))

def FirstLetterUpper(string:str):
    """
    similaire à str.capitalize(), mais sans mettre le reste des lettres en minuscule
    """
    if string == "" or string == None:
        return string
    return string[:1].upper() + string[1:]

def StretchSurfaceToSurface(target:pygame.Surface,source:pygame.Surface):
    source = pygame.transform.scale(source, target.get_size())
    target.blit(source, (0,0))

#Variables nécessaires pour le fonctionnement des boutons encapsulés
selectedFrame = None
mouseOverFB = False
hoveredFB = None
mouseOverButton = False
lastMousePressSequence = (0,0,0)

def EncapsulateButtonInFrame(button:pygame_menu.widgets.Button,frame:pygame_menu.widgets.Frame,onSelect=None, buttonAlign=pygame_menu.locals.ALIGN_CENTER):
    """
    Encapsule un bouton dans un cadre et permet de faire agir le cadre comme si il était un bouton
    """
    #Fonction temporaire permettant de noter si la souris se situe au dessus d'un bouton encapsulé
    def setMouseOver(btn, mouseOver:bool):
        global mouseOverFB, hoveredFB
        #On indique que la souris survole un bouton
        mouseOverFB = mouseOver
        #Si elle survole un bouton, on indique quel bouton est survolé
        if mouseOver:
            hoveredFB = btn
    
    #On retire l'effet de sélection du bouton
    button.set_selection_effect(None)
    
    #Si une fonction de sélection spéciale a été spécifiée, on la met sur le bouton sinon on utilise la fonction de sélection par défaut
    if onSelect != None:
        button.set_onselect(onSelect)
    else:
        button.set_onselect(lambda:setSelectedFrame(frame))
    
    #On met le bouton dans le cadre avec l'alignement spécifié et on ajoute la fonction de survol aux évenements de survol du cadre
    frame.pack(button,align=buttonAlign)
    frame.set_onmouseover(lambda:setMouseOver(button,True))
    frame.set_onmouseleave(lambda:setMouseOver(button,False))
    
def setSelectedFrame(f=None):
    """
    Fonction s'exécutant par défaut lors du survol d'un bouton encapsulé. A copier en cas de besoins spécifiques.
    """
    global selectedFrame
    #Si un cadre est sélectionné, on efface son effet de sélection
    if selectedFrame != None:
        selectedFrame.set_border(0, None)
    #Si un nouveau cadre est fourni, on lui met un effet de sélection
    if f != None:
        f.set_border(1,(255,255,255))
    #Le cadre en entrée devient le nouveau cadre sélectionné
    selectedFrame = f
    
def ManageEncapsulatedButtons():
    """
    Doit être appelé dans la boucle de mise à jour des menus comportant des boutons encapsulés
    """
    global mouseOverFB, hoveredFB, lastMousePressSequence, mouseOverButton
    
    #On récupère la séquence des boutons de souris pressés ou non
    pressSequence = pygame.mouse.get_pressed()
    
    #Si un cadre de bouton encapsulé est survolé...
    if hoveredFB != None:
        #Position de la souris
        mPos = pygame.mouse.get_pos()
        #On regarde si la souris est au dessus du bouton contenu
        mouseOverButton = hoveredFB.get_rect(to_real_position=True).collidepoint(mPos[0], mPos[1])
    
    #SI la souris est sur le cadre...
    if mouseOverFB:
        #Variables pour détecter le début d'un appui ou d'un relâchement d'un bouton de souris
        NewPress = False
        NewRelease = False
        #Pour chaque bouton de la souris...
        for i in range(3):
            #Si un clic est remarqué dans la séquence actuelle mais pas dans la séquence précédente, il a un nouveau clic
            if pressSequence[i] and not lastMousePressSequence[i]:
                NewPress = True
            #Si un clic est remarqué dans la séquence précédente mais pas dans la séquence actuelle, il a un nouveau relâchement
            if lastMousePressSequence[i] and not pressSequence[i]:
                NewRelease = True
        #Si il y a un nouveau clic, on sélectionne le bouton
        if NewPress:
            hoveredFB.select(update_menu=True)
        #Si il y a un nouveau relâchement et que la souris n'est pas sur le bouton du cadre, on enclenche le bouton
        if NewRelease and not mouseOverButton:
            hoveredFB.apply()
    
    #La séquence précédente devient la séquence actuelle
    lastMousePressSequence = pressSequence

def ToDict(o):
    """
    Transforme un objet en dictionnaire en prenant en compte l'existence d'une fonction pour remplacer __dict__
    """
    if callable(o.__dict__):
        return o.__dict__()
    return o.__dict__

def strToList(str:str):
    """
    Convertit un string en liste de caractère
    """
    return str.replace("[","").replace("(","").replace("]", "").replace(")","").split(",")

signe = lambda x: 1 if x >= 0 else -1#fonction renvoyant +1 ou -1 selon le signe d'un nombre

class NumpyDict:
    """
    Dictionnaire basé sur des listes numpy pour accélérer l'utilisation
    La clé doit être un entier, ou un str, les tuples peuvent causer problème
    """
    def __init__(self,sourceDict={}):
        self._keys = np.array(list(sourceDict.keys()), dtype=object)
        self._values = np.array(list(sourceDict.values()), dtype=object)

    def __getitem__(self, key):
        if key not in self._keys:
            raise KeyError(key)

        value_idx = np.argwhere(self._keys == key)
        if len(value_idx) == 0 or value_idx[0][0] >= len(self._values):
            raise KeyError(key)

        return self._values[value_idx[0][0]]


    def __setitem__(self, key, value):
        if key in self._keys:
            value_idx = np.argwhere(self._keys == key).flatten()[0]
            self._values[value_idx] = value
        else:
            self._keys = np.append(self._keys, key)
            self._values = np.append(self._values, value)

    def __delitem__(self, key):
        if key not in self._keys:
            raise KeyError(key)

        value_idx = np.argwhere(self._keys == key).flatten()[0]
        self._keys = np.delete(self._keys, value_idx)
        self._values = np.delete(self._values, value_idx)

    def __len__(self):
        return len(self._keys)

    def __contains__(self, key):
        return key in self._keys
    def __repr__(self):
        items = []
        for key, value in zip(self._keys, self._values):
            item = f"{key}: {value}"
            items.append(item)

        return "{" + ", ".join(items) + "}"
    
    def __dict__(self):
        s={}
        for key, value in zip(self._keys, self._values):
            s[key]=value
        return s

    def keys(self):
        return self._keys

    def values(self):
        return self._values
    
    def get(self,a,b=None):
        try:return self.__getitem__(a)
        except:return b
    
    def clear(self):
        self._keys = np.array([], dtype=object)
        self._values = np.array([], dtype=object)