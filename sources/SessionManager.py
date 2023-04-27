# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 21:43:27 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

#importations des bibliothèques
import pygame
import pygame_menu
#importation des bibliothèques système
import random
#importation des autres fichiers
import TextureManager
import SaveManager
import UiManager
import GameItems
import AudioManager
import SettingsManager
import FunctionUtils
import Localization as L
import OpportunitiesManager
import MarketManager
import TaskManager
import AnimationsManager
import EventManager
import HelpMenu
import Stats



laser=lambda:None
def Play(saveName:str,**kwargs):
    """
    Lance le jeu
    Fonction principale de la Session
    """
    global laser
    GameItems.Laser={}
    UiManager.Loading()#Chargement de l'UI
    if not SaveManager.Load(saveName):#Chargement de la sauvegarde
        return False
    
    seed = kwargs.get("seed",None)#on obtient la seed
    if seed != None:#s'il y a une seed
        SaveManager.mainData.seed = seed#on change la seed dans la sauvegarde (mainData)
    
    planetaryConditions = kwargs.get("planetaryConditions",None)#on obtient les conditions planétaire
    if planetaryConditions != None:#s'il y a des conditions planétaire
        SaveManager.mainData.planetaryConditions = planetaryConditions#on change les conditions planétaire dans la sauvegarde (mainData)
    
    difficulty = kwargs.get("difficulty",None)#on obtient la difficulté
    if difficulty != None:#s'il y a une difficulté
        SaveManager.mainData.difficulty = difficulty#on change la difficulté dans la sauvegarde (mainData)
        
    gamemode = kwargs.get("gamemode",None)#on obtient le mode de jeu
    if gamemode != None:#s'il y a un mode de jeu
        SaveManager.mainData.gamemode = gamemode#on change le mode de jeu dans la sauvegarde (mainData)
    
    if not HelpMenu.IsInit():#Si le menu d'aide n'est pas intialisé
        HelpMenu.Init()#Création du menu d'aide en amont
    
    UiManager.UpdateBackground()#Première mise à jour du fond
    
    runtime=0#la variable runtime sert comme variable pour les animations
    
    if SaveManager.IsTutorial():#si mode tutoriel
        Tutorial.Init()
    
    GameItems.Minerais.SpawnAllScreen()#Spawn des minerais
    
    for i in SaveManager.mainData.items.keys():
        if SaveManager.mainData.items[i].name=="Teleporter":
            GameItems.TeleportPoint.append(SaveManager.mainData.items[i].pos)
    
    drone=AnimationsManager.Drone()#Création du drone

    EventM=EventManager.Events()#Création du gestionnaire d'événements
    
    EventManager.EnnemisList.clear()#On supprime tous les ennemis
    
    AudioManager.BeginGameAmbience()

    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEWHEEL, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION, Stats.STATS_CHANGED] + AudioManager.GetAllSoundsEvents())#réduit le nombre d'évent
    
    while SaveManager.SaveLoaded():#tant que la sauvegarde est chargée
        
        UiManager.UpdateBackground()#mise à jour du fond
        
        UpdateObjects(int(runtime),EventM.CurrentEvent)#Afficher l'objet de manière dynamique

        for c,i in enumerate(EventManager.EnnemisList):#pour chaque ennemi dans EnnemisList
            i.ia(runtime)#calcul de la trajectoire et mouvement
            i.show(c)#affichage de l'ennemi
        
        laser()#affichage du laser

        drone.show()#affichage du drone
        
        for l in GameItems.Laser.values():
            l()#affichage des lasers machines
        
        EventM.UpdateCurrentEvent(int(runtime))
        
        if showUi:
            UiManager.DisplayUi()#Afficher l'Interface Utilisateur
        
        Tutorial.Tick()#Met à jour le tutoriel
        
        pygame.display.update()#Mise à jour de l'affichage Pygame
        
        HandleLongKeyInputs()#gestion des longs clics
        
        AudioManager.Tick()#Actualisation du son
        
        TaskManager.Tick()#Actualisation des tâches
        
        for event in pygame.event.get():#pour chaque événements
            #en cas de fermeture du jeu (sert à ne pas provoquer de bug)
            if event.type == pygame.QUIT:#en cas de Alt+F4 ou de fermeture via la croix de la fenêtre
                if Pause():#On fait pause
                    return True#Si la fonction pause indique vrai, la sauvegarde a été déchargée et il faut quitter
            
            #action de molette de souris
            if event.type == pygame.MOUSEWHEEL:#si un changement molette survient
                zoom = SaveManager.mainData.zoom#on récupère le zoom 
                zoom = FunctionUtils.clamp(zoom+event.y, 10, 150)#on ajoute le y du changement de molette en s'assurant de garder le niveau de zoom entre 10 et 150
                
                #Calcul du facteur de différence entre l'ancien et le nouveau zoom
                zoomDiff = zoom / SaveManager.mainData.zoom
                
                #si le zoom a changé...
                if zoomDiff != 1:
                    SaveManager.mainData.zoom = zoom#on change le zoom dans le SaveManager
                    
                    #On multiplie la position par la différence de zoom pour éviter un décalage
                    pos = SaveManager.GetCamPos()
                    SaveManager.SetCamPos([pos[0] * zoomDiff, pos[1] * zoomDiff])
                    
                    TextureManager.RefreshZoom()#On mets à jour le zoom
                    GameItems.Minerais.SpawnBorder(True)#On spawn les minerais aux bordures
                    
                    Tutorial.IncreaseStep(1)
            
            #action de clic sur une touche
            if event.type == pygame.KEYDOWN:
                if HandleShortKeyInputs(event.key):#Traitement des clics rapides
                    return True
            
            if event.type == pygame.MOUSEBUTTONDOWN:#en cas de clic
                if HandleMouseClicks(event.button,drone):#Traitement des clics
                    return True
            if event.type == pygame.MOUSEBUTTONUP:#si le bouton de la souris est relaché
                    if event.button == 3:#s'il s'agit du bouton droit
                        laser = lambda : None#pas de laser
        
        SaveManager.TickClock()#Actualisation de l'horloge interne
        
        runtime+=SaveManager.clock.get_time() / 10#on augmente le runtime
        if runtime > 50:#si le runtime est supérieur à 50
            runtime = 0#on reset le runtime
            if SaveManager.SaveLoaded():#on vérifie si la sauvegarde est chargée
                OpportunitiesManager.Tick()#on fait passer le temps des Opportunités
                drone.update()#on mets à jour le drone
                if not SaveManager.IsTutorial() or Tutorial.GetGlobalStep() == 23:
                    EventM.LaunchEvent()#Lancer un événement
    return True

