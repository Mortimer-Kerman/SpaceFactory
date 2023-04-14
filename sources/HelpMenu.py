# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 23:11:44 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import pygame_menu

import UiManager
import Localization
import FunctionUtils

def Open(tab:str=None):
    """
    Ouvre le panneau d'aide. Il est possible de spécifier un onglet en particulier.
    """
    
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    background = pygame.display.get_surface().copy()
    background.blit(screenFilter,(0,0))
    
    def DisplayBackground():
        UiManager.screen.blit(background,(0,0))
    
    menu = pygame_menu.Menu(Localization.GetLoc("Aide"), 800, 600, theme=pygame_menu.themes.THEME_DARK, onclose=pygame_menu.events.BACK)#le thème du menu
    
    
    
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons()))