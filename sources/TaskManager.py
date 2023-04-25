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
import Stats


tasksDatabase=[
    {
         "title":"Task.1",
         "reward":lambda lv: 4000,
         "stat":"MaxStoredM1",
         "target":lambda lv: 25*99,
         "absolute":True
    },
    {
         "title":"Task.2",
         "reward":lambda lv: 500,
         "stat":"ExpeditionsSent",
         "target":lambda lv: 5 * lv + 10,
    },
    {
         "title":"Task.3",
         "reward":lambda lv: 1000,
         "stat":"EventsOccured",
         "target":lambda lv: 2 * lv + 5,
    },
]

for task in tasksDatabase:
    if not "absolute" in tasksDatabase:
        task["absolute"] = False

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
    
    for i in range(len(SaveManager.mainData.tasks)):
        
        taskFrame = menu.add.frame_v(700, 150, background_color=(50,50,50), padding=0, frame_id=str(i))
        taskFrame.relax(True)
        
        b = menu.add.button("", lambda index = i : HandleClick(index), font_color=(200,200,200))
        
        FunctionUtils.EncapsulateButtonInFrame(b, taskFrame, buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        taskFrame.pack(menu.add.vertical_margin(50))
        
        subtext = menu.add.label("", font_name=TextureManager.GetFont("nasalization", 20), font_color=(200,200,200))
        taskFrame.pack(subtext)
        
        menu.add.vertical_margin(5)
    
    def RefreshMenu():
        
        needsRefresh = True
        lvs = []
        for task in SaveManager.mainData.tasks:
            lvs.append(task["lv"])
            if not task["claimed"]:
                needsRefresh = False
        
        if needsRefresh:
            SaveManager.mainData.tasks.clear()
            for i in range(3):
                SaveManager.mainData.tasks.append(CreateTask(lvs[i]))
        
        for i in range(len(SaveManager.mainData.tasks)):
            
            task = SaveManager.mainData.tasks[i]
            
            taskDesc = tasksDatabase[task["id"]]
            
            reward = taskDesc["reward"](task["lv"])
            target = taskDesc["target"](task["lv"])
            
            frame = menu.get_widget(str(i),recursive=True)
            
            textColor = (200,200,200)
            backColor = (50,50,50)
            if task["claimed"]:
                textColor = (100,100,100)
                backColor = (25,25,25)
            elif task["done"]:
                textColor = (255,255,255)
                backColor = pygame_menu.baseimage.BaseImage("Assets/textures/ui/orange.png", drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')
            
            button = frame.get_widgets()[0]
            button.set_title(FunctionUtils.ReduceStr(L.GetLoc(taskDesc["title"],target), 40))
            button.update_font({"color":textColor})
            
            subtext = frame.get_widgets()[2]
            subtext.set_title("Récompense: " + str(reward))
            subtext.update_font({"color":textColor})
            
            frame.set_background_color(backColor)
            
        menu.force_surface_update()
    
    def HandleClick(index:int):
        
        task = SaveManager.mainData.tasks[index]
        
        if task["done"] and not task["claimed"]:
            print(tasksDatabase[task["id"]]["reward"](task["lv"]))
            
            task["claimed"] = True
            
            RefreshMenu()
        
    
    RefreshMenu()
    
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),AudioManager.Tick(),SaveManager.TickClock()))

def CreateTask(minimalLevel:int=0):
    """
    Crée une tâche avec un id aléatoire, une difficulté basée sur un niveau minimal fourni et une progression nulle
    """
    taskId = random.randint(0, len(tasksDatabase)-1)
    task = tasksDatabase[taskId]
    return {"id":taskId,"lv":random.randint(minimalLevel, minimalLevel+2),"baseVal": 0 if task["absolute"] else Stats.GetStat(task["stat"]),"done":False,"claimed":False}

def Tick():
    """
    Vérifie si des tâches sont accomplies
    """
    for event in pygame.event.get(eventtype=Stats.STATS_CHANGED):
        data = event.changeData
        for task in SaveManager.mainData.tasks:
            if not task["done"]:
                taskDesc = tasksDatabase[task["id"]]
                if taskDesc["stat"] == data["stat"] and taskDesc["target"](task["lv"]) - task["baseVal"] < data["newVal"]:
                        task["done"] = True
                        UiManager.Popup("Tâche accomplie!")