def UpdateObjects(runtime:int,currentEvent):
    """Met à jour les objets de manière dynamique"""
    
    for m in GameItems.current:#pour chaque minerai dans GameItems.current
        GameItems.Minerais.PlaceFromCurrent(m)#placement du minerai
    
    for item in SaveManager.GetItems():#pour chaque item dans SaveManager.GetItems()
        
        #Si l'item est un four en pleine tempête ou un tapis roulant en pleine tempête de sable...
        if ((currentEvent == EventManager.Sandstorm and item.name == "ConveyorBelt") 
            or (currentEvent == EventManager.Storm and item.name == "Furnace")):
            runtime = 1#On met le runtime à 1 pour bloquer la transmission d'items et les animations
        
        if runtime==0:#si le runtime vaut 0
            item.Give()#transmission de l'inventaire à l'item adjacent
            
            #Si on est en pleine tempête solaire, avec une chance sur 5, on retire un pv à l'objet
            if currentEvent == EventManager.SolarStorm and random.randint(0, 5) == 0:
                item.metadata["pv"] = item.metadata.get("pv",100) - 1
        
        item.Update(runtime)#Afficher l'item
    
    GameItems.ExecuteRender()#Executer le rendu dynamique des items
    
    UiManager.DisplayItemToPlace()#Placement des items à placer

def HandleLongKeyInputs():
    """Gestion des pressions de touches longues"""
    #action du clavier
    keys = pygame.key.get_pressed()#On stocke les touches pressées
    mouseInputs = pygame.mouse.get_pressed()#Boutons de souris pressés
    
    camOffset = [0,0]#Définition de l'offset de la caméra
    if keys[SettingsManager.GetKeybind("up")]:#si touche up
        camOffset[1]+=SaveManager.clock.get_time() / 2
    if keys[SettingsManager.GetKeybind("down")]:#si touche down
        camOffset[1]-=SaveManager.clock.get_time() / 2
    if keys[SettingsManager.GetKeybind("right")]:#si touche right
        camOffset[0]-=SaveManager.clock.get_time() / 2
    if keys[SettingsManager.GetKeybind("left")]:#si touche left
        camOffset[0]+=SaveManager.clock.get_time() / 2
        
    mouseDisplacement = pygame.mouse.get_rel()#On récupère le déplacement de la souris depuis la dernière frame
    if mouseInputs[0] and not SaveManager.IsItemSelected() and not UiManager.IsClickOnUI():#Si le bouton gauche est enfoncé, qu'aucun objet n'est séléctionné et que le clic de souris n'est pas sur l'UI...
        #On ajoute le déplacement de la souris au déplacement de la caméra
        camOffset[0] += mouseDisplacement[0]
        camOffset[1] += mouseDisplacement[1]
        Tutorial.IncreaseStep(0)
    
    SaveManager.TranslateCam(camOffset)#On applique les changements de caméra
    
    global ShiftPressed
    ShiftPressed = keys[pygame.K_LSHIFT]
    
    if camOffset != [0,0]:#si un déplacement a eu lieu
        if SaveManager.GetZoom()<30:#en cas de dézoom trop grand
            
            zoom = SaveManager.GetZoom()+1#on zoom
            
            #Calcul du facteur de différence entre l'ancien et le nouveau zoom
            zoomDiff = zoom / SaveManager.mainData.zoom
            
            SaveManager.mainData.zoom=zoom#On augmente la zoom
            
            #On multiplie la position par la différence de zoom pour éviter un décalage
            pos = SaveManager.GetCamPos()
            SaveManager.SetCamPos([pos[0] * zoomDiff, pos[1] * zoomDiff])
            
            TextureManager.RefreshZoom()#on actualise les textures
            GameItems.Minerais.SpawnBorder(True)#on spawn les minerais aux bordures
        else:
            GameItems.Minerais.SpawnBorder()#on spawn les minerais aux bordures

