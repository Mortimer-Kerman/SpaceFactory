# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 15:26:04 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import pygame_menu

from random import choice, randint
from datetime import datetime

import SettingsManager
import SaveManager
import UiManager
import FunctionUtils
import NoiseTools
import numpy
import Localization
import TextureManager

openedMap = None
background = None

def OpenMap():
    global openedMap
    global background
    
    if openedMap == None:
        screenFilter = pygame.Surface((UiManager.width,UiManager.height))
        screenFilter.set_alpha(50)
        background = pygame.display.get_surface().copy()
        background.blit(screenFilter,(0,0))
    
    def DisplayBackground():
        UiManager.screen.blit(background,(0,0))
    
    h = int((UiManager.height//2)-105)
    w = int(UiManager.height)
    
    columnW = w//2
    
    menu = pygame_menu.Menu(Localization.GetLoc("Opportunities.Title"), w, h+105, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    menu.add.button(Localization.GetLoc('Game.Back'), CloseMap, align=pygame_menu.locals.ALIGN_LEFT)
    openedMap = menu
    
    #menu.add.surface(SaveManager.planetTex)
    
    while len(SaveManager.mainData.opportunities) < 5:
        SaveManager.mainData.opportunities.append(Opportunity())
    
    frame = menu.add.frame_h(w, h, padding=0)
    frame.relax(True)
    
    listFrame = menu.add.frame_v(columnW, max(len(SaveManager.mainData.opportunities) * (int(columnW * (5/18)) + 5), h), max_height=h, padding=0)
    listFrame.relax(True)
    frame.pack(listFrame, align=pygame_menu.locals.ALIGN_LEFT)
    
    global currentOpportunity
    currentOpportunity = None
    
    for opportunity in SaveManager.mainData.opportunities:
        
        color = (50, 50, 50)
        if opportunity.state == Opportunity.State.GOING:
            color = (199, 86, 0)
        
        oppFrame = menu.add.frame_v(columnW, int(columnW * (5/18)), background_color=color, padding=0)
        oppFrame.relax(True)
        listFrame.pack(oppFrame)
        
        b = menu.add.button(FunctionUtils.ReduceStr(opportunity.GetTitle(), 30), lambda opp=opportunity:OpenOpportunity(opp),font_size=int(columnW/18))
        
        FunctionUtils.EncapsulateButtonInFrame(b, oppFrame, buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        oppFrame.pack(menu.add.vertical_margin(int(columnW * (5/54))))
        
        
        if opportunity.GetWalkDistance() >= 24:
            distance = round(opportunity.GetWalkDistance()/24)
            suffix = " jour"
        else :
            distance = opportunity.GetWalkDistance()
            suffix = " heure"
        if distance > 1:
            suffix += "s"
        distance = str(distance) + suffix
        
        subtext = menu.add.label("Temps de voyage: " + distance, font_size=int(columnW/27), font_name=TextureManager.nasalization)
        #subtext.set_font(TextureManager.nasalization, 11, (255,255,255), (255,255,255), (255,255,255), (255,255,255), (50,50,50))
        oppFrame.pack(subtext)
        
        listFrame.pack(menu.add.vertical_margin(5))
    
    def OpenOpportunity(opportunity):
        title.set_title(opportunity.GetTitle())
        SetLabelText(opportunity.GetDesc())
        global currentOpportunity
        currentOpportunity = opportunity
    
    detailsFrame = menu.add.frame_v(columnW, h, max_height=h, padding=0)
    detailsFrame.relax(True)
    frame.pack(detailsFrame)
    
    title = menu.add.label("",font_size=int(columnW*(2/29)))#40 en 1080
    detailsFrame.pack(title,align=pygame_menu.locals.ALIGN_CENTER)
    
    label = menu.add.label("\n\n\n\n\n",font_size=int(columnW*(1/29)))#20 en 1080
    detailsFrame.pack(label)
    
    detailsFrame.pack(menu.add.vertical_margin(100))
    
    detailsFrame.pack(menu.add.button("Lancer une expédition", OpenExpeditionLauncher),align=pygame_menu.locals.ALIGN_CENTER)
    
    def SetLabelText(text:str):
        
        lineLength = 55#int((UiManager.height-500)*(11/116))
        
        cuts = [0]
        lastSpace = 0
        for i in range(len(text)):
            if text[i] == " ":
                lastSpace = i
            lastCut = cuts[-1]
            if i - lastCut > lineLength:
                cuts.append(lastSpace)
        
        
        lines = [text[i:j].strip() for i,j in zip(cuts, cuts[1:]+[None])]
        
        for i in range(6):
            if i < len(lines):
                label[i].set_title(lines[i])
            else:
                label[i].set_title('')
    
    if len(SaveManager.mainData.opportunities) != 0:
        OpenOpportunity(SaveManager.mainData.opportunities[0])
    
    def MenuTick():
        if Tick():
            openedMap.disable()
            OpenMap()
    
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),MenuTick()))

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
    
    menu = pygame_menu.Menu(currentOpportunity.GetTitle(), 550, 450, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    menu.add.button(Localization.GetLoc('Game.Back'), menu.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    menu.add.vertical_margin(50)
    
    menu.add.range_slider("Nombre de membres: ", 5, (2, 10), 1, value_format=lambda x: str(int(x)), align=pygame_menu.locals.ALIGN_LEFT)
    
    def SetTravelTime(Rover:bool):
        if Rover:
            if currentOpportunity.GetDriveDistance() >= 24:
                distance = round(currentOpportunity.GetDriveDistance()/24)
                suffix = " jour"
            else :
                distance = currentOpportunity.GetDriveDistance()
                suffix = " heure"
            if distance > 1:
                suffix += "s"
            distance = str(distance) + suffix
            travelTimeLabel.set_title("Temps de route: " + distance)
        else:
            if currentOpportunity.GetWalkDistance() >= 24:
                distance = round(currentOpportunity.GetWalkDistance()/24)
                suffix = " jour"
            else :
                distance = currentOpportunity.GetWalkDistance()
                suffix = " heure"
            if distance > 1:
                suffix += "s"
            distance = str(distance) + suffix
            travelTimeLabel.set_title("Temps de marche: " + distance)
    
    menu.add.toggle_switch('Moyen de transport', state_text=('A pied', 'Rover'), state_color=((100, 100, 100), (100, 100, 100)), onchange=SetTravelTime)
    
    travelTimeLabel = menu.add.label("")
    
    menu.add.vertical_margin(50)
    
    menu.add.button("Lancer l'expédition",lambda:(currentOpportunity.Begin(),menu.disable(),openedMap.disable(),OpenMap()))
    
    SetTravelTime(True)
    
    menu.mainloop(UiManager.screen, DisplayBackground)

def CloseMap():
    global openedMap
    if openedMap != None:
        openedMap.disable()
        openedMap = None

def Tick()->bool:
    notedChange = False
    for opportunity in SaveManager.mainData.opportunities:
        if opportunity.state != Opportunity.State.PROPOSED:
            beginTime = datetime.fromisoformat(opportunity.beginTime)
            beginTime = beginTime.replace(minute=beginTime.minute+1)
            if datetime.now() > beginTime:
                print("done")
                opportunity.state = Opportunity.State.PROPOSED
                notedChange = True
    return notedChange

class Opportunity:
    
    class State:
        PROPOSED = 0
        GOING = 1
        ONSITE = 2
        RETURNING = 3
        RETURNED = 4
    
    def __init__(self):
        
        self.singular = choice([True,False])
        
        self.descCodes = {
            "people": randint(0, 4 if self.singular else 3),
            "prefix": randint(0, 1),
            "discover": randint(0, 4),
            "way": randint(0, 6),
            "place": randint(0, 8),
            "distance": randint(0, 4),
            "contains": randint(0, 6),
            "quantity": randint(0, 1),
            "ressource": choice(["Gold","Coal","Copper","Iron","M1"])
        }
        
        possibleTitles = []
        if self.descCodes["ressource"] == "Gold":
            possibleTitles.append(1)
        if self.descCodes["place"] == 4:
            possibleTitles.append(2)
        if self.descCodes["way"] == 1:
            possibleTitles.append(3)
        if self.descCodes["distance"] == 4:
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
        
        self.distance = [randint(100,400),randint(80,240),randint(8,28),randint(200,800),randint(400,2000)][self.descCodes["distance"]]
        
        self.state = Opportunity.State.PROPOSED
        
        self.beginTime = datetime.now().isoformat()
        
        self.resources = None
        
    def GetDesc(self):
        q = Localization.GetLoc("Opportunities.Quantity." + str(self.descCodes["quantity"]))
        r = Localization.GetLoc("Resources." + self.descCodes["ressource"])
        if FunctionUtils.IsVowel(r[0]):
            q = q[:-2] + "'"
        
        codes = [
            Localization.GetLoc("Opportunities.People." + ("Singular" if self.singular else "Plurial") + str(self.descCodes["people"])),
            Localization.GetLoc("Opportunities.Prefix." + ("Singular" if self.singular else "Plurial") + str(self.descCodes["prefix"])),
            Localization.GetLoc("Opportunities.Discover." + str(self.descCodes["discover"])),
            Localization.GetLoc("Opportunities.Way." + str(self.descCodes["way"])),
            Localization.GetLoc("Opportunities.Place." + str(self.descCodes["place"])),
            Localization.GetLoc("Opportunities.Distance." + str(self.descCodes["distance"])),
            Localization.GetLoc("Opportunities.Contains." + str(self.descCodes["contains"])),
            q,
            r,
            "."
        ]
        
        return "".join(codes)
        
    def GetTitle(self):
        return Localization.GetLoc("Opportunities.Title." + str(self.title))
    
    def GetDistance(self):
        return self.distance
    
    def GetWalkDistance(self):
        return self.distance//4
    
    def GetDriveDistance(self):
        return self.distance//40
    
    def Begin(self):
        self.state = Opportunity.State.GOING
        self.beginTime = datetime.now().isoformat()


