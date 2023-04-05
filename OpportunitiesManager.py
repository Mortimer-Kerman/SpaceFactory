# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 15:26:04 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import pygame_menu

import random
from datetime import datetime

import SettingsManager
import SaveManager
import UiManager
import FunctionUtils
import NoiseTools
import numpy
import Localization
import TextureManager
import PlanetGenerator

openedMap = None
background = None

def OpenMap():
    global openedMap
    global background
    
    alreadyOpen = False
    translateVal = 0
    if openedMap == None:
        screenFilter = pygame.Surface((UiManager.width,UiManager.height))
        screenFilter.set_alpha(50)
        background = pygame.display.get_surface().copy()
        background.blit(screenFilter,(0,0))
    else:
        translateVal = openedMap.get_widget('oppList', recursive=True).get_scroll_value_percentage(pygame_menu.locals.ORIENTATION_VERTICAL)
        alreadyOpen = True
    
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
    
    listFrame = menu.add.frame_v(columnW, max(len(SaveManager.mainData.opportunities) * (int(columnW * (5/18)) + 5), h), max_height=h, padding=0, frame_id='oppList')
    listFrame.relax(True)
    frame.pack(listFrame, align=pygame_menu.locals.ALIGN_LEFT)
    
    global currentOpportunity
    if not alreadyOpen:
        currentOpportunity = None
    
    for opportunity in SaveManager.mainData.opportunities:
        
        color = (50, 50, 50)
        
        if opportunity.state != Opportunity.State.PROPOSED:
            path = "Assets/textures/ui/orange.png"
            if opportunity.state == Opportunity.State.ONSITE:
                path = "Assets/textures/ui/green.png"
            if opportunity.state == Opportunity.State.RETURNING:
                path = "Assets/textures/ui/blue.png"
            if opportunity.state == Opportunity.State.RETURNED:
                path = "Assets/textures/ui/brown.png"
            color = pygame_menu.baseimage.BaseImage(path, drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')
        
        oppFrame = menu.add.frame_v(columnW, int(columnW * (5/18)), background_color=color, padding=0, frame_id=str(opportunity.seed))
        oppFrame.relax(True)
        listFrame.pack(oppFrame)
        
        b = menu.add.button(FunctionUtils.ReduceStr(opportunity.GetTitle(), 30), lambda opp=opportunity:OpenOpportunity(opp),font_size=int(columnW/18),font_color=(255,255,255))
        
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
        
        subtext = menu.add.label("Temps de voyage: " + distance, font_name=TextureManager.GetFont("nasalization",int(columnW/27)),font_color=(255,255,255))
        #subtext.set_font(TextureManager.nasalization, 11, (255,255,255), (255,255,255), (255,255,255), (255,255,255), (50,50,50))
        oppFrame.pack(subtext)
        
        listFrame.pack(menu.add.vertical_margin(5))
        
        if alreadyOpen and opportunity == currentOpportunity:
            b.select(update_menu=True)
    
    def OpenOpportunity(opportunity):
        title.set_title(opportunity.GetTitle())
        SetLabelText(opportunity.GetDesc())
        global currentOpportunity
        currentOpportunity = opportunity
    
    detailsFrame = menu.add.frame_v(columnW, h, max_height=h, padding=0)
    detailsFrame.relax(True)
    frame.pack(detailsFrame)
    
    textFrame = menu.add.frame_v(columnW, h-50-int(h*(2/29)), max_height=h-50-int(h*(2/29)), padding=0)
    textFrame.relax(True)
    detailsFrame.pack(textFrame,align=pygame_menu.locals.ALIGN_CENTER)
    
    title = menu.add.label("",font_size=int(columnW*(2/29)))#40 en 1080
    textFrame.pack(title,align=pygame_menu.locals.ALIGN_CENTER)
    
    label = menu.add.label("\n\n\n\n\n",font_size=int(columnW*(1/29)))#20 en 1080
    textFrame.pack(label)
    
    btn = menu.add.button(Localization.GetLoc('Opportunities.StartAnExpedition'), OpenExpeditionLauncher,font_size=int(h*(2/29)))
    
    detailsFrame.pack(btn,align=pygame_menu.locals.ALIGN_CENTER)
    
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
    
    if alreadyOpen:
        listFrame.scrollv(translateVal)
        OpenOpportunity(currentOpportunity)
    elif len(SaveManager.mainData.opportunities) != 0:
        OpenOpportunity(SaveManager.mainData.opportunities[0])
    
    def MenuTick():
        if Tick():
            RefreshMenu()
    
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),MenuTick()))

