# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 17:31:39 2023

@author: 29ray
"""

import json
import random
import os

class Data:
    def __init__(self):
        self.camPos = [0,0]
        self.zoom = 100
        self.seed = random.randint(-(9**9),9**9)
        
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent = 4)

saveName = None
mainData = None

def Load(name:str):
    global mainData
    CreateSave(name)
    if SaveExists(name):
        mainData.__dict__ = json.load(open("Saves/" + name + ".spf", "r"))
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