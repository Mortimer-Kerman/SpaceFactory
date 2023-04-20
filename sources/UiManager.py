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
showMenu={"select":0,"inv":0,"delete":0,"question":0}#affichage ou non des menus interne à l'UI

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
    UIelements["opportunities_icon"]=screen.blit(TextureManager.GetTexture("opportunities_icon", 50, is_menu=True), (100, 0)).collidepoint(pygame.mouse.get_pos())#Icone du menu
    UIelements["help_icon"]=screen.blit(TextureManager.GetTexture("help_icon", 50, is_menu=True), (150, 0)).collidepoint(pygame.mouse.get_pos())#Icone du menu
    
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

def WorldPosToScreenPos(pos:tuple):
    """
    Convertit une position dans le monde en position sur l'écran.
    Si la position est hors de l'écran, la valeur renvoyée sera hors de l'écran également.
    """
    cam = SaveManager.GetCamPos()#on obtient les coordonnées de la caméra
    zoom = SaveManager.GetZoom()#obtention du zoom
    return (pos[0]*zoom+(width/2)+cam[0],pos[1]*zoom+(height/2)+cam[1])#renvoie la position par rapport à la caméra+zoom

def IsClickOnUI():
    """
    Sert à savoir si l'utilisateur clique sur l'UI
    """
    for i in UIelements.values():#pour chaque valeur de UIelements (toutes les valeurs sont des booléens)
        if i:#si i
            return True#renvoyer vrai
    return False#renvoyer faux

autoSize={}#dictionnaire contenant les données d'autoSize (utile pour garder une taille constante selon la longueur du texte)
def place_text(text, x, y, size, color=(255,255,255),font=None,n=20,auto_size=False,centerText:bool=False):
    """
    Fonction utilitaire servant au placement du texte sur l'écran
    """
    if not auto_size:#si aucun paramètres d'autosize est donné
        font = pygame.font.Font(None, size) if font==None else font#tentative de charger la police
        t=text.splitlines()#on sépare chaque ligne en une liste
        for i,l in enumerate(t):#pour chaque ligne du texte
            text_surface = font.render(l, True, color)#on crée l'image du texte
            if centerText:#si le texte doit être centré
                rect = text_surface.get_rect(center=(width/2-x, height/2-y))#on modifie le centre du rect text
                screen.blit(text_surface, rect)#on affiche le texte
            else:
                screen.blit(text_surface, (x, y+n*i))#on affiche le texte
    else:#si un paramètre d'auto_size est donné (sous forme d'un tuple (taille max, hauteur max))
        if (auto_size,text) in autoSize.keys():#si le texte existe déjà dans le dictionnaire autoSize
            text_surface = autoSize[(auto_size,text)]#on récupère la surface de texte stockée dans le dictionnaire autoSize
            if centerText:#si le texte est centré
                rect = text_surface.get_rect(center=(width/2-x, height/2-y))#on modifie le centre du rect
                screen.blit(text_surface, rect)#on affiche le texte
            else:
                screen.blit(text_surface, (x, y))#on affiche le texte
        else:#si le texte n'existe pas dans le dictionnaire autoSize
            taille=32#taille de base
            while taille > 0:#tant que la taille est supérieure à 0
                font = TextureManager.GetFont("aquire",taille)#on charge la police à la taille spécifiée
                text_surface = font.render(text, True, (255, 255, 255))#on fait un rendu du texte
                if text_surface.get_width() <= auto_size[0] and text_surface.get_height() <= auto_size[1]:#si le texte correspond au paramètres attendus
                    break#sortir du while
                taille -= 1#on diminue la taille de la police
            autoSize[(auto_size,text)]=text_surface#on ajoute la surface de texte dans le dictionnaire autoSize
            if centerText:#si le texte est centré
                rect = text_surface.get_rect(center=(width/2-x, height/2-y))#on modifie le centre du rect
                screen.blit(text_surface, rect)#on affiche le texte
            else:#si le texte n'est pas centré
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
    Crée une forme miroir à forme
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


