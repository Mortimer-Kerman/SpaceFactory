#!/usr/bin/python3
# coding: utf8
#Projet sous license CC BY-NC-SA 4.0 https://creativecommons.org/licenses/by-nc-sa/4.0/


import pygame
import pygame_menu

import json
from random import seed, randint, choice


currentGame=[]
currentMechants=[]
currentMinerais=[]

cam=[0,0]
se=randint(-(9**9),9**9)
multi=100

textureData={"drill":"./assets/drill.png","m":"./assets/m1.png"}
textureLoaded={}
texture={}

for i in list(textureData.keys()):
    textureLoaded[i]=pygame.image.load(textureData.get(i,"./assets/no.png"))


def actualiserTexture():
    global texture
    texture={}
    for i in list(textureData.keys()):
        texture[i]=pygame.transform.scale(textureLoaded[i],(multi,multi))

class Save:
    def load(name):
        """
        Chargement de la sauvegarde

        name : str
        nom de la sauvegarde
        """
        global savefile, currentGame, se, cam
        savefile = name+".spf"
        with open(savefile,'r') as f:
            s=json.load(f)#on charge la sauvegarde depuis le fichiers
        for ele in s.get("currentGame",[]):
            currentGame.append(Object(ele.get("n","Objet sans nom"),ele.get("c",[0,0]),ele.get("t","texture introuvable"),ele.get("d")))
        se=s.get("seed",se)
        cam=s.get("cam",cam)
        print("Chargement du fichier "+savefile)
    def save():
        s={"currentGame":[],"currentMechants":[],"seed":se,"cam":cam}
        for i in currentGame:
            s["currentGame"].append(i.get())
        with open(savefile,"w") as f:
            json.dump(s,f)
        print("Partie sauvegardée dans le fichier "+savefile)
    def create(name):
        global se
        with open(name+'.spf', 'w') as f:
            f.write("[]")
        print("création de sauvegarde")
        se=randint(-(9**9),9**9)
    def changeSaveFile():
        try:
            Save.load(str(saveFileSelect.get_value()))
        except:
            print("Pas de fichier, création d'une nouvelle sauvegarde")
            Save.save()
class Object:
    def __init__(self,nom,co:tuple,texture=None,data=None):
        self.nom=nom
        self.co=co
        self.data=data
        self.texture=texture
    def get(self):
        return {"n":self.nom,"c":self.co,"t":self.texture,"d":self.data}
    def __repr__(self) -> str:
        return str(self.nom)+str(self.co[0])+":"+str(self.co[1])
    def show(self):
        #pygame.draw.rect(screen, (233,237,239), pygame.Rect(self.co[0]*multi+cam[0], self.co[1]*multi+cam[1], multi, multi), width=0)
        screen.blit(texture[self.texture], (self.co[0]*multi+cam[0], self.co[1]*multi+cam[1]))
        Utiles.place_text(str(self.co),self.co[0]*multi+cam[0], self.co[1]*multi+cam[1],50,(255,0,0))