showUi = True    

def HandleShortKeyInputs(key):
    """Traitement des pressions de touches rapides"""
    if key == SettingsManager.GetKeybind("rotate"):#si la clé pressée est associée à rotate
        SaveManager.UpdateRotation()#mise à jour de la rotation
    if key == pygame.K_F2:#si la clé pressé est F2
        UiManager.TakeScreenshot()#prendre une capture d'écran
        #On en informe le joueur
        UiManager.Popup("Capture d'écran trouvable dans le dossier /Screenshots/")
    if key == pygame.K_F1:
        global showUi
        showUi = not showUi
    if key == SettingsManager.GetKeybind("inv"):#si la clé pressée est associée à inv
        ToggleInv()#Afficher/cacher l'inventaire
    if key == SettingsManager.GetKeybind("buildMenu"):#si la clé pressée est la touche du menu de construction...
        ToggleSelect()#Afficher/cacher le menu de construction
    if key == SettingsManager.GetKeybind("opportunities"):#si la clé pressée est associée à opportunities
        OpportunitiesManager.OpenMap()#ouvrir les opportunités
    if key == SettingsManager.GetKeybind("tasks"):#si la clé pressée est la touche des tâches...
        TaskManager.showMenu()#afficher le menu de taches
    if key == pygame.K_ESCAPE:#si la clé pressée est ESCAPE
        if Pause():#On fait pause
            return True#Si la fonction pause indique vrai, la sauvegarde a été déchargée et il faut quitter
    return False

def ToggleInv():
    """
    Ouvre ou ferme l'inventaire
    """
    UiManager.showMenu["inv"]=1-UiManager.showMenu.get("inv",0)
    UiManager.showMenu["select"]=0

def ToggleSelect():
    """
    Ouvre ou ferme le menu de construction
    """
    UiManager.showMenu["select"]=1-UiManager.showMenu.get("select",0)
    UiManager.showMenu["inv"]=0

