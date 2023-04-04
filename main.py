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
import json

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

pygame.display.set_icon(pygame.image.load("Assets/logos/SPFTR.png"))

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
    """
    Lance le menu principal
    """
    #On crée une variante du thème sombre juste pour ce menu qui a un fond totalement transparent
    transparentTheme = pygame_menu.themes.THEME_DARK.copy()
    #Si pygame menu s'aperçoit que ces deux couleurs sont trop proches, il met un message dans la console.
    #C'est pour éviter ça que l'une est un noir invisible et l'autre un blanc invisible.
    transparentTheme.background_color=(0, 0, 0, 0)
    transparentTheme.title_background_color=(255, 255, 255, 0)
    
    #Définition du Menu (ici, le menu est généré via le module pygame_menu)
    Menus.MainMenu = pygame_menu.Menu('', UiManager.width, UiManager.height, theme=transparentTheme)#le thème du menu
    
    #On charge le logo du menu principal
    logo = pygame.image.load("Assets/logos/SPFTRTXT.png")
    
    #Quantité de place libérée en cas de changement de taille du logo
    additionalHeight = 0
    
    #Si l'écran est trop étroit...
    if UiManager.width < 1500:
        #On calcule une nouvelle taille pour que le logo tienne dans l'écran en lui laissant le même ratio
        logoWidth = UiManager.width * 0.8
        logoHeight = logoWidth * 0.25
        #On règle la nouvelle taille du logo
        logo = pygame.transform.scale(logo,(logoWidth, logoHeight))
        #On stocke la quantité de place libérée par ce changement de taille
        additionalHeight = 300 - logoHeight
    
    #On affiche le logo
    Menus.MainMenu.add.surface(logo)
    
    #On calcule un facteur de taille afin de gérer l'espace entre le logo, les boutons et le bouton de crédits. Calculé sur la base d'un écran en 1920*1080p
    hFactor = (UiManager.height-600)*(23/24)
    
    #Si le facteur plus la taille additionnelle est positive, on place un espace vide
    if hFactor*(13/46) + additionalHeight > 0:
        Menus.MainMenu.add.vertical_margin(hFactor*(13/46)+additionalHeight)
    
    #Création d'un cadre pour contenir un bouton
    f = Menus.MainMenu.add.frame_v(300, 50, background_color=(50,50,50), padding=0)
    b = Menus.MainMenu.add.button(Localization.GetLoc('Game.Play'), OpenSavesList)#Bouton pour lancer le jeu
    FunctionUtils.EncapsulateButtonInFrame(b, f)#Encapsulation du bouton dans le cadre
    
    Menus.MainMenu.add.vertical_margin(20)#Petit espace entre deux boutons
    
    #Création d'un cadre pour contenir un bouton
    f = Menus.MainMenu.add.frame_v(300, 50, background_color=(50,50,50), padding=0)
    b = Menus.MainMenu.add.button(Localization.GetLoc('Settings.Title'), lambda:SettingsManager.OpenSettings(UiManager.DisplayBackground))#Bouton pour ouvrir les options
    FunctionUtils.EncapsulateButtonInFrame(b, f)#Encapsulation du bouton dans le cadre
    
    Menus.MainMenu.add.vertical_margin(20)#Petit espace entre deux boutons
    
    #Création d'un cadre pour contenir un bouton
    f = Menus.MainMenu.add.frame_v(300, 50, background_color=(50,50,50), padding=0)
    b = Menus.MainMenu.add.button(Localization.GetLoc('Game.Quit'), pygame_menu.events.EXIT)#Quitter le jeu
    FunctionUtils.EncapsulateButtonInFrame(b, f)#Encapsulation du bouton dans le cadre
    
    #Si le facteur de taille est positif, on inclut un espace vide
    if hFactor > 0:
        Menus.MainMenu.add.vertical_margin(hFactor*(33/46))
    
    #On ajoute le bouton pour accéder aux crédits
    Menus.MainMenu.add.button(Localization.GetLoc('Game.Credits'), OpenCredits, font_size=20, align=pygame_menu.locals.ALIGN_LEFT).set_onselect(FunctionUtils.setSelectedFrame)
    
    Menus.MainMenu.mainloop(UiManager.screen, lambda : (UiManager.DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),pygame.key.set_repeat(1000)))#Boucle principale du Menu

