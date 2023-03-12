# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 16:01:06 2023

@author: Thomas Sartre et François Patinec-Haxel
"""


__localizations = {}

def Init():
    try:
        with open("Assets/localization.txt", "r", encoding="utf-8") as f:
            for LocKey in f.readlines():
                LocKey = LocKey[:-1]
                if len(LocKey) != 0 and not LocKey.startswith("//"):
                    
                    KeyPair = LocKey.split(' : ', 1)
                    __localizations[KeyPair[0]] = KeyPair[1]
    except:
        pass

def GetLoc(LocKey:str, *args):
    try:
        loc = __localizations[LocKey].replace("%$r", "\n")
        
        for i in range(1,len(args)+1):
            loc = loc.replace("%$" + str(i), str(args[i - 1]))
        
        return loc
    except:
        return LocKey
