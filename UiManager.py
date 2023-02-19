# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 11:47:04 2023

@author: sartre.thomas
"""

import pygame
import SaveManager
import TextureManager

screen = None
width = 0
height = 0

def Init():
    global screen
    global width
    global height
    
    width, height = pygame.display.list_modes()[0]
    screen = pygame.display.set_mode((width, height))

def FillScreen(color:tuple):
    screen.fill(color)

def DisplayUi():
    forme(0,0,width,100,50,200)

    forme2(0,height-50,width,100,50,200)
    
    place_text(str(list(pygame.mouse.get_pos()))+" "+str(SaveManager.GetCamPos()) + " " + str(round(SaveManager.clock.get_fps())),0,height-100,20,(250,250,250),TextureManager.aquire)

def GetMouseWorldPos():
    cam = SaveManager.GetCamPos()
    zoom = SaveManager.GetZoom()
    return ((pygame.mouse.get_pos()[0]-cam[0]-(width/2))//zoom,(pygame.mouse.get_pos()[1]-cam[1]-(height/2))//zoom)

def place_text(text, x, y, size, color,font=None):
    font = pygame.font.Font(None, size) if font==None else font
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))
def forme(x,y,w,wr,h,o):
    a = x, y
    b = x + w - 1, y
    c = x + w - 1, y + h * 0.6
    d = x + wr + 25 + o, y + h * 0.6
    e = x + wr + 5 + o, y + h
    f = x, y + h
    pygame.draw.polygon(screen,(47,48,51),(a,b,c,d,e,f))
def forme2(x,y,w,wr,h,o):
    a = x, y
    b = x + w - 1, y
    c = x + w - 1, y - h * 0.6
    d = x + wr + 25 + o, y - h * 0.6
    e = x + wr + 5 + o, y - h
    f = x, y - h
    pygame.draw.polygon(screen,(47,48,51),(a,b,c,d,e,f))

def UpdateBackground():
    zoom = SaveManager.GetZoom()*10
    cam = SaveManager.GetCamPos()
    for posX in range(-1,(width//zoom)+1):
            for posY in range(-1,(height//zoom)+1):
                Xpos = posX*zoom+((cam[0]+(width/2))%zoom)
                Ypos = posY*zoom+((cam[1]+(height/2))%zoom)
                #colorFilter.fill((0,255,128))
                screen.blit(TextureManager.GetTexture("ground", zoom), (Xpos, Ypos))