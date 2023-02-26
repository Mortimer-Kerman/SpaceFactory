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

pygame.init()#initialisation pygame

UiManager.Init()#initialisation du l'UiManager

pygame.display.set_caption('SpaceFactory')#Définition du tire de la fenêtre

TextureManager.LoadAllTextures()#chargement des textures

AudioManager.Init()

def OpenMainMenu():
    #Définition du Menu (ici, le menu est généré via le module pygame_menu)
    menu = pygame_menu.Menu('Space Factory', 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    bg=pygame_menu.baseimage.BaseImage("./Assets2/background.png", drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')#on définit le fond du menu
    
    menu.add.button('Jouer', OpenSavesList)#Bouton pour lancer le jeu
    menu.add.button('Quitter', pygame_menu.events.EXIT)#Quitter le jeu
    
    menu.mainloop(UiManager.screen, lambda : (bg.draw(UiManager.screen),pygame.key.set_repeat(1000)))#Boucle principale du Menu

def OpenSavesList():
    
    menu = pygame_menu.Menu('Sauvegardes', 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    bg=pygame_menu.baseimage.BaseImage("./Assets2/background.png", drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')#on définit le fond du menu
    
    if not os.path.exists("Saves/"):#si le dossier de sauvegarde n'existe pas, le créer
        os.makedirs("Saves/")
    
    for saveFile in os.listdir('Saves/'):
        if ".spf" in saveFile:
            saveName = saveFile.replace(".spf", "")
            menu.add.button(saveName, lambda : OpenSave(saveName, menu))
    
    menu.add.button('Retour', menu.disable)
    
    menu.mainloop(UiManager.screen, lambda : (bg.draw(UiManager.screen),pygame.key.set_repeat(1000)))
   
def OpenSave(saveName:str, MenuToClose):
    MenuToClose.disable()
    SessionManager.Play(saveName)
    
OpenMainMenu()
