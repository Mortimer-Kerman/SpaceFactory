# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 11:47:04 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

#Chargement des bibliothèques
import pygame
import pygame_menu

from datetime import datetime
import time
import os
import numpy as np
import random

import SaveManager
import TextureManager
import GameItems
import SettingsManager
import SessionManager
import Localization
import MarketManager
import AudioManager
import NoiseTools
import PlanetGenerator
import FunctionUtils

#Les variables importantes
screen = None#la fenêtre principale (élément pygame.display)
#la taille de l'écran
width = 0
height = 0

UIelements={}#dictionnaire stockant les interaction souris/éléments interface
showMenu={"select":0,"inv":0,"delete":0,"question":0,"freeMouse":1}#affichage ou non des menus interne à l'UI

def Init():
    """
    Fonction d'initialisation du fichier
    Sert à définir les variables importantes (voir ci-dessus)
    """
    global screen,width,height#on prends les variables comme globales
    
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)#on définit l'élément pygame.display (la fenêtre sera en plein écran)
    
    width, height = pygame.display.Info().current_w, pygame.display.Info().current_h#on prend la plus grande taille possible

def FillScreen(color:tuple):
    """
    Cette fonction sert juste à remplir l'écran d'une couleur (en cas de problème avec le chargement de la texture du sol ["ground"])
    """
    screen.fill(color)

def DisplayUi():
    """
    Affichage de l'Interface Utilisateur
    """
    forme(0,0,width,100,50,200)#forme affichée en haut de l'écran

    UIelements["menu_icon"]=screen.blit(TextureManager.GetTexture("menu_icon", 100, is_menu=True), (0, 0)).collidepoint(pygame.mouse.get_pos())#Icone du menu

    forme2(0,height,width,100,50,200)#forme2 affichée en bas de l'écran
    
    mousePos = GetMouseWorldPos()
    
    place_text("[" + str(mousePos[0]) + "," + str(mousePos[1]) + "] " + str(round(SaveManager.clock.get_fps())),0,height-50,20,(250,250,250),TextureManager.GetFont("aquire"))#placement du texte (position du curseur + caméra + FPS)

    for index,popup in enumerate(UIPopup):#pour index , popup dans UiManager.UIPopup
            popup.show(index)
            UIelements["popup_area"]=pygame.Rect(width-500,50,500,205*(index+1)).collidepoint(pygame.mouse.get_pos())#on stocke la zone de popup
    for index,popup in enumerate(UiLightPopup):#pour index , popup dans UiManager.UILightPopup
            popup.show(index)
            
    ItemMenu()#placement du menu de sélection d'item

    InvMenu()#placement du menu inventaire

    CostMenu()#placement du menu de coût

    

def GetMouseWorldPos():
    """
    Renvoie la position du curseur dans le monde
    """
    return ScreenPosToWorldPos(pygame.mouse.get_pos())

