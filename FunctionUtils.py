# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 21:13:26 2023

@author: Thomas Sartre et François Patinec-Haxel
"""
import pygame
import pygame_menu

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

def StretchSurfaceToSurface(target:pygame.Surface,source:pygame.Surface):
    source = pygame.transform.scale(source, target.get_size())
    target.blit(source, (0,0))

selectedFrame = None
mouseOverFB = False
hoveredFB = None
lastMousePressSequence = (0,0,0)
def EncapsulateButtonInFrame(button:pygame_menu.widgets.Button,frame:pygame_menu.widgets.Frame,onSelect=None, buttonAlign=pygame_menu.locals.ALIGN_CENTER):
    """
    Encapsule un bouton dans un cadre et permet de faire agir le cadre comme si il était un bouton
    """
    
    def setMouseOver(btn, mouseOver:bool):
        global mouseOverFB, hoveredFB
        mouseOverFB = mouseOver
        if mouseOver:
            hoveredFB = btn
    
    button.set_selection_effect(None)
    
    if onSelect != None:
        button.set_onselect(onSelect)
    else:
        button.set_onselect(lambda:setSelectedFrame(frame))
    
    frame.pack(button,align=buttonAlign)
    frame.set_onmouseover(lambda:setMouseOver(button,True))
    frame.set_onmouseleave(lambda:setMouseOver(button,False))
    
def setSelectedFrame(f=None):
    global selectedFrame
    if selectedFrame != None:
        selectedFrame.set_border(0, None)
    if f != None:
        f.set_border(1,(255,255,255))
    selectedFrame = f
    
def ManageEncapsulatedButtons():
    """
    Doit être appelé dans la boucle de mise à jour des menus comportant des boutons encapsulés
    """
    global mouseOverFB, hoveredFB, lastMousePressSequence
    
    pressSequence = pygame.mouse.get_pressed()
    
    if mouseOverFB:
        
        NewPress = False
        NewRelease = False
        for i in range(3):
            if pressSequence[i] and not lastMousePressSequence[i]:
                NewPress = True
            if lastMousePressSequence[i] and not pressSequence[i]:
                NewRelease = True
        
        if NewPress:
            hoveredFB.select(update_menu=True)
        if NewRelease:
            hoveredFB.apply()
        
    lastMousePressSequence = pressSequence

class NumpyDict:
    """
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