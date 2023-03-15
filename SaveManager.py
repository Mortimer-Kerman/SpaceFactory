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
import TextureManager

SaveFileVersion="f0.9"

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
        self.selectedItem="foreuse"
        self.rotation=0
        self.saveVersion=SaveFileVersion
        
    def toJson(self):
        """
        renvoye toutes les Datas en JSON
        """
        return json.dumps(self, default=lambda o: o.__dict__, indent = 4)

clock = pygame.time.Clock()#horloge du jeu

saveName = None#nom de la sauvegarde
mainData = None#va bientôt contenir la classe Data principale
planetTex = None

def Load(name:str):
    """
    Sert au chargement des sauvegardes
    """
    global mainData
    CreateSave(name)#Création de la sauvegarde
    if SaveExists(name):#si la sauvegarde existe
        path = "Saves/" + saveName + "/"
        with open(path + "save.spf", "r") as f:
            mainData.__dict__ = json.load(f)#charger les Datas
        try:
            if mainData.saveVersion!=SaveFileVersion:
                print("\n#"*5+"format de sauvegarde incompatible, merci d'utiliser la version "+SaveFileVersion+5*"\n#")
                quit()
        except:
            print("\n#"*5+"format de sauvegarde incompatible, merci d'utiliser la version "+SaveFileVersion+5*"\n#")
            quit()
        for item in mainData.items.values():
            a=GameItems.Item.ReadDictRepresentation(item)
            mainData.items[str(list(a.pos))]=a
        global planetTex
        planetTex = None
        if os.path.isfile(path + "planet.png"):
            planetTex = pygame.image.load(path + "planet.png")
    global LastCamPos
    LastCamPos = mainData.camPos.copy()
    print("File loaded!")
    
def Save():
    """
    Sauvegarde
    """
    path = "Saves/" + saveName + "/"
    if not os.path.exists(path):#si le dossier de sauvegarde n'existe pas, le créer
        os.makedirs(path)
    with open(path + "save.spf", "w") as f:
        f.write(mainData.toJson())#écriture dans le fichier de sauvegarde
    if planetTex != None:
        pygame.image.save(planetTex, path + "planet.png")
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
    TextureManager.RefreshZoom()
    print("File unloaded")

def SaveExists(name:str):
    """
    Vérifie si la sauvegarde existe
    """
    path = "Saves/" + name + "/"
    return os.path.exists(path) and os.path.isfile(path + "save.spf")

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
    global LastCamPos
    LastCamPos = mainData.camPos.copy()
    mainData.camPos[0] += offset[0]
    mainData.camPos[1] += offset[1]
    
def GetCamPos():
    """
    Renvoie la position de la caméra
    """
    return mainData.camPos.copy()

def GetLastCamPos():
    """
    Renvoie la position précédente de la caméra
    """
    global LastCamPos
    return LastCamPos

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
    if IsItemHere(pos):
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

def GetRotation():
    """
    Renvoie la rotation actuelle
    """
    return mainData.rotation

def UpdateRotation():
    """
    Mets à jour la rotation
    """
    r=GetRotation()
    if r!=3:
        r+=1
    else:
        r=0
    mainData.rotation=r