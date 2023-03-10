# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 17:51:59 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import json

SettingsChanged = False

def DefaultSettingsInstance():
    return {
        "musicVolume": 70,
        "keybinds": {
            "up": pygame.K_z,
            "down": pygame.K_s,
            "left": pygame.K_q,
            "right": pygame.K_d
        }
    }

__mainSettings = DefaultSettingsInstance()

def GetSetting(name:str):
    return __mainSettings.get(name, None)

def SetSetting(name:str, value):
    __mainSettings[name] = value
    global SettingsChanged
    SettingsChanged = True

def GetKeybind(name:str):
    return __mainSettings["keybinds"].get(name, None)

def SetKeybind(name:str, value):
    __mainSettings["keybinds"][name] = value
    global SettingsChanged
    SettingsChanged = True

def LoadSettings():
    global __mainSettings
    
    try:
        __mainSettings = json.load(open("Settings.json", "r"))
        ApplySettings()
    except:
        ResetSettings()
    global SettingsChanged
    SettingsChanged = False

def SaveSettings():
    open("Settings.json", "w").write(json.dumps(__mainSettings, default=lambda o: o.__dict__, indent = 4))
    global SettingsChanged
    SettingsChanged = False
    ApplySettings()

def ResetSettings():
    global __mainSettings
    __mainSettings = DefaultSettingsInstance()
    SaveSettings()
    
def ApplySettings():
    pygame.mixer.music.set_volume(GetSetting("musicVolume")/100)