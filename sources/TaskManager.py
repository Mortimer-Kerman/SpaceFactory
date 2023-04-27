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
         "title":"Task.0",
         "reward":lambda lv: 500,
         "stat":"TutorialCompleted",
         "target":lambda lv: 1,
         "absolute":True,
         "getOnce" : True
    },
    {
         "title":"Task.1",
         "reward":lambda lv: 4000,
         "stat":"MaxStoredM1",
         "target":lambda lv: 25*99,
         "absolute":True,
         "minLv" : 20,
         "getOnce" : True
    },
    {
         "title":"Task.2",
         "reward":lambda lv: 500 + 10 * lv,
         "stat":"ExpeditionsSent",
         "target":lambda lv: 10 + 5 * lv,
    },
    {
         "title":"Task.3",
         "reward":lambda lv: 1000 + 50 * lv,
         "stat":"EventsOccured",
         "target":lambda lv: 5 + 2 * lv,
    },
    {
         "title":"Task.4",
         "reward":lambda lv: 50 + 5 * lv,
         "stat":"EnnemiesDestroyed",
         "target":lambda lv: 10 + 5 * lv,
    },
    {
         "title":"Task.5",
         "reward":lambda lv: 10 + lv,
         "stat":"MachinesFullyRepaired",
         "target":lambda lv: 10 + 10 * lv,
    },
    {
         "title":"Task.6",
         "reward":lambda lv: 250 + 5 * lv,
         "stat":"SolvedDilemmas",
         "target":lambda lv: 10 + 5 * lv,
    },
    {
         "title":"Task.7",
         "reward":lambda lv: 5 + lv,
         "stat":"ObstaclesDestroyed",
         "target":lambda lv: 10 + 5 * lv,
    },
    {
         "title":"Task.8",
         "reward":lambda lv: 5 + lv,
         "stat":"DecorationBlocksPlaced",
         "target":lambda lv: 10 + 5 * lv,
    },
    {
         "title":"Task.9",
         "reward":lambda lv: 5 + lv,
         "stat":"DrillsPlaced",
         "target":lambda lv: 10 + 5 * lv,
    },
    {
         "title":"Task.10",
         "reward":lambda lv: 5 + lv,
         "stat":"ConveyorBeltsPlaced",
         "target":lambda lv: 10 + 5 * lv,
    },
]

#Pour chaque tâche de la base de données...
for task in tasksDatabase:
    #On ajoute les différents paramètres optionnels si ils ne sont pas présents
    if not "absolute" in tasksDatabase:
        task["absolute"] = False
    if not "minLv" in tasksDatabase:
        task["minLv"] = 0
    if not "getOnce" in tasksDatabase:
        task["getOnce"] = False

def showMenu():
    
    SessionManager.Tutorial.IncreaseStep(19)
    
    screenFilter = pygame.Surface((UiManager.width,UiManager.height)) # Création d'une surface pour le filtre d'écran
    screenFilter.set_alpha(50) # Réglage de la valeur alpha de la surface de filtre d'écran
    background = pygame.display.get_surface().copy() # Création d'une copie de la surface d'affichage pour l'arrière-plan
    background.blit(screenFilter,(0,0)) # Affichage du filtre d'écran sur l'arrière-plan
    def DisplayBackground(): # Définition d'une sous-fonction pour afficher l'arrière-plan et d'autres éléments d'interface utilisateur
        UiManager.screen.blit(background,(0,0)) # Affichage de l'arrière-plan sur l'écran
    
    #Si il y a moins de trois tâches dans la liste...
    if len(SaveManager.mainData.tasks) < 3:
        #Moyenne de 0
        mean = 0
        #Si le nombre de tâches est supérieur à 0:
        if len(SaveManager.mainData.tasks) > 0:
            #On additionne les niveaux de toutes les tâches
            for task in SaveManager.mainData.tasks:
                mean += task["lv"]
            #Division euclidienne par le nombre de tâches pour avoir une moyenne entière
            mean//=len(SaveManager.mainData.tasks)
        #Tant qu'il y a moins de trois tâches dans la liste...
        while len(SaveManager.mainData.tasks) < 3:
            SaveManager.mainData.tasks.append(CreateTask(mean))#On rajoute une tâche dont le niveau de base est la moyenne des autres tâches
    
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
            
            #Si la tâche n'est pas accomplie...
            if not task["done"]:
                #Description de la tâche
                taskDesc = tasksDatabase[task["id"]]
                #Si la valeur cible de cette tâche a été dépassée par la statistique associée...
                if taskDesc["target"](task["lv"]) - task["baseVal"] <= Stats.GetStat(taskDesc["stat"]):
                    task["done"] = True#On marque la tâche comme accomplie
            
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
            
            #Couleur de base du texte et du fond et code de traduction du texte du bas
            textColor = (200,200,200)
            backColor = (50,50,50)
            rewardCode = 'TaskMenu.Reward'
            if task["claimed"]:
                #Si la tâche est réclamée, on assombrit le texte et le fond
                textColor = (100,100,100)
                backColor = (25,25,25)
                rewardCode = 'TaskMenu.AlreadyGot'
            elif task["done"]:
                #Sinon, si la tâche est juste accomplie, on met le texte en blanc et on met un fond en dégradé de orange
                textColor = (255,255,255)
                backColor = pygame_menu.baseimage.BaseImage("Assets/textures/ui/orange.png", drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')
                rewardCode = 'TaskMenu.ClickToGet'
                
            #On récupère le bouton au sommet du cadre, on règle le texte qu'il contient, puis la couleur de la police
            button = frame.get_widgets()[0]
            button.set_title(FunctionUtils.ReduceStr(L.GetLoc(taskDesc["title"],target), 40))
            button.update_font({"color":textColor})
            
            #On récupère le texte en bas du cadre, on règle le texte qu'il contient, puis la couleur de la police
            subtext = frame.get_widgets()[2]
            subtext.set_title(L.GetLoc(rewardCode, reward))
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
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),AudioManager.Tick(),SaveManager.TickClock()),clear_surface=False)

