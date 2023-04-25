# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 15:26:04 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import pygame_menu

import random
from datetime import datetime, timedelta

import SaveManager
import UiManager
import FunctionUtils
import Localization
import TextureManager
import PlanetGenerator
import OpportunitiesInteractions
import AudioManager
import SessionManager
import Stats

#Menu actuellement ouvert
openedMap = None

def OpenMap():
    """
    Ouvre le menu d'opportunités
    """
    global openedMap
    
    SessionManager.Tutorial.IncreaseStep(20)
    
    #On récupère l'écran affiché et on l'assombrit
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    background = pygame.display.get_surface().copy()
    background.blit(screenFilter,(0,0))
    
    #Fonction temporaire pour afficher le fond du menu
    def DisplayBackground():
        UiManager.screen.blit(background,(0,0))
    
    #On calcule la hauteur et la largeur du menu pour qu'elle s'adapte à la taille de l'écran
    h = int((UiManager.height//2)-105)
    w = int(UiManager.height)
    
    #Largeur d'une colonne du menu
    columnW = w//2
    
    #Création du menu
    menu = pygame_menu.Menu(Localization.GetLoc('Opportunities.Title'), w, h+105, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    menu.add.button(Localization.GetLoc('Game.Back'), CloseMap, align=pygame_menu.locals.ALIGN_LEFT)
    openedMap = menu
    
    #On rajoute des opportunités à la liste des opportunités jusqu'à ce qu'il y en ait 5
    while len(SaveManager.mainData.opportunities) < 5:
        SaveManager.mainData.opportunities.append(Opportunity())
    
    #On crée un cadre faisant la taille du menu pour pouvoir placer les deux colonnes du menu
    frame = menu.add.frame_h(w, h, padding=0)
    frame.relax(True)
    
    #Création du cadre contenant qui contiendra la liste des opportunités
    listFrame = menu.add.frame_v(columnW, max(len(SaveManager.mainData.opportunities) * (int(columnW * (5/18)) + 5) + 5, h), max_height=h, padding=0)
    listFrame.relax(True)
    frame.pack(listFrame, align=pygame_menu.locals.ALIGN_LEFT)
    
    #Variable stockant l'opportunité actuelle
    global currentOpportunity
    currentOpportunity = None
    
    #On ajoute un espace vide au sommet de la liste des opportunités
    listFrame.pack(menu.add.vertical_margin(5))
    
    #Pour chaque opportunité de la liste d'opportunités...
    for opportunity in SaveManager.mainData.opportunities:
        
        #Création d'un cadre qui est placé dans la liste des opportunités
        oppFrame = menu.add.frame_v(columnW, int(columnW * (5/18)), background_color=(50, 50, 50), padding=0, frame_id=str(opportunity.seed))
        oppFrame.relax(True)
        listFrame.pack(oppFrame)
        
        """
        Thomas:
        Je tiens à noter un fait.
        Dans ce cas, la graine sert d'ID pour le cadre. Or on ne peut pas utiliser deux fois le même ID dans un menu.
        Donc techniquement, si un joueur se retrouve avec deux fois le même ID, le jeu va lamentablement planter.
        Or les graines sont comprises entre -9^9 et + 9^9.
        
        DONC:
        
        Les probabilités qu'un joueur plante dans ce cas est la probabilité qu'il tire deux fois la même valeur dans un
        intervalle de 9^9*2 nombres, soit 774840978.
        Autrement dit, les probabilités qu'il tire deux fois la même graine avec cinq lancers est de 1-(774840977/774840978)^4,
        soit 5.16234966*10^-9.
        
        Ca veut donc dire que d'après la loi binomiale, même en faisant deux millions de tirages, les probabilités que ça arrive sont de un pourcent.
        
        Si un utilisateur tombe sur ce bug et vient s'en plaindre, soit ce jeu a cartonné, soit il avait plus de chances de gagner à l'euromillion.
        """
        
        #Création d'un bouton contenant le titre de l'opportunité
        b = menu.add.button(FunctionUtils.ReduceStr(opportunity.GetTitle(), 30), lambda opp=opportunity:OpenOpportunity(opp),font_size=int(columnW/18),font_color=(255,255,255))
        
        #On le lie au cadre pour que tout le bouton devienne cliquable
        FunctionUtils.EncapsulateButtonInFrame(b, oppFrame, buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        #Ajout d'une zone vide au milieu du cadre
        oppFrame.pack(menu.add.vertical_margin(int(columnW * (5/54))))
        
        #Ajout de texte contenant le temps de voyage de l'opportunité
        subtext = menu.add.label("Temps de voyage: " + Opportunity.FormatTravelTime(opportunity.GetWalkDistance()), font_name=TextureManager.GetFont("nasalization",int(columnW/27)), font_color=(255,255,255))
        oppFrame.pack(subtext)
        
        #On rajoute un petit espace vide sous le cadre
        listFrame.pack(menu.add.vertical_margin(5))
        
    #Fonction temporaire permettant d'ouvrir une opportunité et d'afficher tous ses détails
    def OpenOpportunity(opportunity):
        #Réglage du titre
        title.set_title(opportunity.GetTitle())
        #Réglage de la description
        SetLabelText(opportunity.GetDesc())
        #Réglage de l'opportunité ouverte
        global currentOpportunity
        currentOpportunity = opportunity
        #Rafraichissement du menu
        RefreshMenu()
    
    #Création du cadre contenant les détails de l'opportunité
    detailsFrame = menu.add.frame_v(columnW, h, max_height=h, padding=0)
    detailsFrame.relax(True)
    frame.pack(detailsFrame)
    
    #Cadre contenant les différentes zones de texte
    textFrame = menu.add.frame_v(columnW, h-50-int(h*(2/29)), max_height=h-50-int(h*(2/29)), padding=0)
    textFrame.relax(True)
    detailsFrame.pack(textFrame,align=pygame_menu.locals.ALIGN_CENTER)
    
    #Zone de texte contenant le titre
    title = menu.add.label("",font_size=int(columnW*(2/29)))#40 en 1080
    textFrame.pack(title,align=pygame_menu.locals.ALIGN_CENTER)
    
    #Création des multiples zones de texte correspondant aux lignes de la description
    label = menu.add.label("\n\n\n\n\n",font_size=int(columnW*(1/29)))#20 en 1080
    textFrame.pack(label)
    
    #Création du bouton permettant d'interagir avec l'opportunité ouverte
    btn = menu.add.button(Localization.GetLoc('Opportunities.StartAnExpedition'), ManageExpeditionAccordingly,font_size=int(h*(2/29)), button_id='oppButton')
    detailsFrame.pack(btn,align=pygame_menu.locals.ALIGN_CENTER)
    
    #Fonction temporaire permettant d'afficher un texte de plusieurs lignes dans la description de l'opportunité
    def SetLabelText(text:str):
        #Longueur d'une ligne en nombre de caractères
        lineLength = 55
        #Liste des index des coupures à faire
        cuts = [0]
        #Dernier espace rencontré
        lastSpace = 0
        #Pour chaque caractère du texte...
        for i in range(len(text)):
            #Si le caractère est un espace, on le note comme dernier espace rencontré
            if text[i] == " ":
                lastSpace = i
            #Si la ligne constituée jusqu'à présent (longueur du texte moins l'index de la dernière coupure) dépasse la longueur d'une ligne...
            if i - cuts[-1] > lineLength:
                #On rajoute une coupure au niveau du dernier espace pour ne pas couper les mots
                cuts.append(lastSpace)
        
        #On crée la liste des lignes en coupant le texte au niveau des index référencés dans la liste des coupures
        lines = [text[i:j].strip() for i,j in zip(cuts, cuts[1:]+[None])]
        
        #Pour chaque ligne de la description...
        for i in range(6):
            #Si on peut y placer une ligne on la place
            if i < len(lines):
                label[i].set_title(lines[i])
            else:#Sinon, on vide la ligne
                label[i].set_title('')
    
    #Si il y a au moins une opportunité dans la liste, on ouvre la première opportunité de la liste
    if len(SaveManager.mainData.opportunities) != 0:
        OpenOpportunity(SaveManager.mainData.opportunities[0])
    
    #runtime permet de mesurer l'espacement entre deux mises à jour du menu
    global runtime
    runtime = 0
    
    #Fonction temporaire permettant de faire des mises à jour du menu
    def MenuTick():
        global runtime
        #On incrémente runtime du temps passé depuis la dernière mise à jour divisé par 8
        runtime+=SaveManager.clock.get_time() / 8
        #Si une mise à jour du menu est nécessaire ou que la dernière mise à jour a eu lieu depuis trop longtemps...
        if Tick() or runtime > 20:
            runtime = 0
            #On remet runtime à 0 et on rafraichit le menu
            RefreshMenu()
    
    #Boucle de mise à jour du menu
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),MenuTick(),SessionManager.TickModules()))

def RefreshMenu():
    """
    Fonction permettant de rafraichir le menu ouvert
    """
    #Si aucun menu n'est ouvert, on annule
    if openedMap == None:
        return
    
    #Pour chaque opportunité de la liste d'opportunités...
    for opportunity in SaveManager.mainData.opportunities:
        
        #On récupère le cadre associé dans le menu
        frame = openedMap.get_widget(str(opportunity.seed), recursive=True)
        
        #Couleur si l'opportunité est juste proposée
        color = (50, 50, 50)
        
        #Si elle n'est pas proposée mais qu'elle est dans un autre stade, on choisit une texture en fonction de la situation et on la charge
        if opportunity.state != Opportunity.State.PROPOSED:
            path = "Assets/textures/ui/orange.png"#Si elle est en trajet, le fond est orange
            if opportunity.state == Opportunity.State.WAITING:
                path = "Assets/textures/ui/green.png"#Si elle est en attente, le fond est vert
            if opportunity.state == Opportunity.State.WORKING:
                path = "Assets/textures/ui/blue.png"#Si elle travaille, le fond est bleu
            if opportunity.state == Opportunity.State.RETURNED:
                path = "Assets/textures/ui/brown.png"#Si elle est de retour, le fond est marron
            #On charge la texture
            color = pygame_menu.baseimage.BaseImage(path, drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')
        
        #Texte du cadre si l'opportunité est proposée: Simple indication du temps de route
        subText = Localization.GetLoc('Opportunities.TravelTime', Opportunity.FormatTravelTime(opportunity.GetWalkDistance()))
        
        #Si l'opportunité est en trajet, on récupère le temps restant
        if opportunity.state == Opportunity.State.GOING:
            subText = Localization.GetLoc('Opportunities.TravelTime', Opportunity.FormatTravelTime(opportunity.GetLeftActivityTime()))
        #Si elle attend, on le note
        if opportunity.state == Opportunity.State.WAITING:
            subText = Localization.GetLoc('Opportunities.ExpeditionWaiting')
        #Si elle travaille, on récupère le temps de travail restant
        if opportunity.state == Opportunity.State.WORKING:
            subText = Localization.GetLoc('Opportunities.WorkingTime', Opportunity.FormatTravelTime(opportunity.GetLeftActivityTime()))
        #Si elle est de retour, on le note
        if opportunity.state == Opportunity.State.RETURNED:
            subText = Localization.GetLoc('Opportunities.ExpeditionBack')
        
        #On place cette nouvelle indication dans le texte en bas du cadre de l'opportunité
        frame.get_widgets()[2].set_title(subText)
        
        #On règle la couleur de fond
        frame.set_background_color(color)
    #On force la mise à jour des couleurs du menu
    openedMap.force_surface_update()
    #On met à jour le bouton d'interaciton avec l'opportunité
    UpdateOppButtonTitle()

def ManageExpeditionAccordingly():
    """
    Fonction s'exécutant lorsque le bouton d'interaction avec l'opportunité est cliqué
    """
    #Si aucune opportunité n'est séléctionnée, on annule l'exécution
    if currentOpportunity == None:
        return
    
    if currentOpportunity.state == Opportunity.State.PROPOSED:
        OpenExpeditionLauncher()#Si l'opportunité est proposée, on ouvre le lanceur d'expéditions
    
    elif currentOpportunity.state == Opportunity.State.GOING:
        if not currentOpportunity.IsReturning():#Si l'opportunité est en trajet et qu'elle ne revient pas...
            currentOpportunity.Recall()
            #On rappelle l'expédition et on rafraichit le menu
            RefreshMenu()
    
    elif currentOpportunity.state == Opportunity.State.WAITING:#Si l'opportunité est en attente...
        if currentOpportunity.lastInterruption == currentOpportunity.GetTravelDuration():
            #Si l'opportunité est arrivé à destination...
            if currentOpportunity.IsReturning():
                #Si elle s'apprête à repartir, c'est qu'elle a fini de travailler, on affiche donc le résultat
                PlayExpeditionInteraction(currentOpportunity,InteractionType.ONSITERESULT)
            else:
                #Sinon, on indique sur quoi elle va travailler
                PlayExpeditionInteraction(currentOpportunity,InteractionType.ONSITE)
        else:
            #Si elle n'est pas arrivée à destination, on affiche pourquoi elle s'est interrompue
            PlayExpeditionInteraction(currentOpportunity,InteractionType.INTERRUPTION)
        #Et on rafraichit le menu
        RefreshMenu()
    
    elif currentOpportunity.state == Opportunity.State.RETURNED:
        #Si l'opportunité est de retour, on la dissout et on rafraichit le menu
        currentOpportunity.Dissolve()
        RefreshMenu()

def OpenExpeditionLauncher():
    """
    Fonction ouvrant le lanceur d'expéditions
    """
    global currentOpportunity
    
    #Si aucune opportunité n'est séléctionnée, on annule
    if currentOpportunity == None:
        return
    
    #On récupère l'écran actuel et on l'assombrit pour faire le fond du menu
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    background = pygame.display.get_surface().copy()
    background.blit(screenFilter,(0,0))
    #Fonction temporaire pour afficher le fond du menu
    def DisplayBackground():
        UiManager.screen.blit(background,(0,0))
    
    #Création du menu
    menu = pygame_menu.Menu(currentOpportunity.GetTitle(), 550, 450, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    menu.add.button(Localization.GetLoc('Game.Back'), menu.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    menu.add.vertical_margin(50)
    
    #Slider permettant de choisir le nombre de membres de l'expédition
    memberSlider = menu.add.range_slider(Localization.GetLoc('Opportunities.MembersAmount'), 5, (2, 10), 1, value_format=lambda x: str(int(x)), align=pygame_menu.locals.ALIGN_LEFT)
    
    #Fonction temporaire permettant de recacluler et afficher le temps de trajet en fonction de est-ce que l'expédition est en rover ou pas
    def SetTravelTime(Rover:bool):
        travelTimeLabel.set_title(Localization.GetLoc('Opportunities.TravelTime', Opportunity.FormatTravelTime(currentOpportunity.GetDriveDistance() if Rover else currentOpportunity.GetWalkDistance())))
    
    #Bouton permettant de choisir le moyen de transport entre le transport à pied et le transport en rover
    roverToggle = menu.add.toggle_switch(Localization.GetLoc('Opportunities.TransportMean'), state_text=tuple(Localization.GetLoc('Opportunities.TransportMean.' + m) for m in ('OnFoot','Rover')), state_color=((100, 100, 100), (100, 100, 100)), onchange=SetTravelTime)
    
    #Zone de texte qui affichera le temps de trajet
    travelTimeLabel = menu.add.label("")
    
    menu.add.vertical_margin(50)
    
    #Bouton permettant de lancer l'expédition
    menu.add.button(Localization.GetLoc('Opportunities.StartExpedition'),lambda:(currentOpportunity.Begin(memberSlider.get_value(),roverToggle.get_value()),menu.disable(),RefreshMenu()))
    
    #On définit une première fois le temps de trajet par le temps à pied
    SetTravelTime(False)
    
    #Boucle du menu
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),AudioManager.Tick()))

def CloseMap():
    """
    Permet de fermer convnablement le menu d'opportunités
    """
    global openedMap
    #Si un menu ouvert existe, on le désactive et on règle la variable le conenant à None
    if openedMap != None:
        openedMap.disable()
        openedMap = None

def UpdateOppButtonTitle():
    """
    Permet de mettre à jour le titre du bouton d'interaction avec les opportunités en fonction du contexte
    """
    #Si un menu d'opportunités est ouvert...
    if openedMap != None:
        #Par défaut, le texte permettant de lancer une expédition
        title = 'Opportunities.StartAnExpedition'
        #Si l'expédition est en route...
        if currentOpportunity.state == Opportunity.State.GOING:
            if currentOpportunity.IsReturning():#Si elle rentre à la base, on l'indique
                title = 'Opportunities.ReturningToBase'
            else:#Sinon, on propose de la rappeler
                title = 'Opportunities.Recall'
        elif currentOpportunity.state == Opportunity.State.WAITING:
            #Si l'expédition attend, on propose de savoir pourquoi
            title = 'Opportunities.ReadReport'
        elif currentOpportunity.state == Opportunity.State.WORKING:
            #Si elle travaille, on l'indique
            title = 'Opportunities.Working'
        elif currentOpportunity.state == Opportunity.State.RETURNED:
            #Si elle est rentrée, on propose de dissoudre l'expédition
            title = 'Opportunities.Dissolve'
        #On applique le nouveau texte traduit au bouton d'interaction avec les opportunités
        openedMap.get_widget('oppButton', recursive=True).set_title(Localization.GetLoc(title))

def Tick()->bool:
    """
    Fonction mettant à jour les opportunités
    """
    #Variable permettant de savoir si un changement a été rencontré
    notedChange = False
    #Pour chaque opportunité de la liste d'opportunités...
    for opportunity in SaveManager.mainData.opportunities:
        #Si l'expédition n'est ni proposée, ni en attente, ni de retour...
        if opportunity.state not in [Opportunity.State.PROPOSED,Opportunity.State.WAITING,Opportunity.State.RETURNED]:
            
            #On récupère le temps de début de l'activité en cours
            beginTime = opportunity.GetBeginTime()
            
            #On récupère la durée totale de l'activité
            duration = opportunity.GetActivityDuration()
            
            #On calcule à quel moment l'activité prendra fin
            arrivalTime = beginTime + timedelta(seconds=duration)
            
            #On récupère la date actuelle
            now = datetime.now()
            
            #Si l'expédition est en trajet...
            if opportunity.state == Opportunity.State.GOING:
                
                #On récupère l'avancement du trajet en faisant la durée totale moins la durée restante
                TravelAdvancement = duration - opportunity.GetLeftActivityTime()
                
                #On récupère le temps de la prochaine interruption de trajet
                nextInterruption = opportunity.GetNextInterruption()
                
                #Si l'avancement du trajet a dépassé la date de la prochaine interruption qui est elle même supérieure à la date de la dernière interruption...
                if TravelAdvancement > nextInterruption > opportunity.lastInterruption:
                    #On met à jour la graine de l'activité
                    opportunity.RefreshActivitySeed()
                    #On met l'opportunité en attente
                    opportunity.SetState(Opportunity.State.WAITING)
                    #On redéfinit la dernière interruption rencontrée
                    opportunity.lastInterruption = nextInterruption
                    #On l'annonce au joueur dans un popup
                    UiManager.Popup("Opportunité interrompue!")
                    #On marque qu'un changement a eu lieu
                    notedChange = True
            
            #Si la date actuelle a dépassé la date d'arrivée...
            if now > arrivalTime:
                #Si l'expédition est en route...
                if opportunity.state == Opportunity.State.GOING:
                    if opportunity.IsReturning():#Si elle est de retour, ça veut dire qu'elle est rentrée à la base
                        opportunity.SetState(Opportunity.State.RETURNED)
                    else:#Sinon, elle est arrivé à destination, on la met donc en attente et on met à jour la date de la dernière interuption
                        opportunity.SetState(Opportunity.State.WAITING)
                        opportunity.lastInterruption = opportunity.GetTravelDuration()
                    
                #Sinon, si l'expédition travaille...
                elif opportunity.state == Opportunity.State.WORKING:
                    #Variable temporaire stockant la dernière interruption
                    lastInterruption = opportunity.lastInterruption
                    #On met l'expédition en attente
                    opportunity.SetState(Opportunity.State.WAITING)
                    #On remet en place la dernière interruption, qui avait été réinitialisée par SetState
                    opportunity.lastInterruption = lastInterruption
                    #On rappelle l'expédition à la base
                    opportunity.Recall()
                #On note qu'un changement a eu lieu
                notedChange = True
    
    #On renvoie notedChange, ce qui permet de dire aux autres fonction si au moins un changement a eu lieu
    return notedChange

class Opportunity:
    """
    Classe permettant de stocker et gérer les opportunités
    """
    
    class State:
        """
        Les différents états d'opportunités
        """
        PROPOSED = 0#L'expédition est proposée
        GOING = 1#L'expédition est sur un trajet
        WAITING = 2#L'expédition est en attente
        WORKING = 3#L'expédition travaille
        RETURNED = 4#L'expédition est de retour
    
    def __init__(self):
        #On récupère une graine aléatoire pour l'opportunité
        self.seed = random.randint(-9**9, 9**9)
        #On récupère une seconde graine aléatoire pour les opportunités
        self.activitySeed = random.randint(-9**9, 9**9)
        #On calcule une distance aléatoire en fonction de l'ordre de distance de l'expédition calculé à partir de la graine de l'expédition
        self.distance = [random.randint(100,400),random.randint(80,240),random.randint(8,28),random.randint(200,800),random.randint(400,2000)][self.GetDescCodes()["distance"]]
        
        #État initial d'une opportunité
        self.state = Opportunity.State.PROPOSED
        self.returning = False
        self.beginTime = datetime.now().isoformat()
        self.activityDuration = 0
        
        #Dictionnaire contenant les caractéristiques de l'expédition envoyée
        self.team = {
            "members" : 5,
            "onRover" : False
        }
        
        #Date de la dernière interruption, indice du dernier choix fait et identifiant de la dernière interaction rencontrée
        self.lastInterruption = 0
        self.lastChoiceMade = None
        self.lastInteraction = None
        
        #Ressources transportées par l'expédition
        self.resources = {}
        
    def GetDescCodes(self)->dict:
        """
        Renvoie les codes de description. Utilisé pour générer la description et le titre de l'opportunité
        """
        #L'aléatoire de ces codes est calculée à partir de la graine de l'expédition
        random.seed(self.seed)
        
        #Est-ce que une personne ou un groupe a découvert ce lieu ou est-ce que plusieurs personnes ou plusieurs groupes sont impliqués?
        singular = random.choice([True,False])
        
        #IDs des lieux disponibles pour cette expédition
        places = [0,1,2,4,5,7,8]
        
        #Si ce monde est une planète avec de la vie, on en rajoute deux
        if SaveManager.GetEnvironmentType() == PlanetGenerator.PlanetTypes.EarthLike:
            places += [3,6]
        
        #On renvoie un dictionnaire avec les différentes données sur la description: singulier, qui a découvert, qu'est-ce qu'ils ont découvert, de quelle manière, ect...
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
        #On récupère les codes de description
        descCodes = self.GetDescCodes()
        
        #On récupère le texte traduit de la quantité et celui des ressources
        q = Localization.GetLoc("Opportunities.Quantity." + str(descCodes["quantity"]))
        r = Localization.GetLoc("Items." + descCodes["ressource"])
        #Si la première lettre des ressources est une voyelle, on ampute la quantité de deux lettres et on met une apostrophe.
        #Cela permet de ne pas écrire "quantités de or", mais "quantités d'or"
        if FunctionUtils.IsVowel(r[0]):
            q = q[:-2] + "'"
        
        #On fait une liste de tous les codes traduits
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
        
        #On les met les uns à la suite des autres et on renvoie le tout
        return "".join(codes)
    
    def GetTitle(self)->str:
        """
        Renvoie le titre de l'opportunité
        """
        #On récupère les codes de description
        descCodes = self.GetDescCodes()
        
        #Liste qui contiendra les ids des titres possibles
        possibleTitles = []
        
        if descCodes["ressource"] == "Gold":
            possibleTitles.append(1)#Si la ressource trouvée est de l'or, on rajoute le titre 1
        if descCodes["place"] == 4:
            possibleTitles.append(2)#Si le lieu cible est le lieu 4, on rajoute le titre 2
        if descCodes["way"] == 1:
            possibleTitles.append(3)#Si la façon de découvrir le lieu est la façon 3, on rajoute le titre 3
        if descCodes["distance"] == 4:
            possibleTitles.append(4)#Si l'ordre de distance est le 4, on rajoute le titre 4
        if descCodes["way"] == 2 or descCodes["way"] == 4:
            possibleTitles.append(5)#Si la façon de découvrir est la façon 2 ou 4, on rajoute le titre 5
        if descCodes["way"] == 5:
            possibleTitles.append(6)#Si la façon de découvrir est la façon 5, on rajoute le titre 6
        if descCodes["way"] == 0:
            possibleTitles.append(7)#Si la façon de découvrir est la façon 0, on rajoute le titre 7
        if len(possibleTitles) == 0:
            possibleTitles.append(0)#Si la liste ne contient aucun titre, on rajoute le titre 0, le plus générique
        
        return Localization.GetLoc("Opportunities.Title." + str(random.choice(possibleTitles)))#On renvoie un titre traduit aléatoire dans la liste des titres
    
    def GetDistance(self)->int:
        """
        Renvoie la distance brute en kilomètres
        """
        return self.distance
    
    def GetWalkDistance(self)->int:
        """
        Renvoie le temps de marche en heures
        """
        #Marche à 4km/h
        return self.GetDistance()//4
    
    def GetDriveDistance(self)->int:
        """
        Renvoie le temps de route en heures
        """
        #Conduite à 40km/h
        return self.GetDistance()//40
    
    def GetTravelDuration(self)->int:
        """
        Renvoie le temps de trajet en heures
        """
        #Temps de route si expédition en rover sinon temps de marche
        return self.GetDriveDistance() if self.IsOnRover() else self.GetWalkDistance()
    
    def FormatTravelTime(travelTime:int)->str:
        """
        Renvoie un temps de trajet formatté
        """
        #On récupère le nombre de jours et d'heures supplémentaire en faisant la division euclidienne du temps de trajet en heures par 24
        days = travelTime//24
        hours = travelTime%24
        
        #Texte du résultat
        result = ""
        
        if days > 0:#Si il y a plus d'un jour de trajet, on le note dans le résultat, au singulier si il n'y en a qu'un seul, sinon au pluriel
            result += str(days) + " " + Localization.GetLoc('Opportunities.Time.Day' + ('' if days == 1 else 's'))
        if hours > 0:#Si il y a plus d'une heure de trajet, on la note dans le résultat (séparée d'un espace des jours si ils sont notés), au singulier si il n'y en a qu'une seul, sinon au pluriel
            if days > 0:
                result += " "
            result += str(hours) + " " + Localization.GetLoc('Opportunities.Time.Hour' + ('' if hours == 1 else 's'))
        
        #Si rien n'a été mis dans le résultat, il reste moins d'une heure de trajet
        if result == "":
            result = Localization.GetLoc('Opportunities.Time.LessThanAnHour')
        
        #Renvoi du résultat
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
        #Le temps d'activité restant est la durée de l'activité moins le temps entre la date de départ et maintenant
        beginTime = self.GetBeginTime()
        now = datetime.now()
        return self.GetActivityDuration() - round((now-beginTime).total_seconds())
    
    def RefreshActivitySeed(self):
        """
        Met à jour la graine d'activité
        """
        #On calcule une nouvelle graine aléatoire à partir de la précédente
        random.seed(self.activitySeed)
        self.activitySeed = random.randint(-9**9, 9**9)
    
    def Begin(self,teamMembers=5,onRover=False):
        """
        Lance l'opportunité
        """
        #On règle les caractéristiques de l'équipe d'après celles données en entrée, on règle l'état sur celui de trajet et on règle le temps de trajet sur la durée estimée
        self.team["members"] = teamMembers
        self.team["onRover"] = onRover
        self.SetState(Opportunity.State.GOING)
        self.SetActivityDuration(self.GetTravelDuration())
        #On incrémente la statistique d'expéditions envoyées
        Stats.IncreaseStat("ExpeditionsSent")

    def GetNextInterruption(self)->float:
        """
        Renvoie à quel moment la prochaine interruption aura lieu
        """
        #On règle la graine aléatoir sur celle de l'activité
        random.seed(self.activitySeed)
        
        #Avec 50% de chance, on renvoie un temps entre 0 et la durée de l'activité
        if random.choice((True,False)):
            return random.randint(0, self.GetActivityDuration())
        #Sinon, on renvoie 0
        return 0

    def SetState(self,state):
        """
        Règle l'état de l'opportunité
        """
        #On règle la variable d'état, on règle le moment de début de l'activité, on rafraichit la graine d'activité et on règle la dernière interruption à 0
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
        #Si l'expédition voyage et ne revient pas...
        if self.IsTravelling() and not self.IsReturning():
            #On met le temps de trajet à faire sur le temps de trajet déjà effectué
            self.SetActivityDuration(self.GetActivityDuration() - self.GetLeftActivityTime())
            self.SetBeginTime(datetime.now())
        #Dans tous les cas, on note qu'elle revient
        self.returning = True
        
    def Dissolve(self):
        """
        Dissout l'expédition et transfère ses membres et ses ressources vers la base.
        """
        #On remet diverses valeurs à leurs valeurs d'origine
        self.SetState(Opportunity.State.PROPOSED)
        self.SetActivityDuration(0)
        self.returning = False
        self.team["members"] = 5
        self.team["onRover"] = False
        
        #Pour chaque ressource du dictionnaire de ressources, on vient rajouter à l'inventaire la quantité correspondante
        for rName in self.resources.keys():
            for i in range(self.resources[rName]):
                SaveManager.AddToInv(rName)
        
        self.resources = {}

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
        
    def ResetLastInteraction(self):
        """
        Remet l'identifiant de la dernière interaction traitée sur None
        """
        self.lastInteraction = None

class InteractionType:
    """
    Les différents types d'interactions
    """
    ONSITE=0#Arrivée sur site
    ONSITERESULT=1#Résultat d'une activité sur site
    INTERRUPTION=2#Interruption
    INTERRUPTIONRESULT=3#Résultat du choix fait lors d'une interruption
    

def PlayExpeditionInteraction(opportunity,interactionType:int):
    """
    Ouvre un menu permettant d'interagir avec les opportunités
    """
    
    #Graine totalement aléatoire
    random.seed(pygame.time.get_ticks())
    
    #Si l'interaction est un résultat...
    if interactionType in [InteractionType.ONSITERESULT,InteractionType.INTERRUPTIONRESULT]:
        
        #On récupère l'interaction précédemment ouverte
        interaction = OpportunitiesInteractions.GetInteractionByCode(opportunity.lastInteraction, interactionType)
        
        #On exécute le résultat de cette interaction en fonction du choix fait
        interaction.GetOptions()[opportunity.lastChoiceMade][1](opportunity)
        
        #On réinitialise les variables sur le choix fait et l'identifiant de l'interaction
        opportunity.SetLastChoiceMade(None)
        opportunity.ResetLastInteraction()
        
        #On bloque le reste de l'exécution
        return
    
    #Si il n'y a pas eu d'interaction rencontrée récemment...
    if opportunity.lastInteraction == None:
        #On récupère un identifiant pour une interaction aléatoire qu'on vient stocker dans l'opportnité
        opportunity.lastInteraction = OpportunitiesInteractions.GetRandomInteractionCode(opportunity, interactionType)
    
    #On récupère l'interaction associée
    interaction = OpportunitiesInteractions.GetInteractionByCode(opportunity.lastInteraction, interactionType)
    
    #On récupère l'écran affiché et on l'assombrit
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    background = pygame.display.get_surface().copy()
    background.blit(screenFilter,(0,0))
    
    #Fonction temporaire pour afficher le fond du menu
    def DisplayBackground():
        UiManager.screen.blit(background,(0,0))
    
    #Création du menu
    menu = pygame_menu.Menu(currentOpportunity.GetTitle(), 800, 600, theme=pygame_menu.themes.THEME_DARK,onclose=pygame_menu.events.BACK)#le thème du menu
    
    #On récupère l'image de l'interaction et on la met à la bonne échelle avant de la mettre dans le menu
    srf = interaction.GetImage()
    srf = pygame.transform.scale(srf,(550,srf.get_height()*550/srf.get_width()))
    menu.add.surface(srf)
    
    #On crée plusieurs labels pour pouvoir y mettre la description
    label = menu.add.label("\n\n\n\n\n\n",font_size=15)
    
    #On sépare le message de l'interaction par lignes
    lines = interaction.GetMessage().split("\n")
    #Pour chaque ligne de la description...
    for i in range(7):
        #Si il y a une ligne correspondante dans la liste, on vient y mettre cette ligne
        if i < len(lines):
            label[i].set_title(lines[i])
        else:#Sinon, cette ligne est vide
            label[i].set_title('')
    
    menu.add.vertical_margin(5)
    
    #Création de la barre du bas qui contiendra les différents choix
    bottomBar=menu.add.frame_h(400, 50, padding=0)
    bottomBar.relax(True)
    
    #On récupère la liste des options
    options = interaction.GetOptions()
    
    #Pour chaque option de la liste...
    for i in range(len(options)):
        option = options[i]
        
        #Durée de l'activité qui va suivre, pour savoir comment elle est lue, se reporter à la docstring de la classe OpportunityInteraction dans le fichier OpportunitiesInteractions.py.
        activityTime = None
        if interactionType == InteractionType.ONSITE:
            #Si l'interaction est sur site, on récupère le temps stocké dans l'interaction
            activityTime = option[2]
            #Si c'est un tuple, la durée est redéfinie aléatoirement entre les deux valeurs de ce tuple.
            if type(activityTime) == tuple:
                activityTime = random.randint(activityTime[0], activityTime[1])
        
        #Si l'interaction est une interruption ou que la durée de l'activité est nulle...
        if interactionType == InteractionType.INTERRUPTION or activityTime == None:
            #Le résultat exécuté en pressant sur le bouton est l'exécution immédiate du résultat de l'opportunité
            result = lambda res=option[1]:(menu.disable(),res(opportunity),opportunity.ResetLastInteraction())
        else:
            #Fonction temporaire permettant de débuter le travail sur site
            def BeginOnSiteActivity(opportunity,duration:int):
                #On stocke temporairement la date de la dernière interruption le temps de régler l'état de l'expédition sur l'état de travail avant de le remettre dans l'opportunité
                lastInterruption = opportunity.lastInterruption
                opportunity.SetState(Opportunity.State.WORKING)
                opportunity.lastInterruption = lastInterruption
                #On règle la durée du travail sur celle donnée en entrée
                opportunity.SetActivityDuration(duration)
            
            #Le résultat exécuté est le lancement de cette session de travail
            result = lambda choice=i,t=activityTime:(menu.disable(),opportunity.SetLastChoiceMade(choice),BeginOnSiteActivity(opportunity,t))
        
        #On ajoute à la barre du bas un bouton avec le titre fourni exécutant le résultat calculé plus haut
        bottomBar.pack(menu.add.button(Localization.GetLoc(option[0]),result,font_size=20),align=pygame_menu.locals.ALIGN_CENTER)
    
    #Boucle du menu
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),AudioManager.Tick()))







