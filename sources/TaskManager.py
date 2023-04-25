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
    
    if len(SaveManager.mainData.tasks) < 3:
        
        mean = 0
        if len(SaveManager.mainData.tasks) > 0:
            for task in SaveManager.mainData.tasks:
                mean += task["lv"]
            mean/=len(SaveManager.mainData.tasks)
        
        while len(SaveManager.mainData.tasks) < 3:
            SaveManager.mainData.tasks.append(CreateTask(mean))
    
    #Création du menu
    menu = pygame_menu.Menu(L.GetLoc("TaskMenu.Title"), 720, 539, theme=pygame_menu.themes.THEME_DARK,onclose=pygame_menu.events.BACK)#le thème du menu
    
    #Espace vide en haut du menu
    menu.add.vertical_margin(5)
    
    #Pour i allant de 1 à 3...
    for i in range(3):
        
        #Création d'un cadre pour acueillir la tâche
        taskFrame = menu.add.frame_v(700, 150, background_color=(50,50,50), padding=0, frame_id=str(i))
        taskFrame.relax(True)
        
        #Bouton et description  de la tâche
        b = menu.add.button("", lambda index = i : HandleClick(index), font_color=(200,200,200))
        
        #On le lie au cadre pour que tout le bouton devienne cliquable
        FunctionUtils.EncapsulateButtonInFrame(b, taskFrame, buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        #Ajout d'une zone vide au milieu du cadre
        taskFrame.pack(menu.add.vertical_margin(50))
        
        #Ajout de texte pour contenir le montant de la récompense
        subtext = menu.add.label("", font_name=TextureManager.GetFont("nasalization", 20), font_color=(200,200,200))
        taskFrame.pack(subtext)
        
        #On rajoute un petit espace vide sous le cadre
        menu.add.vertical_margin(5)
    
    #Fonction temporaire pour rafraichir le menu
    def RefreshMenu():
        
        #Variable pour savoir si il faut recréer les tâches
        needsRefresh = True
        lvs = []#Liste des niveaux des tâches actuelles
        #Pour chaque tâche de la liste...
        for task in SaveManager.mainData.tasks:
            lvs.append(task["lv"])#On ajoute son niveau à la liste des niveaux
            #Si la récompense de cette tâche n'a pas été réclamée, il n'y a pas besoin de recréer les tâches
            if not task["claimed"]:
                needsRefresh = False
        
        #Si il faut recréer les tâches...
        if needsRefresh:
            #On vide la liste des tâches
            SaveManager.mainData.tasks.clear()
            #On ajoute à la liste trois tâches basées sur le niveau de l'ancienne tâche correspondante
            for i in range(3):
                SaveManager.mainData.tasks.append(CreateTask(lvs[i]))
        
        #Pour i allant de 1 à 3...
        for i in range(3):
            
            #On récupère la tâche associée dans la liste
            task = SaveManager.mainData.tasks[i]
            
            #On récupère la description de la tâche associée dans la base de données
            taskDesc = tasksDatabase[task["id"]]
            
            #On récupère le montant de la récompense et la valeur cible
            reward = taskDesc["reward"](task["lv"])
            target = taskDesc["target"](task["lv"])
            
            #On récupère le cadre à l'indice correspondant
            frame = menu.get_widget(str(i),recursive=True)
            
            #Couleur de base du texte et du fond
            textColor = (200,200,200)
            backColor = (50,50,50)
            if task["claimed"]:
                #Si la tâche est réclamée, on assombrit le texte et le fond
                textColor = (100,100,100)
                backColor = (25,25,25)
            elif task["done"]:
                #Sinon, si la tâche est juste accomplie, on met le texte en blanc et on met un fond en dégradé de orange
                textColor = (255,255,255)
                backColor = pygame_menu.baseimage.BaseImage("Assets/textures/ui/orange.png", drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')
            
            #On récupère le bouton au sommet du cadre, on règle le texte qu'il contient, puis la couleur de la police
            button = frame.get_widgets()[0]
            button.set_title(FunctionUtils.ReduceStr(L.GetLoc(taskDesc["title"],target), 40))
            button.update_font({"color":textColor})
            
            #On récupère le texte en bas du cadre, on règle le texte qu'il contient, puis la couleur de la police
            subtext = frame.get_widgets()[2]
            subtext.set_title("Récompense: " + str(reward))
            subtext.update_font({"color":textColor})
            
            #On règle la couleur du fond
            frame.set_background_color(backColor)
        
        #On force la mise à jour de l'affichage
        menu.force_surface_update()
    
    #Fonction temporaire pour gérer le clic sur les tâches
    def HandleClick(index:int):
        
        #On récupère la tâche associée
        task = SaveManager.mainData.tasks[index]
        
        #Si la tâche est accomplie et que la récompense n'a pas été réclamée...
        if task["done"] and not task["claimed"]:
            #On ajoute l'argent correspondant au montant de la récompense
            SaveManager.mainData.coins += tasksDatabase[task["id"]]["reward"](task["lv"])
            task["claimed"] = True#On marque la récompense comme réclamée
            #On rafraîchit le menu
            RefreshMenu()
        
    #On rafraîchit une première fois le menu
    RefreshMenu()
    
    #Boucle du menu
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),AudioManager.Tick(),SaveManager.TickClock()))

def CreateTask(minimalLevel:int=0):
    """
    Crée une tâche avec un id aléatoire, une difficulté basée sur un niveau minimal fourni et une progression nulle
    """
    #ID aléatoire d'une tâche
    taskId = random.randint(0, len(tasksDatabase)-1)
    #Description de la tâche associée
    task = tasksDatabase[taskId]
    #On renvoie la tâche avec l'ID choisi, un id compris entre le niveau minimal et le niveau minimal plus 2, la valeur de base de la statistique associée au moment de la création en fonction de est-ce que la variation doit être absolue, et marquée comme ni accomplie ni réclamée
    return {"id":taskId,"lv":minimalLevel + random.randint(0, 2),"baseVal": 0 if task["absolute"] else Stats.GetStat(task["stat"]),"done":False,"claimed":False}

def Tick():
    """
    Vérifie si des tâches sont accomplies
    """
    #Pour chaque évenement de changement des statistiques...
    for event in pygame.event.get(eventtype=Stats.STATS_CHANGED):
        #Données de changement de la statistique
        data = event.changeData
        #Pour chaque tâche de la liste des tâches...
        for task in SaveManager.mainData.tasks:
            #Si la tâche n'est pas accomplie...
            if not task["done"]:
                #On récupère la description de la tâche associée
                taskDesc = tasksDatabase[task["id"]]
                #Si la statistique associée à cette tâche est celle qui a été modifiée et que la valeur cible de cette tâche a été dépassée par la statistique...
                if taskDesc["stat"] == data["stat"] and taskDesc["target"](task["lv"]) - task["baseVal"] < data["newVal"]:
                        task["done"] = True#On marque la tâche comme accomplie
                        UiManager.Popup("Tâche accomplie!")
