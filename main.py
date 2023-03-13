# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 16:13:46 2023

@author: Thomas Sartre et François Patinec-Haxel
"""
#importation des bibliothèques
import pygame
import pygame_menu

import os
import random

import TextureManager
import UiManager
import SessionManager
import AudioManager
import PlanetGenerator
import SettingsManager
import SaveManager
import Localization


pygame.init()#initialisation pygame

UiManager.Init()#initialisation du l'UiManager

pygame.display.set_caption('SpaceFactory')#Définition du tire de la fenêtre

TextureManager.LoadAllTextures()#chargement des textures

AudioManager.Init()#Initialisation de l'AudioManager

SettingsManager.LoadSettings()#chargement des paramètres

Localization.Init()#chargement des traductions

class Menus:
    """
    Contient des références aux différents menus du menu principal
    """
    MainMenu = None
    SavesList = None
    SaveCreation = None


def OpenMainMenu():
    #Définition du Menu (ici, le menu est généré via le module pygame_menu)
    Menus.MainMenu = pygame_menu.Menu(Localization.GetLoc('Game.Title'), 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    Menus.MainMenu.add.vertical_margin(30)
    
    Menus.MainMenu.add.button(Localization.GetLoc('Game.Play'), OpenSavesList)#Bouton pour lancer le jeu
    Menus.MainMenu.add.button(Localization.GetLoc('Settings.Title'), lambda:SettingsManager.OpenSettings(UiManager.DisplayBackground))#Bouton pour ouvrir les options
    Menus.MainMenu.add.button(Localization.GetLoc('Game.Quit'), pygame_menu.events.EXIT)#Quitter le jeu
    
    Menus.MainMenu.add.button(Localization.GetLoc('Game.Credits'), OpenCredits, align=pygame_menu.locals.ALIGN_LEFT, font_size=20)
    
    Menus.MainMenu.mainloop(UiManager.screen, lambda : (UiManager.DisplayBackground(),pygame.key.set_repeat(1000)))#Boucle principale du Menu

def OpenSavesList():
    if Menus.SavesList != None:
        Menus.SavesList.disable()
    Menus.SavesList = pygame_menu.Menu('Sauvegardes', 500, 400, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    Menus.SavesList.add.button(Localization.GetLoc('Game.Back'), Menus.SavesList.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    Menus.SavesList.add.button(Localization.GetLoc('Saves.NewSave'), OpenSaveCreationMenu)
    
    if not os.path.exists("Saves/"):#si le dossier de sauvegarde n'existe pas, le créer
        os.makedirs("Saves/")
    
    saveNames = []
    for saveFile in os.listdir('Saves/'):
        if SaveManager.SaveExists(saveFile):
            saveNames.append(saveFile)
    
    frame = Menus.SavesList.add.frame_v(460, max(len(saveNames) * 100, 245), background_color=(50, 50, 50), padding=0)
    frame.relax(True)
    
    for saveName in saveNames:
        
        saveFrame = Menus.SavesList.add.frame_h(460, 100, padding=0)
        saveFrame.relax(True)
        frame.pack(saveFrame)
        
        saveFrame.pack(Menus.SavesList.add.button(saveName, lambda save=saveName: (Menus.SavesList.disable(), SessionManager.Play(save))))
        
        planetTex = TextureManager.GetTexture("missingThumb")
        texPath = "Saves/" + saveName + "/planet.png"
        if os.path.isfile(texPath):
            planetTex = pygame.image.load(texPath)
        saveFrame.pack(Menus.SavesList.add.surface(pygame.transform.scale(planetTex,(90,90))), align=pygame_menu.locals.ALIGN_RIGHT)
        
    Menus.SavesList.mainloop(UiManager.screen, UiManager.DisplayBackground)
   
def OpenSaveCreationMenu():
    if Menus.SaveCreation != None:
        Menus.SaveCreation.disable()
    Menus.SaveCreation = pygame_menu.Menu(Localization.GetLoc('Saves.Title'), 600, 500, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    Menus.SaveCreation.add.button(Localization.GetLoc('Game.Back'), Menus.SaveCreation.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    menuSections = Menus.SaveCreation.add.frame_h(560, 195, padding=0)
    menuSections.relax(True)
    
    creationTools = Menus.SaveCreation.add.frame_v(420, 195, padding=0)
    creationTools.relax(True)
    
    menuSections.pack(creationTools)
    
    saveNameInput=Menus.SaveCreation.add.text_input(Localization.GetLoc('Saves.NewSave.Name'), default=Localization.GetLoc('Saves.NewSave'),maxchar=20)
    creationTools.pack(saveNameInput)
    
    global seedInput
    seedInput=Menus.SaveCreation.add.text_input(Localization.GetLoc('Saves.NewSave.Seed'),maxchar=10)
    creationTools.pack(seedInput)
    
    SaveManager.planetTex = PlanetGenerator.Generate()
    thumbDisplayer = Menus.SaveCreation.add.surface(pygame.transform.scale(SaveManager.planetTex,(150,150)))
    
    def SetSurface(surface):
        SaveManager.planetTex = surface
        thumbDisplayer.set_surface(pygame.transform.scale(SaveManager.planetTex,(150,150)))
    
    menuSections.pack(thumbDisplayer)
    
    environmentsDict = {0: Localization.GetLoc('Saves.NewSave.Environment.Random'),
                        1: Localization.GetLoc('Saves.NewSave.Environment.Lunar'),
                        2: Localization.GetLoc('Saves.NewSave.Environment.Desertic'),
                        3: Localization.GetLoc('Saves.NewSave.Environment.Lifefull')}
    Menus.SaveCreation.add.range_slider(Localization.GetLoc('Saves.NewSave.Environment'), 0, list(environmentsDict.keys()),
                      slider_text_value_enabled=False, width=300, align=pygame_menu.locals.ALIGN_RIGHT,
                      value_format=lambda x: environmentsDict[x])
    difficultiesDict = {0: Localization.GetLoc('Saves.NewSave.Difficulty.Easy'),
                        1: Localization.GetLoc('Saves.NewSave.Difficulty.Normal'),
                        2: Localization.GetLoc('Saves.NewSave.Difficulty.Hard')}
    Menus.SaveCreation.add.range_slider(Localization.GetLoc('Saves.NewSave.Difficulty'), 1, list(difficultiesDict.keys()),
                      slider_text_value_enabled=False, width=300, align=pygame_menu.locals.ALIGN_RIGHT,
                      value_format=lambda x: difficultiesDict[x])
    
    global CreateSaveButton
    CreateSaveButton = Menus.SaveCreation.add.button(Localization.GetLoc('Saves.NewSave.Create'), lambda : TryCreateSave(saveNameInput))
    
    Menus.SaveCreation.mainloop(UiManager.screen, UiManager.DisplayBackground)
    
def TryCreateSave(saveNameInput):
    
    saveName = str(saveNameInput.get_value())
    
    if SaveManager.SaveExists(saveName):
        global CreateSaveButton
        CreateSaveButton.set_title(Localization.GetLoc('Saves.NewSave.AlreadyExists')).set_background_color((218, 85, 82), inflate=(0, 0))
        return
    
    Menus.SavesList.disable()
    Menus.SaveCreation.disable()
    SessionManager.Play(saveName,GetSeedFromInput(),tuto=1)
    
def GetSeedFromInput():

    seed = None
    
    if seedInput != None:
        inputedSeed = seedInput.get_value()
        if inputedSeed == "":
            seed = random.randint(-(9**9),9**9)
        else:
            try:
                seed = int(inputedSeed)
            except:
                seed = hash(inputedSeed)
        while seed > 9**9 or seed < -(9**9):
            seed = int(seed/10)
    
    return seed

def OpenCredits():
    
    creditsMenu = pygame_menu.Menu(Localization.GetLoc('Game.Credits'), UiManager.width//1.1, 600, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    creditsMenu.add.button(Localization.GetLoc('Game.Back'), creditsMenu.disable, align=pygame_menu.locals.ALIGN_LEFT)
    creditsMenu.add.vertical_margin(30)
    with open("Assets/credits.txt", "r", encoding="utf-8") as f:
        creditsMenu.add.label(f.read(), font_size=20)
    
    creditsMenu.mainloop(UiManager.screen, UiManager.DisplayBackground)

OpenMainMenu()