def ScreenPosToWorldPos(pos:tuple):
    """
    Convertit une position sur l'écran en position dans le monde
    """
    cam = SaveManager.GetCamPos()#on obtient les coordonnées de la caméra
    zoom = SaveManager.GetZoom()#obtention du zoom
    return ((pos[0]-cam[0]-(width/2))//zoom,(pos[1]-cam[1]-(height/2))//zoom)#renvoie la position par rapport à la caméra+zoom

def IsClickOnUI():
    """
    Sert à savoir si l'utilisateur clique sur l'UI
    """
    for i in UIelements.values():#pour chaque valeur de UIelements (toutes les valeurs sont des booléens)
        if i:#si i
            return True#renvoyer vrai
    return False#renvoyer faux

autoSize={}
def place_text(text, x, y, size, color=(255,255,255),font=None,n=20,auto_size=False,centerText:bool=False):
    """
    Fonction utilitaire servant au placement du texte sur l'écran
    """
    if not auto_size:
        font = pygame.font.Font(None, size) if font==None else font#tentative de charger la police
        t=text.splitlines()
        for i,l in enumerate(t):
            text_surface = font.render(l, True, color)#on crée l'image du texte
            if centerText:
                rect = text_surface.get_rect(center=(width/2-x, height/2-y))
                screen.blit(text_surface, rect)#on affiche le texte
            else:
                screen.blit(text_surface, (x, y+n*i))#on affiche le texte
    else:
        if (auto_size,text) in autoSize.keys():
            text_surface = autoSize[(auto_size,text)]
            if centerText:
                rect = text_surface.get_rect(center=(width/2-x, height/2-y))
                screen.blit(text_surface, rect)#on affiche le texte
            else:
                screen.blit(text_surface, (x, y))#on affiche le texte
        else:
            taille=32
            while taille > 0:
                font = TextureManager.GetFont("aquire",taille)
                text_surface = font.render(text, True, (255, 255, 255))
                if text_surface.get_width() <= auto_size[0] and text_surface.get_height() <= auto_size[1]:
                    break
                taille -= 1
            autoSize[(auto_size,text)]=text_surface
            if centerText:
                rect = text_surface.get_rect(center=(width/2-x, height/2-y))
                screen.blit(text_surface, rect)#on affiche le texte
            else:
                screen.blit(text_surface, (x, y))#on affiche le texte

def forme(x,y,w,wr,h,o,color=(47,48,51)):
    """
    Crée une forme
    """
    #calcul des coordonnées du polygone
    a = x, y
    b = x + w - 1, y
    c = x + w - 1, y + h * 0.6
    d = x + wr + 25 + o, y + h * 0.6
    e = x + wr + 5 + o, y + h
    f = x, y + h
    return pygame.draw.polygon(screen,color,(a,b,c,d,e,f))#affichage du polygone (renvoie l'élément pygame.Rect lié au polygone)
def forme2(x,y,w,wr,h,o,color=(47,48,51)):
    """
    Crée une forme miroire à forme
    """
    #calcul des coordonnées du polygone
    a = x, y
    b = x + w - 1, y
    c = x + w - 1, y - h * 0.6
    d = x + wr + 25 + o, y - h * 0.6
    e = x + wr + 5 + o, y - h
    f = x, y - h
    return pygame.draw.polygon(screen,color,(a,b,c,d,e,f))#affichage du polygone (renvoie l'élément pygame.Rect lié au polygone)
def forme3(x,y,w,wr,h,o,color=(47,48,51)):
    """
    Crée une forme miroire à forme
    """
    #calcul des coordonnées du polygone
    a = x, y
    b = x - w - 1, y
    c = x + w - 1, y - h * 0.6
    d = x + wr + 25 + o, y - h * 0.6
    e = x + wr + 5 + o, y - h
    f = x, y - h
    return pygame.draw.polygon(screen,color,(a,b,c,d,e,f))#affichage du polygone (renvoie l'élément pygame.Rect lié au polygone)


chunkTex=FunctionUtils.NumpyDict()
chunkLimits=FunctionUtils.NumpyDict()
unRefreshed=False
def UpdateBackground():
    """
    Mise à jour du fond
    """
    
    global unRefreshed
    
    needsRefresh = False
    
    zoom = SaveManager.GetZoom()*10#récupération du zoom
    cam = SaveManager.GetCamPos()#récupération de la position de la caméra
    env = SaveManager.GetEnvironmentType()
    for posX in range(-1,(width//zoom)+1):#pour posX dans -1,(width//zoom)+1 
            for posY in range(-1,(height//zoom)+1):#pour posY dans -1,(height//zoom)+1
                
                Xpos = posX*zoom+((cam[0]+(width/2))%zoom)#coordonnées selon zoom
                Ypos = posY*zoom+((cam[1]+(height/2))%zoom)#coordonnées selon zoom
                
                worldPos = ScreenPosToWorldPos((Xpos,Ypos))
                
                posCode = str(worldPos)
                
                if not posCode in chunkTex:
                
                    val = NoiseTools.FractalNoise(worldPos[0]/100, worldPos[1]/100, (SaveManager.GetSeed(),SaveManager.GetSeed()), 1)
                    
                    tex = "rock"
                    if env == PlanetGenerator.PlanetTypes.Dead:
                        tex = "sand"
                        if val > 0.5:
                            tex = "rock"
                    else:
                        if env == PlanetGenerator.PlanetTypes.Desertic:
                            tex = "rock"
                            if val < 0.7:
                                tex = "sand"
                            if val < 0.34:
                                tex = "water"
                        else:
                            tex = "rock"
                            if val < 0.7:
                                tex = "grass"
                            if val < 0.4:
                                tex = "sand"
                            if val < 0.34:
                                tex = "water"
                    
                    chunkTex[posCode] = tex
                    
                    needsRefresh = True
                
                tex = chunkTex[posCode]
                
                screen.blit(TextureManager.GetTexture("ground/" + tex, zoom), (Xpos, Ypos))#placement du fond
                
                if SettingsManager.GetSetting("niceBiomeBorders"):
                    if posCode not in chunkLimits or unRefreshed:
                        
                        limitTex = ""
                        
                        if tex != "sand":
                            for x in range(-1,2):
                                for y in range(-1,2):
                                    tPos = str((worldPos[0]-(x*10),worldPos[1]+(y*10)))
                                    if (x != 0 or y != 0) and tPos in chunkTex:
                                        grabbedTex = chunkTex[tPos]
                                        if grabbedTex != tex and grabbedTex in ["sand","rock"]:
                                            limitTex += grabbedTex + str(x) + str(y) + ";"
                        
                        chunkLimits[posCode] = limitTex
                    
                    limitTex = chunkLimits[posCode]
                    if limitTex != "":
                        if "ground/" + limitTex + ".png" not in TextureManager.loadedTextures:
                            
                            texture = None
                            
                            for t in limitTex.split(";"):
                                if t != "":
                                    if texture == None:
                                        texture = TextureManager.loadedTextures["ground/" + t + ".png"].copy()
                                    else:
                                        texture.blit(TextureManager.loadedTextures["ground/" + t + ".png"],(0,0))
                            
                            TextureManager.loadedTextures["ground/" + limitTex + ".png"] = texture
                            
                                
                        screen.blit(TextureManager.GetTexture("ground/" + limitTex, zoom), (Xpos, Ypos))#placement du fond
                
                #print("3. "+str(time.monotonic()))
    
    unRefreshed = needsRefresh
    
def ForceBackgroundRefresh():
    global unRefreshed
    unRefreshed = True

def ItemMenu():
    """
    Un petit menu de sélection
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
    place_text("Sélectionner",width-400,height-40-500*showMenu.get("select",0),100,(255,255,255),TextureManager.GetFont("aquire"))
    
    #On stocke la valeur bool en cas d'hover sur l'élément (ici le rectangle sous "forme2" du menu de sélection) dans UIelements["select"]
    UIelements["select2"]=pygame.draw.polygon(screen, (98,99,102), [(width-500,height-500*showMenu.get("select",0)),(width,height-500*showMenu.get("select",0)),(width,height),(width-500,height)]).collidepoint(pygame.mouse.get_pos())

    menuElements=GameItems.menuElements
    for i in range(len(menuElements)):
        UIelements["selectElements_"+menuElements[i]]=pygame.draw.rect(screen, (47,48,51), pygame.Rect(width-500+102*(i%5),height-500*showMenu.get("select",0)+102*(i//5), 100, 100)).collidepoint(pygame.mouse.get_pos())
        screen.blit(TextureManager.GetTexture(menuElements[i], 78, True),(width-500+11+102*(i%5),height-500*showMenu.get("select",0)+102*(i//5)))
        place_text(Localization.GetLoc('Items.' + menuElements[i]),width-500+102*(i%5),height-500*showMenu.get("select",0)+102*(i//5)+80,20,(255,255,255),TextureManager.GetFont("aquire"),auto_size=(100,20))
    
    UIelements["selectElements_free"]=pygame.draw.rect(screen, (47,48,51), pygame.Rect(width-500+102,height-100*showMenu.get("select",0), 100, 100)).collidepoint(pygame.mouse.get_pos())
    screen.blit(TextureManager.GetTexture("cursor", 78, True),(width-500+11+102,height-100*showMenu.get("select",0)))
    place_text("Souris libre",width-500+102,height-100*showMenu.get("select",0)+80,20,(255,255,255),TextureManager.GetFont("aquire"),auto_size=(100,20))

    UIelements["selectElements_question"]=pygame.draw.rect(screen, (47,48,51), pygame.Rect(width-500+102*3,height-100*showMenu.get("select",0), 100, 100)).collidepoint(pygame.mouse.get_pos())
    screen.blit(TextureManager.GetTexture("question", 78, True),(width-500+11+102*3,height-100*showMenu.get("select",0)))
    place_text("Interrogation",width-500+102*3,height-100*showMenu.get("select",0)+80,20,(255,255,255),TextureManager.GetFont("aquire"),auto_size=(100,20))

    UIelements["selectElements_delete"]=pygame.draw.rect(screen, (47,48,51), pygame.Rect(width-500+102*4,height-100*showMenu.get("select",0), 100, 100)).collidepoint(pygame.mouse.get_pos())
    screen.blit(TextureManager.GetTexture("detruire", 78, True),(width-500+11+102*4,height-100*showMenu.get("select",0)))
    place_text("détruire",width-500+102*4,height-100*showMenu.get("select",0)+80,20,(255,255,255),TextureManager.GetFont("aquire"),auto_size=(100,20))

    place_text("presse "+pygame.key.name(SettingsManager.GetKeybind("rotate"))+" pour retourner l'élément",width-500,height-120*showMenu.get("select",0),20,(255,255,255),TextureManager.GetFont("aquire"),auto_size=(500,100))
    
def CostMenu():
    if not showMenu["freeMouse"]:
        p=GameItems.getPrice(SaveManager.mainData.selectedItem)
        UIelements["cost"]=pygame.draw.rect(screen, (47,51,52), pygame.Rect(width-600, height-250*showMenu.get("select",0), 100,250) ).collidepoint(pygame.mouse.get_pos())
        place_text(Localization.GetLoc("UiManager.cost"), width-600, height-250*showMenu.get("select",0), 20,auto_size=(100,40))
        for n,(i,c) in enumerate(p):
            screen.blit(TextureManager.GetTexture(i,78,is_menu=True), (width-600,height-250*showMenu.get("select",0)+40*(n+1)))
            place_text(str(c), width-600, height-250*showMenu.get("select",0)+40*(n+1), 40)


def InvMenu():
    global UIelements
    UIelements["inv"]=forme(width-500,500*showMenu.get("inv",0),width,100,50,200,(98,99,102)).collidepoint(pygame.mouse.get_pos())

    #Différents points des petits triangles (t[0]=up t[1]=down)
    t=[[(width-450, 45+500*showMenu.get("inv",0)), (width-475, 15+500*showMenu.get("inv",0)), (width-425, 15+500*showMenu.get("inv",0))],
       [(width-450, 15+500*showMenu.get("inv",0)), (width-475, 45+500*showMenu.get("inv",0)), (width-425, 45+500*showMenu.get("inv",0))]]
    #on dessine le petit triangle 
    pygame.draw.polygon(screen, (255,255,255),t[showMenu.get("inv",0)])
    #on mets du texte
    place_text("Inventaire",width-400,20+500*showMenu.get("inv",0),100,(255,255,255),TextureManager.GetFont("aquire"))

    UIelements["inv2"]=pygame.draw.polygon(screen, (98,99,102), [(width-500,500*showMenu.get("inv",0)),(width,500*showMenu.get("inv",0)),(width,0),(width-500,0)]).collidepoint(pygame.mouse.get_pos())

    for i,e in enumerate(SaveManager.mainData.inv):
        UIelements["invElements_"+str(i)]=pygame.draw.rect(screen, (47,48,51), pygame.Rect(width-500+102*(i%5),-500+500*showMenu.get("inv",0)+102*(i//5), 100, 100)).collidepoint(pygame.mouse.get_pos())
        screen.blit(TextureManager.GetTexture(e["n"], 78, True),(width-500+11+102*(i%5),-500+11+500*showMenu.get("inv",0)+102*(i//5)))
        place_text(str(Localization.GetLoc("Items."+e["n"])),width-500+102*(i%5),-500+500*showMenu.get("inv",0)+102*(i//5),20)
        place_text(str(e["m"]),width-500+102*(i%5),-480+500*showMenu.get("inv",0)+102*(i//5),20)

def addNewlines(text,l):
    """
    Ajoute un caractère \n à une chaîne de caractères tout les 29 caractères, sans couper un mot.
    """
    words = text.split()
    new_text = ""
    line_len = 0
    for word in words:
        word_len = len(word)
        if line_len + word_len + 1 <= int(l):
            new_text += word + " "
            line_len += word_len + 1
        else:
            new_text = new_text.strip() + "\n"
            new_text += word + " "
            line_len = word_len + 1
    return new_text.strip() + "\n"

def DisplayItemToPlace():
    """
    Cette fonction a pour but d'afficher l'item que le joueur s'apprête à placer en transparence pour lui donner une indication de visée
    """
    ItemTexture = None
    if showMenu["delete"]:
        if SaveManager.IsItemHere(GetMouseWorldPos()):
            ItemTexture = TextureManager.GetColorFilter((255,0,0),SaveManager.GetZoom())
    elif showMenu["question"]:
        ItemTexture = "question"
    else:
        if not showMenu["freeMouse"]:
            ItemTexture = SaveManager.mainData.selectedItem

    if ItemTexture == None or (IsClickOnUI() and not showMenu["question"]):
        return
    
    cam = SaveManager.GetCamPos()
    cam = [cam[0],cam[1]]
    zoom = SaveManager.GetZoom()
    cam[0] += width / 2
    cam[1] += height / 2
    pos = GetMouseWorldPos()
    
    if type(ItemTexture) == str:
        tex = TextureManager.GetTexture(ItemTexture, zoom).copy()
    else:
        tex = ItemTexture
    tex.set_alpha(150)
    tex=pygame.transform.rotate(tex,90*SaveManager.mainData.rotation)
    screen.blit(tex, (pos[0]*zoom+cam[0], pos[1]*zoom+cam[1]))
    
def interactItem(item):
    screenFilter = pygame.Surface((width,height))
    screenFilter.set_alpha(50)
    SessionManager.PauseMenuBackground = pygame.display.get_surface().copy()
    SessionManager.PauseMenuBackground.blit(screenFilter,(0,0))
    
    interactMenu = pygame_menu.Menu("Configurez cet élément", 400, 300, theme=pygame_menu.themes.THEME_DARK,onclose=pygame_menu.events.BACK)
    
    interactMenu.add.button('Reprendre', interactMenu.disable)#Reprendre la partie
    b=None
    if item.name=="trieur":
        a=[[i] for i in list(GameItems.allTransportableItems.keys())]
        b=interactMenu.add.selector("Choisissez : ",a)
        interactMenu.mainloop(screen,SessionManager.DisplayPauseMenuBackground)
    if item.name in ["stockage"]:
        
        in_menu=1
        BLOCK_SIZE=100
        rects=[]
        inv=[]
        for x,e in enumerate(item.metadata.get("biginv",[])):
            if e["n"] is None:
                del item.metadata["biginv"][x]
            else:
                rects.append( pygame.Rect(width//4-250+(x%4)*(BLOCK_SIZE+5), height//2-300+(x//4)*(BLOCK_SIZE+5), BLOCK_SIZE, BLOCK_SIZE) )
                inv.append(e)
        for x,e in enumerate(SaveManager.mainData.inv):
            rects.append( pygame.Rect((width//4)*3-250+(x%4)*(BLOCK_SIZE+5), height//2-300+(x//4)*(BLOCK_SIZE+5), BLOCK_SIZE, BLOCK_SIZE) )
            inv.append(e)
        clock = pygame.time.Clock()
        selected=None
        
        while in_menu:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        in_menu = False
 
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for i, r in enumerate(rects):
                            if r.collidepoint(event.pos):
                                selected = i
                                selected_offset_x = r.x - event.pos[0]
                                selected_offset_y = r.y - event.pos[1]
               
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        selected = None
               
                elif event.type == pygame.MOUSEMOTION:
                    if selected is not None: # selected can be `0` so `is not None` is required
                        # move object
                        rects[selected].x = event.pos[0] + selected_offset_x
                        rects[selected].y = event.pos[1] + selected_offset_y
               
            SessionManager.DisplayPauseMenuBackground()
            forme2(width//4-250,height//2-300,500,100,50,200,(98,99,102))
            pygame.draw.polygon(screen, (98,99,102), [(width//4-250,height//2-300),(width//4+250,height//2-300),(width//4+250,height//2+300),(width//4-250,height//2+300)])
            place_text("Stockage",width//4-245,height//2-330,100,(255,255,255),TextureManager.GetFont("aquire"))
            forme2((width//4)*3-250,height//2-300,500,100,50,200,(98,99,102))
            pygame.draw.polygon(screen, (98,99,102), [((width//4)*3-250,height//2-300),((width//4)*3+250,height//2-300),((width//4)*3+250,height//2+300),((width//4)*3-250,height//2+300)])
            place_text("Inventaire",(width//4)*3-245,height//2-330,100,(255,255,255),TextureManager.GetFont("aquire"))
            for r in zip(rects,inv):
                pygame.draw.rect(screen,  (47,48,51), r[0])
                screen.blit(TextureManager.GetTexture(r[1]["n"], 78, True),(r[0].x,r[0].y))

                place_text(str(r[1]["n"]),r[0].x,r[0].y,20)
                place_text(str(r[1]["m"]),r[0].x,r[0].y+20,20)
                
            pygame.display.update()
            clock.tick(25)
        
        #change l'environnement de stockage/inv
        tempInv=[]
        for i in mainData.inv:
            tempInv.append(dict(i))
        tempBigInv=[]
        for i in item.metadata["biginv"]:
            tempBigInv.append(dict(i))
            
        SaveManager.ClearInv()
        item.metadata["biginv"]=[]

        for r in zip(rects,inv):
            if r[0].x<width//2:
                for i in range(r[1]["m"]):
                    if not item.AddToInv(r[1]["n"]):
                        SaveManager.mainData.inv=tempInv
                        item.metadata["biginv"]=tempBigInv
                        Popup(Localization.GetLoc("UiManager.biginv.error"))
                        return
            else:
                for i in range(r[1]["m"]):
                    if not SaveManager.AddToInv(r[1]["n"]):
                        SaveManager.mainData.inv=tempInv
                        item.metadata["biginv"]=tempBigInv
                        Popup(Localization.GetLoc("SaveManager.GetFromInv.error"))
                        return
    
    if item.name=="market":
        MarketManager.showMenu()

    SessionManager.PauseMenuBackground = None
    return b.get_value() if b is not None else None

def Loading():
    FillScreen((0,0,0))
    DisplayBackground()
    
    logoTex = pygame.transform.scale(TextureManager.GetTexture("logos/SPFTR"),(height/2,height/2))
    screen.blit(logoTex,((width-logoTex.get_width())/2, (height-logoTex.get_height())/2))
    
    place_text(Localization.GetLoc("Game.Loading"),0,-height/3,100,(255,255,255),font=TextureManager.GetFont("aquire",100),centerText=True)
    pygame.display.update()

UIPopup=[]
UiLightPopup=[]
class Popup:
    """
    Des popups
    """
    def __init__(self,text,command=None,d=0):
        self.text=addNewlines(text,29)
        self.time=int(pygame.time.get_ticks())
        self.command=command
        self.sliding=0
        self.d=d
        UIPopup.append(self)
    def show(self,i):
        self.sliding+= SaveManager.clock.get_time()
        if self.sliding > 500:
            self.sliding = 500
        
        if int(pygame.time.get_ticks())>(self.time+10000) and self.command is None and not self.d:
               self.close(i)
        else:
            UIelements["popup_"+str(i)]=pygame.draw.rect(screen, (58, 48, 46), pygame.Rect(width-self.sliding,50+205*i,500,200)).collidepoint(pygame.mouse.get_pos())
            place_text(self.text,width-self.sliding,50+205*i,26,(255,255,255),TextureManager.GetFont("nasalization"),n=30)
            if self.command is None:
                UIelements["popup_close_button_"+str(i)]=pygame.draw.rect(screen, (37, 37, 40), pygame.Rect(width-self.sliding,225+205*i,50,25)).collidepoint(pygame.mouse.get_pos())
                place_text("Ok",width-self.sliding,225+205*i,26,(255,255,255),TextureManager.GetFont("aquire"))
            else:
                UIelements["popup_launch_button_"+str(i)]=pygame.draw.rect(screen, (37, 37, 40), pygame.Rect(width-self.sliding,225+205*i,100,25)).collidepoint(pygame.mouse.get_pos())
                place_text("Lancer",width-self.sliding,225+205*i,26,(255,255,255),TextureManager.GetFont("aquire"))
                UIelements["popup_close_button_"+str(i)]=pygame.draw.rect(screen, (37, 37, 40), pygame.Rect(width-self.sliding+150,225+205*i,50,25)).collidepoint(pygame.mouse.get_pos())
                place_text("Non",width-self.sliding+150,225+205*i,26,(255,255,255),TextureManager.GetFont("aquire"))
    def close(self,i):
        UIPopup.remove(self)
        UIelements["popup_"+str(i)]=False
        UIelements["popup_area"]=False
        UIelements["popup_close_button_"+str(i)]=False
        if self.command is not None:
            del UIelements["popup_launch_button_"+str(i)]

    def launch(self):
        self.command()

class LightPopup:
    """
    Popups légères
    """
    def __init__(self,text,d=0):
        self.text=text
        self.time=int(pygame.time.get_ticks())
        self.d=d
        UiLightPopup.append(self)
    def show(self,i):
        if int(pygame.time.get_ticks())>(self.time+10000) and not self.d:
               self.close(i)
        else:
            place_text(self.text, width//4, (height//4)*3+i*20, 20, (255,255,255),TextureManager.GetFont("nasalization"),auto_size=(width//2,height//10))
    def close(self,i):
        UiLightPopup.remove(self)


MenuBackground = pygame_menu.baseimage.BaseImage("./Assets/background.png", drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')#on définit le fond des menus

def DisplayBackground():
    MenuBackground.draw(screen)
    AudioManager.Tick()

def WarnUser(title:str, message:str, confirm, cancel, background=DisplayBackground):
    
    WarnMenu = pygame_menu.Menu(title, 800, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    WarnMenu.add.label(message)
    
    bottomBar = WarnMenu.add.frame_h(800,50)
    bottomBar.relax(True)
    
    confirmButton = WarnMenu.add.button(Localization.GetLoc('Game.Confirm'), WarnMenu.disable)
    if confirm != None:
        confirmButton.set_onreturn(lambda:(WarnMenu.disable(),confirm()))
    bottomBar.pack(confirmButton, align=pygame_menu.locals.ALIGN_LEFT)
    
    cancelButton = WarnMenu.add.button(Localization.GetLoc('Game.Cancel'), WarnMenu.disable)
    if cancel != None:
        confirmButton.set_onreturn(lambda:(WarnMenu.disable(),cancel()))
    bottomBar.pack(cancelButton, align=pygame_menu.locals.ALIGN_RIGHT)
    
    WarnMenu.mainloop(screen, background)

def TakeScreenshot():
    if not os.path.exists("Screenshots/"):
        os.makedirs("Screenshots/")
    pygame.image.save(pygame.display.get_surface(), "Screenshots/screenshot_" + datetime.now().strftime("%Y%m%d%H%M%S%f") + ".png")
    Popup("Capture d'écran trouvable dans le dossier /Screenshots/")