def HandleMouseClicks(button,drone):
    """Gestion des clics"""
    global laser
    if button == 1: # 1 == left button
        if UiManager.IsClickOnUI():#si c'est un clic sur UI
            if UiManager.UIelements.get("select",False):#Si l'élément d'UI cliqué est l'élément stocké à UiManager.UIelements["select"], alors
                ToggleSelect()#montrer/cacher le menu de construction
                Tutorial.IncreaseStep(5)
            elif UiManager.UIelements.get("inv",False):#si l'élément UI cliqué est inventaire
                ToggleInv()#montrer/cacher le menu d'inventaire
            elif UiManager.UIelements.get("menu_icon",False):#Si l'élément d'UI cliqué est l'élément stocké à UiManager.UIelements["menu_icon"], alors
                if Pause():#On fait pause
                    return True#Si la fonction pause indique vrai, la sauvegarde a été déchargée et il faut quitter
            elif UiManager.UIelements.get("opportunities_icon",False):
                #Si le bouton du menu d’opportunités est choisi, on ouvre le menu d'opportunités
                OpportunitiesManager.OpenMap()
            elif UiManager.UIelements.get("taskmenu_icon",False):
                #Si le bouton du menu de tâches est choisi, on ouvre le menu de taches
                TaskManager.showMenu()
            elif UiManager.UIelements.get("help_icon",False):
                #Si le bouton du menu d'aide est choisi, on ouvre le menu d'aide
                HelpMenu.Open()
            elif UiManager.UIelements.get("select2",False):#si l'élément d'UI cliqué est l'élément stocké à UiManager.UIelements["select2"]
                for i in GameItems.menuElements:#pour chaque items de l'élément de sélection
                    if UiManager.UIelements.get("selectElements_"+i,False):#si l'élément d'UI est cliqué est le bon élément de sélection
                        if UiManager.showMenu["delete"]:#si delete est activé
                            UiManager.showMenu["delete"]=0#Désactiver le menu delete
                            SaveManager.ResetRotation()#On réinitialise la rotation
                            SaveManager.SetSelectedItem(None)#On réinitialise la selection
                            UiManager.LightPopup("Mode destruction désactivé")#affichage via une light popup
                        elif UiManager.showMenu.get("question",False):#si question est actif
                            HelpMenu.Open(i)#Affichage de la description
                        else:
                            if i == "Drill":
                                Tutorial.IncreaseStep(6)
                            SaveManager.SetSelectedItem(i)#On change l'item sélectionné
                            UiManager.LightPopup("Clic gauche pour placer, maj gauche + clic gauche pour placer plusieurs, clic droit pour annuler")
                if UiManager.UIelements.get("selectElements_delete",False):#si delete est cliqué
                    if UiManager.showMenu.get("question",False):#si “question” est actif
                        HelpMenu.Open("delete")#Description de delete
                    else:
                        UiManager.showMenu["delete"]=1-UiManager.showMenu["delete"]#désactiver/activer le menu “delete”
                        UiManager.LightPopup("Mode destruction "+ "activé" if UiManager.showMenu["delete"] else "Mode destruction désactivé")#Affiche une LightPopup
                        SaveManager.ResetRotation()#On réinitialise la rotation
                        SaveManager.SetSelectedItem(None)#On réinitialise la selection
                if UiManager.UIelements.get("selectElements_question",False):#si question est cliqué
                    UiManager.showMenu["question"]=1-UiManager.showMenu.get("question",0)#désactiver/activer le menu “question”
                    UiManager.showMenu["delete"]=0#on désactive le menu delete
                    SaveManager.ResetRotation()#On réinitialise la rotation
                    SaveManager.SetSelectedItem(None)#On réinitialise la selection
                    UiManager.LightPopup("Mode interrogation activé" if UiManager.showMenu["question"] else "Mode interrogation désactivé")#Affiche un LightPopup
                    if UiManager.showMenu.get("question",False):#si question est actif
                        UiManager.Popup(L.GetLoc("Session.Question"))#Afficher le principe d'utilisation du mode question
            
            elif UiManager.UIelements.get("inv2",False):#si la souris est dans inv2
                for i,e in enumerate(SaveManager.mainData.inv):#on énumère l'inventaire
                    if UiManager.UIelements.get("invElements_"+str(i),False):#si la souris est sur l'élément de l'inventaire
                        if UiManager.showMenu.get("question",False):#si question est actif
                            HelpMenu.Open(i)#Description de l'élément
                        elif e["n"] in MarketManager.marketItem.keys():#si c'est un item du market
                            SaveManager.SetSelectedItem(e["n"])#placer l'item
                            UiManager.LightPopup("Clic gauche pour placer, maj gauche + clic gauche pour placer plusieurs, clic droit pour annuler")#Affichage de LightPopup

            elif UiManager.UIelements.get("popup_area",False):#si la souris est dans la zone de popup
                for index,popup in enumerate(UiManager.UIPopup):#on parcours la liste des popups
                    if UiManager.UIelements.get("popup_"+str(index),False):#si la souris est dans la pop-up
                        if UiManager.UIelements.get("popup_launch_button_"+str(index)):#si le button de la pop-up est actif (doté d'une commande)
                            popup.launch()#lancer la fonction lié à la popup
                        popup.close(index)#fermer la pop-up
            return False
        
        if SaveManager.IsItemHere(UiManager.GetMouseWorldPos()):#si la position de la souris est dans un item
            if UiManager.showMenu.get("question",False):#si le mode question est activé
                    HelpMenu.Open(SaveManager.GetItemAtPos(UiManager.GetMouseWorldPos()).name)#Description de l'item
            elif UiManager.showMenu["delete"]:#si le mode delete est actif
                SaveManager.DeleteItem(UiManager.GetMouseWorldPos())#Suppression de l'item
                GameItems.Laser[str(UiManager.GetMouseWorldPos())]=lambda:None
                if not ShiftPressed:#si shift n'est pas pressé
                    UiManager.showMenu["delete"]=0#On désactive le mode delete
            elif SaveManager.IsItemSelected():#si item sélectionné
                UiManager.LightPopup(L.GetLoc("Session.AlreadyItemHere"))#affichage de LightPopup
            return False
        
        if UiManager.showMenu.get("question",False):#si le mode question est actif
            a=GameItems.Minerais.Type(*UiManager.GetMouseWorldPos())#On détecte si un minerai avec la position de la souris existe
            if a:#si un minerai existe
                HelpMenu.Open(a)#Affichage de la description
            return False
        
        if SaveManager.IsItemSelected():#si un item est sélectionné
            if SaveManager.ObstacleAtPos(UiManager.GetMouseWorldPos()):
                UiManager.LightPopup(L.GetLoc("Session.AlreadyItemHere"))#affichage de LightPopup
                return False
            if not SaveManager.IsTutorial() or Tutorial.NoticeItemPlacedAtPos(UiManager.GetMouseWorldPos(),SaveManager.GetSelectedItem()):
                b=SaveManager.PlaceItem(GameItems.Item(SaveManager.GetSelectedItem(), UiManager.GetMouseWorldPos(),{}))#Placer item
                if b and SaveManager.GetSelectedItem() in MarketManager.marketItem.keys():#si l'item est au market
                    SaveManager.GetFromInv(SaveManager.GetSelectedItem())#on le retire de l'inventaire
                    if SaveManager.IsInInv(SaveManager.GetSelectedItem())=="NotIn":
                        SaveManager.SetSelectedItem(None)
                if not ShiftPressed:#si shift n'est pas pressé
                    SaveManager.SetSelectedItem(None)#On désactive le mode sélection
    
    if button == 3: # 3 == right button
        #désactive tous les modes
        UiManager.showMenu["delete"]=0
        UiManager.showMenu["question"]=0
        SaveManager.ResetRotation()
        SaveManager.SetSelectedItem(None)
        
        for c,i in enumerate(EventManager.EnnemisList):
            if UiManager.UIelements.get("ennemi"+str(c),False):
                AudioManager.PlaySound("Laser")#jouer le son de laser
                laser=lambda:pygame.draw.polygon(UiManager.screen, (255, 0, 0), (drone.pos,pygame.mouse.get_pos(),(pygame.mouse.get_pos()[0]-20,pygame.mouse.get_pos()[1]-20)))
                i.pv-=10
                if i.pv<=0:
                    del EventManager.EnnemisList[c]
                    del UiManager.UIelements["ennemi"+str(c)]
                    AudioManager.PlaySound("Explosion")#jouer le son d'explosion
                    Stats.IncreaseStat("EnnemiesDestroyed")#On incrémente la statistique d'ennemis détruits
                    Tutorial.IncreaseStep(15)
                return False

        if SaveManager.IsItemHere(UiManager.GetMouseWorldPos()):#si un item est présent à la position de la souris
            clickedItem = SaveManager.GetItemAtPos(UiManager.GetMouseWorldPos())
            if clickedItem.metadata.get("pv",100)!=100:
                laser=lambda:pygame.draw.polygon(UiManager.screen, (0, 255, 0), (drone.pos,pygame.mouse.get_pos(),(pygame.mouse.get_pos()[0]-20,pygame.mouse.get_pos()[1]-20)))
                clickedItem.metadata["pv"] = min(clickedItem.metadata.get("pv", 100) + 25, 100)
                UiManager.LightPopup("Restauration des points de vie de l'appareil : pv "+str(clickedItem.metadata["pv"])+"/100")
                AudioManager.PlaySound("Healing")
                #Si la santé de l'objet égale ou dépasse 100...
                if clickedItem.metadata["pv"] >= 100:
                    #On incrémente la statistique de machines réparées
                    Stats.IncreaseStat("MachinesFullyRepaired")
                return False
            if clickedItem.name in ["Sorter","Storage","Market","Teleporter"]:
                if clickedItem.name == "Market":
                    Tutorial.IncreaseStep(18)
                clickedItem.edit(UiManager.interactItem(clickedItem))#si le nom de l'item est dans la liste, lancer l'interaction
            return False
        
        a=GameItems.Minerais.Type(*UiManager.GetMouseWorldPos())#On récupère le type de minerai
        if a:
            #dessin du laser
            AudioManager.PlaySound("Laser")#jouer le son de laser
            laser=lambda:pygame.draw.polygon(UiManager.screen, (255, 255, 190), (drone.pos,pygame.mouse.get_pos(),(pygame.mouse.get_pos()[0]-20,pygame.mouse.get_pos()[1]-20)))
            if a != "Obstacle":
                SaveManager.AddToInv(d=a)#Ajout à l'inventaire
                UiManager.LightPopup(L.GetLoc("Items."+str(a))+" ajouté à l'inventaire")#Affiche la LightPopup lié au minage
                Stats.IncreaseStat("Mined" + a)
                if a == "Copper":
                    Tutorial.IncreaseStep(3)
            else:
                SaveManager.ClearObstacle(UiManager.GetMouseWorldPos())
                Stats.IncreaseStat("ObstaclesDestroyed")
    
    return False

