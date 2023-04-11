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
from datetime import datetime

import GameItems
import TextureManager
import UiManager
import PlanetGenerator
import OpportunitiesManager
import Localization as L
import FunctionUtils

SaveFileVersion="f0.15"

difficultiesDict = {0: 'Saves.Difficulty.Easy',
                    1: 'Saves.Difficulty.Normal',
                    2: 'Saves.Difficulty.Hard'}
environmentsDict = {0: 'Saves.Environment.Random',
                    1: 'Saves.Environment.Lunar',
                    2: 'Saves.Environment.Desertic',
                    3: 'Saves.Environment.Lifefull'}
gameModesDict = {0: 'Saves.Gamemode.Career',
                 1: 'Saves.Gamemode.Sandbox',
                 2: 'Saves.Gamemode.Tutorial'}

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
        self.planetaryConditions = PlanetGenerator.PlanetaryConditions(seed=self.seed)
        self.items = FunctionUtils.NumpyDict()
        self.coins=0
        self.selectedItem="foreuse"
        self.rotation=0
        self.saveVersion=SaveFileVersion
        self.inv=[]
        self.gamemode=0
        self.difficulty=1
        self.opportunities=[]
        
    def toJson(self):
        """
        renvoye toutes les Datas en JSON
        """
        return json.dumps(self, default=lambda o: o.__dict__, indent = 4)

clock = pygame.time.Clock()#horloge du jeu

saveName = None#nom de la sauvegarde
mainData = None#va bientôt contenir la classe Data principale
planetTex = None

def Load(name:str)->bool:
    """
    Sert au chargement des sauvegardes
    """
    global force
    force = False
    def ForceLoad():
        global force
        force = True
    
    global mainData
    CreateSave(name)#Création de la sauvegarde
    if SaveExists(name):#si la sauvegarde existe
        path = "Saves/" + saveName + "/"
        with open(path + "save.spf", "r") as f:
            mainData.__dict__ = json.load(f)#charger les Datas
        try:
            if mainData.saveVersion!=SaveFileVersion:
                UiManager.WarnUser(L.GetLoc('Game.Warning'), L.GetLoc('Saves.IncompatibilityMessage'),ForceLoad,None)
                if not force:
                    print("\n#"*5+"format de sauvegarde incompatible, merci d'utiliser la version "+SaveFileVersion+5*"\n#")
                    return False
        except:
            UiManager.WarnUser(L.GetLoc('Game.Warning'), L.GetLoc('Saves.IncompatibilityMessage'),ForceLoad,None)
            if not force:
                print("\n#"*5+"format de sauvegarde incompatible, merci d'utiliser la version "+SaveFileVersion+5*"\n#")
                return False
        for item in mainData.items.values():
            a=GameItems.Item.ReadDictRepresentation(item)
            mainData.items[str(list(a.pos))]=a
        global planetTex
        planetTex = None
        if os.path.isfile(path + "planet.png"):
            planetTex = pygame.image.load(path + "planet.png")
    global LastCamPos
    LastCamPos = mainData.camPos.copy()
    
    if type(mainData.planetaryConditions) == dict:
        conditions = PlanetGenerator.PlanetaryConditions(template=True)
        conditions.__dict__ = mainData.planetaryConditions
        mainData.planetaryConditions = conditions
    
    for i in range(len(mainData.opportunities)):
        opportunity = OpportunitiesManager.Opportunity()
        opportunity.__dict__ = mainData.opportunities[i]
        mainData.opportunities[i] = opportunity
    
    if type(mainData.items) == dict:
        mainData.items = FunctionUtils.NumpyDict(mainData.items)
    
    print("File loaded!")
    return True

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
    
    with open(path + "meta.json", "w") as f:
        metaData = {
            "lastPlayed":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "difficulty":mainData.difficulty,
            "environment":mainData.planetaryConditions.type,
            "gameMode":mainData.gamemode
        }
        f.write(json.dumps(metaData, default=str, indent = 4))
    
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
    UiManager.UIPopup.clear()
    GameItems.Minerais.Clear()
    UiManager.chunkTex.clear()
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

def TranslateCam(offset:list):
    """
    Déplace la caméra
    """
    SetCamPos([mainData.camPos[0] + offset[0], mainData.camPos[1] + offset[1]])
    
def SetCamPos(pos:list):
    """
    Définit la position de la caméra
    """
    global LastCamPos
    LastCamPos = mainData.camPos.copy()
    mainData.camPos[0] = round(pos[0])
    mainData.camPos[1] = round(pos[1])
    
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
    Ajoute un item aux items en retirant le coût en minerais
    """
    if mainData.gamemode!=1:
        tempInv=[]
        for i in mainData.inv:
            tempInv.append(dict(i))
        a=[True]
        for i,n in GameItems.doc.get(item.name,{"c":{}}).get("c",{}).items():
            for j in range(n):
                a+=[GetFromInv(i)]
        if all(a):
            mainData.items[str(list(item.pos))]=item
            return True
        mainData.inv=tempInv
        UiManager.Popup(L.GetLoc("SaveManager.GetFromInv.error"))
        return False
    else:
        mainData.items[str(list(item.pos))]=item
        return True

def DeleteItem(pos):
    if IsItemHere(pos):
        del mainData.items[str(list(pos))]

def GetSeed()->int:
    """
    Renvoie la seed de la sauvegarde
    """
    return mainData.seed

def GetEnvironmentType()->int:
    """
    Renvoie le type d'environment de la planète
    """
    return mainData.planetaryConditions.type

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

def GetTextureAtPos(pos:tuple)->str:
    """
    Renvoie la texture d'un chunk à une certaine position
    """
    return UiManager.GetChunkTextureAtChunkPos((pos[0]//10,pos[1]//10))

def IsPosWet(pos:tuple)->bool:
    """
    Dit si une position est dans un point d'eau ou proche de celui-ci
    """
    return GetTextureAtPos(pos) == "water"

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
def ClearInv():
    mainData.inv=[]
def IsInInv(a,p=0):
    for i,e in enumerate(mainData.inv):
        if e.get("n",False)==a:
            if e["m"]+1<100 or p:
                return i
    return "NotIn"

def AddToInv(d):
    a=IsInInv(d)
    if a!="NotIn":
        mainData.inv[a]["m"]+=1
        return True
    if len(mainData.inv)>=25:
        UiManager.Popup(L.GetLoc("SaveManager.AddToInv.error"))
        return False
    else:
        mainData.inv+=[{"n":d,"m":1}]
        return True
def GetFromInv(d):
    a=IsInInv(d,1)
    if a!="NotIn":
        if mainData.inv[a]["m"]>0:
            mainData.inv[a]["m"]-=1
            if mainData.inv[a]["m"]==0:
                mainData.inv.pop(a)
            return True
        else:
            return False
    else:
        return False