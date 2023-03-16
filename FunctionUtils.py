# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 21:13:26 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

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