PauseMenuBackground = None#variable stockant le fond du menu de pause
        
def DisplayPauseMenuBackground():
    """Affiche le fond du menu de pause"""
    TickModules()#Actualisation de différents modules
    if PauseMenuBackground != None:#si le fond du menu de pause est différent de None
        UiManager.screen.blit(PauseMenuBackground,(0,0))#afficher le fond
        
def Pause():
    """Affiche le menu de pause"""
    
    AudioManager.ClearUsedChannels()#On vide les canaux de son utilisés
    
    global PauseMenuBackground
    #création du fond de pause
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    PauseMenuBackground = pygame.display.get_surface().copy()#copie de la surface
    PauseMenuBackground.blit(screenFilter,(0,0))#affichage
    
    quitGame = False
    def QuitGame():
        """Fonction pour quitter proprement le jeu"""
        pauseMenu.disable()#on désactive le menu de pause
        SaveManager.Unload()#on décharge la sauvegarde
        global quitGame
        quitGame = True
    
    #Création du menu de pause
    pauseMenu = pygame_menu.Menu(L.GetLoc("Session.Pause"), 400, 300, theme=pygame_menu.themes.THEME_DARK,onclose=pygame_menu.events.BACK)
    
    pauseMenu.add.button(L.GetLoc("Session.Continue"), pauseMenu.disable)#Reprendre la partie
    pauseMenu.add.button(L.GetLoc("Settings.Title"), lambda:SettingsManager.OpenSettings(DisplayPauseMenuBackground))#Bouton pour ouvrir les options
    pauseMenu.add.button(L.GetLoc("Game.MainMenu"), QuitGame)#Menu principal
    
    pauseMenu.mainloop(UiManager.screen,DisplayPauseMenuBackground)#affiche le menu
    
    PauseMenuBackground = None
    return quitGame

#Variable disant si la touche de capture d'écran a été pressée à la touche précédente
screenshotKeyPressedLast = False

