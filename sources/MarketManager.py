# -*- coding: utf-8 -*-

# Importation des bibliothèques et modules requis
import pygame
import pygame_menu
import UiManager
import TextureManager
import GameItems
import SaveManager
import Localization as L
import FunctionUtils

# Définition d'un dictionnaire d'articles de marché et initialisation des variables currentItem et LabelCoins à None
marketItem = {"MolecularAssembler": 50000, "CoalCentral": 8000, "Teleporter": 99999, "Monika": 57}
currentItem = None
LabelCoins = None

# Définition d'une fonction pour afficher le menu principal
def showMenu():
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
            popup.show(index)
            UiManager.UIelements["popup_area"]=pygame.Rect(UiManager.width-500,50,500,205*(index+1)).collidepoint(pygame.mouse.get_pos())#on stocke la zone de popup

    def setCurrent(a): # Définition d'une fonction pour définir l'article en cours à une valeur donnée
        global currentItem # Déclaration de la variable globale currentItem pour l'utiliser dans la fonction
        currentItem = a # Définition de la valeur de currentItem à l'argument donné
        title.set_title(L.GetLoc("Items."+a))
        SetLabelText(L.GetLoc("Items.d."+a)) # Définition des textes de la fenêtre

    h = int((UiManager.height//2)-105)
    w = int(UiManager.height)
    
    columnW = w//2
    
    menu = pygame_menu.Menu(L.GetLoc("Market.Title"), w, h+105, theme=pygame_menu.themes.THEME_DARK,onclose=pygame_menu.events.BACK)#le thème du menu
    f=menu.add.frame_h(w, 50, max_width=w, max_height=50, padding=0)
    f.relax(True)
    f.pack(menu.add.button(L.GetLoc('Game.Back'), menu.disable, align=pygame_menu.locals.ALIGN_LEFT),align=pygame_menu.locals.ALIGN_LEFT)
    LabelCoins=menu.add.label(str(SaveManager.mainData.coins), align=pygame_menu.locals.ALIGN_RIGHT, padding=25)
    f.pack(LabelCoins,align=pygame_menu.locals.ALIGN_RIGHT)


    frame = menu.add.frame_h(w, h,padding=0)
    frame.relax(True)

    listFrame = menu.add.frame_v(columnW, max(len(marketItem) * 155, h), max_height=h, padding=0)
    listFrame.relax(True)
    frame.pack(listFrame, align=pygame_menu.locals.ALIGN_LEFT)
    
    for i in marketItem.keys():
        oppFrame = menu.add.frame_v(columnW, int(columnW * (5/18)), background_color=(50, 50, 50), padding=0,frame_id=str(i))
        oppFrame.relax(True)
        listFrame.pack(oppFrame)
        
        b = menu.add.button(FunctionUtils.ReduceStr(L.GetLoc("Items."+i), 30), lambda i=i:setCurrent(i))
        
        FunctionUtils.EncapsulateButtonInFrame(b, oppFrame, buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        oppFrame.pack(menu.add.vertical_margin(int(columnW * (5/54))))

        subtext = menu.add.label("Prix: " + str(marketItem[i]),font_name=TextureManager.GetFont("nasalization",int(columnW/27)),font_color=(255,255,255))
        #subtext.set_font(TextureManager.GetFont("nasalization"), 20, (255,255,255), (255,255,255), (255,255,255), (255,255,255), (50,50,50))
        oppFrame.pack(subtext)
        
        listFrame.pack(menu.add.vertical_margin(5))

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
    
    btn = menu.add.button(L.GetLoc('Market.Buy'), Buy,font_size=int(h*(2/29)), button_id='oppButton')
    
    detailsFrame.pack(btn,align=pygame_menu.locals.ALIGN_CENTER)

    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons()))

def Buy():
    # Vérifie que l'utilisateur a sélectionné un item à acheter
    if currentItem is not None:
        # Vérifie que l'utilisateur a suffisamment de "coins" pour acheter l'item
        if marketItem[currentItem] <= SaveManager.mainData.coins:
            # Réduit la quantité de "coins" du joueur et ajoute l'item à son inventaire
            SaveManager.mainData.coins -= marketItem[currentItem]
            SaveManager.AddToInv(currentItem)
            # Met à jour le label affichant la quantité de "coins" du joueur
            LabelCoins.set_title(str(SaveManager.mainData.coins))
        else:
            # Si le jouerai n'a pas suffisamment de "coins"
            # affiche un message d'erreur
            UiManager.Popup("Vous n'avez pas assez de coins")

# Dictionnaire des prix des différents items
price = {"Coal": 1, "Copper": 2, "Gold": 5, "M1": 8,"NanoM1":25,"M2":15,"MeltedCopper":4}
def Sell(item):
    # Ajoute le prix correspondant à la quantité de "coins" du joueur si l'item est dans le dictionnaire
    SaveManager.mainData.coins += price.get(item, 0)