chunkTex=FunctionUtils.NumpyDict()#la texture des chunks (stockées dans un NumpyDict, car plus rapide)
chunkLimits=FunctionUtils.NumpyDict()#la texture de la limite des chunks
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
    width_zoom = width // zoom
    height_zoom = height // zoom
    for posX in np.arange(-1,width_zoom+1):#pour posX dans -1,(width//zoom)+1 
            for posY in np.arange(-1,height_zoom+1):#pour posY dans -1,(height//zoom)+1
                
                Xpos = posX*zoom+((cam[0]+(width/2))%zoom)#coordonnées selon zoom
                Ypos = posY*zoom+((cam[1]+(height/2))%zoom)#coordonnées selon zoom
                
                worldPos = ScreenPosToWorldPos((Xpos,Ypos))#on converti les coordonnées en coordonnées du monde
                
                posCode = str(worldPos)#on converti en str (le NumpyDict n'apprécie pas trop les listes)
                
                if not posCode in chunkTex:#si le code de position n'est pas dans le dictionnaire chunkText
                    #on récupère les données liés au chunk via un bruit fractal
                    val = NoiseTools.FractalNoise(worldPos[0]/100, worldPos[1]/100, (SaveManager.GetSeed(),SaveManager.GetSeed()), 1)
                    
                    tex = "rock"#texture par défaut
                    if env == PlanetGenerator.PlanetTypes.Dead:#s'il s'agit d'une planète morte
                        if val<=0.5:#si le bruit est inférieur ou égal a 0.5
                            tex = "sand"#la texture sera du sable
                    else:#s'il ne s'agit pas d'une planète morte
                        if env == PlanetGenerator.PlanetTypes.Desertic:#s'il s'agit d'une planète désertique
                            if val < 0.7:#sauf si la valeur du bruit fractal est inférieure à 0.7
                                tex = "sand"#la texture devient du sable
                            if val < 0.34:#si la valeur du bruit fractal est inférieure à 0.34
                                tex = "water"#le chunk devient de l'eau
                        else:#s'il s'agit d'un planète vivante
                            if val < 0.7:#sauf si la valeur du bruit fractal est inférieure à 0.7
                                tex = "grass"#le chunk devient de l'herbe
                            if val < 0.4:#si la valeur du bruit fractal est inférieure à 0.4
                                tex = "sand"#la texture devient du sable
                            if val < 0.34:#si la valeur du bruit fractal est inférieure à 0.34
                                tex = "water"#le chunk devient de l'eau
                    
                    chunkTex[posCode] = tex#on ajoute le type de texture du chunk dans le dictionnaire chunkText
                    
                    needsRefresh = True#on demande un rafraîchissement du monde
                
                tex = chunkTex[posCode]#texture associé avec le code de la position
                
                screen.blit(TextureManager.GetTexture("ground/" + tex, zoom), (Xpos, Ypos))#placement de la texture du chunks
                
                if SettingsManager.GetSetting("niceBiomeBorders"):#si les bordures détaillées sont activées
                    if posCode not in chunkLimits or unRefreshed:#si la position n'est pas dans le dictionnaire chunkLimits ou si elle est non rafraîchie
                        
                        limitTex = ""#variable qui va contenir la limite du chunks
                        
                        if tex != "sand":#si la texture est différente du sable
                            for x in range(-1,2):#pour tous les chunks à cotés en x
                                for y in range(-1,2):#pour tous les chunks à cotés en y
                                    tPos = str((worldPos[0]-(x*10),worldPos[1]+(y*10)))#on définie la position de la texture adjacente
                                    if (x != 0 or y != 0) and tPos in chunkTex:#si le chunk est différent du chunk d'où l'on a lancé le calcul des bordures
                                        grabbedTex = chunkTex[tPos]#on stocke la texture du chunk à la position adjacente
                                        if grabbedTex != tex and grabbedTex in ["sand","rock"]:#si la texture est différente de la texture du chunk de base,et est sable ou de rocher
                                            limitTex += grabbedTex + str(x) + str(y) + ";"#on ajoute cette texture dans le nom de la texture de transition
                        
                        chunkLimits[posCode] = limitTex#on ajoute la limite aux coordonnées de la position dans le dictionnaire chunkLimits
                    
                    limitTex = chunkLimits[posCode]#on récupère la limite du chunk associé avec la position
                    if limitTex != "":#si la limite de chunk est différente de rien
                        if "ground/" + limitTex + ".png" not in TextureManager.loadedTextures:#si la texture n'est pas chargée
                            
                            texture = None
                            
                            for t in limitTex.split(";"):#pour le nombre de textures différentes à fusionner
                                if t != "":#si la texture n'est pas rien
                                    if texture == None:#si la texture est None
                                        texture = TextureManager.loadedTextures["ground/" + t + ".png"].copy()#on fait une copie de la texture
                                    else:#si la texture n'est pas None
                                        texture.blit(TextureManager.loadedTextures["ground/" + t + ".png"],(0,0))#on affiche la texture sur l'autre texture
                            
                            TextureManager.loadedTextures["ground/" + limitTex + ".png"] = texture#on stocke la texture
                            
                                
                        screen.blit(TextureManager.GetTexture("ground/" + limitTex, zoom), (Xpos, Ypos))#placement du fond
                    
    unRefreshed = needsRefresh
    
