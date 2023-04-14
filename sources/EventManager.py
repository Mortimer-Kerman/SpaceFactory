# -*- coding: utf-8 -*-
import random
import pygame
import numpy as np

import UiManager
import SaveManager
import TextureManager
import FunctionUtils

from math import copysign

signe = lambda x : copysign(1, x) 

EnnemisList=[]

class Ennemis:
    def __init__(self,co):
        self.pos=co
        self.name="Ennemi"
        self.rotation=1
        
        nearest_pos = [0,0]
        min_dist = float('inf')

        for pos in SaveManager.mainData.items.keys():
            pos=FunctionUtils.strToList(pos)
            pos[0]=float(pos[0])
            pos[1]=float(pos[1])
            dist = FunctionUtils.Distance(pos, self.pos)
            if dist < min_dist:
                min_dist = dist
                nearest_pos = pos
        self.go=list(nearest_pos)
        print(self.go)
    def spawn():
        global EnnemisList
        #a=SaveManager.GetCamPos()
        #a[0]+=random.randint(-100, 100)
        #a[1]+=random.randint(-100, 100)
        a=[0,0]
        EnnemisList.append(Ennemis(a))
    #def __del__(self):
        #global EnnemisList
        #EnnemisList.remove(self)
    def __str__(self):
        return "Ennemis(%s)"%self.pos
    def ia(self,runtime):
        if runtime<=49:
            return
        pos=self.pos
        v=[None,None]
        v[0]=self.go[0]-self.pos[0]
        v[1]=self.go[1]-self.pos[1]
        if v[0]!=0:
            pos[0]+=signe(v[0])
        elif v[1]!=0:
            pos[1]-=signe(v[0])
        else:
            nearest_pos = [random.randint(-100,100),random.randint(-100,100)]
            min_dist = float('inf')

            for pos in SaveManager.mainData.items.keys():
                pos=FunctionUtils.strToList(pos)
                pos[0]=float(pos[0])
                pos[1]=float(pos[1])
                dist = FunctionUtils.Distance(pos, self.pos)
                if dist < min_dist and pos!=self.go:
                    min_dist = dist
                    nearest_pos = pos
            self.go=list(nearest_pos)
            return
        self.pos=pos
    def show(self):
        cam = SaveManager.GetCamPos()
        cam = [cam[0],cam[1]]
        zoom = SaveManager.GetZoom()
        cam[0] += UiManager.width / 2
        cam[1] += UiManager.height / 2
        if not (-cam[0]+UiManager.width+200>=self.pos[0]*zoom>=-cam[0]-200 and -cam[1]+UiManager.height+200>=self.pos[1]*zoom>=-cam[1]-200):#si l'objet n'est pas visible
            return#quitter la fonction
        UiManager.screen.blit(pygame.transform.rotate(TextureManager.GetTexture(self.name, zoom),90*self.rotation), (self.pos[0]*zoom+cam[0], self.pos[1]*zoom+cam[1]))#afficher
class Events:
    def __init__(self):
        self.isEventHappening = False
        self.lastEvent=0
        self.runtime=0
        self.nextEvent = self.lastEvent + 0#random.randint(9900,90000)
    def LaunchEvent(self):
        self.runtime+=1
        if self.nextEvent<self.runtime and not self.isEventHappening:
            self.nextEvent = self.nextEvent + 0#random.randint(9900,90000)
            self.isEventHappening = True
            Ennemis.spawn()