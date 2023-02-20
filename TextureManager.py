# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 16:21:49 2023

@author: 29ray
"""
import pygame
import os

texturesPath = "./Assets2/textures/"#le chemin des textures

missingTexture = None#Si la texture n'existe pas

aquire = None#variable stockant la police principale "aquire"

#tentative de faire un filtre
colorFilter = pygame.Surface((100,100))
colorFilter.set_alpha(50)

def GetColorFilter(color:tuple, scale:float):
    colorFilter.fill(color)
    return pygame.transform.scale(colorFilter,(scale,scale))

loadedTextures = {"no":missingTexture,"colorFilter":colorFilter}
menuTextures = {}
def GetTexture(textureName:str,scale:float=1,is_menu:bool=False)->pygame.Surface:
    """
    Permet d'obtenir la texture
    """
    textureName += ".png"
    if not textureName in loadedTextures.keys():#si la texture n'est pas chargée
        try:#tenter
            loadedTextures[textureName] = pygame.image.load(texturesPath + textureName + ".png")#chargement image
        except:#en cas d'erreur
            textureName = "no.png"
    tex = loadedTextures[textureName]
    if scale != 1:#si la taille est différente de 1
        if textureName in zoomedTextures and not is_menu:#si textureName est dans zoomedTextures et n'est pas dans le menu
            tex = zoomedTextures[textureName]
        elif textureName in menuTextures and is_menu:
            tex=menuTextures[textureName]
        else:
            tex = pygame.transform.scale(tex,(scale,scale))#redimentionner l'image
            if is_menu:
                menuTextures[textureName] = tex
            else:
                zoomedTextures[textureName] = tex
                
    return tex

def LoadAllTextures():
    """
    Chargement de toutes les textures
    """
    global aquire
    try:aquire=pygame.font.Font("./Assets2/font/Aquire.ttf",26)#on tente de charger aquire
    except:aquire=pygame.font.get_default_font()#en cas d'erreur, on tente avec la police par défaut
    
    for subdir, dirs, files in os.walk(texturesPath):#on explore tous les fichiers dans le chemin des textures
        for file in files:#pour chaque fichier dans les fichiers
            filepath = os.path.join(subdir, file)
            filename = filepath.replace(texturesPath, "").replace("\\","/")
            print("Loading " + filename)
            loadedTextures[filename] = pygame.image.load(filepath)#chargement via pygame.image.load
    print("All textures loaded!")#message de confirmation que toutes les textures sont chargées

zoomedTextures = {}#dictionnaire des textures zoomées

def RefreshZoom():
    """
    Cette fonction sert à raffraichir le zoom
    """
    zoomedTextures.clear()#vide le dictionnaire des textures zoomées