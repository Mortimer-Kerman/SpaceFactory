# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 17:31:39 2023

@author: 29ray
"""
#chargement des bibliothèques
import pygame
import json
import random
import os

import GameItems

class Data:
    """
    La classe Data contient le déroulement de tout le jeu
    """
    def __init__(self):
        """
        définition des variables
        """
        self.camPos = [0,0]
        self.zoom = 100
        self.seed = random.randint(-(9**9),9**9)
        self.items = []
        self.selectedItem="drill"
        
    def toJson(self):
        """
        renvoye toutes les Datas en JSON
        """
        return json.dumps(self, default=lambda o: o.__dict__, indent = 4)

clock = pygame.time.Clock()#horloge du jeu

saveName = None#nom de la sauvegarde
mainData = None#va bientôt contenir la classe Data principale

def Load(name:str):
    """
    Sert au chargement des sauvegardes
    """
    global mainData
    CreateSave(name)#Création de la sauvegarde
    if SaveExists(name):#si la sauvegarde existe
        mainData.__dict__ = json.load(open("Saves/" + name + ".spf", "r"))#charger les Datas
        items = []
        for item in mainData.items:
            items.append(GameItems.Item.ReadDictRepresentation(item))#on charge la représentation des items en objet
        mainData.items = items
    print("File loaded!")
    
def Save():
    """
    Sauvegarde
    """
    open("Saves/" + saveName + ".spf", "w").write(mainData.toJson())#écriture dans le fichier de sauvegarde
    print("File saved!")

def CreateSave(name:str):
    """
    Création de la sauvegarde
    """
    global saveName
    global mainData
    saveName = name
    mainData = Data()

def Unload():
    """
    Déchargement de la sauvegarde
    """
    global saveName
    global mainData
    Save()
    saveName = None
    mainData = None
    print("File unloaded")

def SaveExists(name:str):
    """
    Vérifie si la sauvegarde existe
    """
    return os.path.exists("Saves/" + name + ".spf")

def SaveLoaded()->bool:
    """
    Renvoie True si une sauvegarde est chargée, False sinon
    """
    return (saveName is not None) and (mainData is not None)

if not os.path.exists("Saves/"):#si le dossier de sauvegarde n'existe pas, le créer
    os.makedirs("Saves/")

def TranslateCam(offset:list):
    """
    Changement de la position de la caméra
    """
    mainData.camPos[0] += offset[0]
    mainData.camPos[1] += offset[1]
    
def GetCamPos():
    """
    Renvoie la position de la caméra
    """
    return mainData.camPos

def GetZoom():
    """
    Renvoie le zoom
    """
    return mainData.zoom

def GetItems()->list:
    """
    Renvoie la liste d'item
    """
    return mainData.items

def PlaceItem(item):
    """
    Ajoute un item à la liste item
    """
    mainData.items.append(item)

def GetSeed()->int:
    """
    Renvoie la seed de la sauvegarde
    """
    return mainData.seed

def SetSelectedItem(item):
    """
    Change l'item séléctionné
    """
    mainData.selectedItem=item

def GetSelectedItem()->str:
    """
    Renvoie l'item séléctionné
    """
    return mainData.selectedItem