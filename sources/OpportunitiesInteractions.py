# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 12:39:53 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import pygame_menu

from datetime import datetime, timedelta
import random

import TextureManager
import OpportunitiesManager
import UiManager
import Localization
import SaveManager
import PlanetGenerator


class OpportunityInteraction:
    """
    Classe permettant de stocker des modèles d'interactions avec le message, l'image, les tags associés et les différentes options et leurs résultats.
    
    Format des tags:
        {ONROVER:True,DESERTICPLANET:False,MAXMEMBERS:5}
    
    Format des options d'interruptions:
        ("Revenir à la base",lambda o: InteractionResult.ReturnToBase(o)),
        ("Continuer",lambda o: InteractionResult.AddDistanceToPath(o, 15)),
    
    C'est un tuple avec comme première valeur le texte du bouton et seconde valeur le code à exécuter lorsque le bouton est pressé.
    
    Format des options sur site:
        ("Explorer la zone moins de 5h",lambda o:InteractionResult.OpenResultPanel(o,"L'expédition a exploré la zone, sans résultat.","interactionBackgrounds/impactCrater"),(3,5)),
        ("Explorer la zone pendant 10h",lambda o:InteractionResult.OpenResultPanel(o,"L'expédition a trouvé des ressources!","interactionBackgrounds/impactCrater"),10),
        ("Faire demi tour",lambda o:InteractionResult.ReturnToBase(o),None),
        
    Comme les interruptions, sauf qu'une troisième valeur vient s'y attacher. Elle peut être:
        -Un entier, pour symboliser une durée stricte de l'activité
        -Un tuple, pour pouvoir choisir une durée aléatoire entre les deux
        -None, pour pouvoir exécuter directement le code au lieu de faire une activité
    
    Attention: TOUT doit être précisé. Si à la fin d'une activité sur site vous ne précisez pas que l'expédition doit repartir, rien ne se passe.
    Même chose si vous ne précisez pas que l'équipe doit continuer son trajet après une interruption.
    """
    
    def __init__(self,message:str,imagePath:str,tags:dict,*args):
        self.message = message
        self.imagePath = imagePath
        self.tags = tags
        self.options = args
    
    def GetMessage(self):
        """
        Renvoie le message à afficher
        """
        return Localization.GetLoc(self.message)
    
    def GetOptions(self):
        """
        Renvoie les différentes options
        """
        return self.options
    
    def AppliesTo(self,opportunity,oppDescCodes:list=None)->bool:
        """
        Dit si l'interaction s'applique à une opportunité en fonction des tags
        """
        if oppDescCodes == None:
            oppDescCodes = opportunity.GetDescCodes()
        
        applies = True
        """
        if Tags.ONROVER in oppDescCodes:
            if oppDescCodes[Tags.ONROVER] != opportunity.IsOnRover():
                applies = False
        
        if Tags.DEADPLANET in oppDescCodes:
                if oppDescCodes[Tags.DEADPLANET] != (SaveManager.GetEnvironmentType() == PlanetGenerator.PlanetTypes.Dead):
                    applies = False
        
        if Tags.DESERTICPLANET in oppDescCodes:
                if oppDescCodes[Tags.DESERTICPLANET] != (SaveManager.GetEnvironmentType() == PlanetGenerator.PlanetTypes.Desertic):
                    applies = False
        
        if Tags.LIVINGPLANET in oppDescCodes:
                if oppDescCodes[Tags.LIVINGPLANET] != (SaveManager.GetEnvironmentType() == PlanetGenerator.PlanetTypes.EarthLike):
                    applies = False
        
        if Tags.MINMEMBERS in oppDescCodes:
            if oppDescCodes[Tags.MINMEMBERS] > opportunity.GetMembersAmount():
                applies = False
        
        if Tags.MAXMEMBERS in oppDescCodes:
                if oppDescCodes[Tags.MAXMEMBERS] < opportunity.GetMembersAmount():
                    applies = False
        """
        return applies
    
    def GetImage(self):
        """
        Renvoie l'image de l'interaction
        """
        return TextureManager.GetTexture(self.imagePath,is_menu=True)


