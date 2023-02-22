# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 18:05:51 2023

@author: 29ray
"""
#importation des bibliothèques
import SaveManager
import UiManager
import TextureManager
import random

menuElements=["foreuse","c","no","menu_icon","copper","or3"]#éléments du menu de séléction

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
    
    def ReadDictRepresentation(DictRepresentation:dict):
        """
        lecture d'un dictionaire
        """
        item = Item(None,None)
        item.__dict__ = DictRepresentation
        return item
    
    def Display(self):
        """
        Affichage de l'item
        """
        cam = SaveManager.GetCamPos()
        cam = [cam[0],cam[1]]
        zoom = SaveManager.GetZoom()
        cam[0] += UiManager.width / 2
        cam[1] += UiManager.height / 2
        if not (-cam[0]+UiManager.width+200>=self.pos[0]*zoom>=-cam[0]-200 and -cam[1]+UiManager.height+200>=self.pos[1]*zoom>=-cam[1]-200):#si l'objet n'est pas visible
            return#quitter la fonction
        UiManager.screen.blit(TextureManager.GetTexture(self.name, zoom), (self.pos[0]*zoom+cam[0], self.pos[1]*zoom+cam[1]))#afficher
        UiManager.place_text(str(self.metadata.get("inv",None)),self.pos[0]*zoom+cam[0], self.pos[1]*zoom+cam[1],20,(255,0,0))
    
    def Give(self):
        giveTo={"foreuse":[1,1,1,1],"c":[0,1,0,0],"stockage":[1,1,1,1]}#[up down left right]
        if self.name=="foreuse" and self.metadata.get("inv",None) is None:
            #if self.metadata.get("minerais", None) is None:
            self.metadata["minerais"]=Minerais.Type(self.pos[0],self.pos[1])
            if self.metadata["minerais"] is False:self.metadata["minerais"]=None
            self.metadata["inv"]=self.metadata["minerais"]
        
        g=giveTo.get(self.name,[0,0,0,0])
        item=None
        if g[0]:
            item=SaveManager.GetItemAtPos((self.pos[0],self.pos[1]+1))#on récupère l'item du dessus
        if g[1] and item is None:
            item=SaveManager.GetItemAtPos((self.pos[0],self.pos[1]-1))#on récupère l'item du dessous
        if g[2] and item is None:
            item=SaveManager.GetItemAtPos((self.pos[0]-1,self.pos[1]))#on récupère l'item de gauche
        if g[3] and item is None:
            item=SaveManager.GetItemAtPos((self.pos[0]+1,self.pos[1]))#on récupère l'item de droite
        
        if item is not None:
            if item.metadata.get("inv",None) is None:#si l'item n'a rien dans son inventaire
                item.metadata["inv"]=self.metadata.get("inv",None)
                self.metadata["inv"]=None#on vide l'inventaire

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
    def SpawnBorder(camOffset):
        """
        Ne fais spawn les minerais que sur les bordures
        """
        cam = SaveManager.GetCamPos()
        cam = [cam[0]+camOffset[0],cam[1]+camOffset[1]]
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
            if not (-cam[0]+UiManager.width+1000>=i[0]*zoom>=-cam[0]-1000 and -cam[1]+UiManager.height+1000>=i[1]*zoom>=-cam[1]-1000):
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
        random.seed(x*y*se+x+y+se+x)#la graine
        r=3#plus r est grand, moins les minerais spawneront
        if random.randint(0,60*r)==40:
            return "coal"
        elif random.randint(0,80*r)==40:
            return "copper"
        elif random.randint(0,100*r)==10:
            return "or3"
        elif random.randint(0,120*r)==50:
            return "m1"
        else:
            return False