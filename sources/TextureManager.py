# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 16:21:49 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

#chargement des bibliothèques
import pygame

import os

texturesPath = "./Assets/textures/"#le chemin des textures

missingTexture = None#Si la texture n'existe pas

loadedTextures = {"no":missingTexture}
menuTextures = {}
def GetTexture(textureName:str,scale:float=1,is_menu:bool=False,verticalScale:float=None,transportedItem:bool=False)->pygame.Surface:
    """
    Permet d'obtenir la texture
    """
    textureName += ".png"
    if not TextureExists(textureName):#si la texture n'est pas chargée
        try:#tenter
            loadedTextures[textureName] = pygame.image.load(texturesPath + textureName + ".png").convert_alpha()#chargement image
        except:#en cas d'erreur
            textureName = "no.png"
    tex = loadedTextures[textureName]
    
    if transportedItem:#Si la texture est pour un item transporté, on ajoute invItem à la fin pour le démarquer de l'original dans le dictionnaire de zoom
        textureName += "-invItem"
    
    if scale != 1:#si la taille est différente de 1
        if textureName in zoomedTextures and not is_menu:#si textureName est dans zoomedTextures et n'est pas dans le menu
            tex = zoomedTextures[textureName]
        elif textureName in menuTextures and is_menu:
            tex=menuTextures[textureName]
        else:
            if verticalScale == None:
                verticalScale = scale
            tex = pygame.transform.scale(tex,(scale,verticalScale))#redimensionner l'image
            if is_menu:
                menuTextures[textureName] = tex
            else:
                zoomedTextures[textureName] = tex
                
    return tex

def TextureExists(textureName:str):
    """
    Dit si une texture existe ou a été chargée
    """
    if type(textureName) != str:
        return False
    if not textureName.endswith(".png"):
        textureName += ".png"
    return textureName in loadedTextures.keys()

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
    """
    Fonction permettant d'obtenir le filtre de couleur
    """
    
    if not color in filters.keys():#si la couleur n'est pas dans la liste des clés de filtres
        colorFilter = pygame.Surface((100,100))#on crée une surface de 100x100
        colorFilter.fill(color)#on remplis de la couleur
        filters[color] = colorFilter#on l'enregistre dans le dictionnaire des filtres
    tex = filters[color]#tex vaut la surface que l'on vient de créer/trouver dans le dictionnaire
    if scale != 1:#si la taille est différente de 1
        if not color in zoomedFilters.keys():#si la couleur n'est pas dans la liste de filtres zoomées
            zoomedFilters[color] = pygame.transform.scale(tex,(scale,scale))#on redimensionne la surface
        tex = zoomedFilters[color]#tex vaut maintenant la texture zoomée
    return tex

filters = {}
zoomedFilters = {}


fonts = {}
def GetFont(fontName:str,fontSize:int=None)->pygame.font.Font:
    """
    Fonction de chargement de police
    """
    
    fullFontName = fontName + ("" if fontSize == None else "." + str(fontSize))#définition du nom complet de la police
    
    if not fullFontName in fonts:#si le nom n'est pas dans le dictionnaire de police
        try:
            fonts[fullFontName] = pygame.font.Font("./Assets/font/" + fontName + ".ttf", fontSize if fontSize != None else 20)#chargement de la police
        except:
            return pygame.font.Font(pygame.font.get_default_font(),fontSize if fontSize != None else 20)#chargement de la police par défaut
    
    return fonts[fullFontName]#renvoie la police