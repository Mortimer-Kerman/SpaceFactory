# -*- coding: utf-8 -*-

# Importation des bibliothèques et modules requis
import pygame
import pygame_menu
import UiManager
import TextureManager
import SessionManager
import SaveManager
import Localization as L
import FunctionUtils

# Définition d'un dictionnaire d'articles de marché et initialisation des variables currentItem et LabelCoins à None
marketItem = {"MolecularAssembler": 50000, "CoalCentral": 8000, "PlasmaForge": 5745,"RedBlock":100,"GreenBlock":100,"BlueBlock":100,"YellowBlock":100,"BlackBlock":100,"WhiteBlock":100,"Settler":1000,"Rover":5000}
currentItem = None
LabelCoins = None


def showMenu():
    """
    Ouvre le menu du market
    """
    global LabelCoins # Déclaration de la variable globale LabelCoins pour l'utiliser dans la fonction
    screenFilter = pygame.Surface((UiManager.width,UiManager.height)) # Création d'une surface pour le filtre d'écran
    screenFilter.set_alpha(50) # Réglage de la valeur alpha de la surface de filtre d'écran
    background = pygame.display.get_surface().copy() # Création d'une copie de la surface d'affichage pour l'arrière-plan
    background.blit(screenFilter,(0,0)) # Affichage du filtre d'écran sur l'arrière-plan
    def DisplayBackground(): # Définition d'une sous-fonction pour afficher l'arrière-plan et d'autres éléments d'interface utilisateur
        UiManager.screen.blit(background,(0,0)) # Affichage de l'arrière-plan sur l'écran
        pygame.draw.polygon(UiManager.screen,(198, 136, 102),((0,0),(0,UiManager.height//3),(UiManager.width//3,0))) # Dessin d'une forme polygonale sur l'écran
        pygame.draw.polygon(UiManager.screen,(198, 136, 102),((UiManager.width,UiManager.height),(0,(UiManager.height//3)*2),((UiManager.width//3)*2,0))) # Dessin d'une autre forme polygonale sur l'écran
        UiManager.place_text(L.GetLoc("Market.Title"), 20, 50, 100,font=TextureManager.GetFont("nasalization",100)) # Affichage de du texte sur l'écran
        UiManager.place_text(L.GetLoc("Market.Motto"), 20, 150, 50) # Affichage de du texte sur l'écran
        for index,popup in enumerate(UiManager.UIPopup):#pour index , popup dans UiManager.UIPopup
            popup.show(index,False)
            UiManager.UIelements["popup_area"]=pygame.Rect(UiManager.width-500,50,500,205*(index+1)).collidepoint(pygame.mouse.get_pos())#on stocke la zone de popup
    
    #On récupère une liste des items achetables, trié dans l'ordre croisant
    keys = sorted(marketItem.keys(),key=lambda tab: L.GetLoc("Items." + tab).lower())
    
    #On récupère l'écran affiché et on l'assombrit
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    background = pygame.display.get_surface().copy()
    background.blit(screenFilter,(0,0))
    
    #On calcule la hauteur et la largeur du menu pour qu'elle s'adapte à la taille de l'écran
    h = int((UiManager.height//2)-105)
    w = int(UiManager.height)
    
    #Largeur d'une colonne du menu
    columnW = w//2
    
    #Création du menu
    menu = pygame_menu.Menu(L.GetLoc('Market.Title'), w, h+105, theme=pygame_menu.themes.THEME_DARK, onclose=pygame_menu.events.BACK)#le thème du menu
    
    #Label affichant l'argent du joueur
    LabelCoins=menu.add.label(str(SaveManager.mainData.coins),align=pygame_menu.locals.ALIGN_LEFT)
    
    #On crée un cadre faisant la taille du menu pour pouvoir placer les deux colonnes du menu
    frame = menu.add.frame_h(w, h, padding=0)
    frame.relax(True)
    
    #Création du cadre contenant qui contiendra la liste des items
    listFrame = menu.add.frame_v(columnW, max(len(keys) * (int(columnW * (5/18)) + 5) + 5, h), max_height=h, padding=0)
    listFrame.relax(True)
    frame.pack(listFrame, align=pygame_menu.locals.ALIGN_LEFT)
    
    #Variable stockant l'item actuel
    global currentItem
    currentItem = None
    
    #On ajoute un espace vide au sommet de la liste des items
    listFrame.pack(menu.add.vertical_margin(5))
    
    #Pour chaque item de la liste d'items...
    for item in keys:
        
        #Création d'un cadre qui est placé dans la liste des items
        itemFrame = menu.add.frame_v(columnW, int(columnW * (5/18)), background_color=(50, 50, 50), padding=0)
        itemFrame.relax(True)
        listFrame.pack(itemFrame)
        
        #Création d'un bouton contenant le titre de l'item
        b = menu.add.button(FunctionUtils.ReduceStr(L.GetLoc("Items." + item), 30), lambda itm=item:OpenItem(itm),font_size=int(columnW/18),font_color=(255,255,255))
        
        #On le lie au cadre pour que tout le bouton devienne cliquable
        FunctionUtils.EncapsulateButtonInFrame(b, itemFrame, buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        #Ajout d'une zone vide au milieu du cadre
        itemFrame.pack(menu.add.vertical_margin(int(columnW * (5/54))))
        
        #Ajout de texte contenant le prix de l'item
        subtext = menu.add.label(L.GetLoc('Market.Price', marketItem[item]), font_name=TextureManager.GetFont("nasalization",int(columnW/27)), font_color=(255,255,255))
        itemFrame.pack(subtext)
        
        #On rajoute un petit espace vide sous le cadre
        listFrame.pack(menu.add.vertical_margin(5))
        
    #Fonction temporaire permettant d'ouvrir un item et d'afficher tous ses détails
    def OpenItem(item):
        #Réglage du titre
        title.set_title(L.GetLoc("Items." + item))
        #Réglage de la description
        SetLabelText(L.GetLoc("Items.d." + item))
        #Réglage de l'item ouvert
        global currentItem
        currentItem = item
    
    #Création du cadre contenant les détails de l'item
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
    
    #Création du bouton permettant d'interagir avec l'item ouvert
    btn = menu.add.button(L.GetLoc('Market.Buy'), Buy, font_size=int(h*(2/29)))
    detailsFrame.pack(btn,align=pygame_menu.locals.ALIGN_CENTER)
    
    #Fonction temporaire permettant d'afficher un texte de plusieurs lignes dans la description de l'item
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
    
    #On ouvre le premier item de la liste
    OpenItem(keys[0])
    
    #Boucle de mise à jour du menu
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),SessionManager.TickModules()))

def Buy():
    # Vérifie que l'utilisateur a sélectionné un item à acheter
    if currentItem is not None:
        # Vérifie que l'utilisateur a suffisamment d'argent pour acheter l'item
        if marketItem[currentItem] <= SaveManager.mainData.coins or SaveManager.IsSandBox():
            # Réduit la quantité d'argent du joueur
            SaveManager.mainData.coins = max(SaveManager.mainData.coins - marketItem[currentItem], 0)
            
            if currentItem == "Settler":#Si un colon a été acheté, on le rajoute au montant de colons
                SaveManager.mainData.settlers += 1
            elif currentItem == "Rover":#Sinon, si c'est un rover, on le rajoute au montant de rovers
                SaveManager.mainData.rovers += 1
            else:#Sinon, on ajoute l'item à l'inventaire
                SaveManager.AddToInv(currentItem)
            
            # Met à jour le label affichant la quantité de "coins" du joueur
            LabelCoins.set_title(str(SaveManager.mainData.coins))
        else:
            # Si le joueur n'a pas suffisamment d'argent
            # affiche un message d'erreur
            UiManager.Popup(L.GetLoc('Market.NotEnoughMoney'))

# Dictionnaire des prix des différents items
price = {"Coal": 1, "Copper": 2, "Gold": 5, "M1": 8,"NanoM1":25,"M2":15,"MeltedCopper":4,"MeltedGold":10}
def Sell(item):
    # Ajoute le prix correspondant à la quantité de "coins" du joueur si l'item est dans le dictionnaire
    SaveManager.mainData.coins += price.get(item, 0)
