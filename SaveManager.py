# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 17:31:39 2023

@author: Thomas Sartre et François Patinec-Haxel
"""
#chargement des bibliothèques
import pygame
import json
import random
import os

import GameItems

SaveFileVersion="f0.7"

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
        self.items = {}
        self.selectedItem="drill"
        self.saveVersion=SaveFileVersion
        
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
        try:
            if mainData.saveVersion!=SaveFileVersion:
                print("\n#"*5+"format de sauvegarde incompatible, merci d'utiliser la version "+SaveFileVersion+5*"\n#")
                return
        except:
            print("\n#"*5+"format de sauvegarde incompatible, merci d'utiliser la version "+SaveFileVersion+5*"\n#")
            return
        for item in mainData.items.values():
            a=GameItems.Item.ReadDictRepresentation(item)
            mainData.items[str(list(a.pos))]=a
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
    return mainData.items.values()

def PlaceItem(item):
    """
    Ajoute un item aux items
    """
    mainData.items[str(list(item.pos))]=item

def DeleteItem(pos):
    del mainData.items[str(list(pos))]

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

def IsItemHere(pos)->bool:
    """
    Détecte si il y a un item à une position
    """
    return GetItemAtPos(pos) != None

def GetItemAtPos(pos):
    """
    Renvoie l'item à une position si il y en a un, None sinon
    """
    return mainData.items.get(str(list(pos)),None)