def CreateTask(minimalLevel:int=0):
    """
    Crée une tâche avec un id aléatoire, une difficulté basée sur un niveau minimal fourni et une progression nulle
    """
    #Niveau aléatoire incrémenté à partir du niveau minimal en fonction de la difficulté de la sauvegarde
    taskLv = minimalLevel + [random.randint(0, 1),random.randint(0, 2),random.randint(1, 3)][SaveManager.GetDifficultyLevel()]
    
    #ID aléatoire d'une tâche, l'id 0 est exclus car c'est une tâche exclusive au tutoriel
    taskId = random.randint(1, len(tasksDatabase)-1)
    
    #Description de la tâche associée
    taskDesc = tasksDatabase[taskId]
    
    #Tant que l'ID de la tâche est dans la liste des tâches inchoisissables ou que le niveau minimal de la tâche dépasse le niveau choisi...
    while taskId in SaveManager.mainData.nonChoosableTasks or taskDesc["minLv"] > taskLv:
        #Nouvel ID aléatoire d'une tâche
        taskId = random.randint(0, len(tasksDatabase)-1)
        #Nouvelle description de la tâche associée
        taskDesc = tasksDatabase[taskId]
    
    #Si cette tâche ne peut être choisie qu'une fois, on l'ajoute à la liste des tâches inchoisissables
    if taskDesc["getOnce"]:
        SaveManager.mainData.nonChoosableTasks.append(taskId)
    
    #Valeur de base de la statistique associée au moment de la création en fonction de est-ce que la variation doit être absolue
    baseVal = 0 if taskDesc["absolute"] else Stats.GetStat(taskDesc["stat"])
    
    #On crée la tâche avec les parmètres choisis
    task = {"id":taskId,"lv":taskLv,"baseVal":baseVal,"done":False,"claimed":False}
    
    #Si la valeur cible de cette tâche a été dépassée par la statistique associée...
    if taskDesc["target"](taskLv) - task["baseVal"] < Stats.GetStat(taskDesc["stat"]):
            task["done"] = True#On marque la tâche comme déjà accomplie
    
    #On renvoie la tâche
    return task

def Tick():
    """
    Vérifie si des tâches sont accomplies
    """
    
    #Si aucune sauvegarde n'est chargée, on annule l'exécution
    if not SaveManager.SaveLoaded():
        return
    
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
                print("got here")
                #Si la statistique associée à cette tâche est celle qui a été modifiée et que la valeur cible de cette tâche a été dépassée par la statistique...
                if taskDesc["stat"] == data["stat"] and taskDesc["target"](task["lv"]) - task["baseVal"] <= data["newVal"]:
                        task["done"] = True#On marque la tâche comme accomplie
                        UiManager.Popup("Tâche accomplie!")
