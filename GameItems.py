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

import pygame

menuElements=["foreuse","tapis","stockage","trieur","jonction","pont","four","market"]#éléments du menu de sélection

allTransportableItems={"or":(219, 180, 44),"cuivre":(196, 115, 53),"charbon":(0,10,0),"m1":(78, 100, 110)}

Anim=1

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
        self.metadata["trieur_choice"]="or"
        self.metadata["biginv"]=self.metadata.get("biginv",[])
        giveTo={"foreuse":[1,1,1,1],"0":[1,0,0,0],"2":[0,1,0,0],"1":[0,0,1,0],"3":[0,0,0,1],"stockage":[1,1,1,1]}#[up down left right]
        self.rotation=SaveManager.GetRotation()
        if name in ["tapis","jonction","trieur"]:
            name=str(self.rotation)
        self.giveto=giveTo.get(name,[0,0,0,0])
        if self.name == "trieur":
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
        
        order = 0 if self.name in ["tapis","trieur"] else 2
        
        AddToRender(order,lambda:UiManager.screen.blit(pygame.transform.rotate(TextureManager.GetTexture(self.name, zoom),90*self.rotation), (self.pos[0]*zoom+cam[0], self.pos[1]*zoom+cam[1])))#afficher
        
        #UiManager.place_text(str(self.metadata.get("inv",None)),self.pos[0]*zoom+cam[0], self.pos[1]*zoom+cam[1],20,(255,0,0))
        
        if self.name in ["tapis","trieur"]:
            col=allTransportableItems
            a=col.get(self.metadata.get("inv",None),False) if self.name=="tapis" else col.get(self.metadata.get("trieur_choice",None),(255,0,0))
            #b={"tapis Nord":([0,-1],[1/4,1/2,3/4,1/2,1/4,1/2,1/4,0]),"tapis Sud":([0,1],[1/4,1/2,3/4,1/2,1/4,1/2,1/4,0]),"tapis Ouest":([-1,0],[1/4,1/2,1/4,0,1/4,1/2,3/4,1/2]),"tapis Est":([1,0],[1/4,1/2,1/4,0,1/4,1/2,3/4,1/2])}
            #b=[([0,-1],[1/4,1/2,3/4,1/2,1/4,1/2,1/4,0]),([1,0],[0,1/4,0,-1/4,1/4,1/2,3/4,1/2]),([0,1],[1/4,1/2,3/4,1/2,1/4,1/2,1/4,0]),([-1,0],[3/4,1/2,3/4,1,1/4,1/2,3/4,1/2])]
            #b,ca=b[self.rotation]# if runtime<40 else (0,0)
            
            if a:
                renderOffset = (0,0)
                if Anim and self.name=="tapis":

                    item=self.GetItemToGive()
                    renderOffset = (0,-runtime/50)
                    if item is None:
                        renderOffset=(0,0)
                    else:
                        if item.metadata.get("inv",None) is not None:#si l'item n'a rien dans son inventaire
                            renderOffset=(0,0)

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
        if self.name!="trieur":
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
        else:
            a=self.metadata.get("trieur_choice")==self.metadata.get("inv")
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
        return item
    
    def Give(self):
        if self.metadata.get("g",False):
            return
        if self.name=="foreuse" and self.metadata.get("inv",None) is None:
            if self.metadata.get("minerais", None) is None:
                self.metadata["minerais"]=Minerais.Type(self.pos[0],self.pos[1])
                if self.metadata["minerais"] is False:self.metadata["minerais"]=None
            self.metadata["inv"]=self.metadata["minerais"]
        if self.name=="stockage":
            self.metadata["biginv"]=self.metadata.get("biginv",[])
            if self.AddToInv(self.metadata.get("inv",None)):
                self.metadata["inv"]=None
        if self.name=="market" and self.metadata.get("inv",None) is not None:
            MarketManager.Sell(self.metadata["inv"])
        
        item=self.GetItemToGive()
        if item is not None:
            if item.metadata.get("inv",None) is None:#si l'item n'a rien dans son inventaire
                if self.name=="stockage":
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
        self.metadata["g"]=1
        if self.name=="jonction" and list(self.metadata.get("last",[]))==list(giver.pos):
            self.metadata["last"]=[]
        else:
            self.metadata["last"]=list(giver.pos)
            if self.metadata.get("inv",None) is None:
                self.metadata["inv"]=inv
                giver.metadata["inv"]=None
    
    def edit(self,a):
        if self.name == "trieur":self.metadata["trieur_choice"]=a[0][0]
    
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