def ForceBackgroundRefresh():
    """Fonction servant à forcer la mise à jour du fond"""
    global unRefreshed
    unRefreshed = True


def GetChunkTextureAtChunkPos(pos:tuple)->str:
    """
    Renvoie la texture du chunk à une position de chunk (position entière d'un bloc divisée par 10)
    """
    return chunkTex.get(str((pos[0]*10.0,pos[1]*10.0)),None)


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

    menuElements=GameItems.menuElements#on récupère la liste d'éléments du menu de sélection
    for i,n in enumerate(menuElements):#pour chaque élément de menuElements
        #ajout du rect dans le dictionnaire de gestion d'éléments UI
        UIelements["selectElements_"+n]=pygame.draw.rect(screen, (47,48,51), pygame.Rect(width-500+102*(i%5),height-500*showMenu.get("select",0)+102*(i//5), 100, 100)).collidepoint(pygame.mouse.get_pos())
        #affichage de l'objet
        screen.blit(TextureManager.GetTexture(n, 78, True),(width-500+11+102*(i%5),height-500*showMenu.get("select",0)+102*(i//5)))
        #placement du texte de l'objet
        place_text(Localization.GetLoc('Items.' + n),width-500+102*(i%5),height-500*showMenu.get("select",0)+102*(i//5)+80,20,(255,255,255),TextureManager.GetFont("aquire"),auto_size=(100,20))
    #placement du bouton question
    UIelements["selectElements_question"]=pygame.draw.rect(screen, (47,48,51), pygame.Rect(width-500+102*3,height-100*showMenu.get("select",0), 100, 100)).collidepoint(pygame.mouse.get_pos())
    screen.blit(TextureManager.GetTexture("question", 78, True),(width-500+11+102*3,height-100*showMenu.get("select",0)))
    place_text("Interrogation",width-500+102*3,height-100*showMenu.get("select",0)+80,20,(255,255,255),TextureManager.GetFont("aquire"),auto_size=(100,20))
    #placement du bouton delete
    UIelements["selectElements_delete"]=pygame.draw.rect(screen, (47,48,51), pygame.Rect(width-500+102*4,height-100*showMenu.get("select",0), 100, 100)).collidepoint(pygame.mouse.get_pos())
    screen.blit(TextureManager.GetTexture("detruire", 78, True),(width-500+11+102*4,height-100*showMenu.get("select",0)))
    place_text("détruire",width-500+102*4,height-100*showMenu.get("select",0)+80,20,(255,255,255),TextureManager.GetFont("aquire"),auto_size=(100,20))
    #placement d'une aide
    place_text("presse "+pygame.key.name(SettingsManager.GetKeybind("rotate"))+" pour retourner l'élément",width-500,height-120*showMenu.get("select",0),20,(255,255,255),TextureManager.GetFont("aquire"),auto_size=(500,100))
    
def CostMenu():
    """Menu d'affichage des coûts de fabrication d'un objet"""
    if SaveManager.GetSelectedItem() != None:#si l'objet sélectionné n'est pas None
        p=GameItems.getPrice(SaveManager.GetSelectedItem())#on récupère le prix de l'item
        #on ajoute cette zone comme un élément Ui
        UIelements["cost"]=pygame.draw.rect(screen, (47,51,52), pygame.Rect(width-600, height-250*showMenu.get("select",0), 100,250) ).collidepoint(pygame.mouse.get_pos())
        place_text(Localization.GetLoc("UiManager.cost"), width-600, height-250*showMenu.get("select",0), 20,auto_size=(100,40))
        for n,(i,c) in enumerate(p):
            #on place chaque ressources requises pour la création de l'item
            screen.blit(TextureManager.GetTexture(i,78,is_menu=True), (width-600,height-250*showMenu.get("select",0)+40*(n+1)))
            place_text(str(c), width-600, height-250*showMenu.get("select",0)+40*(n+1), 40)


def InvMenu():
    """Affichage de l'inventaire"""
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

    for i,e in enumerate(SaveManager.mainData.inv):#pour chaque item dans l'inventaire
        UIelements["invElements_"+str(i)]=pygame.draw.rect(screen, (47,48,51), pygame.Rect(width-500+102*(i%5),-500+500*showMenu.get("inv",0)+102*(i//5), 100, 100)).collidepoint(pygame.mouse.get_pos())
        screen.blit(TextureManager.GetTexture(e["n"], 78, True),(width-500+11+102*(i%5),-500+11+500*showMenu.get("inv",0)+102*(i//5)))
        place_text(str(Localization.GetLoc("Items."+e["n"])),width-500+102*(i%5),-500+500*showMenu.get("inv",0)+102*(i//5),20)
        place_text(str(e["m"]),width-500+102*(i%5),-480+500*showMenu.get("inv",0)+102*(i//5),20)

# Définition de la fonction addNewlines qui prend en entrée une chaîne de caractères 'text' et une longueur maximale de ligne 'l'
def addNewlines(text, l=29):
    """
    Ajoute un caractère \n à une chaîne de caractères tout les 29 caractères, sans couper un mot.
    """
    # Split de la chaîne de caractères 'text' en mots
    words = text.split()
    # Initialisation de la nouvelle chaîne de caractères 'new_text' et de la longueur de la ligne actuelle 'line_len'
    new_text = ""
    line_len = 0
    # Boucle sur tous les mots de 'words'
    for word in words:
        # Calcul de la longueur du mot actuel 'word_len'
        word_len = len(word)
        # Si la longueur du mot actuel 'word_len' ajoutée à la longueur actuelle de la ligne 'line_len' et 1 (pour le caractère espace) est inférieure ou égale à la longueur maximale de ligne 'l'
        if line_len + word_len + 1 <= int(l):
            # Ajout du mot actuel et d'un espace à la nouvelle chaîne de caractères 'new_text'
            new_text += word + " "
            # Mise à jour de la longueur actuelle de la ligne 'line_len'
            line_len += word_len + 1
        else:
            # Ajout d'un caractère de nouvelle ligne '\n' à la nouvelle chaîne de caractères 'new_text'
            new_text = new_text.strip() + "\n"
            # Ajout du mot actuel et d'un espace à la nouvelle chaîne de caractères 'new_text'
            new_text += word + " "
            # Mise à jour de la longueur actuelle de la ligne 'line_len'
            line_len = word_len + 1
    # Ajout d'un dernier caractère de nouvelle ligne '\n' à la nouvelle chaîne de caractères 'new_text' et retourne la chaîne de caractères finale en supprimant les éventuels espaces de fin
    return new_text.strip() + "\n"


def DisplayItemToPlace():
    """
    Cette fonction a pour but d'afficher l'item que le joueur s'apprête à placer en transparence pour lui donner une indication de visée
    """
    ItemTexture = None
    if showMenu["delete"]:#si le mode suppression est activé
        if SaveManager.IsItemHere(GetMouseWorldPos()):#si un item est présent sur la position de la souris
            ItemTexture = TextureManager.GetColorFilter((255,0,0),SaveManager.GetZoom())#on affiche un filtre de couleur
    elif showMenu["question"]:#si le mode question est activé
        ItemTexture = "question"#la texture est celle du mode question
    else:
        ItemTexture = SaveManager.GetSelectedItem()#autrement, on récupère l'item sélectionné

    if ItemTexture == None or (IsClickOnUI() and not showMenu["question"]):#si la texture est nulle ou (c'est un clic UI et le mode question est désactivé)
        return
    #variables servant au placement
    cam = SaveManager.GetCamPos()
    cam = [cam[0],cam[1]]
    zoom = SaveManager.GetZoom()
    cam[0] += width / 2
    cam[1] += height / 2
    pos = GetMouseWorldPos()
    
    if type(ItemTexture) == str:#si la texture est de type str
        tex = TextureManager.GetTexture(ItemTexture, zoom).copy()#on fait une copie de la texture via TextureManager
    else:
        tex = ItemTexture#autrement, on prends le contenu d'itemTexture
    tex.set_alpha(150)#on applique un filtre
    tex=pygame.transform.rotate(tex,90*SaveManager.GetRotation())#on applique la rotation
    screen.blit(tex, (pos[0]*zoom+cam[0], pos[1]*zoom+cam[1]))#on affiche
    
def interactItem(item):
    """Interface d'interaction avec des objets"""
    #on définit le fond du menu (voir SessionManager)
    screenFilter = pygame.Surface((width,height))
    screenFilter.set_alpha(50)
    SessionManager.PauseMenuBackground = pygame.display.get_surface().copy()
    SessionManager.PauseMenuBackground.blit(screenFilter,(0,0))
    #création du menu
    interactMenu = pygame_menu.Menu("Configurez cet élément", 400, 300, theme=pygame_menu.themes.THEME_DARK,onclose=pygame_menu.events.BACK)
    
    interactMenu.add.button('Reprendre', interactMenu.disable)#Reprendre la partie
    b=None
    if item.name=="Sorter":#Si l'objet à éditer est un trieur...
        
        a=[[i] for i in list(GameItems.allTransportableItems.keys())]#On récupère la liste des éléments transportables
        
        chosenElement = [item.metadata["sorter_choice"]]#on affiche l'item choisit
        
        b=interactMenu.add.selector("Choisissez : ",a,default=a.index(chosenElement))#On crée un sélecteur pour permettre de choisir l'élément trié
        
        interactMenu.mainloop(screen,SessionManager.DisplayPauseMenuBackground)#on lance le menu
        
    if item.name in ["Storage"]:#si l'item peut interagir avec l'inventaire
        
        in_menu=1#booléen si l'on est dans le menu
        BLOCK_SIZE=100#taille des blocs
        rects=[]
        inv=[]
        for x,e in enumerate(item.metadata.get("biginv",[])):#pour chaque élément de l'inventaire de l'item
            if e["n"] is None:#si l'élément est None
                del item.metadata["biginv"][x]#on supprime l'élément
            else:#si l'élément n'est pas None
                #ajout d'un rect à la liste rects
                rects.append( pygame.Rect(width//4-250+(x%4)*(BLOCK_SIZE+5), height//2-300+(x//4)*(BLOCK_SIZE+5), BLOCK_SIZE, BLOCK_SIZE) )
                inv.append(e)#ajout de l'objet à la liste inv
        for x,e in enumerate(SaveManager.mainData.inv):#pour chaque élément de l'inventaire du joueur
            #ajout d'un rect à la liste rects
            rects.append( pygame.Rect((width//4)*3-250+(x%4)*(BLOCK_SIZE+5), height//2-300+(x//4)*(BLOCK_SIZE+5), BLOCK_SIZE, BLOCK_SIZE) )
            inv.append(e)#ajout de l'objet a la liste inv
        clock = pygame.time.Clock()#défintion d'une horloge interne au menu de transfert d'item
        selected=None#élément sélectionné
        
        while in_menu:#tant que l'on est dans le menu
            for event in pygame.event.get():#on parcours la liste des événements
                if event.type == pygame.KEYDOWN:#en cas de touche pressée
                    if event.key == pygame.K_ESCAPE:#si la touche [ESC] est pressée
                        in_menu = False#on sort du menu
 
                elif event.type == pygame.MOUSEBUTTONDOWN:#en cas de bouton de la souris pressé
                    if event.button == 1:#si le btn left est pressé
                        for i, r in enumerate(rects):#pour chaque rect dans rects
                            if r.collidepoint(event.pos):#si le rect subis une collision avec la souris
                                selected = i#on change l'item sélectionné
                                selected_offset_x = r.x - event.pos[0]#affichage de l'offset de sélection
                                selected_offset_y = r.y - event.pos[1]#affichage de l'offset de sélection
               
                elif event.type == pygame.MOUSEBUTTONUP:#si le bouton de la souris est relaché
                    if event.button == 1:#s'il s'agit du bouton gauche
                        selected = None#on ne séléctionne rien
               
                elif event.type == pygame.MOUSEMOTION:#en cas de mouvement de la souris
                    if selected is not None: #si selected n'est pas None
                        # on bouge l'objet selon l'offset
                        rects[selected].x = event.pos[0] + selected_offset_x
                        rects[selected].y = event.pos[1] + selected_offset_y
            #interface
            SessionManager.DisplayPauseMenuBackground()#on affiche le fond
            #interface de l'inventaire du stockage
            forme2(width//4-250,height//2-300,500,100,50,200,(98,99,102))
            pygame.draw.polygon(screen, (98,99,102), [(width//4-250,height//2-300),(width//4+250,height//2-300),(width//4+250,height//2+300),(width//4-250,height//2+300)])
            place_text("Stockage",width//4-245,height//2-330,100,(255,255,255),TextureManager.GetFont("aquire"))
            #interface de l'inventaire du joueur
            forme2((width//4)*3-250,height//2-300,500,100,50,200,(98,99,102))
            pygame.draw.polygon(screen, (98,99,102), [((width//4)*3-250,height//2-300),((width//4)*3+250,height//2-300),((width//4)*3+250,height//2+300),((width//4)*3-250,height//2+300)])
            place_text("Inventaire",(width//4)*3-245,height//2-330,100,(255,255,255),TextureManager.GetFont("aquire"))
            #affichage des items
            for r in zip(rects,inv):#pour chaque rects (et inv)
                pygame.draw.rect(screen,  (47,48,51), r[0])#affichage du rect
                screen.blit(TextureManager.GetTexture(r[1]["n"], 78, True),(r[0].x,r[0].y))#affichage de l'item

                place_text(str(Localization.GetLoc("Items."+r[1]["n"])),r[0].x,r[0].y,20)#affichage du nom de l'item
                place_text(str(r[1]["m"]),r[0].x,r[0].y+20,20)#affichage du nombre d'items
            place_text("[Echap] pour quitter", 0, 0, 40, (255,255,255))#affichage d'une instruction d'aide
            pygame.display.update()#mise à jour de l'écran
            clock.tick(25)
        
        #change l'environnement de stockage/inv
        #on stocke le contenu dans des variables temporaires
        tempInv=[]
        for i in SaveManager.mainData.inv:
            tempInv.append(dict(i))
        tempBigInv=[]
        for i in item.metadata["biginv"]:
            tempBigInv.append(dict(i))
        #on supprime les deux inventaires
        SaveManager.ClearInv()
        item.metadata["biginv"]=[]

        for r in zip(rects,inv):#pour chaque rects et inv
            if r[0].x<width//2:#si le rect est dans la zone du stockage
                for i in range(r[1]["m"]):#pour chaque nombre d'items
                    if not item.AddToInv(r[1]["n"]):#si l'item ne peut pas être ajouté
                        #on remets les inventaires à leur états initiaux
                        SaveManager.mainData.inv=tempInv
                        item.metadata["biginv"]=tempBigInv
                        Popup(Localization.GetLoc("UiManager.biginv.error"))#affichage de l'erreur
                        return#on quitte cette fonction
            else:#si le rect est dans la zone de l'inventaire du joueur
                for i in range(r[1]["m"]):#pour chaque nombre d'items
                    if not SaveManager.AddToInv(r[1]["n"]):#si l'item ne peut pas être ajouté
                        #on remets les inventaires à leur états initiaux
                        SaveManager.mainData.inv=tempInv
                        item.metadata["biginv"]=tempBigInv
                        Popup(Localization.GetLoc("SaveManager.GetFromInv.error"))#affichage de l'erreur
                        return#on quitte cette fonction
    
    if item.name=="Market":#en cas d'interaction avec un market
        MarketManager.showMenu()#on affiche le menu du market

    SessionManager.PauseMenuBackground = None#on vide le fond du menu
    return b.get_value() if b is not None else None#renvoie la valeur de b si B n'est pas None sinon, renvoie None

def Loading():
    """Affichage de l'écran de chargement"""
    FillScreen((0,0,0))#on remplis en noir l'écran (la couleur reste si le background ne se charge pas)
    DisplayBackground()#affichage du fond
    
    logoTex = pygame.transform.scale(TextureManager.GetTexture("logos/SPFTR"),(height/2,height/2))#Récupération du logo
    screen.blit(logoTex,((width-logoTex.get_width())/2, (height-logoTex.get_height())/2))#affichage du logo
    
    place_text(Localization.GetLoc("Game.Loading"),0,-height/3,100,(255,255,255),font=TextureManager.GetFont("aquire",100),centerText=True)#Affichage du chargement
    pygame.display.update()#mise à jour de l'écran

UIPopup=[]#liste des popups
UiLightPopup=[]#liste des LightPopup
class Popup:
    """
    Des popups
    """
    def __init__(self,text,command=None,d=0,p=0):
        """
        Text : texte de la popup
        command : la commande à lancer en cas de clic
        d : Forcer le display (si 0, la popup agit de manière classique, si 1, la popup ne peut être fermée que par self.close)
        p : progression de la barre de progression de la popup
        """
        self.text=addNewlines(text,29)
        self.time=int(pygame.time.get_ticks())
        self.command=command
        self.sliding=0
        self.d=d
        self.prog=p
        UIPopup.append(self)
    def show(self,i):
        self.sliding+= SaveManager.clock.get_time()
        if self.sliding > 500:
            self.sliding = 500
        
        if int(pygame.time.get_ticks())>(self.time+10000) and self.command is None and not self.d:
               self.close(i)
        else:
            a=pygame.draw.rect(screen, (58, 48, 46), pygame.Rect(width-self.sliding,50+205*i,500,200))
            UIelements["popup_"+str(i)]=a.collidepoint(pygame.mouse.get_pos()) if not self.d else False#on détecte les collisions uniquement si le mode d n'est pas activé
            place_text(self.text,width-self.sliding,50+205*i,26,(255,255,255),TextureManager.GetFont("nasalization"),n=30)
            if self.prog!=0:
                pygame.draw.rect(screen, (255,255,255), pygame.Rect(width-self.sliding,50+200*i,500*self.prog,3))
            if not self.d:
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
    def setProg(self,p):
        self.prog=p
    def getProg(self):
        return self.prog

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
            place_text(self.text, 0, (-height//4)-i*30, 20, (255,255,255),TextureManager.GetFont("nasalization"),auto_size=(width//2,height//10),centerText=True)
    def close(self,i):
        UiLightPopup.remove(self)


MenuBackground = pygame_menu.baseimage.BaseImage("./Assets/background.png", drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')#on définit le fond des menus

def DisplayBackground():
    """Affichage du fond, et mise à jour du son"""
    MenuBackground.draw(screen)
    AudioManager.Tick()

def WarnUser(title:str, message:str, confirm, cancel, background=DisplayBackground)->bool:
    """Menu de prévention pour s'assurer de l'action utilisateur"""
    
    WarnMenu = pygame_menu.Menu(title, 800, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    WarnMenu.add.label(message)
    
    bottomBar = WarnMenu.add.frame_h(800,50)
    bottomBar.relax(True)
    
    global confirmed
    confirmed = False
    def setConfirmed():
        WarnMenu.disable()
        global confirmed
        confirmed = True
    
    confirmButton = WarnMenu.add.button(Localization.GetLoc('Game.Confirm'), setConfirmed)
    if confirm != None:
        confirmButton.set_onreturn(lambda:(setConfirmed(),confirm()))
    bottomBar.pack(confirmButton, align=pygame_menu.locals.ALIGN_LEFT)
    
    cancelButton = WarnMenu.add.button(Localization.GetLoc('Game.Cancel'), WarnMenu.disable)
    if cancel != None:
        confirmButton.set_onreturn(lambda:(WarnMenu.disable(),cancel()))
    bottomBar.pack(cancelButton, align=pygame_menu.locals.ALIGN_RIGHT)
    
    WarnMenu.mainloop(screen, background)
    
    return confirmed

def TakeScreenshot():
    """Prendre une capture d'écran"""
    if not os.path.exists("Screenshots/"):
        os.makedirs("Screenshots/")
    pygame.image.save(pygame.display.get_surface(), "Screenshots/screenshot_" + datetime.now().strftime("%Y%m%d%H%M%S%f") + ".png")
    Popup("Capture d'écran trouvable dans le dossier /Screenshots/")
