# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 15:26:04 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import pygame_menu

import random
from datetime import datetime, timedelta

import SettingsManager
import SaveManager
import UiManager
import FunctionUtils
import NoiseTools
import numpy
import Localization
import TextureManager
import PlanetGenerator
import OpportunitiesInteractions

openedMap = None

def OpenMap():
    global openedMap
    
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
        
        oppFrame = menu.add.frame_v(columnW, int(columnW * (5/18)), background_color=(50, 50, 50), padding=0, frame_id=str(opportunity.seed))
        oppFrame.relax(True)
        listFrame.pack(oppFrame)
        
        b = menu.add.button(FunctionUtils.ReduceStr(opportunity.GetTitle(), 30), lambda opp=opportunity:OpenOpportunity(opp),font_size=int(columnW/18),font_color=(255,255,255))
        
        FunctionUtils.EncapsulateButtonInFrame(b, oppFrame, buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        oppFrame.pack(menu.add.vertical_margin(int(columnW * (5/54))))
        
        subtext = menu.add.label("Temps de voyage: " + Opportunity.FormatTravelTime(opportunity.GetWalkDistance()), font_name=TextureManager.GetFont("nasalization",int(columnW/27)),font_color=(255,255,255))
        #subtext.set_font(TextureManager.nasalization, 11, (255,255,255), (255,255,255), (255,255,255), (255,255,255), (50,50,50))
        oppFrame.pack(subtext)
        
        listFrame.pack(menu.add.vertical_margin(5))
        
    
    def OpenOpportunity(opportunity):
        title.set_title(opportunity.GetTitle())
        SetLabelText(opportunity.GetDesc())
        global currentOpportunity
        currentOpportunity = opportunity
        RefreshMenu()
    
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
    
    btn = menu.add.button(Localization.GetLoc('Opportunities.StartAnExpedition'), ManageExpeditionAccordingly,font_size=int(h*(2/29)), button_id='oppButton')
    
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
    
    if len(SaveManager.mainData.opportunities) != 0:
        OpenOpportunity(SaveManager.mainData.opportunities[0])
    
    global runtime
    runtime = 0
    def MenuTick():
        global runtime
        SaveManager.clock.tick()
        runtime+=SaveManager.clock.get_time() / 8
        if Tick() or runtime > 50:
            runtime = 0
            RefreshMenu()
    
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),MenuTick()))

