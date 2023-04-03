# -*- coding: utf-8 -*-*
import pygame
import pygame_menu
import UiManager
import TextureManager
import GameItems
import SaveManager
import Localization as L
import FunctionUtils

currentItem=None
task={"Remplir entièrement un stockage de M1":4000}

def showMenu():
    screenFilter = pygame.Surface((UiManager.width,UiManager.height)) # Création d'une surface pour le filtre d'écran
    screenFilter.set_alpha(50) # Réglage de la valeur alpha de la surface de filtre d'écran
    background = pygame.display.get_surface().copy() # Création d'une copie de la surface d'affichage pour l'arrière-plan
    background.blit(screenFilter,(0,0)) # Affichage du filtre d'écran sur l'arrière-plan
    def DisplayBackground(): # Définition d'une sous-fonction pour afficher l'arrière-plan et d'autres éléments d'interface utilisateur
        UiManager.screen.blit(background,(0,0)) # Affichage de l'arrière-plan sur l'écran
        
    def setCurrent(a): # Définition d'une fonction pour définir l'article en cours à une valeur donnée
        global currentItem # Déclaration de la variable globale currentItem pour l'utiliser dans la fonction
        currentItem = a # Définition de la valeur de currentItem à l'argument donné



    h = int((UiManager.height//2)-105)
    w = int(UiManager.height)
    
    menu = pygame_menu.Menu(L.GetLoc("TaskManager.Title"), w, h+105, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    f=menu.add.frame_h(w, 50, max_width=w, max_height=50, padding=0)
    f.relax(True)
    f.pack(menu.add.button(L.GetLoc('Game.Back'), menu.disable, align=pygame_menu.locals.ALIGN_LEFT),align=pygame_menu.locals.ALIGN_LEFT)
    LabelCoins=menu.add.label(str(SaveManager.mainData.coins), align=pygame_menu.locals.ALIGN_RIGHT, padding=25)
    f.pack(LabelCoins,align=pygame_menu.locals.ALIGN_RIGHT)


    frame = menu.add.frame_h(w, h,padding=0)
    frame.relax(True)

    listFrame = menu.add.frame_v(500, max(len(task) * 155, h), max_height=h, padding=0)
    listFrame.relax(True)
    frame.pack(listFrame, align=pygame_menu.locals.ALIGN_LEFT)
    
    for i in task.keys():
        oppFrame = menu.add.frame_v(500, 150, background_color=(50, 50, 50), padding=0)
        oppFrame.relax(True)
        listFrame.pack(oppFrame)
        
        b = menu.add.button(FunctionUtils.ReduceStr(L.GetLoc("Item."+i), 30), lambda i=i:setCurrent(i))
        
        FunctionUtils.EncapsulateButtonInFrame(b, oppFrame, buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        oppFrame.pack(menu.add.vertical_margin(50))

        subtext = menu.add.label("Récompense: " + str(task[i]))
        subtext.set_font(TextureManager.nasalization, 20, (255,255,255), (255,255,255), (255,255,255), (255,255,255), (50,50,50))
        oppFrame.pack(subtext)
        
        listFrame.pack(menu.add.vertical_margin(5))

    detailsFrame = menu.add.frame_v(w-500, h, max_height=h, padding=0)
    detailsFrame.relax(True)
    frame.pack(detailsFrame)
    
    title = menu.add.label("",font_size=int((UiManager.height-500)*(2/29)))#40 en 1080
    detailsFrame.pack(title,align=pygame_menu.locals.ALIGN_CENTER)
    
    label = menu.add.label("\n\n\n\n\n",font_size=int((UiManager.height-500)*(1/29)))#20 en 1080
    detailsFrame.pack(label)
    
    detailsFrame.pack(menu.add.vertical_margin(100))
    
    detailsFrame.pack(menu.add.button(L.GetLoc("Market.Buy"), lambda : print("a")),align=pygame_menu.locals.ALIGN_CENTER)

    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons()))