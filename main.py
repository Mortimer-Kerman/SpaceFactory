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
from shutil import rmtree
from math import cos

import TextureManager
import UiManager
import SessionManager
import AudioManager
import PlanetGenerator
import SettingsManager
import SaveManager
import Localization
import FunctionUtils


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
    
    transparentTheme = pygame_menu.themes.THEME_DARK.copy()
    transparentTheme.background_color=(0, 0, 0, 0)
    transparentTheme.title_background_color=(255, 255, 255, 0)
    
    #Définition du Menu (ici, le menu est généré via le module pygame_menu)
    Menus.MainMenu = pygame_menu.Menu('', UiManager.width, UiManager.height, theme=transparentTheme)#le thème du menu
    
    Menus.MainMenu.add.surface(pygame.image.load("Assets/logos/SPFTRTXT.png"))
    
    hFactor = (UiManager.height-600)*(23/24)
    
    if hFactor > 0:
        Menus.MainMenu.add.vertical_margin(hFactor*(13/46))
    
    f = Menus.MainMenu.add.frame_v(300, 50, background_color=(50,50,50), padding=0)
    b = Menus.MainMenu.add.button(Localization.GetLoc('Game.Play'), OpenSavesList)#Bouton pour lancer le jeu
    FunctionUtils.EncapsulateButtonInFrame(b, f)
    
    Menus.MainMenu.add.vertical_margin(20)
    
    f = Menus.MainMenu.add.frame_v(300, 50, background_color=(50,50,50), padding=0)
    b = Menus.MainMenu.add.button(Localization.GetLoc('Settings.Title'), lambda:SettingsManager.OpenSettings(UiManager.DisplayBackground))#Bouton pour ouvrir les options
    FunctionUtils.EncapsulateButtonInFrame(b, f)
    
    Menus.MainMenu.add.vertical_margin(20)
    
    f = Menus.MainMenu.add.frame_v(300, 50, background_color=(50,50,50), padding=0)
    b = Menus.MainMenu.add.button(Localization.GetLoc('Game.Quit'), pygame_menu.events.EXIT)#Quitter le jeu
    FunctionUtils.EncapsulateButtonInFrame(b, f)
    
    if hFactor > 0:
        Menus.MainMenu.add.vertical_margin(hFactor*(33/46))
    
    Menus.MainMenu.add.button(Localization.GetLoc('Game.Credits'), OpenCredits, font_size=20, align=pygame_menu.locals.ALIGN_LEFT).set_onselect(FunctionUtils.setSelectedFrame)
    
    Menus.MainMenu.mainloop(UiManager.screen, lambda : (UiManager.DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),pygame.key.set_repeat(1000)))#Boucle principale du Menu

