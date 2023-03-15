# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 15:26:04 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import pygame_menu

import SettingsManager
import SaveManager
import UiManager
import FunctionUtils
import NoiseTools
import numpy
import Localization
import TextureManager

worldMap = pygame.image.load("Assets/background.png")

def OpenMap():
    
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    background = pygame.display.get_surface().copy()
    background.blit(screenFilter,(0,0))
    def DisplayBackground():
        UiManager.screen.blit(background,(0,0))
    
    menu = pygame_menu.Menu("Carte", UiManager.width//1.3, UiManager.height//1.3, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    menu.add.button(Localization.GetLoc('Game.Back'), menu.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    #menu.add.surface(SaveManager.planetTex)
    
    messages = [GenerateMessage() for i in range(5)]
    
    h = int((UiManager.height//1.3)-105)
    
    frame = menu.add.frame_h(UiManager.width//1.3, h, padding=0)
    frame.relax(True)
    
    listFrame = menu.add.frame_v(500, max(len(messages) * 155, h), max_height=h, padding=0)
    listFrame.relax(True)
    frame.pack(listFrame, align=pygame_menu.locals.ALIGN_LEFT)
    
    for message in messages:
        
        oppFrame = menu.add.frame_v(500, 150, background_color=(50, 50, 50), padding=0)
        oppFrame.relax(True)
        listFrame.pack(oppFrame)
        
        linedMessage = message.replace("\n","")
        
        oppFrame.pack(menu.add.button(linedMessage[:30] + ("..." if len(linedMessage) > 30 else ""), lambda x=message:SetLabelText(x)))
        
        oppFrame.pack(menu.add.vertical_margin(50))
        
        subtext = menu.add.label("Temps de voyage: 15 jours")
        subtext.set_font(TextureManager.nasalization, 20, (255,255,255), (255,255,255), (255,255,255), (255,255,255), (50,50,50))
        oppFrame.pack(subtext)
        
        listFrame.pack(menu.add.vertical_margin(5))
    
    w = int(UiManager.width//1.3-500)
    
    detailsFrame = menu.add.frame_v(w, h, max_height=h, padding=0)
    detailsFrame.relax(True)
    frame.pack(detailsFrame)
    
    detailsFrame.pack(menu.add.surface(pygame.transform.scale(pygame.image.load("Assets/background.png"),(w//2,w//4))))
    
    
    
    label = menu.add.label("\n\n")
    detailsFrame.pack(label)
    
    detailsFrame.pack(menu.add.button("Lancer une expédition"))
    
    
    def SetLabelText(text:str):
        lines = text.split('\n',2)
        for i in range(3):
            if i < len(lines):
                label[i].set_title(lines[i])
            else:
                label[i].set_title('')
    
    menu.mainloop(UiManager.screen, DisplayBackground)
    """
    worldMap = CalculateWorldMap()
    
    zoom = 4
    lastZoom = zoom
    camPos = [0,0]
    
    scaledMap = pygame.transform.scale(worldMap,(UiManager.width * zoom,UiManager.height * zoom))
    
    while True:
        
        UiManager.screen.blit(scaledMap, camPos)
        
        pygame.display.update()
        
        #action du clavier
        keys = pygame.key.get_pressed()#On stocke les touches pressées
        
        if keys[SettingsManager.GetKeybind("up")]:#si touche up
            camPos[1]+=SaveManager.clock.get_time() / 2
        if keys[SettingsManager.GetKeybind("down")]:#si touche down
            camPos[1]-=SaveManager.clock.get_time() / 2
        if keys[SettingsManager.GetKeybind("right")]:#si touche right
            camPos[0]-=SaveManager.clock.get_time() / 2
        if keys[SettingsManager.GetKeybind("left")]:#si touche left
            camPos[0]+=SaveManager.clock.get_time() / 2    
        
        camPos[0] = FunctionUtils.clamp(camPos[0], -UiManager.width*(zoom-1), 0)
        camPos[1] = FunctionUtils.clamp(camPos[1], -UiManager.height*(zoom-1), 0)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            
            if event.type == pygame.MOUSEWHEEL:#si un changement molette survient
                zoom = FunctionUtils.clamp(zoom+(event.y / 10), 1, 4)#on ajoute le y du changement de molette en s'assurant de garder le niveau de zoom entre 10 et 150
                if zoom != lastZoom:
                    lastZoom = zoom
                    scaledMap = pygame.transform.scale(worldMap,(UiManager.width * zoom,UiManager.height * zoom))
        
        SaveManager.clock.tick()#on mets à jour l'horloge des FPS
    """

from random import choice

peoplesingular = [
    "Un groupe de chercheurs ",
    "Une équipe ",
    "Une mission de reconaissance ",
    "On ",
    "Une patrouille "
]

peopleplurial = [
    "Des scientifiques ",
    "Des colons ",
    "Des chercheurs ",
    "Plusieurs ouvriers "
]

prefixsingular = [
    "a ",
    "semble avoir ",
]

prefixplurial = [
    "ont ",
    "semblent avoir "
]

discover = [
    "trouvé ",
    "identifié ",
    "découvert ",
    "détécté ",
    "décelé "
]

way = [
    "grâce à des données satellites ",
    "en analysant des archives ",
    "dans le lointain ",
    "lors d'une sortie ",
    "avec des témoignages ",
    "par hasard ",
    ""
]

thing = [
    "une zone ",
    "une région ",
    "un massif montagneux ",
    "un massif végétal ",
    "un cratère ",
    "une plaine ",
    "une steppe désertique ",
    "un ancien bassin volcanique "
]

place = [
    "a plusieurs jours de marche ",
    "a quelques heures de route ",
    "près d'ici ",
    "de l'autre coté des montagnes ",
    "de l'autre coté de la planète "
]

contains = [
    "abritant ",
    "semblant contenir ",
    "pouvant receler ",
    "contenant ",
]

quantity = [
    "d'importants gisements de ",
    "de grandes quantités de ",
]

ressource = [
    "or",
    "charbon",
    "cuivre",
    "fer",
    "m1"
]

def isVowel(letter:str):
    return letter.lower() in "aeiouy"

def GenerateMessage():
    
    singular = choice([True,False])
    
    people = choice(peoplesingular if singular else peopleplurial)
    prefix = choice(prefixsingular if singular else prefixplurial)
    
    foundQuantity = choice(quantity)
    foundRessource = choice(ressource)
    if isVowel(foundRessource[0]):
        foundQuantity = foundQuantity[:-2] + "'"
    
    return people + prefix + choice(discover) + choice(way) + "\n" + choice(thing) + choice(place) + choice(contains) + "\n" + foundQuantity + foundRessource


import matplotlib.pyplot as plt

def CalculateWorldMap():
    pix = []
    
    Offset = (1,1)
    DesertCoverage = 0.5
    PoleCoverage = 0.2
    SandRedFactor = 0.25
    BiomeLerpSpeed = 0.2
    SeaLevel = 0.5
    
    for y in range(200):
        row = []
        for x in range(100):
            
            xCoord = x / 50
            yCoord = y / 50
            
            depth = NoiseTools.FractalNoise(xCoord, yCoord, Offset, 2)
            
            col = (depth,depth,depth)
            
            variationMap = (depth - SeaLevel) / 2
            
            ocean = (0, 0.21, 0.35)
            grass = (0.28 + variationMap, 0.52 + variationMap, 0.07 + variationMap)
            desert = FunctionUtils.lerpcol(((depth * 1) + 0.2, (depth * 0.92) + 0.2, 0.2), (depth, depth / 4, 0), SandRedFactor)
            poles = (depth + 0.3, depth + 0.3, depth + 0.3)
            
            Latitude = abs((x - 50) / 50)
            
            biomeMap = NoiseTools.FractalNoise(xCoord, yCoord, (Offset[0] * 2, Offset[1] * 2), 2)# * 2 + 1
            
            biomeMap = round(biomeMap + 0.5 - DesertCoverage)#FunctionUtils.clamp01(((biomeMap+factor)/(abs(biomeMap+factor)+0.1)+1)/2)
            
            grass = FunctionUtils.lerpcol(desert, grass, biomeMap)

            grass = FunctionUtils.lerpcol(grass, poles, FunctionUtils.clamp01((Latitude - (1 - PoleCoverage)) / PoleCoverage) / BiomeLerpSpeed)

            if depth < SeaLevel:
                col = ocean
            else:
                col = grass
            
            #row.append(col)
            row.append(FunctionUtils.ZeroOneToHexa(col))
        pix.append(row)
    
    plt.imshow(pix)
    
    texture = pygame.Surface((200,100))
    pygame.surfarray.blit_array(texture, numpy.array(pix))
    
    return texture

