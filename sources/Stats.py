# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 13:17:42 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame

import os
import json

import SaveManager

def StatsTemplate()->dict:
    """
    Renvoie un dictionnaire de statistiques par défaut
    """
    return {
        "ExpeditionsSent":0,
        "MinedM1":0,
        "MinedCopper":0,
        "DestroyedEnnemies":0,
        "EventsOccured":0,
        "ObjectsDestroyed":0,
        "ObjectsPlaced":0
    }

current = StatsTemplate()

def Load():
    """
    Chargement des statistiques
    """
    
    if not SaveManager.SaveLoaded():
        return
    
    path = "./Saves/" + SaveManager.saveName + "/stats.json"
    
    if os.path.isfile(path):
        with open(path, "r") as f:
            global current
            current = json.load(f)

def Save():
    """
    Sauvegarde des statistiques
    """
    
    if not SaveManager.SaveLoaded():
        return
    
    with open("./Saves/" + SaveManager.saveName + "/stats.json", "w") as f:
        f.write(json.dumps(current, default=str, indent = 4))

#Évenement lorsqu'une statistique est modifiée
STATS_CHANGED = pygame.USEREVENT + 1

def IncreaseStat(statName:str,increment:float=1):
    """
    Modifie une statistique
    """
    #Si cette statistique n'existe pas dans la liste des statistiques, on l'initialise à 0
    if not statName in current:
        current[statName] = 0
    
    #On envoie un évenement avec toutes les données du changement
    pygame.event.post(pygame.event.Event(STATS_CHANGED, changeData={"stat":statName, "oldVal":current[statName],"newVal":current[statName]+increment,"increment":increment}))
    
    #On incrémente la statistique
    current[statName] += increment
