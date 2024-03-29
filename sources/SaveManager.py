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
import AudioManager
import SettingsManager
import Stats
import SessionManager

SaveFileVersion="f0.20"

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
        self.saveVersion=SaveFileVersion
        self.inv=[]
        self.gamemode=0
        self.difficulty=1
        self.opportunities=[]
        self.clearedObstacles=[]
        self.tasks=[]
        self.nonChoosableTasks=[]
        self.settlers=0
        self.rovers=0
        
    def toJson(self):
        """
        renvoye toutes les Datas en JSON
        """
        return json.dumps(self, default=FunctionUtils.ToDict, indent = 4)

clock = pygame.time.Clock()#horloge du jeu

def TickClock():
    """
    Met à jour l'horloge du jeu
    """
    fps = SettingsManager.GetSetting("maxFps")
    if fps < 201:
        clock.tick(fps)
    else:
        clock.tick()

saveName = None#nom de la sauvegarde
mainData = None#va bientôt contenir la classe Data principale
planetTex = None

def Load(name:str)->bool:
    """
    Sert au chargement des sauvegardes
    """
    global mainData
    CreateSave(name)#Création de la sauvegarde
    if SaveExists(name):#si la sauvegarde existe déjà...
        path = "./Saves/" + saveName + "/"
        with open(path + "save.spf", "r") as f:
            #On charge le dictionnaire depuis le fichier en le fusionnant avec le dictionnaire déjà présent en écrasant les clés présentes dans les deux par les clés chargées
            mainData.__dict__ = {**mainData.__dict__, **json.load(f)}
        try:
            #Si la version de la sauvegarde n'est pas celle de la version actuelle...
            if mainData.saveVersion!=SaveFileVersion:
                #On demande à l'utilisateur une confirmation pour charger
                if not UiManager.WarnUser(L.GetLoc('Game.Warning'), L.GetLoc('Saves.IncompatibilityMessage'),None,None):
                    print("\n#"*5+"format de sauvegarde incompatible, merci d'utiliser la version "+SaveFileVersion+5*"\n#")
                    #Si il refuse, on met fin au chargement
                    return False
                #Si il confirme, on met à jour le code de version de la sauvegarde
                mainData.saveVersion = SaveFileVersion
        #En cas d'erreur...
        except:
            #On demande à l'utilisateur une confirmation pour charger
            if not UiManager.WarnUser(L.GetLoc('Game.Warning'), L.GetLoc('Saves.IncompatibilityMessage'),None,None):
                print("\n#"*5+"format de sauvegarde incompatible, merci d'utiliser la version "+SaveFileVersion+5*"\n#")
                #Si il refuse, on met fin au chargement
                return False
            #Si il confirme, on met à jour le code de version de la sauvegarde
            mainData.saveVersion = SaveFileVersion
        
        #Pour chaque item chargé, on le convertit en item de jeu à partir de sa valeur chargée, un dictionnaire
        for item in mainData.items.values():
            a=GameItems.Item.ReadDictRepresentation(item)
            #Et on le replace dans la liste
            mainData.items[str(list(a.pos))]=a
        
        #On met la texture actuelle de la planète à None
        global planetTex
        planetTex = None
        #On tente de la charger depuis la sauvegarde
        if os.path.isfile(path + "planet.png"):
            planetTex = pygame.image.load(path + "planet.png")
        
        #Si les conditions planétaires chargées sont un dictionnaire...
        if type(mainData.planetaryConditions) == dict:
            #Création d'un objet de conditions planétaires en tant que modèle pour ne pas inclure d'aléatoire
            conditions = PlanetGenerator.PlanetaryConditions(template=True)
            #On vient y charger les conditions planétaires chargées depuis le fichier
            conditions.__dict__ = mainData.planetaryConditions
            #On vient les remettre dans la sauvegarde
            mainData.planetaryConditions = conditions
        
        #Pour chaque dictionnaire représentant une opportunité chargée...
        for i in range(len(mainData.opportunities)):
            #On crée une opportunité
            opportunity = OpportunitiesManager.Opportunity()
            #On vient y stocker l'opportunité chargée
            opportunity.__dict__ = mainData.opportunities[i]
            #On la replace dansle dictionnaire d'opportunit"s
            mainData.opportunities[i] = opportunity
        
        #Si le dictionnaire des items n'est pas un dictionnaire numpy, on le convertit
        if type(mainData.items) == dict:
            mainData.items = FunctionUtils.NumpyDict(mainData.items)
        
    #On initialise la position de la caméra
    global LastCamPos
    LastCamPos = mainData.camPos.copy()   
    
    #Chargement des statistiques
    Stats.Load()
    
    print("File loaded!")
    return True

