# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 16:13:46 2023

@author: 29ray
"""

import pygame
import pygame_menu

import random

import TextureManager
import SaveManager
import UiManager
import GameItems

pygame.init()#initialisation pygame

UiManager.Init()

pygame.display.set_caption('SpaceFactory')
pygame.key.set_repeat(10)

TextureManager.LoadAllTextures()

def Play():
    """
    Lance le jeu
    """
    SaveManager.Load(str(saveFileSelect.get_value()))
    
    
    while SaveManager.SaveLoaded():
        
        UiManager.FillScreen((47,79,79))
        
        
        zoom = SaveManager.GetZoom()*10
        cam = SaveManager.GetCamPos()
        
        #colorFilter = pygame.transform.scale(TextureManager.colorFilter,(zoom,zoom))
        
        for posX in range(-1,(UiManager.width//zoom)+1):
            for posY in range(-1,(UiManager.height//zoom)+1):
                Xpos = posX*zoom+((cam[0]+(UiManager.width/2))%zoom)
                Ypos = posY*zoom+((cam[1]+(UiManager.height/2))%zoom)
                #colorFilter.fill((0,255,128))
                UiManager.screen.blit(TextureManager.GetTexture("ground", zoom), (Xpos, Ypos))
                #UiManager.screen.blit(colorFilter, (Xpos, Ypos))
        """
        cam = SaveManager.GetCamPos()
        cam = [cam[0],cam[1]]
        zoom = SaveManager.GetZoom()
        se=SaveManager.GetSeed()
        for posX in range(int(cam[0])//zoom,UiManager.width//zoom+int(cam[0])//zoom):
            for posY in range(int(cam[1])//zoom,UiManager.height//zoom+int(cam[1])//zoom):
                random.seed(posX*posY*se+posX+posY+se+posX)
                if random.randint(0,60)==40:UiManager.screen.blit(TextureManager.GetTexture("m1", zoom), (posX*zoom, posY*zoom))
        """
        
        for item in SaveManager.GetItems():
            item.Display()
        
        UiManager.DisplayUi()
        
        pygame.display.update()
        
        camOffset = [0,0]
        
        for event in pygame.event.get():
            #en cas de fermeture du jeu (sert à ne pas provoquer de bug)
            if event.type == pygame.QUIT:
                SaveManager.Unload()
                return
            #action du clavier
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    SaveManager.Unload()
                    return
                if event.key == pygame.K_UP:
                    camOffset[1]+=5
                if event.key == pygame.K_DOWN:
                    camOffset[1]-=5
                if event.key == pygame.K_RIGHT:
                    camOffset[0]-=5
                if event.key == pygame.K_LEFT:
                    camOffset[0]+=5
                #UiManager.FillScreen((33,37,39))
            #action de molette de souris
            if event.type == pygame.MOUSEWHEEL:
                zoom = SaveManager.mainData.zoom
                zoom+=event.y if event.y+zoom>0 else 0
                SaveManager.mainData.zoom = zoom
                TextureManager.RefreshZoom()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # 1 == left button
                    SaveManager.PlaceItem(GameItems.Item("lessgo", UiManager.GetMouseWorldPos(), "drill"))
            
            if event.type == MUSIC_ENDED:
                pygame.mixer.music.load("./Assets2/audio/" + random.choice(playlist))
                pygame.mixer.music.play(start=0.0, fade_ms=200)


        SaveManager.TranslateCam(camOffset)
        SaveManager.clock.tick()
        

MUSIC_ENDED = pygame.USEREVENT
pygame.mixer.music.set_endevent(MUSIC_ENDED)
playlist=["theme.mp3","Genesis.mp3","jake-chudnow-moon-men.mp3","buran-voskresenie.mp3"]
#Lancement de la musique
pygame.mixer.music.load("./Assets2/audio/" + random.choice(playlist))

pygame.mixer.music.set_volume(0.7)
pygame.mixer.music.play(start=0.0, fade_ms=200)


menu = pygame_menu.Menu('Bienvenue', 400, 300, theme=pygame_menu.themes.THEME_DARK)
bg=pygame_menu.baseimage.BaseImage("./Assets2/background.png", drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')
saveFileSelect=menu.add.text_input('Fichier :', default='save',maxchar=10)

menu.add.button('Jouer', Play)
menu.add.button('Quitter', pygame_menu.events.EXIT)

menu.mainloop(UiManager.screen, lambda : bg.draw(UiManager.screen))