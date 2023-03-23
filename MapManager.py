# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 15:26:04 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import pygame_menu

from random import choice, randint

import SettingsManager
import SaveManager
import UiManager
import FunctionUtils
import NoiseTools
import numpy
import Localization
import TextureManager


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
    
    opportunities = [Opportunity() for i in range(5)]
    
    frame = menu.add.frame_h(w, h, padding=0)
    frame.relax(True)
    
    listFrame = menu.add.frame_v(500, max(len(opportunities) * 155, h), max_height=h, padding=0)
    listFrame.relax(True)
    frame.pack(listFrame, align=pygame_menu.locals.ALIGN_LEFT)
    
    global currentOpportunity
    currentOpportunity = None
    
    for opportunity in opportunities:
        
        oppFrame = menu.add.frame_v(500, 150, background_color=(50, 50, 50), padding=0)
        oppFrame.relax(True)
        listFrame.pack(oppFrame)
        
        oppFrame.pack(menu.add.button(FunctionUtils.ReduceStr(opportunity.GetTitle(), 30), lambda opp=opportunity:OpenOpportunity(opp)))
        
        oppFrame.pack(menu.add.vertical_margin(50))
        
        
        if opportunity.GetWalkDistance() >= 24:
            distance = round(opportunity.GetWalkDistance()/24)
            suffix = " jour"
        else :
            distance = opportunity.GetWalkDistance()
            suffix = " heure"
        if distance > 1:
            suffix += "s"
        distance = str(distance) + suffix
        
        subtext = menu.add.label("Temps de voyage: " + distance)
        subtext.set_font(TextureManager.nasalization, 20, (255,255,255), (255,255,255), (255,255,255), (255,255,255), (50,50,50))
        oppFrame.pack(subtext)
        
        listFrame.pack(menu.add.vertical_margin(5))
    
    def OpenOpportunity(opportunity):
        title.set_title(opportunity.GetTitle())
        SetLabelText(opportunity.GetDesc())
        global currentOpportunity
        currentOpportunity = opportunity
    
    detailsFrame = menu.add.frame_v(w-500, h, max_height=h, padding=0)
    detailsFrame.relax(True)
    frame.pack(detailsFrame)
    
    title = menu.add.label("",font_size=40)
    detailsFrame.pack(title,align=pygame_menu.locals.ALIGN_CENTER)
    
    label = menu.add.label("\n\n\n\n\n",font_size=20)
    detailsFrame.pack(label)
    
    detailsFrame.pack(menu.add.vertical_margin(100))
    
    detailsFrame.pack(menu.add.button("Lancer une expédition", OpenExpeditionLauncher),align=pygame_menu.locals.ALIGN_CENTER)
    
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

def OpenExpeditionLauncher():
    
    global currentOpportunity
    if currentOpportunity == None:
        return
    
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    background = pygame.display.get_surface().copy()
    background.blit(screenFilter,(0,0))
    def DisplayBackground():
        UiManager.screen.blit(background,(0,0))
    
    menu = pygame_menu.Menu(currentOpportunity.GetTitle(), 500, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    menu.add.button(Localization.GetLoc('Game.Back'), menu.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    if currentOpportunity.GetWalkDistance() >= 24:
        distance = round(currentOpportunity.GetWalkDistance()/24)
        suffix = " jour"
    else :
        distance = currentOpportunity.GetWalkDistance()
        suffix = " heure"
    if distance > 1:
        suffix += "s"
    distance = str(distance) + suffix
    menu.add.label("Temps de marche: " + distance)
    
    if currentOpportunity.GetDriveDistance() >= 24:
        distance = round(currentOpportunity.GetDriveDistance()/24)
        suffix = " jour"
    else :
        distance = currentOpportunity.GetDriveDistance()
        suffix = " heure"
    if distance > 1:
        suffix += "s"
    distance = str(distance) + suffix
    menu.add.label("Temps de route: " + distance)
    
    menu.mainloop(UiManager.screen, DisplayBackground)

def Tick():
    pass

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

class Opportunity:
    def __init__(self):
        
        self.singular = choice([True,False])
        
        self.descCodes = {
            "people": randint(0,len(peoplesingular if self.singular else peopleplurial)-1),
            "prefix": randint(0,len(prefixsingular if self.singular else prefixplurial)-1),
            "discover": randint(0, len(discover)-1),
            "way": randint(0, len(way)-1),
            "thing": randint(0, len(thing)-1),
            "place": randint(0, len(place)-1),
            "contains": randint(0, len(contains)-1),
            "quantity": randint(0, len(quantity)-1),
            "ressource": randint(0, len(ressource)-1)
        }
        
        possibleTitles = []
        if self.descCodes["ressource"] == 0:
            possibleTitles.append(1)
        if self.descCodes["thing"] == 4:
            possibleTitles.append(2)
        if self.descCodes["way"] == 1:
            possibleTitles.append(3)
        if self.descCodes["place"] == 4:
            possibleTitles.append(4)
        if self.descCodes["way"] == 2 or self.descCodes["way"] == 4:
            possibleTitles.append(5)
        if self.descCodes["way"] == 5:
            possibleTitles.append(6)
        if self.descCodes["way"] == 0:
            possibleTitles.append(7)
        if len(possibleTitles) == 0:
            possibleTitles.append(0)
        self.title = choice(possibleTitles)
        
        self.distance = [randint(100,400),randint(80,240),randint(8,28),randint(200,800),randint(400,2000)][self.descCodes["place"]]
        
    def GetDesc(self):
        q = quantity[self.descCodes["quantity"]]
        r = ressource[self.descCodes["ressource"]]
        if FunctionUtils.IsVowel(r[0]):
            q = q[:-2] + "'"
        
        codes = [
            (peoplesingular if self.singular else peopleplurial)[self.descCodes["people"]],
            (prefixsingular if self.singular else prefixsingular)[self.descCodes["prefix"]],
            discover[self.descCodes["discover"]],
            way[self.descCodes["way"]],
            thing[self.descCodes["thing"]],
            place[self.descCodes["place"]],
            contains[self.descCodes["contains"]],
            q,
            r
        ]
        
        return "".join(codes)
        
    def GetTitle(self):
        return titles[self.title]
    
    def GetDistance(self):
        return self.distance
    
    def GetWalkDistance(self):
        return self.distance//4
    
    def GetDriveDistance(self):
        return self.distance//40