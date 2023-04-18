# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 21:43:27 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

#importations des bibliothèques
import pygame
import pygame_menu
import numpy as np
#importation des bibliothèques système
import random
#import threading
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

showTuto=9**9
def Tuto(t=1):
    """
    Fonction d'affichage du tutoriel
    """
    global showTuto
    #si showTuto est dans [] on supprime toutes les popups
    if showTuto in [1,2,3,4,5,6,7,8]:
        for i,popup in enumerate(UiManager.UIPopup):#pour i, popup dans enumerate(UiManager.UIPopup)
            popup.close(i)#fermeture de la popup
    showTuto=showTuto+1 if t else t#si t (1=True) alors showTuto=1, sinon on incrémente showTuto de 1
    #a stocke le texte pour la première étape du tutoriel (affichage des touches de déplacements)
    a=L.GetLoc("Session.Tuto."+str(showTuto),pygame.key.name(SettingsManager.GetKeybind("up")),pygame.key.name(SettingsManager.GetKeybind("down")),pygame.key.name(SettingsManager.GetKeybind("left")),pygame.key.name(SettingsManager.GetKeybind("right")))
    #Affichage de la popup
    UiManager.Popup(a,d=1 if showTuto<len(a)-1 else 0)


laser=lambda:None
def Play(saveName:str,**kwargs):
    """
    Lance le jeu
    Fonction principale de la Session
    """
    global laser
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
    GameItems.Minerais.SpawnAllScreen()#Spawn des minerais
    
    
    if SaveManager.mainData.gamemode == 2:#si mode tutoriel
        Tuto(0)#afficher le tutoriel
    
    drone=AnimationsManager.Drone()#Création du drone

    EventM=EventManager.Events()#Création du gestionnaire d'événements
    
    EventManager.EnnemisList.clear()#On supprime tous les ennemis
    
    AudioManager.BeginGameAmbience()

    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEWHEEL, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION,AudioManager.MUSIC_ENDED, AudioManager.AMBIENCE_ENDED,AudioManager.SOUND_ENDED])#réduit le nombre d'évent
    
    while SaveManager.SaveLoaded():#tant que la sauvegarde est chargée
        
        UiManager.UpdateBackground()#mise à jour du fond
        
        DisplayObjects(int(runtime))#Afficher l'objet de manière dynamique

        for c,i in enumerate(EventManager.EnnemisList):#pour chaque ennemi dans EnnemisList
            i.ia(runtime)#calcul de la trajectoire et mouvement
            i.show(c)#affichage de l'ennemi

        laser()#affichage du laser

        drone.show()#affichage du drone
        
        UiManager.DisplayUi()#Afficher l'Interface Utilisateur

        pygame.display.update()#Mise à jour de l'affichage Pygame
        
        AudioManager.Tick()#Met à jour le gestionnaire de sons
        
        HandleLongKeyInputs()#gestion des longs clics
        
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

                if showTuto==1:#si showTuto==1
                    Tuto()#afficher le tuto
            
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
        
        SaveManager.TickClock()#on mets à jour l'horloge des FPS
        runtime+=SaveManager.clock.get_time() / 8#on augmente le runtime
        if runtime > 50:#si le runtime est supérieur à 50
            runtime = 0#on reset le runtime
            if SaveManager.SaveLoaded():#on vérifie si la sauvegarde est chargée
                OpportunitiesManager.Tick()#on fait passer le temps des Opportunités
                drone.update()#on mets à jour le drone
                EventM.LaunchEvent()#Lancer un événement
    return True
    
        
def DisplayObjects(runtime:int):
    """Affiche les objets de manière dynamique"""
    
    for m in GameItems.current:#pour chaque minerais dans GameItems.current
        GameItems.Minerais.PlaceFromCurrent(m)#placement du minerais
        #threading.Thread(target=lambda:GameItems.Minerais.PlaceFromCurrent(m)).start()#placement du minerais

    for item in SaveManager.GetItems():#pour chaque item dans SaveManager.GetItems()
        if runtime==0:#si le runtime vaut 0
            item.Give()#transmition de l'inventaire à l'item adjacent
        item.Display(runtime)#Afficher l'item
    
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
    
    SaveManager.TranslateCam(camOffset)#On applique les changements de caméra
    
    global ShiftPressed
    ShiftPressed = keys[pygame.K_LSHIFT]
    
    if camOffset != [0,0]:#si un déplacement a eu lieu
        if showTuto==0:#si le joueur a bougé lors du tuto phase 0
            Tuto()#on affiche le tuto
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
            
def HandleShortKeyInputs(key):
    """Traitement des pressions de touches rapides"""
    if key == SettingsManager.GetKeybind("rotate"):#si la clé pressée est associée à rotate
        SaveManager.UpdateRotation()#mise à jour de la rotation
    if key == pygame.K_F2:#si la clé pressé est F2
        UiManager.TakeScreenshot()#prendre une capture d'écran
    if key == SettingsManager.GetKeybind("inv"):#si la clé pressée est associée à inv
        UiManager.showMenu["inv"]=1-UiManager.showMenu["inv"]#Afficher/cacher l'inventaire
    if key == SettingsManager.GetKeybind("opportunities"):#si la clé pressée est associée à opportunities
        OpportunitiesManager.OpenMap()#ouvrir les opportunités
    if key == pygame.K_t:#si la clé pressée est t
        TaskManager.showMenu()#afficher le menu de taches
    if key == pygame.K_ESCAPE:#si la clé pressée est ESCAPE
        if Pause():#On fait pause
            return True#Si la fonction pause indique vrai, la sauvegarde a été déchargée et il faut quitter
    return False
    
