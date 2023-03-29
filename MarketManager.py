# -*- coding: utf-8 -*-

import pygame
import pygame_menu

import UiManager
import TextureManager
import GameItems
import SaveManager
import Localization as L

items=GameItems.doc

def showMenu():
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    background = pygame.display.get_surface().copy()
    background.blit(screenFilter,(0,0))
    def DisplayBackground():
        UiManager.screen.blit(background,(0,0))
        pygame.draw.polygon(UiManager.screen,(198, 136, 102),((0,0),(0,UiManager.height//3),(UiManager.width//3,0)))
        pygame.draw.polygon(UiManager.screen,(198, 136, 102),((UiManager.width,UiManager.height),(0,(UiManager.height//3)*2),((UiManager.width//3)*2,0)))
        #UiManager.screen.blit(TextureManager.GetTexture("GalacticMarket",100,1), (0,0))
        UiManager.place_text(L.GetLoc("Market.Title"), 20, 50, 100,font=TextureManager.nasalization100)
        UiManager.place_text(L.GetLoc("Market.Motto"), 20, 150, 50)
        
    
    h = int((UiManager.height//2)-105)
    w = int(UiManager.height)
    
    menu = pygame_menu.Menu(L.GetLoc("Market.Title"), w, h+105, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    f=menu.add.frame_h(w, h, max_width=w, max_height=h, padding=0)
    f.relax(True)
    f.pack(menu.add.button(L.GetLoc('Game.Back'), menu.disable, align=pygame_menu.locals.ALIGN_LEFT),align=pygame_menu.locals.ALIGN_LEFT)
    f.pack(menu.add.label(str(SaveManager.mainData.coins), align=pygame_menu.locals.ALIGN_RIGHT),align=pygame_menu.locals.ALIGN_RIGHT)
    menu.mainloop(UiManager.screen, DisplayBackground)