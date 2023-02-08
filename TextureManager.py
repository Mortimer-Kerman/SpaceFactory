# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 16:21:49 2023

@author: 29ray
"""
import pygame
import os

texturesPath = "./Assets2/textures/"

missingTexture = None

loadedTextures = {"no":missingTexture}
def GetTexture(textureName:str,scale:float=1)->pygame.Surface:
    textureName += ".png"
    if not textureName in loadedTextures.keys():
        try:
            loadedTextures[textureName] = pygame.image.load(texturesPath + textureName + ".png")
        except:
            textureName = "no.png"
    tex = loadedTextures[textureName]
    if scale != 1:
        tex = pygame.transform.scale(tex,(scale,scale))
    return tex

def LoadAllTextures():
    for subdir, dirs, files in os.walk(texturesPath):
        for file in files:
            filepath = os.path.join(subdir, file)
            filename = filepath.replace(texturesPath, "").replace("\\","/")
            print("Loading " + filename)
            loadedTextures[filename] = pygame.image.load(filepath)
    print("All textures loaded!")