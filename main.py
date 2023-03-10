# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 16:13:46 2023

@author: Thomas Sartre et François Patinec-Haxel
"""
#importation des bibliothèques
import pygame
import pygame_menu

import os

import TextureManager
import UiManager
import SessionManager
import AudioManager
import PlanetGenerator
import SettingsManager


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
    Settings = None
    KeyChanger = None
    WarnMenu = None
    MenuBackground = pygame_menu.baseimage.BaseImage("./Assets/background.png", drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')#on définit le fond des menus

def DisplayBackground():
    Menus.MenuBackground.draw(UiManager.screen)

def OpenMainMenu():
    #Définition du Menu (ici, le menu est généré via le module pygame_menu)
    Menus.MainMenu = pygame_menu.Menu('Space Factory', 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    Menus.MainMenu.add.button('Jouer', OpenSavesList)#Bouton pour lancer le jeu
    Menus.MainMenu.add.button('Options', OpenSettings)#Bouton pour lancer le jeu
    Menus.MainMenu.add.button('Quitter', pygame_menu.events.EXIT)#Quitter le jeu
    
    Menus.MainMenu.mainloop(UiManager.screen, lambda : (DisplayBackground(),pygame.key.set_repeat(1000)))#Boucle principale du Menu

def OpenSavesList():
    
    Menus.SavesList = pygame_menu.Menu('Sauvegardes', 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    Menus.SavesList.add.button('Retour', Menus.SavesList.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    Menus.SavesList.add.button('Nouvelle sauvegarde', OpenSaveCreationMenu)
    
    if not os.path.exists("Saves/"):#si le dossier de sauvegarde n'existe pas, le créer
        os.makedirs("Saves/")
    
    saveNames = []
    for saveFile in os.listdir('Saves/'):
        if ".spf" in saveFile:
            saveNames.append(saveFile.replace(".spf", ""))
    
    frame = Menus.SavesList.add.frame_v(360, max(len(saveNames) * 50, 145), background_color=(50, 50, 50), padding=0)
    frame.relax(True)
    
    for saveName in saveNames:
        frame.pack(Menus.SavesList.add.button(saveName, lambda save=saveName: (Menus.SavesList.disable(), SessionManager.Play(save))))
    
    Menus.SavesList.mainloop(UiManager.screen, DisplayBackground)
   
def OpenSaveCreationMenu():
    
    Menus.SaveCreation = pygame_menu.Menu('Sauvegardes', 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    Menus.SaveCreation.add.button('Retour', Menus.SaveCreation.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    menuSections = Menus.SaveCreation.add.frame_h(360, 195, padding=0)
    menuSections.relax(True)
    
    creationTools = Menus.SaveCreation.add.frame_v(220, 195, padding=0)
    creationTools.relax(True)
    
    menuSections.pack(creationTools)
    
    saveNameInput=Menus.SaveCreation.add.text_input('Nom: ', default='save',maxchar=10)
    
    creationTools.pack(saveNameInput)
    """
    creationTools.pack(Menus.SaveCreation.add.dropselect(
        title='',
        items=[('Lunaire', 0),('Hadéen', 1),('Précambien', 2),('Carbonifèrien', 3)],
        default=0
    ))
    """
    creationTools.pack(Menus.SaveCreation.add.button('Créer', lambda : TryCreateSave(saveNameInput)))
    
    
    planetTex = pygame.transform.scale(PlanetGenerator.Generate(),(150,150))
    
    menuSections.pack(Menus.SaveCreation.add.surface(planetTex))
    
    Menus.SaveCreation.mainloop(UiManager.screen, DisplayBackground)
    
def TryCreateSave(saveNameInput):

    global SavePopup

    saveName = str(saveNameInput.get_value())
    
    if os.path.isfile("Saves/" + saveName + ".spf"):

        try:SavePopup.hide()
        except:pass

        SavePopup=Menus.SaveCreation.add.label("Ce nom existe déjà !").set_background_color((218, 85, 82), inflate=(0, 0))
        return
    
    Menus.SavesList.disable()
    Menus.SaveCreation.disable()
    SessionManager.Play(saveName,tuto=1)
    
def OpenSettings():
    
    Menus.Settings = pygame_menu.Menu('Options', 800, 600, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    def TryLeave():
        if not SettingsManager.SettingsChanged:
            SettingsManager.LoadSettings()
            Menus.Settings.disable()
            return
        WarnUser("Attention", "Cetains paramètres ne sont pas sauvegardés.\nVoulez-vous quand même quitter?\n", lambda:(SettingsManager.LoadSettings(), Menus.Settings.disable()), None)
        
        
    topBar = Menus.Settings.add.frame_h(800,50)
    topBar.relax(True)
    topBar.pack(Menus.Settings.add.button('Retour', TryLeave), align=pygame_menu.locals.ALIGN_LEFT)
    topBar.pack(Menus.Settings.add.button('Enregistrer', SettingsManager.SaveSettings), align=pygame_menu.locals.ALIGN_RIGHT)
    
    Menus.Settings.add.vertical_margin(20)
    
    Menus.Settings.add.range_slider('Volume de la musique', SettingsManager.GetSetting("musicVolume"), (0, 100), 1, value_format=lambda x: str(int(x)), onchange=lambda x:(pygame.mixer.music.set_volume(int(x)/100),SettingsManager.SetSetting("musicVolume", int(x))), align=pygame_menu.locals.ALIGN_LEFT)
    
    Menus.Settings.add.vertical_margin(20)
    
    Menus.Settings.add.label("Touches", align=pygame_menu.locals.ALIGN_LEFT)
    
    Menus.Settings.add.vertical_margin(20)
    
    bindings = SettingsManager.GetSetting("keybinds")
    
    for key in bindings.keys():
        frame = Menus.Settings.add.frame_h(300, 50, padding=0, align=pygame_menu.locals.ALIGN_LEFT)
        frame.relax(True)
        frame.pack(Menus.Settings.add.label(key))
        
        name = pygame.key.name(bindings[key])
        leak = int((10 - len(name))/2)
        for i in range(leak):
            name = " " + name + " "
        
        button = Menus.Settings.add.button(name)
        frame.pack(button, align=pygame_menu.locals.ALIGN_RIGHT)
        button.set_onreturn(lambda btn=button,kname=key:ChangeKey(btn,kname))
    
    Menus.Settings.mainloop(UiManager.screen, DisplayBackground)

def ChangeKey(KeyButton,KeyId):
    keyName = KeyButton.get_title().strip()
    
    Menus.KeyChanger = pygame_menu.Menu('Changer la touche', 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    Menus.KeyChanger.add.label(KeyId)
    Menus.KeyChanger.add.label("Touche actuelle: " + keyName)
    
    def kLoop():
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key != pygame.K_ESCAPE:
                    SettingsManager.SetKeybind(KeyId, event.key)
                    KeyButton.set_title(pygame.key.name(event.key))
                Menus.KeyChanger.disable()
    
    Menus.KeyChanger.mainloop(UiManager.screen, lambda:(DisplayBackground(),kLoop()))

def WarnUser(title:str,message:str, confirm, cancel):
    
    Menus.WarnMenu = pygame_menu.Menu(title, 800, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    Menus.WarnMenu.add.label(message)
    
    bottomBar = Menus.WarnMenu.add.frame_h(800,50)
    bottomBar.relax(True)
    
    confirmButton = Menus.WarnMenu.add.button('Confirmer', Menus.WarnMenu.disable)
    if confirm != None:
        confirmButton.set_onreturn(lambda:(confirm(),Menus.WarnMenu.disable()))
    bottomBar.pack(confirmButton, align=pygame_menu.locals.ALIGN_LEFT)
    
    cancelButton = Menus.WarnMenu.add.button('Annuler', Menus.WarnMenu.disable)
    if cancel != None:
        confirmButton.set_onreturn(lambda:(cancel(),Menus.WarnMenu.disable()))
    bottomBar.pack(cancelButton, align=pygame_menu.locals.ALIGN_RIGHT)
    
    Menus.WarnMenu.mainloop(UiManager.screen, DisplayBackground)

OpenMainMenu()
