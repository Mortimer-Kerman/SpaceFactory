# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 16:21:49 2023

@author: Thomas Sartre et François Patinec-Haxel
"""
import pygame
import os

texturesPath = "./Assets/textures/"#le chemin des textures

missingTexture = None#Si la texture n'existe pas

loadedTextures = {"no":missingTexture}
menuTextures = {}
def GetTexture(textureName:str,scale:float=1,is_menu:bool=False)->pygame.Surface:
    """
    Permet d'obtenir la texture
    """
    textureName += ".png"
    if not textureName in loadedTextures.keys():#si la texture n'est pas chargée
        try:#tenter
            loadedTextures[textureName] = pygame.image.load(texturesPath + textureName + ".png").convert_alpha()#chargement image
        except:#en cas d'erreur
            textureName = "no.png"
    tex = loadedTextures[textureName]
    if scale != 1:#si la taille est différente de 1
        if textureName in zoomedTextures and not is_menu:#si textureName est dans zoomedTextures et n'est pas dans le menu
            tex = zoomedTextures[textureName]
        elif textureName in menuTextures and is_menu:
            tex=menuTextures[textureName]
        else:
            tex = pygame.transform.scale(tex,(scale,scale))#redimensionner l'image
            if is_menu:
                menuTextures[textureName] = tex
            else:
                zoomedTextures[textureName] = tex
                
    return tex

def LoadAllTextures():
    """
    Chargement de toutes les textures
    """

    try:
        fonts["aquire"] = pygame.font.Font("./Assets/font/aquire.ttf",26)#on tente de charger aquire
    except:
        fonts["aquire"] = pygame.font.Font(pygame.font.get_default_font(),20)# en cas d'erreur, on tente avec la police par défaut
    
    try:
        fonts["nasalization"] = pygame.font.Font("./Assets/font/nasalization.ttf",30)#on tente de charger nasalization
    except:
        fonts["nasalization"] = pygame.font.Font(pygame.font.get_default_font(),20)# en cas d'erreur, on tente avec la police par défaut
    
    for subdir, dirs, files in os.walk(texturesPath):#on explore tous les fichiers dans le chemin des textures
        for file in files:#pour chaque fichier dans les fichiers
            if file.endswith(".png"):
                filepath = os.path.join(subdir, file)
                filename = filepath.replace(texturesPath, "").replace("\\","/")
                print("Loading " + filename)
                loadedTextures[filename] = pygame.image.load(filepath).convert_alpha()#chargement via pygame.image.load
    print("All textures loaded!")#message de confirmation que toutes les textures sont chargées

zoomedTextures = {}#dictionnaire des textures zoomées

def RefreshZoom():
    """
    Cette fonction sert à rafraîchir le zoom
    """
    zoomedTextures.clear()#vide le dictionnaire des textures zoomées
    zoomedFilters.clear()


def GetColorFilter(color:tuple,scale:float):
    
    if not color in filters.keys():
        colorFilter = pygame.Surface((100,100))
        colorFilter.fill(color)
        filters[color] = colorFilter
    tex = filters[color]
    if scale != 1:
        if not color in zoomedFilters.keys():
            zoomedFilters[color] = pygame.transform.scale(tex,(scale,scale))
        tex = zoomedFilters[color]
    return tex

filters = {}
zoomedFilters = {}


fonts = {}
def GetFont(fontName:str,fontSize:int=None)->pygame.font.Font:
    
    fullFontName = fontName + ("" if fontSize == None else "." + str(fontSize))
    
    if not fullFontName in fonts:
        try:
            fonts[fullFontName] = pygame.font.Font("Assets/font/" + fontName + ".ttf", fontSize if fontSize != None else 20)
        except:
            return pygame.font.Font(pygame.font.get_default_font(),fontSize if fontSize != None else 20)
    
    return fonts[fullFontName]