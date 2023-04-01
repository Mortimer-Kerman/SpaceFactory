# -*- coding: utf-8 -*-

import pygame
import pygame_menu

import UiManager
import TextureManager
import GameItems
import SaveManager
import Localization as L
import FunctionUtils

marketItem={"Onion":275272,"Sovietiu":78578575,"Siberiu":7585785,"Titlu":785785785,"Monika":57}

currentItem=None
LabelCoins=None

def showMenu():
    global LabelCoins
    screenFilter = pygame.Surface((UiManager.width,UiManager.height))
    screenFilter.set_alpha(50)
    background = pygame.display.get_surface().copy()
    background.blit(screenFilter,(0,0))
    def DisplayBackground():
        UiManager.screen.blit(background,(0,0))
        pygame.draw.polygon(UiManager.screen,(198, 136, 102),((0,0),(0,UiManager.height//3),(UiManager.width//3,0)))
        pygame.draw.polygon(UiManager.screen,(198, 136, 102),((UiManager.width,UiManager.height),(0,(UiManager.height//3)*2),((UiManager.width//3)*2,0)))
        UiManager.place_text(L.GetLoc("Market.Title"), 20, 50, 100,font=TextureManager.nasalization100)
        UiManager.place_text(L.GetLoc("Market.Motto"), 20, 150, 50)
        
    def setCurrent(a):
        global currentItem
        currentItem=a

    h = int((UiManager.height//2)-105)
    w = int(UiManager.height)
    
    menu = pygame_menu.Menu(L.GetLoc("Market.Title"), w, h+105, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    f=menu.add.frame_h(w, 50, max_width=w, max_height=50, padding=0)
    f.relax(True)
    f.pack(menu.add.button(L.GetLoc('Game.Back'), menu.disable, align=pygame_menu.locals.ALIGN_LEFT),align=pygame_menu.locals.ALIGN_LEFT)
    LabelCoins=menu.add.label(str(SaveManager.mainData.coins), align=pygame_menu.locals.ALIGN_RIGHT, padding=25)
    f.pack(LabelCoins,align=pygame_menu.locals.ALIGN_RIGHT)


    frame = menu.add.frame_h(w, h,padding=0)
    frame.relax(True)

    listFrame = menu.add.frame_v(500, max(len(marketItem) * 155, h), max_height=h, padding=0)
    listFrame.relax(True)
    frame.pack(listFrame, align=pygame_menu.locals.ALIGN_LEFT)
    
    for i in marketItem.keys():
        oppFrame = menu.add.frame_v(500, 150, background_color=(50, 50, 50), padding=0)
        oppFrame.relax(True)
        listFrame.pack(oppFrame)
        
        b = menu.add.button(FunctionUtils.ReduceStr(i, 30), lambda i=i:setCurrent(i))
        
        FunctionUtils.EncapsulateButtonInFrame(b, oppFrame, buttonAlign=pygame_menu.locals.ALIGN_LEFT)
        
        oppFrame.pack(menu.add.vertical_margin(50))

        subtext = menu.add.label("Prix: " + str(marketItem[i]))
        subtext.set_font(TextureManager.nasalization, 20, (255,255,255), (255,255,255), (255,255,255), (255,255,255), (50,50,50))
        oppFrame.pack(subtext)
        
        listFrame.pack(menu.add.vertical_margin(5))

    detailsFrame = menu.add.frame_v(w-500, h, max_height=h, padding=0)
    detailsFrame.relax(True)
    frame.pack(detailsFrame)
    
    title = menu.add.label("",font_size=int((UiManager.height-500)*(2/29)))#40 en 1080
    detailsFrame.pack(title,align=pygame_menu.locals.ALIGN_CENTER)
    
    label = menu.add.label("\n\n\n\n\n",font_size=int((UiManager.height-500)*(1/29)))#20 en 1080
    detailsFrame.pack(label)
    
    detailsFrame.pack(menu.add.vertical_margin(100))
    
    detailsFrame.pack(menu.add.button(L.GetLoc("Market.Buy"), Buy),align=pygame_menu.locals.ALIGN_CENTER)

    menu.mainloop(UiManager.screen, lambda:(DisplayBackground(),FunctionUtils.ManageEncapsulatedButtons()))

def Buy():
    if currentItem is not None:
        if marketItem[currentItem] <= SaveManager.mainData.coins:
            SaveManager.mainData.coins -= marketItem[currentItem]
            SaveManager.AddToInv(currentItem)
            LabelCoins.set_title(str(SaveManager.mainData.coins))

def Sell(item):
    price={"charbon":1,"cuivre":2,"or":5,"m1":8}
    SaveManager.mainData.coins += price.get(item,0)