def OpenSavesList():
    """
    Ouvre le menu listant les sauvegardes
    """
    if not os.path.exists("Saves/"):#si le dossier de sauvegardes n'existe pas, le créer
        os.makedirs("Saves/")
    
    saveNames = []
    #On liste toutes les sauvegardes existant dans le dossier de sauvegardes
    for saveFile in os.listdir('Saves/'):
        if SaveManager.SaveExists(saveFile):
            saveNames.append(saveFile)
    
    if Menus.SavesList != None:#Si ce menu existe déjà, on le ferme par précaution
        Menus.SavesList.disable()
    
    #Si aucune sauvegarde n'est disponible, on lance directement le menu de création de sauvegardes
    if len(saveNames) == 0:
        OpenSaveCreationMenu(True)
        return
    
    #Dictionnaire de métadonnées
    savesMetaDatas = {}
    
    #Pour chaque sauvegarde de la liste...
    for saveName in saveNames:
        #Si la sauvegarde a un fichier de métadonnées, on les charge et on les stocke dans le dictionnaire au nom de la save
        if os.path.isfile("Saves/" + saveName + "/meta.json"):
            with open("Saves/" + saveName + "/meta.json", "r") as f:
                savesMetaDatas[saveName] = json.load(f)
        
    #Fonction interne pour directement récupérer la date du dernier lancement d'une sauvegarde
    def GetLastPlayTime(saveName:str)->str:
        return savesMetaDatas.get(saveName,{"lastPlayed":"0"})["lastPlayed"]
    
    #On trie la liste des sauvegardes de la plus récente à la plus ancienne
    saveNames.sort(key=GetLastPlayTime,reverse=True)
    
    #On crée le menu et on y ajoute un bouton retour
    Menus.SavesList = pygame_menu.Menu('Sauvegardes', 500, 450, theme=pygame_menu.themes.THEME_DARK)
    Menus.SavesList.add.button(Localization.GetLoc('Game.Back'), Menus.SavesList.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    #Ajout d'un bouton de création de sauvegardes
    Menus.SavesList.add.button(Localization.GetLoc('Saves.NewSave'), OpenSaveCreationMenu)
    
    #Ajout du cadre qui contiendra la liste des sauvegardes
    frame = Menus.SavesList.add.frame_v(460, max(len(saveNames) * 112, 245), max_height=245, background_color=(30, 30, 30), padding=0)
    frame.relax(True)
    
    #Récupération de variables globales pour stocker quelle sauvegarde et quel cadre sont sélectionnée par l'utilisateur
    global selectedMap, selectedFrame
    selectedMap = selectedFrame = None
    
    #Pour chaque sauvegarde de la liste...
    for saveName in saveNames:
        
        #On rajoute un nouveau cadre pour représenter la sauvegarde dans le cadre listant les sauvegarde
        saveFrame = Menus.SavesList.add.frame_v(460, 110, background_color=(50, 50, 50), padding=0)
        saveFrame.relax(True)
        frame.pack(saveFrame)
        
        #Fonction variante de FunctionUtils.setSelectedFrame() pour correspondre aux besoins de cette liste
        def setSelectedFrame(f,name):
            global selectedMap, selectedFrame
            if selectedFrame != None:
                selectedFrame.set_border(0, None)
            f.set_border(1,(255,255,255))
            selectedFrame = f
            selectedMap = name
        
        #On ajoute le bouton contenant le nom de la sauvegarde
        frameButton = Menus.SavesList.add.button(FunctionUtils.ReduceStr(saveName, 22))
        #On encapsule le bouton dans le cadre en changeant la fonction de sélection et l'alignement
        FunctionUtils.EncapsulateButtonInFrame(frameButton, saveFrame, onSelect=lambda f=saveFrame, name=saveName:setSelectedFrame(f,name), buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        #Métadonnées basiques au cas où la sauvegarde n'en contienne pas
        meta = {
            "lastPlayed":-1,
            "difficulty":-1,
            "environment":-1,
            "gameMode":-1
        }
        #On tente de les récupérer depuis la sauvegarde
        if saveName in savesMetaDatas:
            meta = savesMetaDatas[saveName]
        
        #On récupère le temps de jeu depuis les métadonnées. Si on ne la trouve pas, on le note.
        lastPlayed = meta.get("lastPlayed",-1)
        if lastPlayed == -1:
            lastPlayed = Localization.GetLoc('Saves.UnknownInfo')
        else:
            lastPlayed = lastPlayed[:-3]
        #On récupère la difficulté depuis les métadonnées. Si on ne la trouve pas, on le note.
        difficulty = meta.get("difficulty",-1)
        if difficulty == -1:
            difficulty = "Saves.UnknownInfo"
        else:
            difficulty = SaveManager.difficultiesDict[difficulty]
        #On récupère le type d'environment depuis les métadonnées. Si on ne la trouve pas, on le note.
        conditions = meta.get("environment",-1)
        if conditions == -1:
            conditions = "Saves.UnknownInfo"
        else:
            conditions = SaveManager.environmentsDict[conditions]
        #On récupère le mode de jeu depuis les métadonnées. Si on ne la trouve pas, on le note.
        gameMode = meta.get("gameMode",-1)
        if gameMode == -1:
            gameMode = "Saves.UnknownInfo"
        else:
            gameMode = SaveManager.gameModesDict[gameMode]
        
        #On ajoute au cadre une ligne contenant les infos sur la sauvegarde
        saveFrame.pack(Menus.SavesList.add.label(Localization.GetLoc(difficulty) + " - " +
                                                 Localization.GetLoc(conditions) + " - " +
                                                 Localization.GetLoc(gameMode), font_size=15))
        #On ajoute au cadre une ligne contenant la date de la dernière session
        saveFrame.pack(Menus.SavesList.add.label(Localization.GetLoc('Saves.LastSession') + lastPlayed, font_size=15))
        
        #On tente de récupérer l'icône de la sauvegarde
        planetTex = TextureManager.GetTexture("missingThumb")
        texPath = "Saves/" + saveName + "/planet.png"
        if os.path.isfile(texPath):
            planetTex = pygame.image.load(texPath)
        
        #Si l'icône ne fait pas une taille de 100*100, on règle la taille de force
        if planetTex.get_width() != 100 or planetTex.get_height() != 100:
            planetTex = pygame.transform.scale(planetTex,(100, 100))
        
        #On ajoute cette icône au cadre en la remontant pour qu'elle ne dépasse pas
        saveFrame.pack(Menus.SavesList.add.surface(planetTex), align=pygame_menu.locals.ALIGN_RIGHT).translate(0, -106)
        
        #On ajoute un espace vide sous le cadre
        frame.pack(Menus.SavesList.add.vertical_margin(2))
    
    #Création d'un cadre contenant les boutons au bas de l'image
    bottomFrame = Menus.SavesList.add.frame_h(460, 50, padding=0)
    def ShowLoading():
        Menus.SavesList.add.label("Chargement")
    bottomFrame.pack(Menus.SavesList.add.button(Localization.GetLoc('Game.Play'),lambda: (ShowLoading(),TryLoadSave(selectedMap))), align=pygame_menu.locals.ALIGN_CENTER)#Bouton de lancement de sauvegarde
    bottomFrame.pack(Menus.SavesList.add.frame_v(50,50),align=pygame_menu.locals.ALIGN_CENTER)#Espace vide entre les deux boutons
    bottomFrame.pack(Menus.SavesList.add.button(Localization.GetLoc('Saves.Delete'),#Bouton de supression de sauvegarde avec demande de confirmation
        lambda:UiManager.WarnUser(Localization.GetLoc('Game.Warning'),Localization.GetLoc('Saves.Delete.Warn',selectedMap),lambda:(rmtree("Saves/" + selectedMap),OpenSavesList()),None)),
        align=pygame_menu.locals.ALIGN_CENTER)
    
    Menus.SavesList.mainloop(UiManager.screen, lambda:(UiManager.DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons()))#Boucle principale du Menu
   
def OpenSaveCreationMenu(defaultTuto:bool=False):
    """
    Ouvre le menu de création des sauvegardes
    """
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
    
    global chosenSettings
    chosenSettings = [1, 2 if defaultTuto else 0]
    def setDiff(x:int):
        chosenSettings[0] = x
    def setMode(x:int):
        chosenSettings[1] = x
    

    DifficultySlider = Menus.SaveCreation.add.range_slider(Localization.GetLoc('Saves.Difficulty'), 1, list(SaveManager.difficultiesDict.keys()),
                      slider_text_value_enabled=False, width=300, align=pygame_menu.locals.ALIGN_LEFT,
                      onchange=lambda x: setDiff(x),
                      value_format=lambda x: Localization.GetLoc(SaveManager.difficultiesDict[x]))
    creationTools.pack(DifficultySlider, align=pygame_menu.locals.ALIGN_LEFT)
    
    
    EnvironmentSlider = Menus.SaveCreation.add.range_slider(Localization.GetLoc('Saves.Environment'), 0, list(SaveManager.environmentsDict.keys()),
                      slider_text_value_enabled=False, width=300, align=pygame_menu.locals.ALIGN_LEFT,
                      onchange=lambda x: (SetLabelText(Localization.GetLoc(SaveManager.environmentsDict[x] + '.desc')), SetCorrectPlanetMap(x,GetSeedFromInput())),
                      #range_values=int,
                      value_format=lambda x: Localization.GetLoc(SaveManager.environmentsDict[x]))
    creationTools.pack(EnvironmentSlider, align=pygame_menu.locals.ALIGN_LEFT)
    
    
    GameModeSlider = Menus.SaveCreation.add.range_slider(Localization.GetLoc('Saves.Gamemode'), 2 if defaultTuto else 0, list(SaveManager.gameModesDict.keys()),
                      slider_text_value_enabled=False, width=300, align=pygame_menu.locals.ALIGN_LEFT,
                      onchange=lambda x: setMode(x),
                      value_format=lambda x: Localization.GetLoc(SaveManager.gameModesDict[x]))
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
    SetLabelText(Localization.GetLoc('Saves.Environment.Random.desc'))
    
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
    global chosenSettings
    
    SessionManager.Play(saveName,seed=GetSeedFromInput(),planetaryConditions=conditions,difficulty=chosenSettings[0],gamemode=chosenSettings[1])
    
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
    
    
    suffixes = [ "I", "II", "III", "IV", "V", "Prime", "Alpha", "Beta", "Delta", "Zeta", "Omega", "Sigma", "Minoris", "Majoris" ]
    
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
    """
    Lance l'intro du jeu
    """
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

#Lancement de l'intro, et si il est concluant, lancement du menu principal
if Intro():
    OpenMainMenu()