def RefreshMenu():
    if openedMap == None:
        return
    for opportunity in SaveManager.mainData.opportunities:
        
        frame = openedMap.get_widget(str(opportunity.seed), recursive=True)
        
        color = (50, 50, 50)
        
        if opportunity.state != Opportunity.State.PROPOSED:
            path = "Assets/textures/ui/orange.png"
            if opportunity.state == Opportunity.State.WAITING:
                path = "Assets/textures/ui/green.png"
            if opportunity.state == Opportunity.State.WORKING:
                path = "Assets/textures/ui/blue.png"
            if opportunity.state == Opportunity.State.RETURNED:
                path = "Assets/textures/ui/brown.png"
            color = pygame_menu.baseimage.BaseImage(path, drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')
        
        
        subText = "Temps de voyage: " + Opportunity.FormatTravelTime(opportunity.GetWalkDistance())
        
        if opportunity.state == Opportunity.State.GOING:
            subText = "Temps de voyage: " + Opportunity.FormatTravelTime(opportunity.GetLeftActivityTime())
        if opportunity.state == Opportunity.State.WAITING:
            subText = "L'expédition attend vos ordres..."
        if opportunity.state == Opportunity.State.WORKING:
            subText = "Temps de travail: " + Opportunity.FormatTravelTime(opportunity.GetLeftActivityTime())
        if opportunity.state == Opportunity.State.RETURNED:
            subText = "L'expédition est rentrée!"
        
        frame.get_widgets()[2].set_title(subText)
            
        frame.set_background_color(color)
    openedMap.force_surface_update()
    UpdateOppButtonTitle()

def ManageExpeditionAccordingly():
    
    if currentOpportunity == None:
        return
    
    if currentOpportunity.state == Opportunity.State.PROPOSED:
        #PlayExpeditionInteraction(currentOpportunity,InteractionType.ONSITE)
        OpenExpeditionLauncher()
    elif currentOpportunity.state == Opportunity.State.GOING:
        if not currentOpportunity.IsReturning():
            currentOpportunity.Recall()
            RefreshMenu()
    elif currentOpportunity.state == Opportunity.State.WAITING:
        if currentOpportunity.lastInterruption == currentOpportunity.GetTravelDuration():
            if currentOpportunity.IsReturning():
                PlayExpeditionInteraction(currentOpportunity,InteractionType.ONSITERESULT)
            else:
                PlayExpeditionInteraction(currentOpportunity,InteractionType.ONSITE)
        else:
            PlayExpeditionInteraction(currentOpportunity,InteractionType.INTERRUPTION)
        RefreshMenu()
    elif currentOpportunity.state == Opportunity.State.WORKING:
        pass
    else:
        currentOpportunity.Dissolve()
        RefreshMenu()

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
    
    memberSlider = menu.add.range_slider("Nombre de membres: ", 5, (2, 10), 1, value_format=lambda x: str(int(x)), align=pygame_menu.locals.ALIGN_LEFT)
    
    def SetTravelTime(Rover:bool):
        travelTimeLabel.set_title("Temps de route: " + Opportunity.FormatTravelTime(currentOpportunity.GetDriveDistance() if Rover else currentOpportunity.GetWalkDistance()))
    
    roverToggle = menu.add.toggle_switch('Moyen de transport', state_text=('A pied', 'Rover'), state_color=((100, 100, 100), (100, 100, 100)), onchange=SetTravelTime)
    
    travelTimeLabel = menu.add.label("")
    
    menu.add.vertical_margin(50)
    
    menu.add.button(Localization.GetLoc('Opportunities.StartExpedition'),lambda:(currentOpportunity.Begin(memberSlider.get_value(),roverToggle.get_value()),menu.disable(),RefreshMenu()))
    
    SetTravelTime(False)
    
    menu.mainloop(UiManager.screen, DisplayBackground)

def CloseMap():
    global openedMap
    if openedMap != None:
        openedMap.disable()
        openedMap = None

def UpdateOppButtonTitle():
    if openedMap != None:
        
        title = 'Opportunities.StartAnExpedition'
        if currentOpportunity.state == Opportunity.State.GOING:
            if currentOpportunity.IsReturning():
                title = "L'expédition rentre à la base..."
            else:
                title = 'Rappeler'
        elif currentOpportunity.state == Opportunity.State.WAITING:
            title = "Lire le rapport"
        elif currentOpportunity.state == Opportunity.State.WORKING:
            title = "L'expédition travaille..."
        elif currentOpportunity.state == Opportunity.State.RETURNED:
            title = "Dissoudre l'expédition"
        
        openedMap.get_widget('oppButton', recursive=True).set_title(Localization.GetLoc(title))

def Tick()->bool:
    notedChange = False
    for opportunity in SaveManager.mainData.opportunities:
        if opportunity.state not in [Opportunity.State.PROPOSED,Opportunity.State.WAITING,Opportunity.State.RETURNED]:
            
            beginTime = opportunity.GetBeginTime()
            
            duration = opportunity.GetActivityDuration()
            
            arrivalTime = beginTime + timedelta(seconds=duration)
            
            now = datetime.now()
            
            TravelAdvancement = duration - opportunity.GetLeftActivityTime()
            
            nextInterruption = opportunity.GetNextInterruption()
            
            if TravelAdvancement > nextInterruption > opportunity.lastInterruption:
                opportunity.RefreshActivitySeed()
                opportunity.SetState(Opportunity.State.WAITING)
                opportunity.lastInterruption = nextInterruption
                UiManager.Popup("Opportunité interrompue!")
                notedChange = True
            
            if now > arrivalTime:
                if opportunity.state == Opportunity.State.GOING:
                    if opportunity.IsReturning():
                        opportunity.SetState(Opportunity.State.RETURNED)
                    else:
                        opportunity.SetState(Opportunity.State.WAITING)
                        opportunity.lastInterruption = opportunity.GetTravelDuration()
                    
                elif opportunity.state == Opportunity.State.WORKING:
                    lastInterruption = opportunity.lastInterruption
                    opportunity.SetState(Opportunity.State.WAITING)
                    opportunity.lastInterruption = lastInterruption
                    opportunity.Recall()
                notedChange = True
    return notedChange

class Opportunity:
    """
    Classe permettant de stocker et gérer les opportunités
    """
    
    class State:
        """
        Les différents états d'opportunités
        """
        PROPOSED = 0
        GOING = 1
        WAITING = 2
        WORKING = 3
        RETURNED = 4
    
    def __init__(self):
        
        self.seed = random.randint(-9**9, 9**9)
        
        self.activitySeed = random.randint(-9**9, 9**9)
        
        self.distance = [random.randint(100,400),random.randint(80,240),random.randint(8,28),random.randint(200,800),random.randint(400,2000)][self.GetDescCodes()["distance"]]
        
        self.state = Opportunity.State.PROPOSED
        
        self.returning = False
        
        self.beginTime = datetime.now().isoformat()
        
        self.activityDuration = 0
        
        self.team = {
            "members" : 5,
            "onRover" : False
        }
        
        self.lastInterruption = 0
        self.lastChoiceMade = None
        
        self.resources = None
        
    def GetDescCodes(self)->dict:
        """
        Renvoie les codes de description. Utilisé pour générer la description et le titre de l'opportunité
        """
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
        
        
    def GetDesc(self)->str:
        """
        Renvoie la description de l'opportunité
        """
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
    
    def GetTitle(self)->str:
        """
        Renvoie le titre de l'opportunité
        """
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
    
    def GetDistance(self)->int:
        """
        Renvoie la distance brute en kilomètres
        """
        return self.distance
    
    def GetWalkDistance(self)->int:
        """
        Renvoie le temps de marche en heures
        """
        return self.GetDistance()//4
    
    def GetDriveDistance(self)->int:
        """
        Renvoie le temps de route en heures
        """
        return self.GetDistance()//40
    
    def GetTravelDuration(self)->int:
        """
        Renvoie le temps de trajet en heures
        """
        return self.GetDriveDistance() if self.IsOnRover() else self.GetWalkDistance()
    
    def FormatTravelTime(travelTime:int)->str:
        """
        Renvoie un temps de trajet formatté
        """
        hours = travelTime%24
        days = travelTime//24
        
        result = ""
        
        if days > 0:
            result += str(days) + " " + ("jour" if days == 1 else "jours")
        if hours > 0:
            if days > 0:
                result += " "
            result += str(hours) + " " + ("heure" if hours == 1 else "heures")
        
        return result
    
    def GetActivityDuration(self)->int:
        """
        Renvoie la durée de l'activité actuelle
        """
        return self.activityDuration
    
    def SetActivityDuration(self,duration:int):
        """
        Règle la durée de l'activité actuelle
        """
        self.activityDuration = duration
    
    def GetLeftActivityTime(self)->int:
        """
        Renvoie le temps d'activité restant
        """
        beginTime = self.GetBeginTime()
        now = datetime.now()
        return self.GetActivityDuration() - round((now-beginTime).total_seconds())
    
    def RefreshActivitySeed(self):
        """
        Met à jour la graine d'activité
        """
        random.seed(self.activitySeed)
        self.activitySeed = random.randint(-9**9, 9**9)
    
    def Begin(self,teamMembers=5,onRover=False):
        """
        Lance l'opportunité
        """
        self.team["members"] = teamMembers
        self.team["onRover"] = onRover
        self.SetState(Opportunity.State.GOING)
        self.SetActivityDuration(self.GetTravelDuration())

    def GetNextInterruption(self)->float:
        """
        Renvoie à quel moment la prochaine interruption aura lieu
        """
        random.seed(self.activitySeed)
        
        if random.choice((True,False)):
            return random.randint(0, self.GetActivityDuration())
        return 0

    def SetState(self,state):
        """
        Règle l'état de l'opportunité
        """
        self.state = state
        self.SetBeginTime(datetime.now())
        self.RefreshActivitySeed()
        self.lastInterruption = 0
        
    def IsTravelling(self)->bool:
        """
        Dit si l'expédition est en train de voyager
        """
        return self.state == Opportunity.State.GOING
    
    def GetBeginTime(self)->datetime:
        """
        Renvoie la date de l'ordinateur au début de l'activité actuelle
        """
        return datetime.fromisoformat(self.beginTime)
    
    def SetBeginTime(self,date:datetime):
        """
        Règle la date de l'ordinateur au début de l'activité actuelle
        """
        self.beginTime = date.isoformat()
    
    def Recall(self):
        """
        Rappelle l'expédition.
        Elle ne revient pas directement à la base, mais la destination du prochain trajet (ou du trajet actuel) sera la base.
        """
        if self.IsTravelling() and not self.IsReturning():
            self.SetActivityDuration(self.GetActivityDuration() - self.GetLeftActivityTime())
            self.SetBeginTime(datetime.now())
        self.returning = True
        
    def Dissolve(self):
        """
        Dissout l'expédition et transfère ses membres et ses ressources vers la base.
        """
        self.SetState(Opportunity.State.PROPOSED)
        self.SetActivityDuration(0)
        self.returning = False
        self.resources = None
        self.team["members"] = 5
        self.team["onRover"] = False

    def GetMembersAmount(self):
        """
        Renvoie le nombre de membres de l'expédition
        """
        return self.team["members"]

    def IsOnRover(self)->bool:
        """
        Dit si l'expédition se déplace en rover
        """
        return self.team["onRover"]

    def IsReturning(self)->bool:
        """
        Dit si l'expédition est sur le chemin du retour
        """
        return self.returning

    def GetLastChoiceMade(self)->int:
        """
        Renvoie le dernier choix fait.
        Si aucun choix n'a été fait ou si le joueur a déjà prit conaissance des conséquences de son choix, cette fonction renverra None.
        """
        return self.lastChoiceMade
    
    def SetLastChoiceMade(self,choiceIndex:int):
        """
        Définit le dernier choix fait par le joueur.
        """
        self.lastChoiceMade = choiceIndex

class InteractionType:
    """
    Les différents types d'interactions
    """
    ONSITE=0
    ONSITERESULT=1
    INTERRUPTION=2
    INTERRUPTIONRESULT=3
    

def PlayExpeditionInteraction(opportunity,interactionType:int):
    """
    Ouvre un menu permettant d'interagir avec les opportunités
    """
    interaction = OpportunitiesInteractions.GetRandomInteraction(opportunity, interactionType)
    
    if interactionType in [InteractionType.ONSITERESULT,InteractionType.INTERRUPTIONRESULT]:
        
        interaction.GetOptions()[opportunity.lastChoiceMade][1](opportunity)
        
        opportunity.SetLastChoiceMade(None)
        
        return
    
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    background = pygame.display.get_surface().copy()
    background.blit(screenFilter,(0,0))
    def DisplayBackground():
        UiManager.screen.blit(background,(0,0))
    
    menu = pygame_menu.Menu(currentOpportunity.GetTitle(), 800, 600, theme=pygame_menu.themes.THEME_DARK,onclose=pygame_menu.events.BACK)#le thème du menu
    
    srf = interaction.GetImage()
    srf = pygame.transform.scale(srf,(550,srf.get_height()*550/srf.get_width()))
    
    menu.add.surface(srf)
    
    label = menu.add.label("\n\n\n\n\n\n",font_size=15)
    
    lines = interaction.GetMessage().split("\n")
    for i in range(7):
        if i < len(lines):
            label[i].set_title(lines[i])
        else:
            label[i].set_title('')
    
    #SetLabelText("Voici une longue description de ce qui attend l'expédition.\nDe nombreux détails peuvent être fournis afin de donner un rendu sympa.\nCa le fait?")
    
    menu.add.vertical_margin(5)
    
    bottomBar=menu.add.frame_h(400, 50, padding=0)
    bottomBar.relax(True)
    """
    bottomBar.pack(menu.add.button("Action 1",font_size=20),align=pygame_menu.locals.ALIGN_CENTER)
    bottomBar.pack(menu.add.button("Action 2",font_size=20),align=pygame_menu.locals.ALIGN_CENTER)
    bottomBar.pack(menu.add.button("Action 3",font_size=20),align=pygame_menu.locals.ALIGN_CENTER)
    """
    
    options = interaction.GetOptions()
    
    for i in range(len(options)):
        option = options[i]
        
        
        activityTime = None
        if interactionType == InteractionType.ONSITE:
            activityTime = option[2]
            if type(activityTime) == tuple:
                activityTime = random.randint(activityTime[0], activityTime[1])
        
        if interactionType == InteractionType.INTERRUPTION or activityTime == None:
            result = lambda res=option[1]:(menu.disable(),res(opportunity))
        else:
            
            def BeginOnSiteActivity(opportunity,duration:int):
                lastInterruption = opportunity.lastInterruption
                opportunity.SetState(Opportunity.State.WORKING)
                opportunity.lastInterruption = lastInterruption
                opportunity.SetActivityDuration(duration)
            
            result = lambda choice=i,t=activityTime:(menu.disable(),opportunity.SetLastChoiceMade(choice),BeginOnSiteActivity(opportunity,activityTime))
        
        bottomBar.pack(menu.add.button(option[0],result,font_size=20),align=pygame_menu.locals.ALIGN_CENTER)
    
    menu.mainloop(UiManager.screen, DisplayBackground)







