# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 23:11:44 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import pygame_menu

import UiManager
import Localization
import FunctionUtils
import GameItems
import MarketManager
import TextureManager
import SessionManager
import AudioManager

#Onglets qui ne sont pas générés automatiquement
MenuTabs = [
    {
        "id" : "Sandstorm",
        "title" : "HelpMenu.Sandstorm",
        "desc" : "HelpMenu.Sandstorm.Desc",
        "thumb" : "helpMenu/Sandstorm",
        "thumbSize" : (370,176)
    },
    {
        "id" : "SolarStorm",
        "title" : "HelpMenu.SolarStorm",
        "desc" : "HelpMenu.SolarStorm.Desc",
        "thumb" : None
    },
    {
        "id" : "MeteorRain",
        "title" : "HelpMenu.MeteorRain",
        "desc" : "HelpMenu.MeteorRain.Desc",
        "thumb" : "helpMenu/MeteorRain",
        "thumbSize" : (370,230)
    },
]

#Instance de menu à ouvrir
menu = None

def IsInit()->bool:
    """
    Dit si le menu a déjà été initialisé
    """
    return menu != None

def Init():
    """
    Le panneau d'aide étant lent à charger, il est préférable de le créer en amont.
    """
    #On récupère la liste des onglets à afficher: Les onglets spécifiés plus haut et des onglets générés automatiquement
    tabsList = MenuTabs + list(set(GameItems.menuElements + list(GameItems.craft.keys()) + list(GameItems.allTransportableItems.keys()) + list(MarketManager.marketItem.keys()))) + ["delete"]
    
    #On trie la liste en fonction du titre traduit
    tabsList = sorted(tabsList,key=lambda tab:GetTabTitle(tab).lower())
    
    #Création du menu
    global menu
    menu = pygame_menu.Menu(Localization.GetLoc('HelpMenu.title'), 800, 600, enabled=False, theme=pygame_menu.themes.THEME_DARK, onclose=pygame_menu.events.BACK)#le thème du menu
    
    #Cadre horizontal qui contiendra les deux zones du menu
    frame = menu.add.frame_h(800, 540, padding=0)
    frame.relax(True)
    frame.set_float(float_status=True)
    
    #Zone qui contendra la liste des onglets
    listFrame = menu.add.frame_v(380, max(len(tabsList) * 55 + 5, 541), max_height=540, padding=0)
    listFrame.relax(True)
    frame.pack(listFrame, align=pygame_menu.locals.ALIGN_LEFT)
    
    #On ajoute un espace vide au sommet de la liste des onglets
    listFrame.pack(menu.add.vertical_margin(5))
    
    #Pour onglet de la list des onglets...
    for tab in tabsList:
        
        if type(tab) == str:
            tab = TabStrToTabDict(tab)
        
        #Création d'un cadre qui est placé dans la liste des onglets
        helpFrame = menu.add.frame_v(380, 50, background_color=(50, 50, 50), padding=0)
        helpFrame.relax(True)
        listFrame.pack(helpFrame)
        
        #Création d'un bouton contenant le titre de l'onglet
        b = menu.add.button(FunctionUtils.ReduceStr(FunctionUtils.FirstLetterUpper(Localization.GetLoc(tab["title"])), 23),lambda tabToOpen=tab:OpenMenu(tabToOpen),button_id=tab["id"])
        
        #On le lie au cadre pour que tout le bouton devienne cliquable
        FunctionUtils.EncapsulateButtonInFrame(b, helpFrame, buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        #On rajoute un petit espace vide sous le cadre
        listFrame.pack(menu.add.vertical_margin(5))
    
    #Zone qui contiendra la description d'un onglet
    detailsFrame = menu.add.frame_v(380, 541, max_height=540, padding=0)
    detailsFrame.relax(True)
    frame.pack(detailsFrame)
    
    #Titre de l'onglet
    title = menu.add.label(Localization.GetLoc('HelpMenu.title'),font_size=30)
    detailsFrame.pack(title, align=pygame_menu.locals.ALIGN_CENTER)
    
    #Création des multiples zones de texte correspondant aux lignes de la description
    desc = menu.add.label("\n\n\n\n\n",font_size=20)#20 en 1080
    detailsFrame.pack(desc)
    
    #Tableau qui peut contenir les différents crafts d'un objet
    global table
    table = menu.add.table(font_size=15, border_width=0)
    detailsFrame.pack(table, align=pygame_menu.locals.ALIGN_CENTER)
    
    #Icône ou image de l'onglet
    icon=menu.add.surface(TextureManager.GetTexture("no",0.1,True))
    detailsFrame.pack(icon, align=pygame_menu.locals.ALIGN_CENTER)
    
    #Fonction temporaire permettant d'ouvrir un onglet et d'afficher sa description
    def OpenMenu(tab):
        
        if type(tab) == str:
            tab = TabStrToTabDict(tab)
        
        #Affichage du titre
        title.set_title(FunctionUtils.FirstLetterUpper(Localization.GetLoc(tab["title"])))
        
        #Les tableaux de pygame_menu ne contiennent pas de fonction pour supprimer toutes les lignes facilement, il faut donc le supprimer et le recréer
        global table
        detailsFrame.unpack(table)
        menu.remove_widget(table)
        table = menu.add.table(font_size=15, border_width=0)
        detailsFrame.pack(table, align=pygame_menu.locals.ALIGN_CENTER)
        
        #Si l'onglet a une description, on l'affiche, sinon on vide la zone de description
        descText = Localization.GetLoc(tab["desc"])
        if descText != tab["desc"]:
            SetDescText(descText)
        else:
            SetDescText("")
        
        #Si l'item dont traite l'onglet peut être utilisé pour faire des crafts...
        if tab["id"] in GameItems.craft:
            
            #On récupère les crafts de l'item
            crafts = GameItems.craft[tab["id"]]
            
            #Pour chacun des crafts...
            for craft in crafts:
                
                #On crée une ligne
                row = []
                #Pour chaque ingrédient du craft...
                for c in craft["c"]:
                    #On le rajoute à la ligne et on ajoute un + par derrière
                    row.append(FunctionUtils.FirstLetterUpper(Localization.GetLoc('Items.' + c)))
                    row.append(" + ")
                
                #On transforme le dernier élément de la liste en =
                row[-1] = " = "
                #On ajoute le résultat
                row.append(FunctionUtils.FirstLetterUpper(Localization.GetLoc('Items.' + craft["r"])))
                
                #On ajoute la ligne au tableau
                table.add_row(row,cell_align=pygame_menu.locals.ALIGN_CENTER,cell_border_width=0)
        
        #Si l'item dont traite l'onglet est le résultat d'un craft...
        if tab["id"] in GameItems.craftResults:
            
            #On récupère l'item et le craft avec lequel on peut crafter cet item
            i,craft=GameItems.findCraft(tab["id"])
            
            #On crée une ligne contenant déjà le nm de l'item utilisé pour le craft
            row = [Localization.GetLoc('Items.'+i)+" : "]
            
            #A partir de ce point, c'est la même chose qu'entre la ligne 126 et 137
            for c in craft["c"]:
                row.append(FunctionUtils.FirstLetterUpper(Localization.GetLoc('Items.' + c)))
                row.append(" + ")
            
            row[-1] = " = "
            row.append(FunctionUtils.FirstLetterUpper(Localization.GetLoc('Items.' + craft["r"])))
            
            table.add_row(row,cell_align=pygame_menu.locals.ALIGN_CENTER,cell_border_width=0)
        
        #Si la miniature de cet onglet existe...
        if TextureManager.TextureExists(tab["thumb"]):
            #On l'affiche
            icon.set_surface(TextureManager.GetTexture(tab["thumb"],tab["thumbSize"][0],True,tab["thumbSize"][1]))
        else:
            #Sinon, on affiche la texture d'objet manquant, suffisament petite pour être invisible
            icon.set_surface(TextureManager.GetTexture("no",0.1,True))
        
        #On calcule la nouvelle hauteur du cadre de description en additionnant la hauteur de tous les widgets qu'il contient
        h = 0
        for w in detailsFrame.get_widgets(unpack_subframes=False):
            h += w.get_height()
        
        #Pour redimensionner le cadre de description, il est nécéssaire d'en détacher chaque widget qu'il contient et de réactiver le placement automatique
        detailsFrame.unpack(table)
        table.set_float(float_status=False)
        detailsFrame.unpack(title)
        title.set_float(float_status=False)
        detailsFrame.unpack(icon)
        icon.set_float(float_status=False)
        for label in desc:
            detailsFrame.unpack(label)
            label.set_float(float_status=False)
        
        #On change la taille du cadre
        detailsFrame.resize(380, max(541,h), max_height=540)
        
        #On réattache chaque widget
        detailsFrame.pack(title, align=pygame_menu.locals.ALIGN_CENTER)
        detailsFrame.pack(desc)
        detailsFrame.pack(table, align=pygame_menu.locals.ALIGN_CENTER)
        detailsFrame.pack(icon, align=pygame_menu.locals.ALIGN_CENTER)
    
    #Fonction temporaire permettant de régler le texte de la description
    def SetDescText(text:str):
        #Longueur d'une ligne en nombre de caractères
        lineLength = 35
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
                desc[i].set_title(lines[i])
            else:#Sinon, on vide la ligne
                desc[i].set_title('')

def Open(tab:str=None):
    """
    Ouvre le panneau d'aide. Il est possible de spécifier un onglet en particulier.
    """
    #Si le menu n'est pas initialisé, on l'initialise
    if not IsInit():
        Init()
    
    #On récupère l'écran affiché et on l'assombrit
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    background = pygame.display.get_surface().copy()
    background.blit(screenFilter,(0,0))
    
    #Fonction temporaire pour afficher le fond du menu
    def DisplayBackground():
        UiManager.screen.blit(background,(0,0))
    
    #On active le menu
    menu.enable()
    
    #Si un onglet est choisi...
    if tab != None:
        #On récupère le bouton dont l'id correspond à l'onglet
        button = menu.get_widget(tab,True)
        #On le sélectionne
        button.select(update_menu=True)
        #On simule un clic dessus
        button.apply()
    
    #Boucle du menu
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),SessionManager.TickModules()))

def GetTabTitle(tab):
    if type(tab) == str:
        return Localization.GetLoc('Items.' + tab)
    return Localization.GetLoc(tab["title"])

def TabStrToTabDict(tab:str)->dict:
    """
    Crée un dictionnaire d'onglet à partir du code str d'un onglet généré automatiquement
    """
    return {
        "id" : tab,
        "title" : "Items." + tab,
        "desc" : "Items.d." + tab,
        "thumb" : tab,
        "thumbSize" : (100,100)
    }