def OpenSavesList():
    
    if not os.path.exists("Saves/"):#si le dossier de sauvegarde n'existe pas, le créer
        os.makedirs("Saves/")
    
    saveNames = []
    for saveFile in os.listdir('Saves/'):
        if SaveManager.SaveExists(saveFile):
            saveNames.append(saveFile)
    
    if Menus.SavesList != None:
        Menus.SavesList.disable()
    
    if len(saveNames) == 0:
        OpenSaveCreationMenu(True)
        return
    
    Menus.SavesList = pygame_menu.Menu('Sauvegardes', 500, 450, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    Menus.SavesList.add.button(Localization.GetLoc('Game.Back'), Menus.SavesList.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    Menus.SavesList.add.button(Localization.GetLoc('Saves.NewSave'), OpenSaveCreationMenu)
    
    frame = Menus.SavesList.add.frame_v(460, max(len(saveNames) * 102, 245), max_height=245, background_color=(30, 30, 30), padding=0)
    frame.relax(True)
    
    global selectedMap, selectedFrame
    selectedMap = selectedFrame = None
    
    for saveName in saveNames:
        
        saveFrame = Menus.SavesList.add.frame_h(460, 100, background_color=(50, 50, 50), padding=0)
        saveFrame.relax(True)
        frame.pack(saveFrame)
        
        def setSelectedFrame(f,name):
            global selectedMap, selectedFrame
            if selectedFrame != None:
                selectedFrame.set_border(0, None)
            f.set_border(1,(255,255,255))
            selectedFrame = f
            selectedMap = name
        
        frameButton = Menus.SavesList.add.button(FunctionUtils.ReduceStr(saveName, 22))
        
        FunctionUtils.EncapsulateButtonInFrame(frameButton, saveFrame, onSelect=lambda f=saveFrame, name=saveName:setSelectedFrame(f,name), buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        planetTex = TextureManager.GetTexture("missingThumb")
        texPath = "Saves/" + saveName + "/planet.png"
        if os.path.isfile(texPath):
            planetTex = pygame.image.load(texPath)
        saveFrame.pack(Menus.SavesList.add.surface(pygame.transform.scale(planetTex,(90,90))), align=pygame_menu.locals.ALIGN_RIGHT)
        
        frame.pack(Menus.SavesList.add.vertical_margin(2))
    
    bottomFrame = Menus.SavesList.add.frame_h(460, 50, padding=0)
    bottomFrame.pack(Menus.SavesList.add.button(Localization.GetLoc('Game.Play'),lambda: TryLoadSave(selectedMap)), align=pygame_menu.locals.ALIGN_CENTER)
    bottomFrame.pack(Menus.SavesList.add.frame_v(50,50),align=pygame_menu.locals.ALIGN_CENTER)
    bottomFrame.pack(Menus.SavesList.add.button(Localization.GetLoc('Saves.Delete'),
        lambda:UiManager.WarnUser(Localization.GetLoc('Game.Warning'),Localization.GetLoc('Saves.Delete.Warn',selectedMap),lambda:(rmtree("Saves/" + selectedMap),OpenSavesList()),None)),
        align=pygame_menu.locals.ALIGN_CENTER)
    
    Menus.SavesList.mainloop(UiManager.screen, lambda:(UiManager.DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons()))
   
def OpenSaveCreationMenu(defaultTuto:bool=False):
    if Menus.SaveCreation != None:
        Menus.SaveCreation.disable()
    Menus.SaveCreation = pygame_menu.Menu(Localization.GetLoc('Saves.NewSave'), 700, 600, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    Menus.SaveCreation.add.button(Localization.GetLoc('Game.Back'), Menus.SaveCreation.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    menuSections = Menus.SaveCreation.add.frame_h(660, 325, padding=0)
    menuSections.relax(True)
    
    creationTools = Menus.SaveCreation.add.frame_v(520, 325, padding=0)
    creationTools.relax(True)
    
    menuSections.pack(creationTools, align=pygame_menu.locals.ALIGN_LEFT)
    
    saveNameInput=Menus.SaveCreation.add.text_input(Localization.GetLoc('Saves.NewSave.Name'), default=RandomSaveName(),maxchar=30)
    creationTools.pack(saveNameInput, align=pygame_menu.locals.ALIGN_LEFT)
    
    global seedInput
    seedInput=Menus.SaveCreation.add.text_input(Localization.GetLoc('Saves.NewSave.Seed'),maxchar=10)
    creationTools.pack(seedInput, align=pygame_menu.locals.ALIGN_LEFT)
    
    difficultiesDict = {0: 'Saves.NewSave.Difficulty.Easy',
                        1: 'Saves.NewSave.Difficulty.Normal',
                        2: 'Saves.NewSave.Difficulty.Hard'}
    DifficultySlider = Menus.SaveCreation.add.range_slider(Localization.GetLoc('Saves.NewSave.Difficulty'), 1, list(difficultiesDict.keys()),
                      slider_text_value_enabled=False, width=300, align=pygame_menu.locals.ALIGN_LEFT,
                      value_format=lambda x: Localization.GetLoc(difficultiesDict[x]))
    creationTools.pack(DifficultySlider, align=pygame_menu.locals.ALIGN_LEFT)
    
    environmentsDict = {0: 'Saves.NewSave.Environment.Random',
                        1: 'Saves.NewSave.Environment.Lunar',
                        2: 'Saves.NewSave.Environment.Desertic',
                        3: 'Saves.NewSave.Environment.Lifefull'}
    EnvironmentSlider = Menus.SaveCreation.add.range_slider(Localization.GetLoc('Saves.NewSave.Environment'), 0, list(environmentsDict.keys()),
                      slider_text_value_enabled=False, width=300, align=pygame_menu.locals.ALIGN_LEFT,
                      onchange=lambda x: (SetLabelText(Localization.GetLoc(environmentsDict[x] + '.desc')), SetCorrectPlanetMap(x,GetSeedFromInput())),
                      #range_values=int,
                      value_format=lambda x: Localization.GetLoc(environmentsDict[x]))
    creationTools.pack(EnvironmentSlider, align=pygame_menu.locals.ALIGN_LEFT)
    
    gameModesDict = {0: 'Saves.NewSave.Gamemode.Career',
                     1: 'Saves.NewSave.Gamemode.Sandbox',
                     2: 'Saves.NewSave.Gamemode.Tutorial'}
    GameModeSlider = Menus.SaveCreation.add.range_slider(Localization.GetLoc('Saves.NewSave.Gamemode'), 2 if defaultTuto else 0, list(gameModesDict.keys()),
                      slider_text_value_enabled=False, width=300, align=pygame_menu.locals.ALIGN_LEFT,
                      value_format=lambda x: Localization.GetLoc(gameModesDict[x]))
    creationTools.pack(GameModeSlider, align=pygame_menu.locals.ALIGN_LEFT)
    
    thumbDisplayer = Menus.SaveCreation.add.surface(pygame.transform.scale(TextureManager.GetTexture("missingThumb"),(150,150)))
    
    global PrevEnvironment
    PrevEnvironment = 0
    def SetCorrectPlanetMap(x:int,seed=None,forceGenerate=False):
        global PrevEnvironment
        if x == PrevEnvironment and not forceGenerate:
            return
        PrevEnvironment = x
        
        global conditions
        
        conditions = PlanetGenerator.PlanetaryConditions(seed=seed)
        if x == 0:
            
            SetSurface(PlanetGenerator.Generate(conditions,seed))
            thumbDisplayer.set_surface(pygame.transform.scale(TextureManager.GetTexture("missingThumb"),(150,150)))
            return
        
        while conditions.type != x:
            conditions = PlanetGenerator.PlanetaryConditions()
        
        SetSurface(PlanetGenerator.Generate(conditions,seed))
    
    def SetSurface(surface):
        SaveManager.planetTex = surface
        thumbDisplayer.set_surface(pygame.transform.scale(SaveManager.planetTex,(150,150)))
    
    SetCorrectPlanetMap(0,forceGenerate=True)
    
    menuSections.pack(thumbDisplayer)
    
    DescLabel = Menus.SaveCreation.add.label('\n\n', font_size=15)
    def SetLabelText(text:str):
        lines = text.split('\n',2)
        for i in range(3):
            if i < len(lines):
                DescLabel[i].set_title(lines[i])
            else:
                DescLabel[i].set_title('')
    SetLabelText(Localization.GetLoc('Saves.NewSave.Environment.Random.desc'))
    
    Menus.SaveCreation.add.vertical_margin(20)
    
    global CreateSaveButton
    CreateSaveButton = Menus.SaveCreation.add.button(Localization.GetLoc('Saves.NewSave.Create'), lambda : (SetCorrectPlanetMap(EnvironmentSlider.get_value(),GetSeedFromInput(),forceGenerate=True),TryCreateSave(saveNameInput)))
    
    Menus.SaveCreation.mainloop(UiManager.screen, UiManager.DisplayBackground)
    
def TryCreateSave(saveNameInput):
    
    saveName = str(saveNameInput.get_value())
    
    if SaveManager.SaveExists(saveName):
        global CreateSaveButton
        CreateSaveButton.set_title(Localization.GetLoc('Saves.NewSave.AlreadyExists')).set_background_color((218, 85, 82), inflate=(0, 0))
        return
    
    Menus.SaveCreation.disable()
    if Menus.SavesList != None:
        Menus.SavesList.disable()
    
    global conditions
    SessionManager.Play(saveName,seed=GetSeedFromInput(),tuto=1,planetaryConditions=conditions)
    
def TryLoadSave(saveName:str):
    if SessionManager.Play(saveName):
        Menus.SavesList.disable()
    
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

def RandomSaveName()->str:   

    length = random.randint(4,10)
    consonants = [ "b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "l", "n", "p", "q", "r", "s", "sh", "zh", "t", "v", "w", "x" ]
    vowels = [ "a", "e", "i", "o", "u", "ae", "y" ]
    Name = ""
    b = 0
    while b < length:
    
        Name += random.choice(consonants)
        b += 1
        if b == length:
            break
        Name += random.choice(vowels)
        b += 1
    
    
    suffixes = [ "I", "II", "III", "IV", "V", "Prime", "Alpha", "Beta", "Delta", "Zeta", "Omega", "Minoris", "Majoris" ]
    
    if random.choice((True,False)):
        Name += " " + random.choice(suffixes)
    
    Name = Name[0].upper() + Name[1:]
    
    return Name


def OpenCredits():
    
    creditsMenu = pygame_menu.Menu(Localization.GetLoc('Game.Credits'), UiManager.width//1.1, 600, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    creditsMenu.add.button(Localization.GetLoc('Game.Back'), creditsMenu.disable, align=pygame_menu.locals.ALIGN_LEFT)
    creditsMenu.add.vertical_margin(30)
    with open("Assets/credits.txt", "r", encoding="utf-8") as f:
        creditsMenu.add.label(f.read(), font_size=20)
    
    creditsMenu.mainloop(UiManager.screen, UiManager.DisplayBackground)

def Intro()->bool:
    
    #récupération des logos à afficher dans l'ordre d'affichage
    logos = [
        pygame.Surface((2, 2)),#juste une texture noire avant le premier logo
        pygame.transform.scale(pygame.image.load("Assets/logos/SPFTR.png"),(UiManager.height/2,UiManager.height/2)),
        pygame.transform.scale(pygame.image.load("Assets/logos/PYTHONLIBS.png"),(UiManager.height/1.5,UiManager.height/1.5)),
        pygame.transform.scale(pygame.image.load("Assets/logos/TROPHEES.png"),(UiManager.height/1.5,UiManager.height/1.5))
    ]
    
    changedIcon = False
    logoIndex = 0
    
    #tant que l'animation se joue...
    playing = True
    while playing:
        
        #boucle d'évenements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #si la fenêtre est fermée, on renvoie faux
                pygame.quit()
                return False
            #si la touche echap, entrer ou espace est pressée...
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE,pygame.K_RETURN,pygame.K_SPACE]:
                #on renvoie vrai, ce qui interromp l'animation
                return True
        
        #calcul de la visibilité en fonction du temps d'exécution
        visibility = (cos(pygame.time.get_ticks()/700+1))*200+150
        
        #on fait une copie de la texture à afficher et on règle sa visibilité
        currentTex = logos[logoIndex].copy()
        currentTex.set_alpha(visibility)
        
        #on affiche l'écran, le logo et on met à jour la fenêtre
        UiManager.screen.fill((0,0,0))
        UiManager.screen.blit(currentTex,((UiManager.width-currentTex.get_width())/2, (UiManager.height-currentTex.get_height())/2))
        pygame.display.update()
        
        #si l'icône est invisible et qu'aucun changement d'icône n'a eu lieu...
        if not changedIcon and visibility < 0:
            #on change d'icône
            changedIcon = True
            logoIndex += 1
            #si on est arrivé à la fin de la liste des icônes, on met fin à l'animation
            if logoIndex == len(logos):
                playing = False
        #si l'icône est visible et qu'un changement d'icône a eu lieu...
        elif changedIcon and visibility > 0:
            changedIcon = False
    
    return True

if Intro():
    OpenMainMenu()
