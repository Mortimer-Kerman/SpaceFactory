# -*- coding: utf-8 -*-

#importation des bibliothèques externes
import random
import pygame
import numpy as np
#importation des fichier local
import UiManager
import SaveManager
import TextureManager
import FunctionUtils
import AudioManager
import PlanetGenerator
import GameItems
#importation de copysign du module système math
from math import cos

EnnemisList=[]#Liste des ennemis

class Ennemis:
    """Classe ennemis, les ennemis sont une forme évoluée de problème pour le joueur"""
    def __init__(self,co):
        self.pos=co
        self.name="Ennemy"
        self.pv=100
        self.rotation=random.randint(0, 3)
        
        #On donne un objectif à l'ennemi
        nearest_pos = list(UiManager.GetMouseWorldPos())
        nearest_pos = [nearest_pos[0]+random.randint(-20,20),nearest_pos[1]+random.randint(-20,20)]
        min_dist = float('inf')#float('inf) renvoie une valeur très très très très très très très très très très grande
        
        for pos , item in dict(SaveManager.mainData.items).items():#pour chaque clé du dictionnaire d'item de la sauvegarde
            pos=FunctionUtils.strToList(pos)#on convertit la position en liste (stockée en tant que str) (renvoie une liste de str)
            pos[0]=float(pos[0])#on convertit en flottant
            pos[1]=float(pos[1])#on convertit en flottant
            dist = FunctionUtils.Distance(pos, self.pos)#calcul de la distance entre la position actuelle et la position de l'item
            if dist < min_dist and item.metadata.get("pv",100):#si la distance est plus petite que la distance minimale précédente
                min_dist = dist#on change la distance minimale
                nearest_pos = pos#on change la position la plus proche
        self.go=list(nearest_pos)#on stocke la destination dans une variable
    def spawn(a=None):
        """Fonction d'apparition d'un ennemi"""
        global EnnemisList
        for i in range(random.randint(1,5)):
            a=list(UiManager.GetMouseWorldPos())#on récupère la position de la souris dans le monde
            #on ajoute des nombres aléatoire aux coordonnées
            a[0]+=random.randint(-100, 100)
            a[1]+=random.randint(-100, 100)
            print(a)
            EnnemisList.append(Ennemis(a))#Ajout de l'ennemi dans la liste EnnemiList
    def __str__(self):
        return "Ennemis(%s)"%self.pos#affiche les coordonnées de l'ennemi
    def ia(self,runtime):
        """Le cerveau même de notre ennemi, sa conscience de son environnement, et son envie de vivre, son envie de tuer, son envie de détruire"""
        if runtime<=48:#si le runtime est inférieur ou égal à 49
            return#quitter la fonction
        pos=self.pos#on stocke la position
        v=[None,None]#V nous servira comme d'un vecteur
        v[0]=self.go[0]-self.pos[0]#on insère le x du vecteur
        v[1]=self.go[1]-self.pos[1]#on insère le y du vecteur
        if v[0]!=0:#si l'on est pas arrivé à la cible en x
            pos[0]+=FunctionUtils.signe(v[0])#on ajoute +1 ou -1 à la position x
        elif v[1]!=0:#si l'on est pas arrivé à la cible y
            pos[1]+=FunctionUtils.signe(v[1])#on ajoute +1 ou -1 à la position y
        else:
            nearest_pos = [self.pos[0]+random.randint(-100,100),self.pos[1]+random.randint(-100,100)]#on choisit une nouvelle position aléatoirement
            min_dist = float('inf')

            for pos, item in dict(SaveManager.mainData.items).items():#pour chaque clé dans la sauvegarde
                pos=FunctionUtils.strToList(pos)#on transforme la chaîne de caractère en liste
                pos[0]=float(pos[0])#on transforme la position x en flottant
                pos[1]=float(pos[1])#on transforme la position y en flottant
                dist = FunctionUtils.Distance(pos, self.pos)#on calcule la distance
                if dist < min_dist and pos!=self.go and item.metadata.get("pv",100):#si la distance est plus petite que la plus petite distance
                    min_dist = dist#on stocke la distance
                    nearest_pos = pos#on stocke la position
            self.go=list(nearest_pos)#on change la position de destination
            return
        if SaveManager.IsItemHere(pos):
            a=SaveManager.GetItemAtPos(pos).metadata
            if a.get("pv",100)>0:
                a["pv"]=a.get("pv",100)-50
        self.pos=pos
    def show(self,c):
        """
        Fonction servant à afficher l'ennemi
        """
        #variables d'affichages
        cam = SaveManager.GetCamPos()
        cam = [cam[0],cam[1]]
        zoom = SaveManager.GetZoom()
        cam[0] += UiManager.width / 2
        cam[1] += UiManager.height / 2
        #AudioManager.PlaySound("Robot",self.pos)
        #si l'ennemi est dans le champ visuel du joueur, on l'affiche, sinon on sort de la fonction
        if not (-cam[0]+UiManager.width+200>=self.pos[0]*zoom>=-cam[0]-200 and -cam[1]+UiManager.height+200>=self.pos[1]*zoom>=-cam[1]-200):#si l'objet n'est pas visible
            return#quitter la fonction
        UiManager.UIelements["ennemi"+str(c)]=UiManager.screen.blit(pygame.transform.rotate(TextureManager.GetTexture(self.name, zoom),90*self.rotation), (self.pos[0]*zoom+cam[0], self.pos[1]*zoom+cam[1])).collidepoint(pygame.mouse.get_pos())#afficher

