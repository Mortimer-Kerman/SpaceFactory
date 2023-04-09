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


class OpportunityInteraction:
    """
    Classe permettant de stocker des modèles d'interactions avec le message, l'image, les tags associés et les différentes options et leurs résultats.
    
    Format des tags:
        {ONROVER:True,DESERTICPLANET:False,MAXMEMBERS:5}
    
    Format des options d'interruptions:
        ("Revenir à la base",lambda o: InteractionResult.ReturnToBase(o)),
        ("Continuer",lambda o: InteractionResult.AddDistanceToPath(o, 15)),
    
    Format des options sur site:
        ("Explorer la zone pendant 5h",lambda o:InteractionResult.OpenResultPanel(o,"L'expédition a exploré la zone, sans résultat.","interactionBackgrounds/impactCrater"),5),
        ("Explorer la zone pendant 10h",lambda o:InteractionResult.OpenResultPanel(o,"L'expédition a trouvé des ressources!","interactionBackgrounds/impactCrater"),10),
        ("Faire demi tour",lambda o:InteractionResult.ReturnToBase(o),None),
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
    
    def AppliesTo(self,opportunity)->bool:
        """
        Dit si l'interaction s'applique à une opportunité en fonction des tags
        """
        return True
    
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
            
    def OpenResultPanel(opportunity,message:str,imagePath:str):
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
        
        lines = message.split("\n")
        for i in range(7):
            if i < len(lines):
                label[i].set_title(lines[i])
            else:
                label[i].set_title('')
        
        menu.add.vertical_margin(5)
        
        menu.add.button(Localization.GetLoc('Game.Ok'), menu.disable, font_size=20)
        
        menu.mainloop(UiManager.screen, DisplayBackground)

onSiteInteractions=[
    OpportunityInteraction("L'équipe de reconnaissance est arrivée à hauteur du bassin d'impact!\nCependant, une gigantesque masse ferreuse au centre du bassin provoque un champ magnétique qui brouille\ntous les signaux radio. Au moment où l'équipe entrera dans la zone, elle perdra toute connexion avec la\nbase. Si elle s'aventure longtemps dans la zone, elle ne pourra donc pas être prévenue en cas de\ndanger, mais pourra peut-être découvrir plus de choses. Elle peut également rentrer et revenir plus tard.\n\nQue faire ?", "interactionBackgrounds/impactCrater",
                           {Tags.DEADPLANET:True},
                           ("Rebrousser chemin",
                            lambda o:InteractionResult.ReturnToBase(o),
                            None),
                           ("Explorer la zone pendant 5h",
                            lambda o:(InteractionResult.OpenResultPanel(o,"L'expédition a exploré la zone, sans résultat.","interactionBackgrounds/impactCrater"),
                                      InteractionResult.ReturnToBase(o)),
                            5),
                           ),
]

interruptionInteractions=[
    OpportunityInteraction("L'expédition est prise dans une tempête de sable!\nLa visibilité est nulle, la progression est au point mort et le châssis du rover commence à protester.\nL'équipe de reconaissance peut attendre la fin de la tempête dans le rover, mais il ne sera peut-être\nplus en état de fonctionnement, et ils peuvent se retrouver bloqués par le sable accumulé autour.\nIls peuvent également continuer à pied et abandonner le rover, mais leur progression sera ralentie.\n\nQue faire?", "interactionBackgrounds/sandstorm",
                           {Tags.ONROVER:True,Tags.DESERTICPLANET:True},
                           ("Abandonner le rover",
                            lambda o:(InteractionResult.SetOnRover(o, False),
                                      InteractionResult.ResumeTravel(o))),
                           ("Attendre la fin de la tempête",
                            lambda o:(InteractionResult.DoWithChance(o,0.1,
                                lambda o:(InteractionResult.SetOnRover(o, False),
                                          InteractionResult.OpenResultPanel(o,"L'expédition a abandonné le rover et continue à avancer vers la destination.", "interactionBackgrounds/roverJungle"))),
                                      InteractionResult.ResumeTravel(o)))
                           ),
]


def GetRandomInteraction(opportunity,InteractionType:int)->OpportunityInteraction:
    """
    Renvoie une interaction aléatoire.
    """
    if InteractionType in [OpportunitiesManager.InteractionType.ONSITE,OpportunitiesManager.InteractionType.ONSITERESULT]:
        
        i = random.randint(0, len(onSiteInteractions)-1)
        
        while not onSiteInteractions[i].AppliesTo(opportunity):
            i = random.randint(0, len(onSiteInteractions)-1)
        
        return onSiteInteractions[i]
    
    elif InteractionType in [OpportunitiesManager.InteractionType.INTERRUPTION,OpportunitiesManager.InteractionType.INTERRUPTIONRESULT]:
        
        i = random.randint(0, len(interruptionInteractions)-1)
        
        while not interruptionInteractions[i].AppliesTo(opportunity):
            i = random.randint(0, len(interruptionInteractions)-1)
        
        return interruptionInteractions[i]