class Tags:
    """
    Les différents tags d'interaction existants.
    """
    ONROVER=0#bool
    DEADPLANET=1#bool
    DESERTICPLANET=2#bool
    LIVINGPLANET=3#bool
    MINMEMBERS=4#int
    MAXMEMBERS=5#int


class InteractionResult:
    """
    Les différentes fonctions résultat des interactions des opportunités. Ont vocation à être stockées dans des lambdas pour utilisation dans les option d'un objet OpportunityInteraction.
    """
    
    locCodes = {}#Stocke temporairement des valeurs à passer à localization.getloc dans les fonctions ci dessous avec des IDs
    
    def AddDistanceToPath(opportunity,distance:int):
        """
        Ajoute de la distance au trajet aller retour.
        Utile pour simuler un obstacle à contourner ou alors, avec une distance négative, simuler un raccourci.
        """
        opportunity.distance += distance
        
    def SetOnRover(opportunity,onRover:bool):
        """
        Règle le moyen de transport et adapte la durée du trajet en conséquence.
        Utile pour simuler l'abandon ou la découverte d'un rover.
        """
        alreadyOnRover = opportunity.IsOnRover()
        
        if alreadyOnRover == onRover:
            return
        
        opportunity.team["onRover"] = onRover
        
        if opportunity.state == OpportunitiesManager.Opportunity.State.GOING:
            
            TravelAdvancement = opportunity.GetActivityDuration() - opportunity.GetLeftActivityTime()
            
            if onRover:
                opportunity.SetBeginTime(datetime.now() - timedelta(seconds=TravelAdvancement//4))
                opportunity.SetActivityDuration(opportunity.GetActivityDuration()//4)
            else:
                opportunity.SetBeginTime(datetime.now() - timedelta(seconds=TravelAdvancement*4))
                opportunity.SetActivityDuration(opportunity.GetActivityDuration()*4)
    
    def AddMembers(opportunity,amount:int):
        """
        Ajoute des membres à l'équipe.
        Utile pour simuler des membres intégrés à l'équipe ou alors, avec un nombre négatif, des membres abandonnés.
        """
        opportunity.team["members"] += amount

    def EndExpedition(opportunity,recoverTeam:bool):
        """
        Met directement fin à l'expédition.
        Utile pour simuler une catastrophe ayant mis fin à la vie de l'équipe ou pour simuler sa récupération par une autre équipe.
        """
        if recoverTeam:
            opportunity.Dissolve()
            return
        
        opportunity.SetState(OpportunitiesManager.Opportunity.State.PROPOSED)
        opportunity.SetActivityDuration(0)
        opportunity.returning = False
        opportunity.resources = {}
        opportunity.team["members"] = 5
        opportunity.team["onRover"] = False

    def ReturnToBase(opportunity):
        """
        Met l'expédtion sur le chemin du retour, indépendamment du contexte.
        """
        if not opportunity.IsTravelling():
            opportunity.returning = True
            opportunity.SetState(OpportunitiesManager.Opportunity.State.GOING)
            opportunity.SetActivityDuration(opportunity.GetTravelDuration())
        else:
            opportunity.Recall()

    def ResumeTravel(opportunity):
        """
        Permet de reprendre le trajet après une interruption.
        """
        lastInterruption = opportunity.lastInterruption
        opportunity.SetState(OpportunitiesManager.Opportunity.State.GOING)
        opportunity.SetBeginTime(datetime.now() - timedelta(seconds=lastInterruption))

    def DoWithChance(opportunity,chance:float,success,defeat=None):
        """
        Permet d'exécuter une fonction résultat avec une probabilité entre 0 et 1, et une autre en cas d'échet si besoin
        """
        #random.seed(opportunity.activitySeed)
        if random.uniform(0,1) < chance:
            success(opportunity)
        elif defeat != None:
            defeat(opportunity)
    
    def AddResourceToInv(opportunity,rName:str,amount:int,amountCode:str=None):
        """
        Permet d'ajouter ou de retirer des ressources de l'inventaire de l'expédition.
        Utile pour simuler la découverte de ressources ou leur perte.
        amount peut être un entier ou un tuple pour une quantité aléatoire de resources (bornes inclues)
        """
        if not rName in opportunity.resources:
            opportunity.resources[rName] = 0
        
        if type(amount) == tuple:
            amount = random.randint(amount[0], amount[1])
        
        if amountCode != None:
            InteractionResult.locCodes[amountCode] = amount
        
        opportunity.resources[rName] += amount
        
        if opportunity.resources[rName] <= 0:
            opportunity.resources.pop(rName)
    
    def OpenResultPanel(opportunity,message:str,imagePath:str,*args):
        """
        Ouvre un panneau de résultat d'interaction.
        """
        screenFilter = pygame.Surface((UiManager.width,UiManager.height))
        screenFilter.set_alpha(50)
        background = pygame.display.get_surface().copy()
        background.blit(screenFilter,(0,0))
        def DisplayBackground():
            UiManager.screen.blit(background,(0,0))
        
        menu = pygame_menu.Menu(opportunity.GetTitle(), 800, 600, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
        
        srf = TextureManager.GetTexture(imagePath,is_menu=True)
        srf = pygame.transform.scale(srf,(550,srf.get_height()*550/srf.get_width()))
        
        menu.add.surface(srf)
        
        label = menu.add.label("\n\n\n\n\n\n",font_size=15)
        
        lines = Localization.GetLoc(message,*[InteractionResult.locCodes.get(code,code) for code in args]).split("\n")
        for i in range(7):
            if i < len(lines):
                label[i].set_title(lines[i])
            else:
                label[i].set_title('')
        
        menu.add.vertical_margin(5)
        
        menu.add.button(Localization.GetLoc('Game.Ok'), menu.disable, font_size=20)
        
        menu.mainloop(UiManager.screen, DisplayBackground)

onSiteInteractions=[
    OpportunityInteraction("OppInteractions.OnSite.1", "interactionBackgrounds/impactCrater",
                           {},
                           ("OppInteractions.OnSite.1.b1",
                            lambda o:(InteractionResult.OpenResultPanel(o,"OppInteractions.OnSite.1.b1.1","interactionBackgrounds/walkingDesert"),
                                      InteractionResult.ReturnToBase(o)),
                            None),
                           ("OppInteractions.OnSite.1.b2",
                            lambda o:(InteractionResult.OpenResultPanel(o,"OppInteractions.OnSite.1.b2.1","interactionBackgrounds/walkingDesert"),
                                      InteractionResult.ReturnToBase(o)),
                            (3,5)),
                           ("OppInteractions.OnSite.1.b3",
                            lambda o:(InteractionResult.OpenResultPanel(o,"OppInteractions.OnSite.1.b3.1","interactionBackgrounds/meteor"),
                                      InteractionResult.EndExpedition(o,False)),
                            24),
                           ),
    OpportunityInteraction("OppInteractions.OnSite.2", "interactionBackgrounds/greenValley",
                           {Tags.LIVINGPLANET:True},
                           ("OppInteractions.OnSite.2.b1",
                            lambda o:(InteractionResult.AddResourceToInv(o, "Copper", (150,400),"rAmount"),
                                      InteractionResult.OpenResultPanel(o,"OppInteractions.OnSite.2.b1.1","interactionBackgrounds/mineJungle","rAmount"),
                                      InteractionResult.ReturnToBase(o)),
                            (20,30)),
                           ("OppInteractions.OnSite.2.b2",
                            lambda o:(InteractionResult.AddResourceToInv(o, "Copper", (50,90),"rAmount"),
                                      InteractionResult.OpenResultPanel(o,"OppInteractions.OnSite.2.b2.1","interactionBackgrounds/greenValley","rAmount"),
                                      InteractionResult.ReturnToBase(o)),
                            (10,15)),
                           ),
]

interruptionInteractions=[
    OpportunityInteraction("OppInteractions.Interruption.1", "interactionBackgrounds/sandstorm",
                           {Tags.ONROVER:True,Tags.DESERTICPLANET:True},
                           ("OppInteractions.Interruption.1.b1",
                            lambda o:(InteractionResult.SetOnRover(o, False),
                                      InteractionResult.OpenResultPanel(o,"OppInteractions.Interruption.1.b1.1","interactionBackgrounds/walkingDesert"),
                                      InteractionResult.ResumeTravel(o))),
                           ("OppInteractions.Interruption.1.b2",
                            lambda o:(InteractionResult.DoWithChance(o,0.1,
                                lambda o:(InteractionResult.SetOnRover(o, False),
                                          InteractionResult.OpenResultPanel(o,"OppInteractions.Interruption.1.b2.1","interactionBackgrounds/walkingDesert")),
                                lambda o: InteractionResult.OpenResultPanel(o,"OppInteractions.Interruption.1.b2.2","interactionBackgrounds/roverDesert")),
                                      InteractionResult.ResumeTravel(o)))
                           ),
    OpportunityInteraction("OppInteractions.Interruption.2", "interactionBackgrounds/blockedWay",
                           {Tags.ONROVER:False},
                           ("OppInteractions.Interruption.2.b1",
                            lambda o:(InteractionResult.AddDistanceToPath(o, 3),
                                      InteractionResult.OpenResultPanel(o,"OppInteractions.Interruption.2.b1.1","interactionBackgrounds/walkingDesert"),
                                      InteractionResult.ResumeTravel(o))),
                           ("OppInteractions.Interruption.2.b2",
                            lambda o:(InteractionResult.DoWithChance(o,0.4,
                                lambda o:(InteractionResult.AddMembers(o, -1),
                                          InteractionResult.OpenResultPanel(o,"OppInteractions.Interruption.2.b2.1","interactionBackgrounds/falling")),
                                lambda o: InteractionResult.OpenResultPanel(o,"OppInteractions.Interruption.2.b2.2","interactionBackgrounds/walkingDesert")),
                                      InteractionResult.ResumeTravel(o)))
                           ),
]


def GetRandomInteractionCode(opportunity,InteractionType:int)->int:
    """
    Renvoie le code d'une interaction aléatoire.
    """
    if InteractionType in [OpportunitiesManager.InteractionType.ONSITE,OpportunitiesManager.InteractionType.ONSITERESULT]:
        
        i = random.randint(0, len(onSiteInteractions)-1)
        
        oppDescCodes = opportunity.GetDescCodes()
        
        while not onSiteInteractions[i].AppliesTo(opportunity,oppDescCodes):
            i = random.randint(0, len(onSiteInteractions)-1)
        
        return i
    
    elif InteractionType in [OpportunitiesManager.InteractionType.INTERRUPTION,OpportunitiesManager.InteractionType.INTERRUPTIONRESULT]:
        
        i = random.randint(0, len(interruptionInteractions)-1)
        
        oppDescCodes = opportunity.GetDescCodes()
        
        while not interruptionInteractions[i].AppliesTo(opportunity,oppDescCodes):
            i = random.randint(0, len(interruptionInteractions)-1)
        
        return i


def GetInteractionByCode(code:int,InteractionType:int)->OpportunityInteraction:
    """
    Renvoie une interaction par son type et son code.
    """
    if InteractionType in [OpportunitiesManager.InteractionType.ONSITE,OpportunitiesManager.InteractionType.ONSITERESULT]:
        return onSiteInteractions[code]
    else:
        return interruptionInteractions[code]
