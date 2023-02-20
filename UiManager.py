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

UIelements={}
showMenu={"select":0}

def Init():
    global screen
    global width
    global height
    
    width, height = pygame.display.list_modes()[0]
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)

def FillScreen(color:tuple):
    screen.fill(color)

def DisplayUi():
    forme(0,0,width,100,50,200)
    UIelements["menu_icon"]=screen.blit(TextureManager.GetTexture("menu_icon", 100), (0, 0)).collidepoint(pygame.mouse.get_pos())

    forme2(0,height,width,100,50,200)
    
    place_text(str(list(pygame.mouse.get_pos()))+" "+str(SaveManager.GetCamPos()) + " " + str(round(SaveManager.clock.get_fps())),0,height-50,20,(250,250,250),TextureManager.aquire)

    ItemMenu()

def GetMouseWorldPos():
    cam = SaveManager.GetCamPos()
    zoom = SaveManager.GetZoom()
    return ((pygame.mouse.get_pos()[0]-cam[0]-(width/2))//zoom,(pygame.mouse.get_pos()[1]-cam[1]-(height/2))//zoom)

def IsClickOnUI():
    for i in UIelements.values():#pour chaque valeur de UIelements
        if i:
            return True
    return False
    

def place_text(text, x, y, size, color=(255,255,255),font=None):
    font = pygame.font.Font(None, size) if font==None else font
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def forme(x,y,w,wr,h,o,color=(47,48,51)):
    a = x, y
    b = x + w - 1, y
    c = x + w - 1, y + h * 0.6
    d = x + wr + 25 + o, y + h * 0.6
    e = x + wr + 5 + o, y + h
    f = x, y + h
    return pygame.draw.polygon(screen,color,(a,b,c,d,e,f))
def forme2(x,y,w,wr,h,o,color=(47,48,51)):
    a = x, y
    b = x + w - 1, y
    c = x + w - 1, y - h * 0.6
    d = x + wr + 25 + o, y - h * 0.6
    e = x + wr + 5 + o, y - h
    f = x, y - h
    return pygame.draw.polygon(screen,color,(a,b,c,d,e,f))

def UpdateBackground():
    zoom = SaveManager.GetZoom()*10
    cam = SaveManager.GetCamPos()
    for posX in range(-1,(width//zoom)+1):
            for posY in range(-1,(height//zoom)+1):
                Xpos = posX*zoom+((cam[0]+(width/2))%zoom)
                Ypos = posY*zoom+((cam[1]+(height/2))%zoom)
                #colorFilter.fill((0,255,128))
                screen.blit(TextureManager.GetTexture("ground", zoom), (Xpos, Ypos))

def ItemMenu():
    """
    Un petit menu de séléction
    """
    global UIelements
    #On stocke la valeur bool en cas d'hover sur l'élément dans UIelements["select"]
    UIelements["select"]=forme2(width-500,height-500*showMenu.get("select",0),width,100,50,200,(98,99,102)).collidepoint(pygame.mouse.get_pos())
    
    #Différents points des petits triangles (t[0]=up t[1]=down)
    t=[[(width-450, height-45-500*showMenu.get("select",0)), (width-475, height-15-500*showMenu.get("select",0)), (width-425, height-15-500*showMenu.get("select",0))],
       [(width-450, height-15-500*showMenu.get("select",0)), (width-475, height-45-500*showMenu.get("select",0)), (width-425, height-45-500*showMenu.get("select",0))]]
    #on dessine le petit triangle 
    pygame.draw.polygon(screen, (255,255,255),t[showMenu.get("select",0)])
    #on mets du texte
    place_text("Séléctionner",width-400,height-40-500*showMenu.get("select",0),100,(255,255,255),TextureManager.aquire)
    
    #On stocke la valeur bool en cas d'hover sur l'élément (ici le rectangle sous "forme2" du menu de séléction) dans UIelements["select"]
    UIelements["select2"]=pygame.draw.polygon(screen, (98,99,102), [(width-500,height-500*showMenu.get("select",0)),(width,height-500*showMenu.get("select",0)),(width,height),(width-500,height)]).collidepoint(pygame.mouse.get_pos())

    place_text("À faire",width-500,height-400*showMenu.get("select",0),200,(255,0,0))