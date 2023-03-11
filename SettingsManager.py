# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 17:51:59 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import json

SettingsChanged = False

def DefaultSettingsInstance():
    """
    Instance par défaut des paramètres.
    """
    return {
        "musicVolume": 70,
        "keybinds": {
            "up": pygame.K_z,
            "down": pygame.K_s,
            "left": pygame.K_q,
            "right": pygame.K_d,
            "rotate": pygame.K_r
        }
    }

__mainSettings = DefaultSettingsInstance()

def GetSetting(name:str):
    """
    Permet de récupérer un paramètre avec son nom.
    Si le paramètre n'est pas trouvé, la fonction renvoie None
    Le fait que la fonction renvoie None peut aussi signifier que le paramètre est réglé sur None
    """
    return __mainSettings.get(name, None)

def SetSetting(name:str, value):
    """
    Permet de régler un paramètre avec son nom et sa valeur.
    Il n'est pas enregistré dans le disque dur, seulement dans la mémoire du jeu
    L'application des paramètres peut s'avérer nécessaire
    """
    __mainSettings[name] = value
    global SettingsChanged
    SettingsChanged = True

def GetKeybind(name:str):
    """
    Permet de récupérer l'identifiant d'une touche avec son nom
    Si la touche n'est pas trouvée, la fonction renvoie None
    Le fait que la fonction renvoie None peut aussi signifier que la touche est simplement désactivée par l'utilisateur
    """
    return __mainSettings["keybinds"].get(name, None)

def SetKeybind(name:str, value):
    """
    Permet de régler une touche avec son nom et son code.
    Elle n'est pas enregistrée dans le disque dur, seulement dans la mémoire du jeu
    L'application des paramètres peut s'avérer nécessaire
    """
    __mainSettings["keybinds"][name] = value
    global SettingsChanged
    SettingsChanged = True

def LoadSettings():
    """
    Charge les paramètres depuis le disque dur et les applique sur le jeu
    """
    global __mainSettings
    
    try:
        __mainSettings = json.load(open("Settings.json", "r"))
        EnsureSettingsValidity()
        ApplySettings()
    except:
        ResetSettings()
    global SettingsChanged
    SettingsChanged = False

def SaveSettings():
    """
    Sauvegarde les paramètres dans le disque dur et les applique au jeu
    """
    open("Settings.json", "w").write(json.dumps(__mainSettings, default=lambda o: o.__dict__, indent = 4))
    global SettingsChanged
    SettingsChanged = False
    ApplySettings()

def ResetSettings():
    """
    Remet les paramètres à leur valeur de départ, les sauvegarde et les applique au jeu
    """
    global __mainSettings
    __mainSettings = DefaultSettingsInstance()
    SaveSettings()
    
def EnsureSettingsValidity():
    """
    Exécuter cette fonction lors du chargement des paramètres permet d'assurer la validité des paramètres en ajoutant les entrées manquantes
    """
    defaultInstance = DefaultSettingsInstance()
    for option in defaultInstance:
        if not option in __mainSettings:
            __mainSettings[option] = defaultInstance[option]
    
    for keyBind in defaultInstance["keybinds"]:
        if not keyBind in __mainSettings["keybinds"]:
            __mainSettings["keybinds"][keyBind] = defaultInstance["keybinds"][keyBind]
    
def ApplySettings():
    """
    Applique les paramètres au jeu
    """
    pygame.mixer.music.set_volume(GetSetting("musicVolume")/100)