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
    tabsList = list(set(GameItems.menuElements + list(GameItems.craft.keys()) + list(GameItems.allTransportableItems.keys())))
    
    global menu
    menu = pygame_menu.Menu(Localization.GetLoc("Aide"), 800, 600, enabled=False, theme=pygame_menu.themes.THEME_DARK, onclose=pygame_menu.events.BACK)#le thème du menu
    
    frame = menu.add.frame_h(800, 540, padding=0)
    frame.relax(True)
    frame.set_float(float_status=True)
    
    listFrame = menu.add.frame_v(380, max(len(tabsList) * 55 + 5, 541), max_height=540, padding=0)
    listFrame.relax(True)
    frame.pack(listFrame, align=pygame_menu.locals.ALIGN_LEFT)
    
    listFrame.pack(menu.add.vertical_margin(5))
    
    for c in tabsList:
        
        helpFrame = menu.add.frame_v(380, 50, background_color=(50, 50, 50), padding=0)
        helpFrame.relax(True)
        listFrame.pack(helpFrame)
        
        b = menu.add.button(FunctionUtils.ReduceStr(Localization.GetLoc('Items.' + c), 23),lambda item=c:OpenMenu(item),button_id=c)
        
        FunctionUtils.EncapsulateButtonInFrame(b, helpFrame, buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        listFrame.pack(menu.add.vertical_margin(5))
    
    detailsFrame = menu.add.frame_v(380, 541, max_height=540, padding=0)
    detailsFrame.relax(True)
    frame.pack(detailsFrame)
    
    title = menu.add.label("Menu d'aide",font_size=30)
    detailsFrame.pack(title, align=pygame_menu.locals.ALIGN_CENTER)
    
    desc = menu.add.label("\n\n\n\n\n",font_size=20)#20 en 1080
    detailsFrame.pack(desc)
    
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
        
        descText = Localization.GetLoc('Items.d.' + item)
        if descText != 'Items.d.' + item:
            SetDescText(descText)
        else:
            SetDescText("")
        
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
            h += w.get_height()
        
        detailsFrame.unpack(table)
        table.set_float(float_status=False)
        detailsFrame.unpack(title)
        title.set_float(float_status=False)
        for label in desc:
            detailsFrame.unpack(label)
            label.set_float(float_status=False)
        detailsFrame.resize(380, max(541,h), max_height=540)
        detailsFrame.pack(title, align=pygame_menu.locals.ALIGN_CENTER)
        detailsFrame.pack(desc)
        detailsFrame.pack(table, align=pygame_menu.locals.ALIGN_CENTER)
        
    def SetDescText(text:str):
        
        lineLength = 35#int((UiManager.height-500)*(11/116))
        
        cuts = [0]
        lastSpace = 0
        for i in range(len(text)):
            if text[i] == " ":
                lastSpace = i
            lastCut = cuts[-1]
            if i - lastCut > lineLength:
                cuts.append(lastSpace)
        
        lines = [text[i:j].strip() for i,j in zip(cuts, cuts[1:]+[None])]
        
        for i in range(6):
            if i < len(lines):
                desc[i].set_title(lines[i])
            else:
                desc[i].set_title('')

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
    
    if tab != None:
        button = menu.get_widget(tab,True)
        button.select(update_menu=True)
        button.apply()
    
    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons(),SaveManager.TickClock()))