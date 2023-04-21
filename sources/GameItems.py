# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 18:05:51 2023

@author: Thomas Sartre et François Patinec-Haxel
"""
#importation des bibliothèques
import SaveManager
import UiManager
import MarketManager
import TextureManager
import random
import Localization as L
import HelpMenu
import AudioManager
import FunctionUtils
import PlanetGenerator
import EventManager
import SessionManager

import numpy as np

import pygame

menuElements=["Drill","ConveyorBelt","Storage","Sorter","Junction","Bridge","Furnace","Market","CopperWall","Turret","NanoFabricator","Synthetron"]#éléments du menu de sélection

allTransportableItems={"Gold":(219, 180, 44),"Copper":(196, 115, 53),"Coal":(0,10,0),"M1":(78, 100, 110),"M2":(78,130,110),"MeltedCopper":(255,0,0),"NanoM1":(50,10,110),"PlasmaGold":(220,170,44),"SyntheticGold":(230,130,50)}

Anim=1

TeleportPoint=[]

craft={
    #id_block:{"c":(item 1, item 2),"r":résultat}
    "Furnace":{"c":("Copper","Coal"),"r":"MeltedCopper"},
    "MolecularAssembler":{"c":("M1","Gold"),"r":"M2"},
    "NanoFabricator":{"c":("M1","MeltedCopper"),"r":"NanoM1"},
    "Synthetron":{"c":("Copper","Gold"),"r":"SyntheticGold"},
    "QuantumFurnace": {"c":("Copper","NanoM1"),"r":"CopperM1"},
    "PlasmaForge": {"c":("M2","SyntheticGold"),"r":"PlasmaGold"},
    "GravityManipulator": {"c":("M2","PlasmaGold"),"r":"GravitonCore"}

}

Laser={}

RenderQueues = {}
def AddToRender(order:int,action):
    if not order in RenderQueues:
        RenderQueues[order] = []
    RenderQueues[order].append(action)
def ExecuteRender():
    for queue in sorted(RenderQueues):
        for action in RenderQueues[queue]:
            action()
    RenderQueues.clear()

class Item:
    """
    Objet Item
    """
    def __init__(self,name:str,pos:tuple,metadata={}):
        """
        Définition de l'objet
        """
        self.name=name
        self.pos=pos
        self.metadata=metadata
        self.metadata["sorter_choice"]="Gold"
        self.metadata["biginv"]=self.metadata.get("biginv",[])
        giveTo={"Drill":[1,1,1,1],"0":[1,0,0,0],"2":[0,1,0,0],"1":[0,0,1,0],"3":[0,0,0,1],"Storage":[1,1,1,1],"Junction":[1,1,1,1],"Bridge":[1,1,1,1]}#[up down left right]

        self.rotation=SaveManager.GetRotation()
        if name in ["ConveyorBelt","Sorter"]:
            name=str(self.rotation)
        self.giveto=giveTo.get(name,[0,0,0,0])
        if self.name in list(craft.keys()):
            self.giveto=[1,1,1,1]
        if self.name == "Sorter":
            if 1 in self.giveto[0:2]:
                self.giveto[0]*=2
                self.giveto[1]*=2
                self.giveto[2]=1
                self.giveto[3]=1
            elif 1 in self.giveto[2:4]:
                self.giveto[0]=1
                self.giveto[1]=1
                self.giveto[2]*=2
                self.giveto[3]*=2
        if self.name=="Teleporter":
            TeleportPoint.append(self.pos)
        if self.name == "CopperWall":
            self.metadata["pv"]=500
    
    def ReadDictRepresentation(DictRepresentation:dict):
        """
        lecture d'un dictionaire
        """
        item = Item(None,None)
        item.__dict__ = DictRepresentation
        return item
    
    def Display(self,runtime):
        """
        Affichage de l'item
        """
        self.metadata["g"]=0
        
        cam = SaveManager.GetCamPos()
        cam = [cam[0],cam[1]]
        zoom = SaveManager.GetZoom()
        cam[0] += UiManager.width / 2
        cam[1] += UiManager.height / 2
        if not (-cam[0]+UiManager.width+200>=self.pos[0]*zoom>=-cam[0]-200 and -cam[1]+UiManager.height+200>=self.pos[1]*zoom>=-cam[1]-200):#si l'objet n'est pas visible
            return#quitter la fonction
        
        order = 0 if self.name in ["ConveyorBelt","Sorter"] else 2
        
        AddToRender(order,lambda:UiManager.screen.blit(pygame.transform.rotate(TextureManager.GetTexture(self.name, zoom),90*self.rotation), (self.pos[0]*zoom+cam[0], self.pos[1]*zoom+cam[1])))#afficher
        
        if not self.metadata.get("pv",100):
            AddToRender(order,lambda:UiManager.screen.blit(pygame.transform.rotate(TextureManager.GetTexture("Broken", zoom),90*self.rotation), (self.pos[0]*zoom+cam[0], self.pos[1]*zoom+cam[1])))#afficher
            return
        if self.name == "Drill" and runtime == 0:
            AudioManager.PlaySound("Drill",self.pos)
        
        if self.name in ["ConveyorBelt","Sorter"]:
            col=allTransportableItems
            a=col.get(self.metadata.get("inv",None),False) if self.name=="ConveyorBelt" else col.get(self.metadata.get("sorter_choice",None),(255,0,0))
              
            if a:
                renderOffset = (0,0)
                if Anim and self.name=="ConveyorBelt":
                    
                    item=self.GetItemToGive()
                    renderOffset = (0,-runtime/50)
                    moving = True
                    if item is None:
                        renderOffset=(0,0)
                        moving = False
                    else:
                        if item.metadata.get("inv",None) is not None:#si l'item n'a rien dans son inventaire
                            renderOffset=(0,0)
                            moving = False

                    if moving and runtime == 0:
                        AudioManager.PlaySound("ConveyorBelt",self.pos)

                    if self.rotation == 1:
                        renderOffset = (renderOffset[1],-renderOffset[0])
                    elif self.rotation == 2:
                        renderOffset = (-renderOffset[0],-renderOffset[1])
                    elif self.rotation == 3:
                        renderOffset = (-renderOffset[1],renderOffset[0])

                renderOffset = (renderOffset[0]*zoom,renderOffset[1]*zoom)            
                AddToRender(1,lambda: pygame.draw.polygon(UiManager.screen, a, [(self.pos[0]*zoom+cam[0]+1/2*zoom+renderOffset[0],
                                                                                 self.pos[1]*zoom+cam[1]+1/4*zoom+renderOffset[1]),
                                                                                (self.pos[0]*zoom+cam[0]+3/4*zoom+renderOffset[0],
                                                                                 self.pos[1]*zoom+cam[1]+1/2*zoom+renderOffset[1]),
                                                                                (self.pos[0]*zoom+cam[0]+1/2*zoom+renderOffset[0],
                                                                                 self.pos[1]*zoom+cam[1]+3/4*zoom+renderOffset[1]),
                                                                                (self.pos[0]*zoom+cam[0]+1/4*zoom+renderOffset[0],
                                                                                 self.pos[1]*zoom+cam[1]+1/2*zoom+renderOffset[1])]))
            
    def GetItemToGive(self):
        g=self.giveto
        item=None
        if not self.name in ["Sorter","Bridge"]:
                if g[0]:
                    item=SaveManager.GetItemAtPos((self.pos[0],self.pos[1]-1))#on récupère l'item du dessus
                    if item is not None:
                        if item.giveto==[0,1,0,0] or item.metadata.get("inv",None) is not None:item=None
                if g[1] and item is None:
                    item=SaveManager.GetItemAtPos((self.pos[0],self.pos[1]+1))#on récupère l'item du dessous
                    if item is not None:
                        if item.giveto==[1,0,0,0] or item.metadata.get("inv",None) is not None:item=None
                if g[2] and item is None:
                    item=SaveManager.GetItemAtPos((self.pos[0]-1,self.pos[1]))#on récupère l'item de gauche
                    if item is not None:
                        if item.giveto==[0,0,0,1] or item.metadata.get("inv",None) is not None:item=None
                if g[3] and item is None:
                    item=SaveManager.GetItemAtPos((self.pos[0]+1,self.pos[1]))#on récupère l'item de droite
                    if item is not None:
                        if item.giveto==[0,0,1,0] or item.metadata.get("inv",None) is not None:item=None
        elif self.name=="Sorter":
            a=self.metadata.get("sorter_choice")==self.metadata.get("inv")
            if ((g[0]==2 and a) or (g[0]==1 and not a)) and item is None:
                item=SaveManager.GetItemAtPos((self.pos[0],self.pos[1]-1))#on récupère l'item du dessus
                if item is not None:
                    if item.giveto==[0,1,0,0] or item.metadata.get("inv",None) is not None:item=None
            if ((g[1]==2 and a) or (g[1]==1 and not a)) and item is None:
                item=SaveManager.GetItemAtPos((self.pos[0],self.pos[1]+1))#on récupère l'item du dessous
                if item is not None:
                    if item.giveto==[1,0,0,0] or item.metadata.get("inv",None) is not None:item=None
            if ((g[2]==2 and a) or (g[2]==1 and not a)) and item is None:
                item=SaveManager.GetItemAtPos((self.pos[0]-1,self.pos[1]))#on récupère l'item de gauche
                if item is not None:
                    if item.giveto==[0,0,0,1] or item.metadata.get("inv",None) is not None:item=None
            if ((g[3]==2 and a) or (g[3]==1 and not a)) and item is None:
                item=SaveManager.GetItemAtPos((self.pos[0]+1,self.pos[1]))#on récupère l'item de droite
                if item is not None:
                    if item.giveto==[0,0,1,0] or item.metadata.get("inv",None) is not None:item=None
        elif self.name=="Bridge":
            if len(self.metadata.get("last",self.pos))==2:
                a=list(self.metadata.get("last",self.pos))
                a[0]=FunctionUtils.signe(self.pos[0]-a[0]) if self.pos[0]-a[0]!=0 else 0
                a[1]=FunctionUtils.signe(self.pos[1]-a[1]) if self.pos[1]-a[1]!=0 else 0
                item=SaveManager.GetItemAtPos((self.pos[0]+a[0],self.pos[1]+a[1]))#on récupère l'item du
                if item is not None:
                    if item.metadata.get("inv",None) is not None:item=None
        return item
    
    def Give(self):
        global Laser
        if not self.metadata.get("pv",100):
            return
        if self.metadata.get("g",0):
            return
        if self.name=="Turret" and self.IsInInv("Gold")!="NotIn":
            for c,a in enumerate(EventManager.EnnemisList):
                if self.pos[0]-10<a.pos[0]<self.pos[0]+10 and self.pos[1]+10>a.pos[1]>self.pos[1]-10:
                    Laser[str(self.pos)]=lambda:pygame.draw.polygon(UiManager.screen, (255, 0, 0), (UiManager.WorldPosToScreenPos(self.pos),UiManager.WorldPosToScreenPos(a.pos),(UiManager.WorldPosToScreenPos(a.pos)[0]-20,UiManager.WorldPosToScreenPos(a.pos)[1]-20)))
                    AudioManager.PlaySound("laser",self.pos)
                    a.pv-=5
                    self.GetFromInv("Gold")
                    if a.pv<=0:
                        del EventManager.EnnemisList[c]
                        del UiManager.UIelements["ennemi"+str(c)]
                        AudioManager.PlaySound("Explosion",self.pos)#jouer le son d'explosion
                else:
                    Laser[str(self.pos)]=lambda:None
        if self.name=="Drill" and self.metadata.get("inv",None) is None:
            if self.metadata.get("ores", None) is None:
                self.metadata["ores"]=Minerais.Type(self.pos[0],self.pos[1])
                if self.metadata["ores"] is False:self.metadata["ores"]=None
            self.metadata["inv"]=self.metadata["ores"]
        if self.name in ["Storage","Turret"]+list(craft.keys()):
            self.metadata["biginv"]=self.metadata.get("biginv",[])
            if self.AddToInv(self.metadata.get("inv",None)):
                self.metadata["inv"]=None
        if self.name=="Market" and self.metadata.get("inv",None) is not None:
            MarketManager.Sell(self.metadata["inv"])
            self.metadata["inv"]=None
        if self.name in list(craft.keys()):
            c=craft[self.name]
            if all(self.IsInInv(i)!="NotIn" for i in c["c"]):
                if all(self.GetFromInv(i) for i in c["c"]):
                    self.metadata["inv"]=c["r"]
        
        item=self.GetItemToGive()
        if item is not None:
            if item.metadata.get("inv",None) is None:#si l'item n'a rien dans son inventaire
                if self.name=="Storage":
                    a=self.IsInInv(None)
                    if a!="NotIn":
                        del self.metadata["biginv"][a]
                    try:
                        a=self.metadata["biginv"][0]["n"]
                    except:
                        a=None
                    item.Obtain(a,self)
                    if a is not None:
                        self.GetFromInv(a)
                else:
                    item.Obtain(self.metadata.get("inv",None),self)
                    
    def Obtain(self,inv,giver):
        if not self.metadata.get("pv",100):
            return
        self.metadata["g"]=1
        if self.name in ["Junction","Bridge"]+list(craft.keys()) and list(self.metadata.get("last",[]))==list(giver.pos):
            self.metadata["last"]=[]
        else:
            self.metadata["last"]=list(giver.pos)
            if self.metadata.get("inv",None) is None:
                self.metadata["inv"]=inv
                giver.metadata["inv"]=None
    
    def edit(self,a):
        if self.name == "Sorter":self.metadata["sorter_choice"]=a[0][0]
        if self.name == "Teleporter":
            pos=TeleportPoint[a[1]]
            SaveManager.SetCamPos(pos)
    
    def IsInInv(self,a,p=0):
        for i,e in enumerate(self.metadata["biginv"]):
            if e.get("n",False)==a:
                if e["m"]+1<100 or p:
                    return i
            if e.get("n",None) is None:
                del self.metadata["biginv"][i]
        return "NotIn"

    def AddToInv(self,d):
        a=self.IsInInv(d)
        if a!="NotIn":
            self.metadata["biginv"][a]["m"]+=1
            return True
        if len(self.metadata["biginv"])>=25:
            return False
        else:
            self.metadata["biginv"]+=[{"n":d,"m":1}]
            return True
    def GetFromInv(self,d):
        a=self.IsInInv(d,1)
        if a!="NotIn":
            self.metadata["biginv"][a]["m"]-=1
            if self.metadata["biginv"][a]["m"]==0:
                del self.metadata["biginv"][a]
            return True
        else:
            return False



current = []  # liste des minerais affichés
extrasMinerais = {}# dictionnaire des minerais autres que ceux attribués

class Minerais:
    """
    Toutes les fonctions relatives aux minerais
    """

    def SpawnAllScreen():
        """
        Fait apparaître des minerais sur tout l'écran
        """
        pos1 = UiManager.ScreenPosToWorldPos((0,0))
        pos2 = UiManager.ScreenPosToWorldPos((UiManager.width,UiManager.height))
        for x in range(int(pos1[0]),int(pos2[0])+1):
            for y in range(int(pos1[1]),int(pos2[1])+1):
                Minerais.Place(x, y)

    def SpawnBorder(wideBorder:bool=False):
        """
        Fait apparaître des minerais sur les bords de l'écran
        """
        
        pos1 = list(UiManager.ScreenPosToWorldPos((0,0)))
        pos1[0] = int(pos1[0])-1
        pos1[1] = int(pos1[1])-1
        pos2 = list(UiManager.ScreenPosToWorldPos((UiManager.width,UiManager.height)))
        pos2[0] = int(pos2[0])+1
        pos2[1] = int(pos2[1])+1
        
        if wideBorder:
            for x in range(pos1[0],pos2[0]+1):
                for y1 in range(0,5):
                    Minerais.Place(x, pos1[1]+y1)
                    Minerais.Place(x, pos2[1]-y1)
            for y in range(pos1[1],pos2[1]+1):
                for x1 in range(0,5):
                    Minerais.Place(pos1[0]+x1, y)
                    Minerais.Place(pos2[0]-x1, y)
        else:
            for x in range(pos1[0],pos2[0]+1):
                Minerais.Place(x, pos1[1])
                Minerais.Place(x, pos2[1])
            for y in range(pos1[1],pos2[1]+1):
                Minerais.Place(pos1[0], y)
                Minerais.Place(pos2[0], y)
                
        # retirer les minerais non affichés (loin du joueur)
        for i in current:
            if not ((pos1[0] - 9000 < i[0] < pos2[0] + 9000) and 
                    (pos1[1] - 9000 < i[1] < pos2[1] + 9000)):
                current.remove(i)

    def Place(x, y):
        """
        Place le minerais selon son type
        """
        cam = SaveManager.GetCamPos()
        cam = [cam[0], cam[1]]
        zoom = SaveManager.GetZoom()
        cam[0] += UiManager.width / 2
        cam[1] += UiManager.height / 2
        a = Minerais.Type(x, y)
        if a:
            if [x, y, a] not in current:
                current.append([x, y, a])
            UiManager.screen.blit(TextureManager.GetTexture(a, zoom), (x * zoom + cam[0], y * zoom + cam[1]))


    def PlaceFromCurrent(a):
        """
        Placement depuis current (le type de minerais est connu)
        """
        cam = SaveManager.GetCamPos()
        cam = [cam[0],cam[1]]
        zoom = SaveManager.GetZoom()
        cam[0] += UiManager.width / 2
        cam[1] += UiManager.height / 2
        (x,y,a)=a
        UiManager.screen.blit(TextureManager.GetTexture(a, zoom), (x*zoom+cam[0], y*zoom+cam[1]))
    def Type(x,y):
        """
        Renvoie le type de minerais, si ce n'est pas un minerais, renvoie False
        """
        se=SaveManager.GetSeed()
        x=int(x)
        y=int(y)
        random.seed(x*y*se+x+y+se+x)#Calcul d'une graine pour l'aléatoire en fonction de la position et de la graine de la sauvegarde
        r=3#plus r est grand, moins les minerais apparaîtront
        if (x,y) in extrasMinerais.keys():
            return extrasMinerais[(x,y)]
        if not SaveManager.IsPosWet((x,y)):
            if random.randint(0,60*r)==40:
                return "Coal"
            elif random.randint(0,80*r)==40:
                return "Copper"
            elif random.randint(0,100*r)==10:
                return "Gold"
            elif random.randint(0,120*r)==50:
                return "M1"
            
        return False
        
        
    def Clear():
        """
        Efface tous les minerais
        """
        current.clear()
    def ForceSpawn(pos,type):
        """
        Permet de forcer l'apparition d'un minerai avec un type donné
        """
        global extrasMinerais
        extrasMinerais[tuple(pos)]=type
        Minerais.Place(*pos)

doc={
    "Drill":{"c":{"Copper":50}},
     "ConveyorBelt":{"c":{"Copper":10}},
     "Storage":{"c":{"Copper":100}},
     "Junction":{"c":{"Copper":20}},
     "Bridge":{"c":{"Copper":30,"Gold":20}},
     "Furnace":{"c":{"Copper":30,"Gold":80}},
     "Sorter":{"c":{"Copper":20,"Gold":10}},
     "Market":{"c":{"M1":50,"Copper":50,"Gold":10}},
     "CopperWall":{"c":{"MeltedCopper":50,"Copper":40}},
     "Turret":{"c":{"Copper":50,"Gold":50,"M1":20}},
     "NanoFabricator":{"c":{"Gold":20,"MeltedCopper":50}},
     "Coal":{"g":1},
     "Copper":{"g":2},
     "Gold":{"g":5},
     "M1":{"g":10},
     "MeltedCopper":{"g":8},
     "PlasmaGold":{"g":50}
     }
def getDescription(type):
    HelpMenu.Open(type)
    """
    loc = L.GetLoc("Items.d." + type)
    
    if loc == "Items.d." + type:
        loc = L.GetLoc("Items.d.error")
    
    UiManager.Popup(loc)
    """

def getPrice(type):
    #UiManager.Popup(str(list(doc.get(type,{}).get("c",{}).items())))
    return list(doc.get(type,{}).get("c",{}).items())