class Minerais:
    def place_m():
        for x in range(-cam[0]//multi-2,(-cam[0]+largeur)//multi+2):
                y=-cam[1]
                seed(x*y*se+x+y+se+x)
                if randint(0,60)==40:currentMinerais.append([x,y])
        for y in range(-cam[0]//multi-2,(-cam[0]+largeur)//multi+2):
                x=-cam[0]
                seed(x*y*se+x+y+se+x)
                if randint(0,60)==40:currentMinerais.append([x,y])
    def place(x,y):
        screen.blit(texture["m"], (x*multi+cam[0], y*multi+cam[1]))


class Utiles:
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

class Button:
    def __init__(self,text,texture,co,taille,action):
        self.text=text
        self.texture=texture
        self.co=co
        self.taille=taille
        self.show_=1
        self.action=action
    def show(self):
        self.show_=1
        self.draw()
    def hide(self):
        self.show_=0
    def getCo(self):
        return [self.co,self.show_]
    def draw(self):
        pygame.Rect(10,10,10,10)

pygame.init()#initialisation pygame

clock = pygame.time.Clock()  
largeur, hauteur = pygame.display.list_modes()[0]#auto fullscreen
print(largeur,hauteur)
screen = pygame.display.set_mode((largeur, hauteur))

try:aquire=pygame.font.Font("./assets/Aquire.ttf",26)
except:aquire=pygame.font.get_default_font()

pygame.display.set_caption('SpaceFactory')

def draw_burger_menu(x, y):
    pygame.draw.rect(screen, (255,255,255), [x+10, y+10, 50, 10])
    pygame.draw.rect(screen, (255,255,255), [x+10, y + 30, 50, 10])
    pygame.draw.rect(screen,(255,255,255), [x+10, y + 50, 50, 10])

def hud():
    Utiles.forme(0,0,largeur,100,50,200)

    Utiles.forme2(0,hauteur-50,largeur,100,50,200)


    draw_burger_menu(x, y)

    Utiles.place_text(str(list(pygame.mouse.get_pos()))+" "+str(cam),0,hauteur-100,20,(250,250,250),aquire)
        

def play():
    """
    Lance le jeu
    """
    pygame.key.set_repeat(10)
    global cam,multi
    actualiserTexture()
    running = True
    Minerais.place_m()

    burgerMenuButton = Button(gameDisplay, 10, 10, 70, 70, onRelease=p)
 
    while running:#
        print(clock.get_fps())
        #génération du terrain
        screen.fill((47,79,79))

        #placement minerais
        #print(currentMinerais)
        for ele in currentMinerais:
            Minerais.place(*ele)
            if not (-cam[0]+largeur+200>=ele[0]*multi>=-cam[0]-200 and -cam[1]+hauteur+200>=ele[1]*multi>=-cam[1]-200):
                currentMinerais.remove(ele)
        #placement blocs usine
        for ele in currentGame:
            if -cam[0]+largeur+200>=ele.co[0]*multi>=-cam[0]-200 and -cam[1]+hauteur+200>=ele.co[1]*multi>=-cam[1]-200:#si élément dans écran, montrer
                ele.show()
        #interface
        hud()

        pygame.display.update()
        
        #traitement des événements
        for event in pygame.event.get():
            #en cas de fermeture du jeu (sert à ne pas provoquer de bug)
            if event.type == pygame.QUIT:
                running = False
            #action du clavier
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    cam[1]+=5
                if event.key == pygame.K_DOWN:
                    cam[1]-=5
                if event.key == pygame.K_RIGHT:
                    cam[0]-=5
                if event.key == pygame.K_LEFT:
                    cam[0]+=5
                screen.fill((33,37,39))
                Minerais.place_m()
            #action de molette de souris
            if event.type == pygame.MOUSEWHEEL:
                multi+=event.y if event.y+multi>0 else 0
                actualiserTexture()
                Minerais.place_m()
            #action du clic
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # 1 == left button
                    
                    #a faire
                    currentGame.append(Object("test2",((pygame.mouse.get_pos()[0]-cam[0])//multi,(pygame.mouse.get_pos()[1]-cam[1])//multi),"drill"))
                    
                    Save.save()
        clock.tick()

pygame.mixer.music.load("./assets/theme.mp3")
  
# Setting the volume
pygame.mixer.music.set_volume(0.7)
  
# Start playing the song
pygame.mixer.music.play(loops=-1, start=0.0, fade_ms=200)

menu = pygame_menu.Menu('Bienvenue', 400, 300,
                       theme=pygame_menu.themes.THEME_DARK)
bg=pygame_menu.baseimage.BaseImage("./assets/background.png", drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')
saveFileSelect=menu.add.text_input('Fichier :', default='save',maxchar=10)

menu.add.button('Jouer', lambda :(Save.changeSaveFile(),play()))
menu.add.button('Quitter', pygame_menu.events.EXIT)

menu.mainloop(screen,lambda : bg.draw(screen))