class EventTemplate:
    def Init():
        pass
    def Update(eventStrength:float,runtime:int):
        pass
    def FixedUpdate():
        pass
    def End():
        pass
    def GetEventDuration()->int:
        return 100#:random.randint(20,500)

class EnnemyAttack(EventTemplate):
    def Init():
        Ennemis.spawn()#apparition d'un ennemi
        UiManager.Popup("Un ennemi a été détecté dans votre zone")

class Sandstorm(EventTemplate):
    
    tex = None
    
    def Init():
        UiManager.Popup("Une tempête de sable est en approche!")
        Sandstorm.tex = pygame.transform.scale(TextureManager.GetTexture("ground/sand"),(UiManager.width,UiManager.height))
    
    def Update(eventStrength:float,runtime:int):
        ticksSinceInit = (pygame.time.get_ticks()%2000)/2000
        tex = Sandstorm.tex.copy()
        tex.set_alpha(128 * eventStrength)
        for i in range(-1,1):
            UiManager.screen.blit(tex, (UiManager.width*(ticksSinceInit+i), 0))#afficher
    
    def End():
        UiManager.Popup("Fin de la tempête!")

class SolarStorm(EventTemplate):
    
    tex = None
    
    def Init():
        UiManager.Popup("Une tempête solaire a été détectée!")
        SolarStorm.tex = pygame.transform.scale(TextureManager.GetTexture("ui/radiationEffect"),(UiManager.width,UiManager.height))
        
    def Update(eventStrength:float,runtime:int):
        tex = SolarStorm.tex.copy()
        tex.set_alpha(150 * FunctionUtils.clamp01(cos(pygame.time.get_ticks()/500)/2+1.3) * eventStrength)
        UiManager.screen.blit(tex, (0, 0))#afficher
        
    def End():
        UiManager.Popup("Fin de la tempête!")

class MeteorStorm(EventTemplate):
    def Init():
        UiManager.Popup("Une pluie de météorites est en approche!")
    def Update(eventStrength:float,runtime:int):
        tex = TextureManager.GetColorFilter((128,128,0), UiManager.width).copy()
        tex.set_alpha(100 * eventStrength)
        UiManager.screen.blit(tex, (0, 0))#afficher
    
    def End():
        UiManager.Popup("Fin de la pluie de météorites!")


class Events:
    """
    Classe servant à provoquer la destruction, à provoquer le chaos, à provoquer la chute du joueur
    """
    def __init__(self):
        self.isEventHappening = False
        self.runtime=0
        self.lastEvent = 0
        self.nextEvent = 5#random.randint(5,500)#prochain événement
        self.CurrentEvent = None
    
    def LaunchEvent(self):
        """
        Se lance deux fois par seconde pour savoir si un évenement a pris fin et si il faut en lancer un nouveau
        """
        self.runtime+=1
        
        if self.CurrentEvent != None:
            self.CurrentEvent.FixedUpdate()
        
        if self.nextEvent<self.runtime:#si le runtime est supérieur au nextEvent
            
            self.SetTimeBeforeNextEvent(10)#random.randint(20,500))#prochain événement
            
            if self.isEventHappening:#si un évenement est en cours
                self.isEventHappening = False#On met fon à l'évenement
                self.CurrentEvent.End()
                self.CurrentEvent = None
                
            elif random.randint(0,3) <= SaveManager.GetDifficultyLevel():#Sinon, avec une chance sur 3 en facile, deux sur trois en normal et 100% du temps en difficile...
                    
                    self.isEventHappening = True#On marque le lancement d'un évenement
                    
                    possibleEvents = [EnnemyAttack]
                    
                    if SaveManager.GetEnvironmentType() == PlanetGenerator.PlanetTypes.Desertic:
                        possibleEvents.append(Sandstorm)
                    
                    elif SaveManager.GetEnvironmentType() == PlanetGenerator.PlanetTypes.Dead:
                        possibleEvents.append(SolarStorm)
                    """  
                        if SaveManager.GetDifficultyLevel() == 3:
                            possibleEvents.append(MeteorStorm)
                    """
                    self.CurrentEvent = random.choice(possibleEvents)
                    
                    self.CurrentEvent.Init()
                    
                    self.SetTimeBeforeNextEvent(self.CurrentEvent.GetEventDuration())
    
    def SetTimeBeforeNextEvent(self,duration:int):
        """
        Règle le temps avant le prochain évenement, ou la durée restante à l'évenement en cours
        """
        self.lastEvent = self.nextEvent
        self.nextEvent = self.runtime + duration

    def UpdateCurrentEvent(self,runtime:int):
        """
        Lance la fonction de mise à jour de l'évenement actuel
        """        
        if self.CurrentEvent != None:
            
            timeBeforeEnd = FunctionUtils.clamp01((self.nextEvent - (self.runtime + (runtime / 50)))/2)
            timeSinceBegin = FunctionUtils.clamp01((self.runtime + (runtime / 50) - self.lastEvent)/2)
            
            if timeBeforeEnd == 1:
                time = timeSinceBegin
            else:
                time = timeBeforeEnd
            
            self.CurrentEvent.Update(time,runtime)