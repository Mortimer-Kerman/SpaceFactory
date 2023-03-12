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


pygame.init()#initialisation pygame

UiManager.Init()#initialisation du l'UiManager

pygame.display.set_caption('SpaceFactory')#Définition du tire de la fenêtre

TextureManager.LoadAllTextures()#chargement des textures

AudioManager.Init()#Initialisation de l'AudioManager

SettingsManager.LoadSettings()#chargement des paramètres

class Menus:
    """
    Contient des références aux différents menus du menu principal
    """
    MainMenu = None
    SavesList = None
    SaveCreation = None


def OpenMainMenu():
    #Définition du Menu (ici, le menu est généré via le module pygame_menu)
    Menus.MainMenu = pygame_menu.Menu('Space Factory', 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    Menus.MainMenu.add.vertical_margin(30)
    
    Menus.MainMenu.add.button('Jouer', OpenSavesList)#Bouton pour lancer le jeu
    Menus.MainMenu.add.button('Options', lambda:SettingsManager.OpenSettings(UiManager.DisplayBackground))#Bouton pour ouvrir les options
    Menus.MainMenu.add.button('Quitter', pygame_menu.events.EXIT)#Quitter le jeu
    
    Menus.MainMenu.add.button('Crédits', OpenCredits, align=pygame_menu.locals.ALIGN_LEFT, font_size=20)
    
    Menus.MainMenu.mainloop(UiManager.screen, lambda : (UiManager.DisplayBackground(),pygame.key.set_repeat(1000)))#Boucle principale du Menu

def OpenSavesList():
    if Menus.SavesList != None:
        Menus.SavesList.disable()
    Menus.SavesList = pygame_menu.Menu('Sauvegardes', 500, 400, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    Menus.SavesList.add.button('Retour', Menus.SavesList.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    Menus.SavesList.add.button('Nouvelle sauvegarde', OpenSaveCreationMenu)
    
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
    Menus.SaveCreation = pygame_menu.Menu('Sauvegardes', 600, 500, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    Menus.SaveCreation.add.button('Retour', Menus.SaveCreation.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    menuSections = Menus.SaveCreation.add.frame_h(560, 195, padding=0)
    menuSections.relax(True)
    
    creationTools = Menus.SaveCreation.add.frame_v(420, 195, padding=0)
    creationTools.relax(True)
    
    menuSections.pack(creationTools)
    
    saveNameInput=Menus.SaveCreation.add.text_input('Nom: ', default='save',maxchar=10)
    creationTools.pack(saveNameInput)
    
    global seedInput
    seedInput=Menus.SaveCreation.add.text_input("Graine: ",maxchar=10)
    creationTools.pack(seedInput)
    
    SaveManager.planetTex = PlanetGenerator.Generate()
    thumbDisplayer = Menus.SaveCreation.add.surface(pygame.transform.scale(SaveManager.planetTex,(150,150)))
    
    def SetSurface(surface):
        SaveManager.planetTex = surface
        thumbDisplayer.set_surface(pygame.transform.scale(SaveManager.planetTex,(150,150)))
    
    menuSections.pack(thumbDisplayer)
    
    environmentsDict = {0: 'Aléatoire', 1: 'Lunaire', 2: 'Désertique', 3: 'Vivant'}
    Menus.SaveCreation.add.range_slider('Environment', 0, list(environmentsDict.keys()),
                      slider_text_value_enabled=False, width=300, align=pygame_menu.locals.ALIGN_RIGHT,
                      value_format=lambda x: environmentsDict[x])
    difficultiesDict = {0: 'Facile', 1: 'Normal', 2: 'Difficile'}
    Menus.SaveCreation.add.range_slider('Difficulté', 1, list(difficultiesDict.keys()),
                      slider_text_value_enabled=False, width=300, align=pygame_menu.locals.ALIGN_RIGHT,
                      value_format=lambda x: difficultiesDict[x])
    
    global CreateSaveButton
    CreateSaveButton = Menus.SaveCreation.add.button('Créer', lambda : TryCreateSave(saveNameInput))
    
    Menus.SaveCreation.mainloop(UiManager.screen, UiManager.DisplayBackground)
    
def TryCreateSave(saveNameInput):
    
    saveName = str(saveNameInput.get_value())
    
    if SaveManager.SaveExists(saveName):
        global CreateSaveButton
        CreateSaveButton.set_title("Ce nom existe déjà !").set_background_color((218, 85, 82), inflate=(0, 0))
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
    
    creditsMenu = pygame_menu.Menu("Crédits", 1500, 600, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    creditsMenu.add.button('Retour', creditsMenu.disable, align=pygame_menu.locals.ALIGN_LEFT)
    creditsMenu.add.vertical_margin(30)
    with open("Assets/credits (merci)", "r", encoding="utf-8") as f:
        creditsMenu.add.label(f.read(), font_size=20)
    
    creditsMenu.mainloop(UiManager.screen, UiManager.DisplayBackground)

OpenMainMenu()
