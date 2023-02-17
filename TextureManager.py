# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 16:21:49 2023

@author: 29ray
"""
import pygame
import os

texturesPath = "./Assets2/textures/"

missingTexture = None

aquire = None

colorFilter = pygame.Surface((100,100))
colorFilter.set_alpha(50)

def GetColorFilter(color:tuple, scale:float):
    colorFilter.fill(color)
    return pygame.transform.scale(colorFilter,(scale,scale))

loadedTextures = {"no":missingTexture,"colorFilter":colorFilter}
def GetTexture(textureName:str,scale:float=1)->pygame.Surface:
    textureName += ".png"
    if not textureName in loadedTextures.keys():
        try:
            loadedTextures[textureName] = pygame.image.load(texturesPath + textureName + ".png")
        except:
            textureName = "no.png"
    tex = loadedTextures[textureName]
    if scale != 1:
        if textureName in zoomedTextures:
            tex = zoomedTextures[textureName]
        else:
            tex = pygame.transform.scale(tex,(scale,scale))
            zoomedTextures[textureName] = tex
    return tex

def LoadAllTextures():
    global aquire
    try:aquire=pygame.font.Font("./Assets2/font/Aquire.ttf",26)
    except:aquire=pygame.font.get_default_font()
    
    for subdir, dirs, files in os.walk(texturesPath):
        for file in files:
            filepath = os.path.join(subdir, file)
            filename = filepath.replace(texturesPath, "").replace("\\","/")
            print("Loading " + filename)
            loadedTextures[filename] = pygame.image.load(filepath)
    print("All textures loaded!")

zoomedTextures = {}

def RefreshZoom():
    zoomedTextures.clear()