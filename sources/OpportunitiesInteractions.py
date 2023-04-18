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
import AudioManager


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
        if Tags.ONROVER in self.tags:
            if self.tags[Tags.ONROVER] != opportunity.IsOnRover():
                applies = False
        
        if Tags.DEADPLANET in self.tags:
                if self.tags[Tags.DEADPLANET] != (SaveManager.GetEnvironmentType() == PlanetGenerator.PlanetTypes.Dead):
                    applies = False
        
        if Tags.DESERTICPLANET in self.tags:
                if self.tags[Tags.DESERTICPLANET] != (SaveManager.GetEnvironmentType() == PlanetGenerator.PlanetTypes.Desertic):
                    applies = False
        
        if Tags.LIVINGPLANET in self.tags:
                if self.tags[Tags.LIVINGPLANET] != (SaveManager.GetEnvironmentType() == PlanetGenerator.PlanetTypes.EarthLike):
                    applies = False
        
        if Tags.MINMEMBERS in self.tags:
            if self.tags[Tags.MINMEMBERS] > opportunity.GetMembersAmount():
                applies = False
        
        if Tags.MAXMEMBERS in self.tags:
                if self.tags[Tags.MAXMEMBERS] < opportunity.GetMembersAmount():
                    applies = False
        
        if Tags.LOCATIONTYPE in self.tags:
            if oppDescCodes["place"] not in self.tags[Tags.LOCATIONTYPE]:
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
    #Est-ce que l'expédition doit utiliser un rover
    ONROVER=0#bool
    #Est-ce que la planète a un environment lunaire
    DEADPLANET=1#bool
    #Est-ce que la planète a un environment désertique
    DESERTICPLANET=2#bool
    #Est-ce que la planète a un environment vivant
    LIVINGPLANET=3#bool
    #Nombre minimal inclus de membres de l'expédition
    MINMEMBERS=4#int
    #Nombre maximal inclus de membres de l'expédition
    MAXMEMBERS=5#int
    #IDs du lieu visé par l'expédition
    LOCATIONTYPE=6#liste d'ints


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
        #Est-ce que l'expédition utilisait déjà un rover
        alreadyOnRover = opportunity.IsOnRover()
        
        #Si l'ancien moyen de transport et le nouveau sont identiques, inutile d'exécuter la fonction
        if alreadyOnRover == onRover:
            return
        
        #On règle le moyen de transport dans la description de l'équipe
        opportunity.team["onRover"] = onRover
        
        #Si l'expédition est en trajet...
        if opportunity.state == OpportunitiesManager.Opportunity.State.GOING:
            #On récupère l'avancement du trajet en faisant la durée totale moins la durée restante
            TravelAdvancement = opportunity.GetActivityDuration() - opportunity.GetLeftActivityTime()
            
            #Si l'expédition est maintenant en rover...
            if onRover:
                #On rapproche la date de départ en divisant par 4 la durée depuis le départ et on fait de même pour la durée prévue de l'activité
                opportunity.SetBeginTime(datetime.now() - timedelta(seconds=TravelAdvancement//4))
                opportunity.SetActivityDuration(opportunity.GetActivityDuration()//4)
                
            #Sinon, si elle se retrouve à pied...
            else:
                #On éloigne la date de départ en multipliant par 4 la durée depuis le départ et on fait de même pour la durée prévue de l'activité
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
        if recoverTeam:#Si l'équipe et son inventaire doivent être récupérés, cela revient à dissoudre l'expédition
            opportunity.Dissolve()
            return
        
        #On réinitialise l'opportunité aux valeurs de départ sans transférer quoi que ce soit vers la base
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
        #Si elle est déjà sur le chemin du retour, inutile de la rappeler
        if opportunity.IsTravelling() and opportunity.IsReturning():
            return
        
        #Si l'opportunité n'est pas en trajet...
        if not opportunity.IsTravelling():
            opportunity.returning = True#On lui demande de revenir
            opportunity.SetState(OpportunitiesManager.Opportunity.State.GOING)#On la met en route
            opportunity.SetActivityDuration(opportunity.GetTravelDuration())#On règle le temps de trajet
        else:
            #Sinon, cela revient à la rappeler
            opportunity.Recall()

    def ResumeTravel(opportunity):
        """
        Permet de reprendre le trajet après une interruption.
        """
        #On récupère la date de la dernière interruption qui est concrètement maintenant
        lastInterruption = opportunity.lastInterruption
        #On met l'expédition en route
        opportunity.SetState(OpportunitiesManager.Opportunity.State.GOING)
        #On remet la date de départ pour que le temps passé depuis le début soit identique à celui qu'il y avait avant l'interruption
        opportunity.SetBeginTime(datetime.now() - timedelta(seconds=lastInterruption))

    def DoWithChance(opportunity,chance:float,success,defeat=None):
        """
        Permet d'exécuter une fonction résultat avec une probabilité entre 0 et 1, et une autre en cas d'échet si besoin
        """
        #Si le flottant aléatoire calculé est inférieur à la chance de succès...
        if random.uniform(0,1) < chance:
            success(opportunity)#On exécute la fonction de succès
        elif defeat != None:#Sinon, si une fonction en cas d'échec est définie...
            defeat(opportunity)#On l'exécute
    
    def AddResourceToInv(opportunity,rName:str,amount:int,amountCode:str=None):
        """
        Permet d'ajouter ou de retirer des ressources de l'inventaire de l'expédition.
        Utile pour simuler la découverte de ressources ou leur perte.
        amount peut être un entier ou un tuple pour une quantité aléatoire de resources (bornes inclues)
        amountCode peut être utilisé pour afficher la quantité récupérée avec OpenResultPanel.
        """
        #Si cette ressource n'est pas déjà présente dans l'inventaire, on l'initialise à 0
        if not rName in opportunity.resources:
            opportunity.resources[rName] = 0
        
        #S la quantité est un tuple, on la règle sur une valeur aléatoire entre les deux nombres qu'elle contient
        if type(amount) == tuple:
            amount = random.randint(amount[0], amount[1])
        
        #Si un code de quantité a été spécifié...
        if amountCode != None:
            #On l'y ajoute à locCodes avec la quantité spécifiée
            InteractionResult.locCodes[amountCode] = amount
        
        #On ajoute la quantité de ressources à l'inventaire
        opportunity.resources[rName] += amount
        
        #Si la quantité de ressources finale est inférieure ou égale à 0, on efface cette ressource de l'inventaire
        if opportunity.resources[rName] <= 0:
            opportunity.resources.pop(rName)
    
    def OpenResultPanel(opportunity,message:str,imagePath:str,*args):
        """
        Ouvre un panneau de résultat d'interaction.
        """
        
        #On récupère l'écran affiché et on l'assombrit
        screenFilter = pygame.Surface((UiManager.width,UiManager.height))
        screenFilter.set_alpha(50)
        background = pygame.display.get_surface().copy()
        background.blit(screenFilter,(0,0))
        
        #Fonction temporaire pour afficher le fond du menu
        def DisplayBackground():
            UiManager.screen.blit(background,(0,0))
        
        #Création du menu
        menu = pygame_menu.Menu(opportunity.GetTitle(), 800, 600, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
        
        #On récupère l'image de l'interaction et on la met à la bonne échelle avant de la mettre dans le menu
        srf = TextureManager.GetTexture(imagePath,is_menu=True)
        srf = pygame.transform.scale(srf,(550,srf.get_height()*550/srf.get_width()))
        menu.add.surface(srf)
        
        #On crée plusieurs labels pour pouvoir y mettre la description
        label = menu.add.label("\n\n\n\n\n\n",font_size=15)
        
        #On sépare le message de l'interaction par lignes
        lines = Localization.GetLoc(message,*[InteractionResult.locCodes.get(code,code) for code in args]).split("\n")
        #Pour chaque ligne de la description...
        for i in range(7):
            #Si il y a une ligne correspondante dans la liste, on vient y mettre cette ligne
            if i < len(lines):
                label[i].set_title(lines[i])
            else:#Sinon, cette ligne est vide
                label[i].set_title('')
        
        menu.add.vertical_margin(5)
        
        #On ajoute un bouton ok pour fermer le menu
        menu.add.button(Localization.GetLoc('Game.Ok'), menu.disable, font_size=20)
        
        #Boucle du menu
        menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),AudioManager.Tick()))

onSiteInteractions=[
    OpportunityInteraction("OppInteractions.OnSite.1", "interactionBackgrounds/impactCrater",
                           {Tags.LOCATIONTYPE:[4,7]},
                           ("OppInteractions.OnSite.1.b1",
                            lambda o:(InteractionResult.OpenResultPanel(o,"OppInteractions.OnSite.1.b1.1","interactionBackgrounds/walkingDesert"),
                                      InteractionResult.ReturnToBase(o)),
                            None),
                           ("OppInteractions.OnSite.1.b2",
                            lambda o:(InteractionResult.DoWithChance(o,0.6,
                                lambda o:(InteractionResult.AddResourceToInv(o, "Copper", (20,50),"rAmount"),
                                          InteractionResult.OpenResultPanel(o,"OppInteractions.OnSite.1.b2.1","interactionBackgrounds/walkingDesert")),
                                lambda o:(InteractionResult.OpenResultPanel(o,"OppInteractions.OnSite.1.b2.2","interactionBackgrounds/walkingDesert"))),
                                      InteractionResult.ReturnToBase(o)),
                            (3,5)),
                           ("OppInteractions.OnSite.1.b3",
                            lambda o: InteractionResult.DoWithChance(o,0.6,
                                lambda o:(InteractionResult.AddResourceToInv(o, "Copper", (70,130),"rAmount"),
                                          InteractionResult.OpenResultPanel(o,"OppInteractions.OnSite.1.b3.1","interactionBackgrounds/meteor"),
                                          InteractionResult.ReturnToBase(o)),
                                lambda o:(InteractionResult.EndExpedition(o,False),
                                          InteractionResult.OpenResultPanel(o,"OppInteractions.OnSite.1.b3.2","interactionBackgrounds/meteor"))),
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
    OpportunityInteraction("OppInteractions.Interruption.3", "interactionBackgrounds/blockedWay",
                           {Tags.LIVINGPLANET:True},
                           ("OppInteractions.Interruption.3.b1",
                            lambda o:(InteractionResult.OpenResultPanel(o,"OppInteractions.Interruption.3.b1.1","interactionBackgrounds/walkingDesert"),
                                      InteractionResult.ResumeTravel(o))),
                           ("OppInteractions.Interruption.3.b2",
                            lambda o:(InteractionResult.OpenResultPanel(o,"OppInteractions.Interruption.3.b2.1","interactionBackgrounds/walkingDesert"),
                                      InteractionResult.ResumeTravel(o))),
                           ("OppInteractions.Interruption.3.b3",
                            lambda o:(InteractionResult.AddMembers(o, -1),
                                      InteractionResult.OpenResultPanel(o,"OppInteractions.Interruption.3.b3.1","interactionBackgrounds/runningJungle"),
                                      InteractionResult.ResumeTravel(o)))
                           ),
    
]


def GetRandomInteractionCode(opportunity,InteractionType:int)->int:
    """
    Renvoie le code d'une interaction aléatoire.
    """
    #Si cette interaction est une interaction sur site...
    if InteractionType in [OpportunitiesManager.InteractionType.ONSITE,OpportunitiesManager.InteractionType.ONSITERESULT]:
        #On récupère l'indice d'une interaction aléatoire dans la liste des interactions sur site
        i = random.randint(0, len(onSiteInteractions)-1)
        
        #On précalcule les codes de description de l'opportunité pour ne pas le refaire à chaque boucle
        oppDescCodes = opportunity.GetDescCodes()
        
        #Tant que l'interaction dont l'indice a été récupéré ne s'applique pas à cette opportunité...
        while not onSiteInteractions[i].AppliesTo(opportunity,oppDescCodes):#On récupère un nouvel indice aléatoire
            i = random.randint(0, len(onSiteInteractions)-1)
        
        #On renvoie cet indice
        return i
    
    #Sinon, si c'est une interruption...
    elif InteractionType in [OpportunitiesManager.InteractionType.INTERRUPTION,OpportunitiesManager.InteractionType.INTERRUPTIONRESULT]:
        #On récupère l'indice d'une interaction aléatoire dans la liste des interactions sur site
        i = random.randint(0, len(interruptionInteractions)-1)
        
        #On précalcule les codes de description de l'opportunité pour ne pas le refaire à chaque boucle
        oppDescCodes = opportunity.GetDescCodes()
        
        #Tant que l'interaction dont l'indice a été récupéré ne s'applique pas à cette opportunité...
        while not interruptionInteractions[i].AppliesTo(opportunity,oppDescCodes):#On récupère un nouvel indice aléatoire
            i = random.randint(0, len(interruptionInteractions)-1)
        
        #On renvoie cet indice
        return i


def GetInteractionByCode(code:int,InteractionType:int)->OpportunityInteraction:
    """
    Renvoie une interaction par son type et son code.
    """
    #Si cette interaction est une interaction sur site...
    if InteractionType in [OpportunitiesManager.InteractionType.ONSITE,OpportunitiesManager.InteractionType.ONSITERESULT]:
        return onSiteInteractions[code]#On renvoie l'interaction correspondante dans la liste des interactions sur site
    else:
        return interruptionInteractions[code]#Sinon, on cherche dans la liste des interactions d'interruptions à la place
