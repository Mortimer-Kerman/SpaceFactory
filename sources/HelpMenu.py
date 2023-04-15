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
import GameItems
import SaveManager


menu = None

def IsInit()->bool:
    """
    Dit si le menu a déjà été initialisé
    """
    return menu != None

def Init():
    """
    Le panneau d'aide étant lent à charger, il est préférable de le créer en amont.
    """
    global menu
    menu = pygame_menu.Menu(Localization.GetLoc("Aide"), 800, 600, enabled=False, theme=pygame_menu.themes.THEME_DARK, onclose=pygame_menu.events.BACK)#le thème du menu
    
    frame = menu.add.frame_h(800, 540, padding=0)
    frame.relax(True)
    
    listFrame = menu.add.frame_v(380, max(len(GameItems.craft) * 55, 541), max_height=540, padding=0)
    listFrame.relax(True)
    frame.pack(listFrame, align=pygame_menu.locals.ALIGN_LEFT)
    
    for c in GameItems.craft.keys():
        
        helpFrame = menu.add.frame_v(380, 50, background_color=(50, 50, 50), padding=0)
        helpFrame.relax(True)
        listFrame.pack(helpFrame)
        
        b = menu.add.button(FunctionUtils.ReduceStr(Localization.GetLoc('Items.' + c), 23),lambda item=c:OpenMenu(item))
        
        FunctionUtils.EncapsulateButtonInFrame(b, helpFrame, buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        listFrame.pack(menu.add.vertical_margin(5))
    
    detailsFrame = menu.add.frame_v(380, 541, max_height=540, padding=0)
    detailsFrame.relax(True)
    frame.pack(detailsFrame)
    
    title = menu.add.label("Menu d'aide",font_size=30)
    detailsFrame.pack(title, align=pygame_menu.locals.ALIGN_CENTER)
    
    table = menu.add.table(font_size=15, border_width=0)
    
    detailsFrame.pack(table, align=pygame_menu.locals.ALIGN_CENTER)
    
    def OpenMenu(item):
        title.set_title(Localization.GetLoc('Items.' + item))
        
        rowsLeft = True
        while rowsLeft:
            try:
                currentRow = table.get_cell(1,1).get_frame()
                table.remove_row(currentRow)
                menu.remove_widget(currentRow)
            except AssertionError:
                rowsLeft = False
        
        if item in GameItems.craft:
            crafts = GameItems.craft[item]
        
            row = []
            for c in crafts["c"]:
                row.append(Localization.GetLoc('Items.' + c))
                row.append(" + ")
            
            row[-1] = " = "
            row.append(Localization.GetLoc('Items.' + crafts["r"]))
            
            table.add_row(row,cell_align=pygame_menu.locals.ALIGN_CENTER,cell_border_width=0)
        
        h = 0
        
        for w in detailsFrame.get_widgets(unpack_subframes=False):
            h += w.get_size()[1]
        
        """
        detailsFrame.unpack(table)
        detailsFrame.unpack(title)
        detailsFrame.resize(380, max(541,h), max_height=540)
        detailsFrame.pack(title, align=pygame_menu.locals.ALIGN_CENTER)
        detailsFrame.pack(table, align=pygame_menu.locals.ALIGN_CENTER)
        """

def Open(tab:str=None):
    """
    Ouvre le panneau d'aide. Il est possible de spécifier un onglet en particulier.
    """
    
    if not IsInit():
        Init()
    
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    background = pygame.display.get_surface().copy()
    background.blit(screenFilter,(0,0))
    
    def DisplayBackground():
        UiManager.screen.blit(background,(0,0))
    
    menu.enable()
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),SaveManager.TickClock()))