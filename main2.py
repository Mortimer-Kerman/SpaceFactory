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
#import PlanetGenerator

pygame.init()#initialisation pygame

UiManager.Init()#initialisation du l'UiManager

pygame.display.set_caption('SpaceFactory')#Définition du tire de la fenêtre

TextureManager.LoadAllTextures()#chargement des textures

AudioManager.Init()#Initialisation de l'AudioManager

class Menus:
    """
    Contient des références aux différents menus du menu principal
    """
    MainMenu = None
    SavesList = None
    SaveCreation = None
    MenuBackground = bg=pygame_menu.baseimage.BaseImage("./Assets2/background.png", drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')#on définit le fond des menus

def OpenMainMenu():
    #Définition du Menu (ici, le menu est généré via le module pygame_menu)
    Menus.MainMenu = pygame_menu.Menu('Space Factory', 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    Menus.MainMenu.add.button('Jouer', OpenSavesList)#Bouton pour lancer le jeu
    Menus.MainMenu.add.button('Quitter', pygame_menu.events.EXIT)#Quitter le jeu
    
    Menus.MainMenu.mainloop(UiManager.screen, lambda : (Menus.bg.draw(UiManager.screen),pygame.key.set_repeat(1000)))#Boucle principale du Menu

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
    
    frame = Menus.SavesList.add.frame_v(360, len(saveNames) * 50, background_color=(50, 50, 50), padding=0)
    frame.relax(True)
    
    for saveName in saveNames:
        frame.pack(Menus.SavesList.add.button(saveName, lambda save=saveName: (Menus.SavesList.disable(), SessionManager.Play(save))))
    
    Menus.SavesList.mainloop(UiManager.screen, lambda : (Menus.bg.draw(UiManager.screen),pygame.key.set_repeat(1000)))
   
def OpenSaveCreationMenu():
    
    Menus.SaveCreation = pygame_menu.Menu('Sauvegardes', 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    Menus.SaveCreation.add.button('Retour', Menus.SaveCreation.disable, align=pygame_menu.locals.ALIGN_LEFT)
    
    saveNameInput=Menus.SaveCreation.add.text_input('Nom: ', default='save',maxchar=10)
    
    Menus.SaveCreation.add.button('Créer', lambda : TryCreateSave(saveNameInput))
    """
    texture = pygame.Surface((100,100))
    
    pygame.surfarray.blit_array(texture, PlanetGenerator.Generate())
    
    Menus.SaveCreation.add.surface(texture)
    """
    Menus.SaveCreation.mainloop(UiManager.screen, lambda : (Menus.bg.draw(UiManager.screen),pygame.key.set_repeat(1000)))
    
def TryCreateSave(saveNameInput):
    
    saveName = str(saveNameInput.get_value())
    
    if os.path.isfile("Saves/" + saveName + ".spf"):
        #penser a mettre un truc genre un popup pour alerter le joueur
        return
    
    Menus.SavesList.disable()
    Menus.SaveCreation.disable()
    SessionManager.Play(saveName)
    
OpenMainMenu()