def TickModules():
    """
    Exécute les fonctions de tick des différents modules et gère la prise de captures d'écrans dans les menus
    """
    SaveManager.TickClock()#Actualisation de l'horloge interne
    AudioManager.Tick()#Actualisation du son
    TaskManager.Tick()#Actualisation des tâches
    
    global screenshotKeyPressedLast
    
    #Est-ce que la touche de capture d'écran est pressée
    screenshotKeyPressed = pygame.key.get_pressed()[pygame.K_F2]
    
    #Si la touche de capture d'écran est pressée mais qu'elle n'était pas pressée à la frame précédente...
    if screenshotKeyPressed and not screenshotKeyPressedLast:
        UiManager.TakeScreenshot()#On prend une capture d'écran
    
    #On met à jour la variable d'appui à la frame précédente
    screenshotKeyPressedLast = screenshotKeyPressed

class Tutorial:
    """
    Fonctions liées au tutoriel
    """
    #Étape du tutoriel. Le premier membre est l'étape générale (construire des tapis roulants par exemple), et le second est l'étape intermédaire (7 tapis construits sur 10 par exemple)
    step = [0,0]
    #Popup servant à afficher le tutoriel
    popup = None
    
    def Init():
        """
        Initialise le tutoriel
        """
        #On tente de récupérer l'étape du tutoriel dans les données de la sauvegarde
        Tutorial.step = SaveManager.mainData.__dict__.get("TutorialStep",[0,0])
        #On force l'apparition d'un minerai de cuivre et d'un minerai de charbon qui seront utilisés dans le tutoriel
        GameItems.Minerais.ForceSpawn((0, 0), "Copper")
        GameItems.Minerais.ForceSpawn((10, -1), "Coal")
        
        #Si le tutoriel n'est pas à l'étape 23 (tutoriel fini)...
        if Tutorial.GetGlobalStep() != 23:
            #On crée un popup avec le texte de l'étape en cours
            Tutorial.popup = UiManager.Popup(L.GetLoc("Tuto." + str(Tutorial.GetGlobalStep()),*Tutorial.GetLocKeys()),d=1)
            #On règle la barre davancement
            Tutorial.popup.setProg(Tutorial.GetIntermediateStep()/Tutorial.GetStepMaxProg())
            #On s'assure qu'il n'y ait aucun obstacle sur les emplacement sur lesquels le joueur devra placer des objets
            SaveManager.mainData.clearedObstacles = [(7,-8),(7,-7),(11,-7),(7,-6),(0,-5),
                                                     (1,-5),(2,-5),(3,-5),(4,-5),(5,-5),
                                                     (6,-5),(7,-5),(8,-5),(9,-5),(10,-5),
                                                     (0,-4),(10,-4),(0,-3),(10,-3),(0,-2),
                                                     (10,-2),(0,-1),(10,-1),(0, 0)]
            
            #tâche spéciale et spécifique aux tutoriels
            task = {"id":0,"lv":0,"baseVal":0,"done":False,"claimed":False}
            
            #Si il n'y a aucune tâche dans la liste des tâches, on allonge la liste avec la tâche spéciale
            if len(SaveManager.mainData.tasks) == 0:
                SaveManager.mainData.tasks.append(task)
            #Sinon, si l'id de la tâche au début de la liste des tâches n'est pas 0...
            elif SaveManager.mainData.tasks[0]["id"] != 0:
                #On met dans la liste des tâches la tâche spéciale
                SaveManager.mainData.tasks[0] = task
    
    def SaveStep():
        """
        Sauvegarde l'étape du tutoriel en dur dans les données de la sauvegarde
        """
        SaveManager.mainData.TutorialStep = Tutorial.step
    
    def GetItemsToPlace()->tuple:
        """
        Renvoie la liste des textures et des position des objets à placer pendant cette étape du tutoriel
        """
        globalStep = Tutorial.GetGlobalStep()
        #Liste des textures (tuple avec le nom de la texture et la rotation)
        texList = []
        #Liste des positions (tuple x et y, l'indice doit correspondre à la texture correspondante dans texList)
        posList = []
        if globalStep == 7:
            texList = [("Drill", 0)]
            posList = [(0, 0)]
        if globalStep == 8:
            texList = [("ConveyorBelt", 0),("ConveyorBelt", 0),("ConveyorBelt", 0),("ConveyorBelt", 0)]
            posList = [(0,-4),(0,-3),(0,-2),(0,-1)]
        if globalStep == 9:
            texList = [("ConveyorBelt", 3),("ConveyorBelt", 3),("ConveyorBelt", 3),("ConveyorBelt", 3)]
            posList = [(0,-5),(1,-5),(2,-5),(3,-5)]
        if globalStep == 10:
            texList = [("Storage", 0)]
            posList = [(4,-5)]
        if globalStep == 12:
            texList = [("ConveyorBelt", 3),("ConveyorBelt", 3),("Furnace", 0)]
            posList = [(5,-5),(6,-5),(7,-5)]
        if globalStep == 13:
            texList = [("ConveyorBelt", 1),("ConveyorBelt", 1),("ConveyorBelt", 1),("ConveyorBelt", 0),("ConveyorBelt", 0),("ConveyorBelt", 0),("Drill", 0)]
            posList = [(8,-5),(9,-5),(10,-5),(10,-4),(10,-3),(10,-2),(10,-1)]
        if globalStep == 14:
            texList = [("Storage", 0),("ConveyorBelt", 0),("ConveyorBelt", 0)]
            posList = [(7,-8),(7,-7),(7,-6)]
        if globalStep == 18:
            texList = [("Market", 0)]
            posList = [(11,-7)]
        return (texList,posList)
    
    def Tick():
        """
        Affiche les effets visuels du tutoriel
        """
        #Étape globale du tutoriel
        globalStep = Tutorial.GetGlobalStep()
        
        #Ces étapes doivent rester affichées un certain nombre de secondes, il faut donc constamment les mettre à jour
        if globalStep in [2,16,17,21,22,4,11]:
            Tutorial.IncreaseStep(globalStep)
        
        if globalStep in [5,6,19,20]:
            s = pygame.Surface((UiManager.width,UiManager.height),pygame.SRCALPHA, 32).convert_alpha()
            if globalStep == 5:
                #Surlignage du menu de construction
                pygame.draw.polygon(s,(255,255,0,100),((UiManager.width-500, UiManager.height),(2*UiManager.width-501, UiManager.height),(2*UiManager.width-501, UiManager.height-30),(UiManager.width-175,UiManager.height-30),(UiManager.width-195, UiManager.height-50),(UiManager.width-500, UiManager.height-50)))
            if globalStep == 6:
                #Surlignage du bouton pour séléctionner la foreuse
                pygame.draw.polygon(s,(255,255,0,100),[(UiManager.width-500,UiManager.height-500),(UiManager.width-400,UiManager.height-500),(UiManager.width-400,UiManager.height-400),(UiManager.width-500,UiManager.height-400)])
            if globalStep == 20:
                #Surlignage du bouton de tâches
                pygame.draw.polygon(s,(255,255,0,100),[(100,0),(150,0),(150,50),(100,50)])
            if globalStep == 20:
                #Surlignage du bouton d'opportunités
                pygame.draw.polygon(s,(255,255,0,100),[(150,0),(200,0),(200,50),(150,50)])
            UiManager.screen.blit(s, (0,0))
        
        #On récupère les listes stockant les items à afficher en transparence
        texList, posList = Tutorial.GetItemsToPlace()
        
        zoom = SaveManager.GetZoom()
        
        #Pour chaque élément de la liste des textures...
        for i in range(len(posList)):
            texData = texList[i]
            #On récupère une copie transparente de la texture à afficher
            tex = TextureManager.GetTexture(texData[0], zoom).copy()
            tex.set_alpha(150)
            #On affiche la texture avec la position et la rotation souhaitées
            GameItems.AddToRender(0,lambda pos=posList[i],texture=tex,rot=texData[1]:UiManager.screen.blit(pygame.transform.rotate(texture,90*rot), UiManager.WorldPosToScreenPos(pos)))
    
    def NoticeItemPlacedAtPos(pos:tuple,item:str)->bool:
        """
        Fait avancer le tutoriel en fonction de l'item placé par le joueur et de sa position, et dit si il faut le placer ou pas
        """
        texList, posList = Tutorial.GetItemsToPlace()
        
        globalStep = Tutorial.GetGlobalStep()
        
        #Si l'étape globale est l'étape 23 (tuto fini), on valide le placement
        if globalStep == 23:
            return True
        
        #Si cette position n'est pas dans la liste des positions, on interdit le placement
        if pos not in posList:
            return False
        
        #Données sur le placement: Un tuple avec en 0 le type d'item et en 1 la rotation
        placementData = texList[posList.index(pos)]
        
        #Si l'item à placer correspond et que, si c'est un tapis roulant la rotation correspond également...
        if placementData[0] == item and (item != "ConveyorBelt" or placementData[1] == SaveManager.GetRotation()):
            #On met à jour le tuto et on autorise le placement
            Tutorial.IncreaseStep(globalStep)
            return True
        
        return False
    
    def IncreaseStep(currentStep:int):
        """
        Met à jour le tutoriel en fonction de l'étape en entrée
        """
        #Si la partie n'est pas en mode tutoriel, inutile d'exécuter
        if not SaveManager.IsTutorial():
            return
        
        #Si l'étape actuelle ne correspond pa à l'étape indiquée, ce n'est pas au tour de cet appel de la fonction d'effectuer des changements
        if currentStep != Tutorial.GetGlobalStep():
            return
        
        #progression maximale de l'étape en cours
        maxProg = Tutorial.GetStepMaxProg()
        
        #Si l'étape est une des étapes de cette liste, c'est une étape qui s'affiche pendant un temps donné
        if currentStep in [0,1,2,16,17,21,22,4,11]:
            #On incrémente donc l'étape intermédiaire en fonction du temps passé depuis la dernière boucle du heu
            Tutorial.IncreaseIntermediateStep(SaveManager.clock.get_time())
            #Si l'étape intermédiaire a dépassé la progression maximale, on passe a l'étape suivante
            if Tutorial.GetIntermediateStep() > maxProg:
                Tutorial.NextGlobalStep()
                Tutorial.SaveStep()
            return
        
        #On incrémente de 1 l'étape intermédiaire
        Tutorial.IncreaseIntermediateStep()
        #Si l'étape intermédiaire est arrivée à l'étape maximale, on passe à l'étape suivante
        if Tutorial.GetIntermediateStep() == maxProg:
            Tutorial.NextGlobalStep()
        
        #On sauvegarde l'étape en cours
        Tutorial.SaveStep()

    def NextGlobalStep():
        """
        Passe le tutoriel à l'étape suivante
        """
        Tutorial.step[0] += 1
        Tutorial.step[1] = 0
        
        globalStep = Tutorial.GetGlobalStep()
        
        if globalStep == 23:
            Tutorial.popup.close()
            Stats.SetStat("TutorialCompleted", 1)
        else:
            Tutorial.popup.setText(L.GetLoc("Tuto." + str(globalStep),*Tutorial.GetLocKeys()))
            Tutorial.popup.setProg(0)
        
        resources = {}
        
        if globalStep == 5:
            resources["Copper"] = 40
        if globalStep == 8:
            resources["Copper"] = 40
        if globalStep == 9:
            resources["Copper"] = 40
        if globalStep == 10:
            resources["Copper"] = 100
        if globalStep == 12:
            resources["Copper"] = 50
            resources["Gold"] = 80
        if globalStep == 13:
            resources["Copper"] = 110
        if globalStep == 14:
            resources["Copper"] = 120
        if globalStep == 15:
            EventManager.Ennemis.spawn()
        if globalStep == 18:
            resources["M1"] = 50
            resources["Copper"] = 50
            resources["Gold"] = 10
        
        for rName in resources.keys():
            for i in range(resources[rName]):
                SaveManager.AddToInv(rName)
    
    def GetGlobalStep()->int:
        """
        Renvoie l'étape globale du tutoriel
        """
        return Tutorial.step[0]
    
    def IncreaseIntermediateStep(value:float=1):
        """
        Augmente l'étape intermédaire du tutoriel
        """
        Tutorial.step[1] += value
        Tutorial.popup.setProg(Tutorial.GetIntermediateStep()/Tutorial.GetStepMaxProg())
    
    def GetStepMaxProg()->int:
        """
        Renvoie le maximum de l'étape intermédiaire du tutoriel en fonction de l'étape globale
        """
        globalStep = Tutorial.GetGlobalStep()
        if globalStep in [0,1,2,16,17,21,22,4,11]:
            return 1000 if globalStep == 1 else 5000
        if globalStep in [5,6,7,10,15,19,20]:
            return 1
        if globalStep == 18:
            return 2
        if globalStep in [12,14]:
            return 3
        if globalStep in [8,9]:
            return 4
        if globalStep == 13:
            return 7
        if globalStep == 3:
            return 10
        return 1
        
    def GetLocKeys()->list:
        """
        Renvoie les éléments additionels des clés de traduction des popups de tutoriel
        """
        globalStep = Tutorial.GetGlobalStep()
        if globalStep == 2:
            return [pygame.key.name(SettingsManager.GetKeybind(key)) for key in ("up","down","left","right")]
        if globalStep == 4:
            return [pygame.key.name(SettingsManager.GetKeybind("inv"))]
        if globalStep == 9:
            return [pygame.key.name(SettingsManager.GetKeybind("rotate"))]
        if globalStep == 19:
            return [pygame.key.name(SettingsManager.GetKeybind("tasks"))]
        if globalStep == 20:
            return [pygame.key.name(SettingsManager.GetKeybind("opportunities"))]
        return []
    
    def GetIntermediateStep()->float:
        """
        Renvoie l'étape intermédiaire du tutoriel
        """
        return Tutorial.step[1]

"""
Petite aide visuelle pour aider la création du tutoriel

c = "ConveyorBelt"
s = "Storage"
d = "Drill"
f = "Furnace"
m = "Market"

texList = [
                                                     (s, 0),
                                                     (c, 0),                     (m, 0),
                                                     (c, 0),
    (c, 3),(c, 3),(c, 3),(c, 3),(s, 0),(c, 3),(c, 3),(f, 0),(c, 1),(c, 1),(c, 1),
    (c, 0),                                                               (c, 0),
    (c, 0),                                                               (c, 0),
    (c, 0),                                                               (c, 0),
    (c, 0),                                                               (d, 0),
    (d, 0),
    ]

posList = [
                                                     (7,-8),
                                                     (7,-7),                      (11,-7),
                                                     (7,-6),
    (0,-5),(1,-5),(2,-5),(3,-5),(4,-5),(5,-5),(6,-5),(7,-5),(8,-5),(9,-5),(10,-5),
    (0,-4),                                                               (10,-4),
    (0,-3),                                                               (10,-3),
    (0,-2),                                                               (10,-2),
    (0,-1),                                                               (10,-1),
    (0, 0),
    ]
"""
