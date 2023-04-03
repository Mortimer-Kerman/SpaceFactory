# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 21:43:27 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import pygame_menu

import random

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

showTuto=9**9
def Tuto(t=1):
    global showTuto
    if showTuto in [1,2,3,4,5,6,7,8]:
        for i,popup in enumerate(UiManager.UIPopup):
            popup.close(i)
    showTuto=showTuto+1 if t else t
    a=L.GetLoc("Session.Tuto."+str(showTuto),pygame.key.name(SettingsManager.GetKeybind("up")),pygame.key.name(SettingsManager.GetKeybind("down")),pygame.key.name(SettingsManager.GetKeybind("left")),pygame.key.name(SettingsManager.GetKeybind("right")))
    
    UiManager.Popup(a,d=1 if showTuto<len(a)-1 else 0)

def Play(saveName:str,**kwargs):
    """
    Lance le jeu
    """
    if not SaveManager.Load(saveName):#Chargement de la sauvegarde
        return False
    
    seed = kwargs.get("seed",None)
    if seed != None:
        SaveManager.mainData.seed = seed
    
    planetaryConditions = kwargs.get("planetaryConditions",None)
    if planetaryConditions != None:
        SaveManager.mainData.planetaryConditions = planetaryConditions
    
    difficulty = kwargs.get("difficulty",None)
    if difficulty != None:
        SaveManager.mainData.difficulty = difficulty
        
    gamemode = kwargs.get("gamemode",None)
    if gamemode != None:
        SaveManager.mainData.gamemode = gamemode
    
    runtime=0
    GameItems.Minerais.SpawnAllScreen()#Spawn des minerais
    
    
    if SaveManager.mainData.gamemode == 2:
        Tuto(0)
    
    while SaveManager.SaveLoaded():#tant que la sauvegarde est chargée
        
        UiManager.UpdateBackground()#mise à jour du fond
        
        DisplayObjects(int(runtime))
        
        UiManager.DisplayUi()#Afficher l'Interface Utilisateur
        
        pygame.display.update()#Mise à jour de l'affichage Pygame
        
        AudioManager.Tick()#Met à jour le gestionnaire de sons
        
        HandleLongKeyInputs()
        
        for event in pygame.event.get():
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
                    GameItems.Minerais.SpawnBorder()#On spawn les minerais aux bordures

                if showTuto==1:
                    Tuto()
            
            #action de clic sur une touche
            if event.type == pygame.KEYDOWN:
                if HandleShortKeyInputs(event.key):
                    return True
            
            if event.type == pygame.MOUSEBUTTONDOWN:#en cas de clic
                if HandleMouseClicks(event.button):
                    return True
        
        SaveManager.clock.tick()#on mets à jour l'horloge des FPS
        runtime+=SaveManager.clock.get_time() / 8
        if runtime > 50:
            runtime = 0
            if SaveManager.SaveLoaded():
                OpportunitiesManager.Tick()
    return True
    
        
def DisplayObjects(runtime:int):
    
    for m in GameItems.current:#pour chaque minerais dans GameItems.current
        GameItems.Minerais.PlaceFromCurrent(m)#placement du minerais

    for item in SaveManager.GetItems():#pour chaque item dans SaveManager.GetItems()
        if runtime==0:
            item.Give()#transmition de l'inventaire à l'item adjacent
        item.Display(runtime)#Afficher l'item
    
    GameItems.ExecuteRender()
    
    UiManager.DisplayItemToPlace()

def HandleLongKeyInputs():
    #action du clavier
    keys = pygame.key.get_pressed()#On stocke les touches pressées
    
    camOffset = [0,0]#Définition de l'offset de la caméra
    if keys[SettingsManager.GetKeybind("up")]:#si touche up
        camOffset[1]+=SaveManager.clock.get_time() / 2
    if keys[SettingsManager.GetKeybind("down")]:#si touche down
        camOffset[1]-=SaveManager.clock.get_time() / 2
    if keys[SettingsManager.GetKeybind("right")]:#si touche right
        camOffset[0]-=SaveManager.clock.get_time() / 2
    if keys[SettingsManager.GetKeybind("left")]:#si touche left
        camOffset[0]+=SaveManager.clock.get_time() / 2
    SaveManager.TranslateCam(camOffset)#On applique les changements de caméra
    
    if camOffset != [0,0]:#si un déplacement a eu lieu
        GameItems.Minerais.SpawnBorder()#on spawn les minerais aux bordures
        if showTuto==0:
            Tuto()
            