current=[]#liste des minerais affichés
class Minerais:
    """
    Toutes les fonctions relatives aux Minerais
    """
    def SpawnAllScreen():
        """
        Apparition des minerais sur tout l'écran
        """
        cam = SaveManager.GetCamPos()
        cam = [cam[0],cam[1]]
        zoom = SaveManager.GetZoom()
        cam[0] += UiManager.width / 2
        cam[1] += UiManager.height / 2
        for x in range(int((0-cam[0])//zoom),int((UiManager.width+cam[0])//zoom)):
            for y in range(int((0-cam[1])//zoom),int((UiManager.height+cam[1])//zoom)):
                Minerais.Place(x,y)
    def SpawnBorder():
        """
        Ne fais spawn les minerais que sur les bordures
        """
        cam = SaveManager.GetLastCamPos()
        zoom = SaveManager.GetZoom()
        cam[0] += UiManager.width / 2
        cam[1] += UiManager.height / 2
        for x in range(int((0-cam[0])//zoom)-1,int((UiManager.width+cam[0])//zoom)+1):
            Minerais.Place(x,int((0-cam[1])//zoom))
            Minerais.Place(x,int((UiManager.height+cam[1])//zoom))
        for y in range(int((0-cam[1])//zoom)-1,int((UiManager.height+cam[1])//zoom)+1):
            Minerais.Place(int((0-cam[0])//zoom),y)
            Minerais.Place(int((UiManager.width+cam[0])//zoom),y)
        #retirer les minerais non affichés (loin du joueur)
        for i in current:
            if not (-cam[0]+UiManager.width+9000>=i[0]*zoom>=-cam[0]-9000 and -cam[1]+UiManager.height+9000>=i[1]*zoom>=-cam[1]-9000):
                current.remove(i)
        

    def Place(x,y):
        """
        Place le minerais selon son type
        """
        cam = SaveManager.GetCamPos()
        cam = [cam[0],cam[1]]
        zoom = SaveManager.GetZoom()
        cam[0] += UiManager.width / 2
        cam[1] += UiManager.height / 2
        a=Minerais.Type(x,y)
        if a:
            if [x,y,a] not in current:current.append([x,y,a])
            UiManager.screen.blit(TextureManager.GetTexture(a, zoom), (x*zoom+cam[0], y*zoom+cam[1]))

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
        random.seed(x*y*se+x+y+se+x)#la graine
        r=3#plus r est grand, moins les minerais spawneront
        if random.randint(0,60*r)==40:
            return "charbon"
        elif random.randint(0,80*r)==40:
            return "cuivre"
        elif random.randint(0,100*r)==10:
            return "or"
        elif random.randint(0,120*r)==50:
            return "m1"
        else:
            return False
        
    def Clear():
        """
        Efface tous les minerais
        """
        current.clear()

doc={
    "foreuse":{"c":{"cuivre":50}},
     "tapis":{"c":{"cuivre":10}},
     "stockage":{"c":{"cuivre":100}},
     "jonction":{"c":{"cuivre":20}},
     "trieur":{"c":{"cuivre":20,"or":10}},
     "market":{"c":{"m1":50,"cuivre":50,"or":10}},
     "delete":{},
     "charbon":{"g":1},
     "cuivre":{"g":2},
     "or":{"g":5},
     "m1":{"g":10},
     #objets du shop
     "téléporteur":{"c":{"coins":100},"s":1}
     }
def getDescription(type):
    loc = L.GetLoc("GameItems.d." + type)
    
    if loc == "GameItems.d." + type:
        loc = L.GetLoc("GameItems.d.error")
    
    UiManager.Popup(loc)