def RefreshMenu():
    if openedMap == None:
        return
    #openedMap.disable()
    #OpenMap()
    for opportunity in SaveManager.mainData.opportunities:
        
        frame = openedMap.get_widget(str(opportunity.seed), recursive=True)
        
        color = (50, 50, 50)
        
        if opportunity.state != Opportunity.State.PROPOSED:
            path = "Assets/textures/ui/orange.png"
            if opportunity.state == Opportunity.State.ONSITE:
                path = "Assets/textures/ui/green.png"
            if opportunity.state == Opportunity.State.RETURNING:
                path = "Assets/textures/ui/blue.png"
            if opportunity.state == Opportunity.State.RETURNED:
                path = "Assets/textures/ui/brown.png"
            color = pygame_menu.baseimage.BaseImage(path, drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')
            
        frame.set_background_color(color)
        
    openedMap.force_surface_update()

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
    
    menu.add.button(Localization.GetLoc('Opportunities.StartExpedition'),lambda:(currentOpportunity.Begin(),menu.disable(),RefreshMenu()))
    
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
            beginTime = beginTime.replace(second=(beginTime.second+5)%60)
            now = datetime.now()
            if now > beginTime:
                if opportunity.state == Opportunity.State.GOING:
                    opportunity.state = Opportunity.State.ONSITE
                elif opportunity.state == Opportunity.State.ONSITE:
                    opportunity.state = Opportunity.State.RETURNING
                elif opportunity.state == Opportunity.State.RETURNING:
                    opportunity.state = Opportunity.State.RETURNED
                else:
                    opportunity.state = Opportunity.State.PROPOSED
                
                opportunity.beginTime = now.isoformat()
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
        
        self.seed = random.randint(-9**9, 9**9)
        
        self.distance = [random.randint(100,400),random.randint(80,240),random.randint(8,28),random.randint(200,800),random.randint(400,2000)][self.GetDescCodes()["distance"]]
        
        self.state = Opportunity.State.PROPOSED
        
        self.beginTime = datetime.now().isoformat()
        
        self.resources = None
        
    def GetDescCodes(self)->dict:
        
        random.seed(self.seed)
        
        singular = random.choice([True,False])
        
        places = [0,1,2,4,5,7,8]
        
        if SaveManager.GetEnvironmentType() == PlanetGenerator.PlanetTypes.EarthLike:
            places += [3,6]
        
        return {
            "singular" : singular,
            "people": random.randint(0, 4 if singular else 3),
            "prefix": random.randint(0, 1),
            "discover": random.randint(0, 4),
            "way": random.randint(0, 6),
            "place": random.choice(places),
            "distance": random.randint(0, 4),
            "contains": random.randint(0, 6),
            "quantity": random.randint(0, 1),
            "ressource": random.choice(["Gold","Coal","Copper","Iron","M1"])
        }
        
        
    def GetDesc(self):
        
        descCodes = self.GetDescCodes()
        
        q = Localization.GetLoc("Opportunities.Quantity." + str(descCodes["quantity"]))
        r = Localization.GetLoc("Resources." + descCodes["ressource"])
        if FunctionUtils.IsVowel(r[0]):
            q = q[:-2] + "'"
        
        codes = [
            Localization.GetLoc("Opportunities.People." + ("Singular" if descCodes["singular"] else "Plurial") + str(descCodes["people"])),
            Localization.GetLoc("Opportunities.Prefix." + ("Singular" if descCodes["singular"] else "Plurial") + str(descCodes["prefix"])),
            Localization.GetLoc("Opportunities.Discover." + str(descCodes["discover"])),
            Localization.GetLoc("Opportunities.Way." + str(descCodes["way"])),
            Localization.GetLoc("Opportunities.Place." + str(descCodes["place"])),
            Localization.GetLoc("Opportunities.Distance." + str(descCodes["distance"])),
            Localization.GetLoc("Opportunities.Contains." + str(descCodes["contains"])),
            q,
            r,
            "."
        ]
        
        return "".join(codes)
    
    def GetTitle(self):
        
        descCodes = self.GetDescCodes()
        
        possibleTitles = []
        if descCodes["ressource"] == "Gold":
            possibleTitles.append(1)
        if descCodes["place"] == 4:
            possibleTitles.append(2)
        if descCodes["way"] == 1:
            possibleTitles.append(3)
        if descCodes["distance"] == 4:
            possibleTitles.append(4)
        if descCodes["way"] == 2 or descCodes["way"] == 4:
            possibleTitles.append(5)
        if descCodes["way"] == 5:
            possibleTitles.append(6)
        if descCodes["way"] == 0:
            possibleTitles.append(7)
        if len(possibleTitles) == 0:
            possibleTitles.append(0)
        
        return Localization.GetLoc("Opportunities.Title." + str(random.choice(possibleTitles)))
    
    def GetDistance(self):
        return self.distance
    
    def GetWalkDistance(self):
        return self.GetDistance()//4
    
    def GetDriveDistance(self):
        return self.GetDistance()//40
    
    def Begin(self):
        self.state = Opportunity.State.GOING
        self.beginTime = datetime.now().isoformat()


