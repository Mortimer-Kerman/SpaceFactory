# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 11:47:04 2023

@author: sartre.thomas
"""

#Chargement des bibliothèques
import pygame
import SaveManager
import TextureManager
import GameItems

#Les variables importantes
screen = None#la fenêtre pricipale (élément pygame.display)
#la taille de l'écran
width = 0
height = 0

UIelements={}#dictionaire stockant les interaction souris/éléments interface
showMenu={"select":0,"delete":0}#affichage ou non des menus interne à l'UI

def Init():
    """
    Fonction d'initialisation du fichier
    Sert à définir les variables importantes (voir ci-dessus)
    """
    global screen,width,height#on prends les variables comme globales
    
    width, height = pygame.display.list_modes()[0]#on prends la plus grande taille possible
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)#on définit l'élément pygame.display (la fenêtre sera en plein écran)

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
    
    place_text(str(list(pygame.mouse.get_pos()))+" "+str(SaveManager.GetCamPos()) + " " + str(round(SaveManager.clock.get_fps())),0,height-50,20,(250,250,250),TextureManager.aquire)#placement du texte (position du curseur + caméra + FPS)

    ItemMenu()#placement du menu de séléction d'item

def GetMouseWorldPos():
    """
    Renvoie la position du curseur dans le monde
    """
    cam = SaveManager.GetCamPos()#on obtient les coordonées de la caméra
    zoom = SaveManager.GetZoom()#obtention du zoom
    return ((pygame.mouse.get_pos()[0]-cam[0]-(width/2))//zoom,(pygame.mouse.get_pos()[1]-cam[1]-(height/2))//zoom)#renvoie la position par rapport à la caméra+zoom

def IsClickOnUI():
    """
    Sert à savoir si l'utilisateur clique sur l'UI
    """
    for i in UIelements.values():#pour chaque valeur de UIelements (toutes les valeurs sont des booléens)
        if i:#si i
            return True#renvoier vrai
    return False#renvoier faux

autoSize={}
def place_text(text, x, y, size, color=(255,255,255),font=None,n=20,auto_size=False):
    """
    Fonction utilitaire servant au placement du texte sur l'écran
    """
    if not auto_size:
        font = pygame.font.Font(None, size) if font==None else font#tentative de charger la police
        t=text.splitlines()
        for i,l in enumerate(t):
            text_surface = font.render(l, True, color)#on crée l'image du texte
            screen.blit(text_surface, (x, y+n*i))#on affiche le texte
    else:
        if (auto_size,text) in autoSize.keys():
            text_surface = autoSize[(auto_size,text)]
            screen.blit(text_surface, (x, y))#on affiche le texte
        else:
            taille=32
            while taille > 0:
                font = pygame.font.Font("./Assets2/font/Aquire.ttf",taille)#on tente de charger aquire
                text_surface = font.render(text, True, (255, 255, 255))
                if text_surface.get_width() <= auto_size[0] and text_surface.get_height() <= auto_size[1]:
                    break
                taille -= 1
            autoSize[(auto_size,text)]=text_surface
            screen.blit(text_surface, (x, y))#on affiche le texte

def forme(x,y,w,wr,h,o,color=(47,48,51)):
    """
    Crée une forme
    """
    #calcul des coordonées du polygone
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
    #calcul des coordonées du polygone
    a = x, y
    b = x + w - 1, y
    c = x + w - 1, y - h * 0.6
    d = x + wr + 25 + o, y - h * 0.6
    e = x + wr + 5 + o, y - h
    f = x, y - h
    return pygame.draw.polygon(screen,color,(a,b,c,d,e,f))#affichage du polygone (renvoie l'élément pygame.Rect lié au polygone)

def UpdateBackground():
    """
    Mise à jour du fond
    """
    zoom = SaveManager.GetZoom()*10#récupération du zoom
    cam = SaveManager.GetCamPos()#récupération de la position de la caméra
    for posX in range(-1,(width//zoom)+1):#pour posX dans -1,(width//zoom)+1 
            for posY in range(-1,(height//zoom)+1):#pour posY dans -1,(height//zoom)+1
                Xpos = posX*zoom+((cam[0]+(width/2))%zoom)#coordonées selon zoom
                Ypos = posY*zoom+((cam[1]+(height/2))%zoom)#coordonées selon zoom
                screen.blit(TextureManager.GetTexture("ground", zoom), (Xpos, Ypos))#placement du fond

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

    menuElements=GameItems.menuElements
    for i in range(len(menuElements)):
        UIelements["selectElements_"+menuElements[i]]=pygame.draw.rect(screen, (47,48,51), pygame.Rect(width-500+102*(i%5),height-500*showMenu.get("select",0)+102*(i//5), 100, 100)).collidepoint(pygame.mouse.get_pos())
        screen.blit(TextureManager.GetTexture(menuElements[i], 78, True),(width-500+11+102*(i%5),height-500*showMenu.get("select",0)+102*(i//5)))
        place_text(menuElements[i],width-500+102*(i%5),height-500*showMenu.get("select",0)+102*(i//5)+80,20,(255,255,255),TextureManager.aquire,auto_size=(100,20))

    UIelements["selectElements_delete"]=pygame.draw.rect(screen, (47,48,51), pygame.Rect(width-500+102*(i%5),height-100*showMenu.get("select",0), 100, 100)).collidepoint(pygame.mouse.get_pos())
    screen.blit(TextureManager.GetTexture("detruire", 78, True),(width-500+11+102*(i%5),height-100*showMenu.get("select",0)))
    place_text("détruire",width-500+102*(i%5),height-100*showMenu.get("select",0)+80,20,(255,255,255),TextureManager.aquire,auto_size=(100,20))

def addNewlines(text,l):
    """
    Ajoute un caractère \n à une chaine de caractères tout les 29 caractères, sans couper un mot.
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


UIPopup=[]
class Popup:
    """
    Des popups
    """
    def __init__(self,text):
        self.text=addNewlines(text,29)
        self.time=int(pygame.time.get_ticks())
        self.sliding=0
        UIPopup.append(self)
    def show(self,i):
        self.sliding+=5 if self.sliding<=500 else 0
        if int(pygame.time.get_ticks())>(self.time+10000):
               self.close(i)
        else:
            UIelements["popup_"+str(i)]=pygame.draw.rect(screen, (58, 48, 46), pygame.Rect(width-self.sliding,50+205*i,500,200)).collidepoint(pygame.mouse.get_pos())
            place_text(self.text,width-self.sliding,50+205*i,26,(255,255,255),TextureManager.aquire)
            UIelements["popup_close_button_"+str(i)]=pygame.draw.rect(screen, (37, 37, 40), pygame.Rect(width-self.sliding,225+205*i,50,25)).collidepoint(pygame.mouse.get_pos())
            place_text("Ok",width-self.sliding,225+205*i,26,(255,255,255),TextureManager.aquire)
    def close(self,i):
        UIPopup.remove(self)
        UIelements["popup_"+str(i)]=False
        UIelements["popup_area"]=False
        UIelements["popup_close_button_"+str(i)]=False
        