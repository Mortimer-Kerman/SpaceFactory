# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 17:31:39 2023

@author: 29ray
"""

import pygame
import json
import random
import os

import GameItems

class Data:
    def __init__(self):
        self.camPos = [0,0]
        self.zoom = 100
        self.seed = random.randint(-(9**9),9**9)
        self.items = []
        
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent = 4)

clock = pygame.time.Clock()

saveName = None
mainData = None

def Load(name:str):
    global mainData
    CreateSave(name)
    if SaveExists(name):
        mainData.__dict__ = json.load(open("Saves/" + name + ".spf", "r"))
        items = []
        for item in mainData.items:
            items.append(GameItems.Item.ReadDictRepresentation(item))
        mainData.items = items
    print("File loaded!")
    
def Save():
    open("Saves/" + saveName + ".spf", "w").write(mainData.toJson())
    print("File saved!")

def CreateSave(name:str):
    global saveName
    global mainData
    saveName = name
    mainData = Data()

def Unload():
    global saveName
    global mainData
    Save()
    saveName = None
    mainData = None
    print("File unloaded")

def SaveExists(name:str):
    return os.path.exists("Saves/" + name + ".spf")

def SaveLoaded()->bool:
    return (saveName is not None) and (mainData is not None)

if not os.path.exists("Saves/"):
    os.makedirs("Saves/")

def TranslateCam(offset:list):
    mainData.camPos[0] += offset[0]
    mainData.camPos[1] += offset[1]
    
def GetCamPos():
    return mainData.camPos

def GetZoom():
    return mainData.zoom

def GetItems()->list:
    return mainData.items

def PlaceItem(item):
    mainData.items.append(item)