def Save():
    """
    Sauvegarde
    """
    path = "./Saves/" + saveName + "/"
    if not os.path.exists(path):#si le dossier de sauvegarde n'existe pas, le créer
        os.makedirs(path)
    with open(path + "save.spf", "w") as f:
        f.write(mainData.toJson())#écriture dans le fichier de sauvegarde
    if planetTex != None:
        pygame.image.save(planetTex, path + "planet.png")
    
    #On vient sauvegarder les métadonnées sous format json dans un fichier dédié
    with open(path + "meta.json", "w") as f:
        metaData = {
            "lastPlayed":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "difficulty":mainData.difficulty,
            "environment":mainData.planetaryConditions.type,
            "gameMode":mainData.gamemode
        }
        f.write(json.dumps(metaData, default=str, indent = 4))
    
    #Sauvegarde des statistiques
    Stats.Save()
    
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
    #On sauvegarde
    Save()
    #On réinitialise et remet à zéro les différentes variables du jeu
    saveName = None
    mainData = None
    TextureManager.RefreshZoom()
    UiManager.UIPopup.clear()
    UiManager.UiLightPopup.clear()
    GameItems.Minerais.Clear()
    UiManager.chunkTex.clear()
    SetSelectedItem(None)
    ResetRotation()
    AudioManager.StopGameSounds()
    SessionManager.showUi = True
    print("File unloaded")

def SaveExists(name:str):
    """
    Vérifie si la sauvegarde existe
    """
    path = "./Saves/" + name + "/"
    #On vérifie si le dossier de sauvegarde et le fichier save.spf qu'il contient existent
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
    
def GetCamPos()->list:
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

def GetZoom()->int:
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
    Ajoute un item aux items en retirant le coût en ressources
    """
    #Si le joueur n'est pas en mode bac à sable...
    if not IsSandBox():
        tempInv=[]
        for i in mainData.inv:
            tempInv.append(dict(i))
        a=[True]
        for i,n in GameItems.doc.get(item.name,{"c":{}}).get("c",{}).items():
            for j in range(n):
                a+=[GetFromInv(i)]
        if not all(a):
            mainData.inv=tempInv
            UiManager.Popup(L.GetLoc("SaveManager.GetFromInv.error"))
            return False
        FormatInv()
    #On place l'item dans le dictionnaire d'items
    mainData.items[str(list(item.pos))]=item
    
    #Si l'item est l'un des items suivants...
    if item.name in ["RedBlock","BlueBlock","YellowBlock","GreenBlock","BlackBlock","WhiteBlock"]:
        Stats.IncreaseStat("DecorationBlocksPlaced")#On incrémente la statistique de blocs décoratifs placés
    
    Stats.IncreaseStat(item.name + "sPlaced")#On incrémente la statistique de ce bloc spécifique placé
    
    return True

def DeleteItem(pos):
    """
    Supprime un item si il en existe un à cette position
    """
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

def GetGamemode()->int:
    """
    Renvoie le mode de jeu.
    0 pour carrière
    1 pour bac à sable
    2 pour tutoriel
    """
    return mainData.gamemode

def IsSandBox()->bool:
    """
    Dit si la sauvegarde actuelle est un bac à sable.
    
    """
    return GetGamemode() == 1

def IsTutorial()->bool:
    """
    Dit si la sauvegarde actuelle est un tutoriel.
    """
    return GetGamemode() == 2

def GetDifficultyLevel()->int:
    """
    Renvoie le niveau de difficulté:
        0 = facile
        1 = normal
        2 = difficile
    """
    return mainData.difficulty

selectedItem=None

def SetSelectedItem(item):
    """
    Change l'item séléctionné
    """
    global selectedItem
    selectedItem=item

def GetSelectedItem()->str:
    """
    Renvoie l'item séléctionné
    """
    return selectedItem

def IsItemSelected()->bool:
    """
    Dit si un item est séléctionné
    """
    return not GetSelectedItem() is None

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

def ObstacleAtPos(pos:tuple)->bool:
    """
    Dit si une position est occupée par un obstacle
    """
    return not pos in mainData.clearedObstacles and GameItems.Minerais.Type(pos[0], pos[1]) == "Obstacle"

def ClearObstacle(pos:tuple):
    """
    Élimine un obstacle de la carte
    """
    #On ajoute la position de l'obstacle éliminé à la liste des obstacles éliminés
    mainData.clearedObstacles.append(pos)
    
    #On reconstitue l'info sur l'obstacle
    d = [pos[0],pos[1],"Obstacle"]
    
    #Si elle existe dans la liste des minerais et obstacles affichés, on l'y retire
    if d in GameItems.current:
        GameItems.current.remove(d)

rotation = 0

def GetRotation():
    """
    Renvoie la rotation actuelle
    """
    return rotation

def UpdateRotation():
    """
    Met à jour la rotation
    """
    global rotation
    if rotation!=3:
        rotation+=1
    else:
        rotation=0

def ResetRotation():
    """
    Réinitialise la rotation
    """
    global rotation
    rotation=0

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
def FormatInv():
    tempInv=[]
    for i in mainData.inv:
        tempInv.append(dict(i))
    mainData.inv=[]
    for i in tempInv:
        for j in range(i["m"]):
            AddToInv(i["n"])