def HandleMouseClicks(button,drone):
    """Gestion des clics"""
    global laser
    if button == 1: # 1 == left button
        if UiManager.IsClickOnUI():#si c'est un clic sur UI
            if UiManager.UIelements.get("select",False):#Si l'élément d'UI cliqué est l'élément stocké à UiManager.UIelements["select"], alors
                UiManager.showMenu["select"]=1-UiManager.showMenu.get("select",0)#montrer le menu "select"
            elif UiManager.UIelements.get("inv",False):#si l'élément UI cliqué est inventaire
                UiManager.showMenu["inv"]=1-UiManager.showMenu.get("inv",0)#montrer le menu "inv"
            elif UiManager.UIelements.get("menu_icon",False):#Si l'élément d'UI cliqué est l'élément stocké à UiManager.UIelements["menu_icon"], alors
                if Pause():#On fait pause
                    return True#Si la fonction pause indique vrai, la sauvegarde a été déchargée et il faut quitter
            elif UiManager.UIelements.get("opportunities_icon",False):
                #Si le bouton du menu d'opportunitées est choisi, on ouvre le menu d'opportunités
                OpportunitiesManager.OpenMap()
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
                            GameItems.getDescription(i)#Affichage de la description
                        else:
                            SaveManager.SetSelectedItem(i)#On change l'item sélectionné
                            UiManager.LightPopup("Clic gauche pour placer, maj gauche + clic gauche pour placer plusieurs, clic droit pour annuler")
                if UiManager.UIelements.get("selectElements_delete",False):#si delete est cliqué
                    if UiManager.showMenu.get("question",False):#si “question” est actif
                        GameItems.getDescription("delete")#Description de delete
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
                            GameItems.getDescription(i)#Description de l'élément
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
                    GameItems.getDescription(SaveManager.GetItemAtPos(UiManager.GetMouseWorldPos()).name)#Description de l'item
            elif UiManager.showMenu["delete"]:#si le mode delete est actif
                SaveManager.DeleteItem(UiManager.GetMouseWorldPos())#Suppression de l'item
                if not ShiftPressed:#si shift n'est pas pressé
                    UiManager.showMenu["delete"]=0#On désactive le mode delete
            elif SaveManager.IsItemSelected():#si item sélectionné
                UiManager.LightPopup(L.GetLoc("Session.AlreadyItemHere"))#affichage de LightPopup
            return False
        
        if UiManager.showMenu.get("question",False):#si le mode question est actif
            a=GameItems.Minerais.Type(*UiManager.GetMouseWorldPos())#On détecte si un Minerai avec la position de la souris existe
            if a:#si un minerai existe
                GameItems.getDescription(a)#Affichage de la description
            return False
        
        if SaveManager.IsItemSelected():#si un item est sélectionné
            b=SaveManager.PlaceItem(GameItems.Item(SaveManager.GetSelectedItem(), UiManager.GetMouseWorldPos(),{}))#Placer item
            if b and ((showTuto==3 and SaveManager.GetSelectedItem()=="Drill")#si le mode tuto 3 est actif et item = drill
                   or (showTuto==4 and "ConveyorBelt" in SaveManager.GetSelectedItem())#ou si tuto=4 item = ConveyorBelt
                   or (showTuto==5 and SaveManager.GetSelectedItem()=="Storage")):#ou si tuto=5 item = storage
                Tuto()#afficher le tuto
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
                    AudioManager.PlaySound("Explosion")#jouer le son d'explosion

        if SaveManager.IsItemHere(UiManager.GetMouseWorldPos()):#si un item est présent à la position de la souris
            clickedItem = SaveManager.GetItemAtPos(UiManager.GetMouseWorldPos())
            #UiManager.LightPopup(clickedItem.name+"\n"+str(clickedItem.giveto)+"\n"+str(clickedItem.metadata)+"\n"+str(GameItems.Minerais.Type(*UiManager.GetMouseWorldPos()))+str(GameItems.Minerais.Type(*clickedItem.pos)))
            if clickedItem.name in ["Sorter","Storage","Market"]:clickedItem.edit(UiManager.interactItem(clickedItem))#si le nom de l'item est dans la liste, lancer l'interaction
            return False
        
        a=GameItems.Minerais.Type(*UiManager.GetMouseWorldPos())#On récupère le type de minerais
        if a:
            #dessin du laser
            AudioManager.PlaySound("Laser")#jouer le son de laser
            laser=lambda:pygame.draw.polygon(UiManager.screen, (255, 255, 190), (drone.pos,pygame.mouse.get_pos(),(pygame.mouse.get_pos()[0]-20,pygame.mouse.get_pos()[1]-20)))
            SaveManager.AddToInv(d=a)#Ajout à l'inventaire
            UiManager.LightPopup(L.GetLoc("Items."+str(a))+" ajouté à l'inventaire")#Affiche la LightPopup lié au minage
            if showTuto==2:#si tuto=2
                    Tuto()#afficher le tuto
        

    
    return False

PauseMenuBackground = None#variable stockant le fond du menu de pause
        
def DisplayPauseMenuBackground():
    """Affiche le fond du menu de pause"""
    SaveManager.TickClock()#actualisation de l'horloge interne
    AudioManager.Tick()#Actualisation du son
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
    