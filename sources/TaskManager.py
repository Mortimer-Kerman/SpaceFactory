# -*- coding: utf-8 -*-*
import pygame
import pygame_menu

import random

import UiManager
import TextureManager
import AudioManager
import SaveManager
import Localization as L
import FunctionUtils
import SessionManager


tasksDatabase=[
    {
         "title":"Remplir entièrement un stockage de M1",
         "reward":4000
    },
    {
         "title":"Envoyer 10 expéditions",
         "reward":500
    },
    {
         "title":"Survivre a 5 évenements",
         "reward":1000
    },
]

def showMenu():
    
    SessionManager.Tutorial.IncreaseStep(19)
    
    screenFilter = pygame.Surface((UiManager.width,UiManager.height)) # Création d'une surface pour le filtre d'écran
    screenFilter.set_alpha(50) # Réglage de la valeur alpha de la surface de filtre d'écran
    background = pygame.display.get_surface().copy() # Création d'une copie de la surface d'affichage pour l'arrière-plan
    background.blit(screenFilter,(0,0)) # Affichage du filtre d'écran sur l'arrière-plan
    def DisplayBackground(): # Définition d'une sous-fonction pour afficher l'arrière-plan et d'autres éléments d'interface utilisateur
        UiManager.screen.blit(background,(0,0)) # Affichage de l'arrière-plan sur l'écran
    
    menu = pygame_menu.Menu(L.GetLoc("TaskMenu.Title"), 720, 539, theme=pygame_menu.themes.THEME_DARK,onclose=pygame_menu.events.BACK)#le thème du menu
        
    menu.add.vertical_margin(5)
    
    if len(SaveManager.mainData.tasks) < 3:
        
        mean = 0
        if len(SaveManager.mainData.tasks) > 0:
            for task in SaveManager.mainData.tasks:
                mean += task["lv"]
            mean/=len(SaveManager.mainData.tasks)
        
        while len(SaveManager.mainData.tasks) < 3:
            SaveManager.mainData.tasks.append(CreateTask(mean))
    
    for task in SaveManager.mainData.tasks:
        taskFrame = menu.add.frame_v(700, 150, background_color=(50, 50, 50), padding=0)
        taskFrame.relax(True)
        
        taskDesc = tasksDatabase[task["id"]]
        
        b = menu.add.button(FunctionUtils.ReduceStr(L.GetLoc(taskDesc["title"]), 40))
        
        FunctionUtils.EncapsulateButtonInFrame(b, taskFrame, buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        taskFrame.pack(menu.add.vertical_margin(50))

        subtext = menu.add.label("Récompense: " + str(taskDesc["reward"]))
        subtext.set_font(TextureManager.GetFont("nasalization"), 20, (255,255,255), (255,255,255), (255,255,255), (255,255,255), (50,50,50))
        taskFrame.pack(subtext)
        
        menu.add.vertical_margin(5)
    
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),AudioManager.Tick(),SaveManager.TickClock()))

def CreateTask(minimalLevel:int=0):
    """
    Crée une tâche avec un id aléatoire, une difficulté basée sur un niveau minimal fourni et une progression nulle
    """
    return {"id":random.randint(0, len(tasksDatabase)-1),"lv":random.randint(minimalLevel, minimalLevel+2),"progress":0}