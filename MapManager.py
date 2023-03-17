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
    
    h = int((UiManager.height//2)-105)
    w = int(UiManager.height)
    
    menu = pygame_menu.Menu("Carte", w, h+105, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    menu.add.button(Localization.GetLoc('Game.Back'), menu.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    #menu.add.surface(SaveManager.planetTex)
    
    messages = [GenerateMessage() for i in range(5)]
    
    frame = menu.add.frame_h(w, h, padding=0)
    frame.relax(True)
    
    listFrame = menu.add.frame_v(500, max(len(messages) * 155, h), max_height=h, padding=0)
    listFrame.relax(True)
    frame.pack(listFrame, align=pygame_menu.locals.ALIGN_LEFT)
    
    for message in messages:
        
        oppFrame = menu.add.frame_v(500, 150, background_color=(50, 50, 50), padding=0)
        oppFrame.relax(True)
        listFrame.pack(oppFrame)
        
        oppFrame.pack(menu.add.button(FunctionUtils.ReduceStr(message[0], 30), lambda x=message:(title.set_title(x[0]),SetLabelText(x[1]))))
        
        oppFrame.pack(menu.add.vertical_margin(50))
        
        subtext = menu.add.label("Temps de voyage: 15 jours")
        subtext.set_font(TextureManager.nasalization, 20, (255,255,255), (255,255,255), (255,255,255), (255,255,255), (50,50,50))
        oppFrame.pack(subtext)
        
        listFrame.pack(menu.add.vertical_margin(5))
    
    detailsFrame = menu.add.frame_v(w-500, h, max_height=h, padding=0)
    detailsFrame.relax(True)
    frame.pack(detailsFrame)
    
    title = menu.add.label("",font_size=40)
    detailsFrame.pack(title,align=pygame_menu.locals.ALIGN_CENTER)
    
    label = menu.add.label("\n\n\n\n\n",font_size=20)
    detailsFrame.pack(label)
    
    detailsFrame.pack(menu.add.vertical_margin(100))
    
    detailsFrame.pack(menu.add.button("Lancer une expédition"),align=pygame_menu.locals.ALIGN_CENTER)
    
    
    def SetLabelText(text:str):
        
        cuts = [0]
        lastSpace = 0
        for i in range(len(text)):
            if text[i] == " ":
                lastSpace = i
            lastCut = cuts[-1]
            if i - lastCut > 55:
                cuts.append(lastSpace)
        
        
        lines = [text[i:j].strip() for i,j in zip(cuts, cuts[1:]+[None])]
        
        for i in range(6):
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
    "or.",
    "charbon.",
    "cuivre.",
    "fer.",
    "m1."
]

titles = [
    "Intriguantes ressources",
    "Ruée vers l'or",
    "Deep Inpact",
    "Archives",
    "La grande traversée",
    "Mirages et rumeurs",
    "Découverte fortuite",
    "Données orbitales"
]

def isVowel(letter:str):
    return letter.lower() in "aeiouy"

def GenerateMessage():
    
    singular = choice([True,False])
    
    people = choice(peoplesingular if singular else peopleplurial)
    prefix = choice(prefixsingular if singular else prefixplurial)
    
    foundDiscover = choice(discover)
    foundThing = choice(thing)
    foundWay = choice(way)
    foundPlace = choice(place)
    foundContains = choice(contains)
    
    foundQuantity = choice(quantity)
    foundRessource = choice(ressource)
    if isVowel(foundRessource[0]):
        foundQuantity = foundQuantity[:-2] + "'"
    
    possibleTitles = []
    if foundRessource == ressource[0]:
        possibleTitles.append(titles[1])
    if foundThing == thing[4]:
        possibleTitles.append(titles[2])
    if foundWay == way[1]:
        possibleTitles.append(titles[3])
    if foundPlace == place[4]:
        possibleTitles.append(titles[4])
    if foundWay == way[2] or foundWay == way[4]:
        possibleTitles.append(titles[5])
    if foundWay == way[5]:
        possibleTitles.append(titles[6])
    if foundWay == way[0]:
        possibleTitles.append(titles[7])
    if len(possibleTitles) == 0:
        possibleTitles.append(titles[0])
    
    return (choice(possibleTitles), people + prefix + foundDiscover + foundWay + foundThing + foundPlace + foundContains + foundQuantity + foundRessource)


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