def HandleShortKeyInputs(key):
    if key == SettingsManager.GetKeybind("rotate"):
        SaveManager.UpdateRotation()#mise à jour de la rotation
    if key == pygame.K_F2:
        UiManager.TakeScreenshot()
    if key == SettingsManager.GetKeybind("inv"):
        UiManager.showMenu["inv"]=1-UiManager.showMenu["inv"]
    if key == pygame.K_m:
        OpportunitiesManager.OpenMap()
    if key == pygame.K_t:
        TaskManager.showMenu()
    if key == pygame.K_ESCAPE:
        if Pause():#On fait pause
            return True#Si la fonction pause indique vrai, la sauvegarde a été déchargée et il faut quitter
    return False
    
def HandleMouseClicks(button):
    if button == 1: # 1 == left button
        if not UiManager.IsClickOnUI():#si ce n'est pas un clic sur UI
            if not SaveManager.IsItemHere(UiManager.GetMouseWorldPos()):
                if not UiManager.showMenu["delete"]:
                    if not SaveManager.IsItemHere(UiManager.GetMouseWorldPos()):
                        if UiManager.showMenu.get("question",False):
                            a=GameItems.Minerais.Type(*UiManager.GetMouseWorldPos())
                            if a:
                                GameItems.getDescription(a)
                        else:
                            SaveManager.PlaceItem(GameItems.Item(SaveManager.GetSelectedItem(), UiManager.GetMouseWorldPos(),{}))#Placer item
                        if (showTuto==3 and SaveManager.GetSelectedItem()=="foreuse") or (showTuto==4 and "tapis" in SaveManager.GetSelectedItem()) or (showTuto==5 and SaveManager.GetSelectedItem()=="stockage"):
                            Tuto()
                else:
                    SaveManager.DeleteItem(UiManager.GetMouseWorldPos())
            else:
                if UiManager.showMenu.get("question",False):
                        GameItems.getDescription(SaveManager.GetItemAtPos(UiManager.GetMouseWorldPos()).name)
                        a=GameItems.Minerais.Type(*UiManager.GetMouseWorldPos())
                        if a:
                            GameItems.getDescription(a)
                elif UiManager.showMenu["delete"]:
                    SaveManager.DeleteItem(UiManager.GetMouseWorldPos())
                elif UiManager.showMenu.get("craft",False):
                                GameItems.getPrice(a)
                else:
                    UiManager.LightPopup(L.GetLoc("Session.AlreadyItemHere"))

        elif UiManager.UIelements.get("select",False):#Si l'élément d'UI cliqué est l'élément stocké à UiManager.UIelements["select"], alors
            UiManager.showMenu["select"]=1-UiManager.showMenu.get("select",0)#montrer le menu "select"
        elif UiManager.UIelements.get("inv",False):#si l'élément UI cliqué est inventaire
            UiManager.showMenu["inv"]=1-UiManager.showMenu.get("inv",0)#montrer le menu "inv"
        elif UiManager.UIelements.get("menu_icon",False):#Si l'élément d'UI cliqué est l'élément stocké à UiManager.UIelements["menu_icon"], alors
            if Pause():#On fait pause
                return True#Si la fonction pause indique vrai, la sauvegarde a été déchargée et il faut quitter
        elif UiManager.UIelements.get("select2",False):
            for i in GameItems.menuElements:
                if UiManager.UIelements.get("selectElements_"+i,False):
                    if UiManager.showMenu["delete"]:
                        UiManager.showMenu["delete"]=0
                        UiManager.LightPopup("Mode destruction désactivé")
                    elif UiManager.showMenu.get("question",False):
                        GameItems.getDescription(i)
                    elif UiManager.showMenu.get("craft",False):
                        GameItems.getPrice(i)
                    else:
                        SaveManager.SetSelectedItem(i)
            if UiManager.UIelements.get("selectElements_delete",False):
                if UiManager.showMenu.get("question",False):
                    GameItems.getDescription("delete")
                else:
                    UiManager.showMenu["delete"]=1-UiManager.showMenu["delete"]
                    UiManager.LightPopup("Mode destruction "+ "activé" if UiManager.showMenu["delete"] else "désactivé")
            if UiManager.UIelements.get("selectElements_question",False):
                UiManager.showMenu["question"]=1-UiManager.showMenu.get("question",0)
                UiManager.showMenu["delete"]=0
                UiManager.LightPopup("Mode interrogation activé")
                if UiManager.showMenu.get("question",False):
                    UiManager.Popup(L.GetLoc("Session.Question"))
            if UiManager.UIelements.get("selectElements_craft",False):
                UiManager.showMenu["craft"]=1-UiManager.showMenu["craft"]
                UiManager.Popup(L.GetLoc("Session.Craft"))
                UiManager.LightPopup(text="Mode composition activé")
        
        elif UiManager.UIelements.get("inv2",False):
            for i,e in enumerate(SaveManager.mainData.inv):
                if UiManager.UIelements.get("invElements_"+str(i),False):
                    if UiManager.showMenu.get("question",False):
                        GameItems.getDescription(i)
                    elif e["n"] in MarketManager.marketItem.keys():
                        SaveManager.SetSelectedItem(e["n"])

        elif UiManager.UIelements.get("popup_area",False):
            for index,popup in enumerate(UiManager.UIPopup):
                if UiManager.UIelements.get("popup_"+str(index),False):
                    if UiManager.UIelements.get("popup_launch_button_"+str(index)):
                        popup.launch()
                    popup.close(index)
    
    if button == 3: # 3 == right button
        if not UiManager.IsClickOnUI():#si ce n'est pas un clic sur UI
            clickedItem = SaveManager.GetItemAtPos(UiManager.GetMouseWorldPos())
            if clickedItem != None:
                UiManager.LightPopup(clickedItem.name+"\n"+str(clickedItem.giveto)+"\n"+str(clickedItem.metadata)+"\n"+str(GameItems.Minerais.Type(*UiManager.GetMouseWorldPos()))+str(GameItems.Minerais.Type(*clickedItem.pos)))
                if clickedItem.name in ["trieur","stockage","market"]:clickedItem.edit(UiManager.interactItem(clickedItem))
            else:
                a=GameItems.Minerais.Type(*UiManager.GetMouseWorldPos())
                if a:
                    SaveManager.AddToInv(d=a)
                    UiManager.LightPopup(str(a)+" ajouté à l'inventaire")
                    if showTuto==2:
                            Tuto()
        elif UiManager.UIelements.get("select2",False):
            for i in GameItems.menuElements:
                if UiManager.UIelements.get("selectElements_"+i,False):
                    GameItems.getPrice(i)

    
    return False


PauseMenuBackground = None    
        
def DisplayPauseMenuBackground():
    if PauseMenuBackground != None:
        UiManager.screen.blit(PauseMenuBackground,(0,0))
        
def Pause():
    global PauseMenuBackground
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    PauseMenuBackground = pygame.display.get_surface().copy()
    PauseMenuBackground.blit(screenFilter,(0,0))
    
    quitGame = False
    def QuitGame():
        pauseMenu.disable()
        SaveManager.Unload()
        global quitGame
        quitGame = True
    
    pauseMenu = pygame_menu.Menu(L.GetLoc("Session.Pause"), 400, 300, theme=pygame_menu.themes.THEME_DARK)
    
    pauseMenu.add.button(L.GetLoc("Session.Continue"), pauseMenu.disable)#Reprendre la partie
    pauseMenu.add.button(L.GetLoc("Settings.Title"), lambda:SettingsManager.OpenSettings(DisplayPauseMenuBackground))#Bouton pour ouvrir les options
    pauseMenu.add.button(L.GetLoc("Game.MainMenu"), QuitGame)#Menu principal
    
    pauseMenu.mainloop(UiManager.screen,DisplayPauseMenuBackground)
    
    
    PauseMenuBackground = None
    return quitGame
    