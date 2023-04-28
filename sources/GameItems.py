# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 18:05:51 2023

@author: Thomas Sartre et François Patinec-Haxel
"""
#importation des bibliothèques
import pygame

import random

import SaveManager
import UiManager
import MarketManager
import TextureManager
import AudioManager
import FunctionUtils
import PlanetGenerator
import EventManager
import Stats
import SettingsManager


menuElements=["Drill","ConveyorBelt","Storage","Sorter","Junction","Bridge","Furnace","Market","CopperWall","Turret","NanoFabricator","Synthetron"]#éléments du menu de sélection

#représentation des items sur un tapis roulant
allTransportableItems={"Gold":(219, 180, 44),"Copper":(196, 115, 53),"Coal":(0,10,0),"M1":(78, 100, 110),"RefinedM1":(68, 90, 100),"M2":(78,130,110),"MeltedCopper":(255,0,0),"MeltedGold":(210,160,50),"NanoM1":(50,10,110),"PlasmaGold":(220,170,44),"SyntheticGold":(230,130,50)}

#Fonction expérimentale de téléportation
TeleportPoint=[]

#Dictionnaire contenant toutes les recettes de crafts
craft={
    #id_block:[{"c":(item 1, item 2),"r":résultat}]
    "Furnace":[{"c":("Copper","Coal"),"r":"MeltedCopper"},{"c":("Gold","Coal"),"r":"MeltedGold"},{"c":("M1","Coal"),"r":"RefinedM1"}],
    "MolecularAssembler":[{"c":("RefinedM1","MeltedGold"),"r":"M2"}],
    "NanoFabricator":[{"c":("RefinedM1","MeltedCopper"),"r":"NanoM1"}],
    "Synthetron":[{"c":("MeltedCopper","MeltedGold"),"r":"SyntheticGold"}],
    "PlasmaForge": [{"c":("M2","SyntheticGold"),"r":"PlasmaGold"}]
}
#Liste des résultats de crafts
craftResults=[]
for j in craft.values():#pour chaque valeur de craft
    for i in list(j):#pour chaque craft de la liste de craft de l'item
        #on ajoute dans la liste le résultat du craft
        craftResults.append(i["r"])
def findCraft(item):
    """
    Renvoie la clé et le craft d'un item
    """
    for key, value in craft.items():
        for j in list(value):
            if item == j["r"]:
                return key,j
    return None

Laser={}#dictionnaire stockant tout les lasers affichés par les tourelles

#Affichage dynamique du rendu
RenderQueues = {}
def AddToRender(order:int,action):
    """Ajout au rendu dynamique"""
    if not order in RenderQueues:
        RenderQueues[order] = []
    RenderQueues[order].append(action)
def ExecuteRender():
    """Lancer le rendu dynamique"""
    for queue in sorted(RenderQueues):
        for action in RenderQueues[queue]:
            #chaque action est stockée via un lambda
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
        #Variables par défaut
        self.name=name
        self.pos=pos
        self.metadata=metadata
        self.metadata["sorter_choice"]="Gold"
        self.metadata["biginv"]=self.metadata.get("biginv",[])
        #Dictionnaire contenant les différents paterne de distribution
        giveTo={"Drill":[1,1,1,1],"0":[1,0,0,0],"2":[0,1,0,0],"1":[0,0,1,0],"3":[0,0,0,1],"Storage":[1,1,1,1],"Junction":[1,1,1,1],"Bridge":[1,1,1,1]}#[up down left right]

        self.rotation=SaveManager.GetRotation()#on récupère la rotation actuelle
        if name in ["ConveyorBelt","Sorter"]:#si le nom est ConveyorBelt ou Sorter
            name=str(self.rotation)#on change le nom comme étant le type précis de la rotation
        self.giveto=giveTo.get(name,[0,0,0,0])#on récupère le paterne de distribution
        if self.name in list(craft.keys()):#si le nom est dans la liste des items servant aux crafts
            self.giveto=[1,1,1,1]
        if self.name == "Sorter":
            #S'il s'agit d'un Sorter, on va mettre en évidence le côté de distribution pour les items choisis
            if 1 in self.giveto[0:2]:#si le paterne correspond pour up/down
                self.giveto[0]*=2
                self.giveto[1]*=2
                self.giveto[2]=1
                self.giveto[3]=1
            elif 1 in self.giveto[2:4]:#si le paterne correspond pour left/right
                self.giveto[0]=1
                self.giveto[1]=1
                self.giveto[2]*=2
                self.giveto[3]*=2
        if self.name=="Teleporter":#si l'item est un Teleporter
            TeleportPoint.append(self.pos)#on ajoute ses coordonnées aux points de téléportation
        if self.name == "CopperWall":#si il s'agit d'un mur de cuivre
            self.metadata["pv"]=500#on mets les pv à 500
    
    def ReadDictRepresentation(DictRepresentation:dict):
        """
        lecture d'un dictionaire
        """
        item = Item(None,None)
        item.__dict__ = DictRepresentation
        return item
    
    def Update(self,runtime):
        """
        Mise à jour de l'item
        """
        self.metadata["g"]=0#Variable pour savoir si l'item a reçu/donné / sert à ralentir la transition entre items
        
        cam = SaveManager.GetCamPos()
        cam = [cam[0],cam[1]]
        zoom = SaveManager.GetZoom()
        cam[0] += UiManager.width / 2
        cam[1] += UiManager.height / 2
        if not (-cam[0]+UiManager.width+200>=self.pos[0]*zoom>=-cam[0]-200 and -cam[1]+UiManager.height+200>=self.pos[1]*zoom>=-cam[1]-200):#si l'objet n'est pas visible
            return#quitter la fonction
        
        order = 0 if self.name in ["ConveyorBelt","Sorter"] else 2#S'il s'agit d'un ConveyorBelt ou d'un Sorter, ordre=0, sinon 2
        
        #ajout au rendu dynamique
        AddToRender(order,lambda:UiManager.screen.blit(pygame.transform.rotate(TextureManager.GetTexture(self.name, zoom),90*self.rotation), (self.pos[0]*zoom+cam[0], self.pos[1]*zoom+cam[1])))#afficher
        #si les pvs sont à 0, on ajoute une texture cassée
        if not self.metadata.get("pv",100):
            AddToRender(order,lambda:UiManager.screen.blit(pygame.transform.rotate(TextureManager.GetTexture("Broken", zoom),90*self.rotation), (self.pos[0]*zoom+cam[0], self.pos[1]*zoom+cam[1])))#afficher
            return
        if self.name == "Drill" and runtime == 0:#s'il s'agit d'une foreuse, jouer le son associé
            AudioManager.PlaySound("Drill",self.pos)
        
        #Si l'item est un tapis roulant ou un trieur...
        if self.name in ["ConveyorBelt","Sorter"]:
            #On récupère l'item dans l'inventaire temporaire
            itemToDisplay = self.metadata.get("inv",None)
            if self.name == "Sorter":#Si l'objet est un trieur, on récupère l'item dans son menu de choix de tri à la place
                itemToDisplay = self.metadata.get("sorter_choice",None)
            
            if itemToDisplay != None:#si l'item transporté n'est pas none
                renderOffset = (0,0)
                
                #Est-ce que les tapis roulants doivent être détaillés
                niceBelts = SettingsManager.GetSetting("conveyorBeltRender")
                
                item=self.GetItemToGive()#On récupère l'item que l'on veut donner
                if self.name=="ConveyorBelt":#si il s'agit d'un tapis roulant
                    renderOffset = (0,-runtime/50)
                moving = True
                if item is None:#s'il n'y a pas d'item, on ne bouge pas
                    renderOffset=(0,0)
                    moving = False
                else:
                    if item.metadata.get("inv",None) is not None:#si l'item n'a pas rien dans son inventaire
                        renderOffset=(0,0)
                        moving = False
                
                if moving:#Si le tapis roulant bouge...
                    
                    if niceBelts:#Si les tapis roulants doivent être détaillés, on affiche la texture de tapis roulant qui bouge
                        AddToRender(order,lambda:UiManager.screen.blit(pygame.transform.rotate(TextureManager.GetTexture(self.name + "/" + str((runtime//10)%5), zoom),90*self.rotation), (self.pos[0]*zoom+cam[0], self.pos[1]*zoom+cam[1])))
                    
                    if runtime == 0:#Si runtime est à 0, on joue le son du tapis roulant
                        AudioManager.PlaySound("ConveyorBelt",self.pos)
                    
                #calcul des mouvements
                if self.rotation == 1:
                    renderOffset = (renderOffset[1],-renderOffset[0])
                elif self.rotation == 2:
                    renderOffset = (-renderOffset[0],-renderOffset[1])
                elif self.rotation == 3:
                    renderOffset = (-renderOffset[1],renderOffset[0])

                renderOffset = (renderOffset[0]*zoom,renderOffset[1]*zoom)
                
                #affichage des items
                
                #Si les tapis roulants doivent être détaillés...
                if niceBelts:
                    AddToRender(1,lambda:UiManager.screen.blit(TextureManager.GetTexture(itemToDisplay, zoom/2, transportedItem=True), (self.pos[0]*zoom+cam[0]+1/4*zoom+renderOffset[0], self.pos[1]*zoom+cam[1]+1/4*zoom+renderOffset[1])))#afficher
                #Sinon...
                else:
                    #Couleur de l'item à affcher
                    col = allTransportableItems.get(itemToDisplay,(255,255,255))
                    #Rendu
                    AddToRender(1,lambda: pygame.draw.polygon(UiManager.screen, col, [(self.pos[0]*zoom+cam[0]+1/2*zoom+renderOffset[0],
                                                                                     self.pos[1]*zoom+cam[1]+1/4*zoom+renderOffset[1]),
                                                                                    (self.pos[0]*zoom+cam[0]+3/4*zoom+renderOffset[0],
                                                                                     self.pos[1]*zoom+cam[1]+1/2*zoom+renderOffset[1]),
                                                                                    (self.pos[0]*zoom+cam[0]+1/2*zoom+renderOffset[0],
                                                                                     self.pos[1]*zoom+cam[1]+3/4*zoom+renderOffset[1]),
                                                                                    (self.pos[0]*zoom+cam[0]+1/4*zoom+renderOffset[0],
                                                                                     self.pos[1]*zoom+cam[1]+1/2*zoom+renderOffset[1])]))
            
    def GetItemToGive(self):
        """Renvoie l'item à donner"""
        g=self.giveto
        item=None
        if not self.name in ["Sorter","Bridge"]:
            #On vérifie juste en haut, en bas, à gauche, à droite si il y a un item, et que son inventaire est bien vide
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
            #On vérifie juste en haut, en bas, à gauche, à droite si il y a un item, et que son inventaire est bien vide, on ajoute aussi la considération de l'item à transmettre (type du Sorter ou non)
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
            #on calcule juste de l'autre côté du dernier item reçu
            if len(self.metadata.get("last",self.pos))==2:
                a=list(self.metadata.get("last",self.pos))
                a[0]=FunctionUtils.signe(self.pos[0]-a[0]) if self.pos[0]-a[0]!=0 else 0
                a[1]=FunctionUtils.signe(self.pos[1]-a[1]) if self.pos[1]-a[1]!=0 else 0
                item=SaveManager.GetItemAtPos((self.pos[0]+a[0],self.pos[1]+a[1]))#on récupère l'item du
                if item is not None:
                    if item.metadata.get("inv",None) is not None:item=None
        return item
    
    def Give(self):
        """Permet de transmettre un item à une autre machine"""
        global Laser
        if not self.metadata.get("pv",100):#si l'on ne dispose pas de pv, on quitte
            return
        if self.metadata.get("g",0):#si un item a déjà été donné/reçu, on quitter
            return
        if self.name=="Turret" and self.IsInInv("Gold")!="NotIn":
            #Calcul de la tourelle
            for c,a in enumerate(EventManager.EnnemisList):
                if self.pos[0]-10<a.pos[0]<self.pos[0]+10 and self.pos[1]+10>a.pos[1]>self.pos[1]-10:#on cherche une cible proche
                    Laser[str(self.pos)]=lambda:pygame.draw.polygon(UiManager.screen, (255, 0, 0), (UiManager.WorldPosToScreenPos(self.pos),UiManager.WorldPosToScreenPos(a.pos),(UiManager.WorldPosToScreenPos(a.pos)[0]-20,UiManager.WorldPosToScreenPos(a.pos)[1]-20)))
                    AudioManager.PlaySound("laser",self.pos)
                    a.pv-=5
                    self.GetFromInv("Gold")
                    if a.pv<=0:
                        #"tuer" l'ennemi
                        del EventManager.EnnemisList[c]
                        del UiManager.UIelements["ennemi"+str(c)]
                        AudioManager.PlaySound("Explosion",self.pos)#jouer le son d'explosion
                else:
                    Laser[str(self.pos)]=lambda:None
        if self.name=="Drill" and self.metadata.get("inv",None) is None:
            #s'il s'agit d'une foreuse, et que son inventaire est vide
            if self.metadata.get("ores", None) is None:
                self.metadata["ores"]=Minerais.Type(self.pos[0],self.pos[1])#On récupère le type de minerai
                if self.metadata["ores"] is False:self.metadata["ores"]=None#si la foreuse n'est pas sur un minerais, on mets None dans cette variable
            self.metadata["inv"]=self.metadata["ores"]#on ajoute le minerai dans la foreuse
        if self.name in ["Storage","Turret"]+list(craft.keys()):#si l'item est un stockage, tourelle, ou est inclus dans la liste des crafts
            self.metadata["biginv"]=self.metadata.get("biginv",[])
            if self.AddToInv(self.metadata.get("inv",None)):#on ajoute l'item à l'inventaire
                self.metadata["inv"]=None#si tout s'est bian passé, on retire l'item de l'inventaire
        if self.name=="Market" and self.metadata.get("inv",None) is not None:
            #on vends le contenu au market
            MarketManager.Sell(self.metadata["inv"])
            self.metadata["inv"]=None
        if self.name in list(craft.keys()):#si on a un craft associé
            c=craft[self.name]
            for a in c:
                if all(self.IsInInv(i)!="NotIn" for i in a["c"]):
                    if all(self.GetFromInv(i) for i in a["c"]):
                        #si tous les ingrédients du crafts sont dans l'inventaire, on crée un item
                        self.metadata["inv"]=a["r"]
                        break
        
        item=self.GetItemToGive()#on récupère l'item
        if item is not None:#si l'item existe
            if item.metadata.get("inv",None) is None:#si l'item n'a rien dans son inventaire
                if self.name=="Storage":#si self est un stockage
                    a=self.IsInInv(None)#si il y a un objet None dans l'inventaire, on le supprime
                    if a!="NotIn":
                        del self.metadata["biginv"][a]

                    #on récupère, si possible, un item dans l'inventaire
                    try:
                        a=self.metadata["biginv"][0]["n"]
                    except:
                        a=None
                    item.Obtain(a,self)#on demande à l'item d'obtenir
                    if a is not None:
                        self.GetFromInv(a)#on récupère de l'inventaire
                else:
                    item.Obtain(self.metadata.get("inv",None),self)
                    
    def Obtain(self,inv,giver):
        """Obtiens un item"""
        if not self.metadata.get("pv",100):#si l'item est cassé, on quitte
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
        """
        Permet d'éditer l'item
        """
        if self.name == "Sorter":self.metadata["sorter_choice"]=a
        if self.name == "Teleporter":
            pos=TeleportPoint[a[1]]
            SaveManager.SetCamPos(pos)
    
    def IsInInv(self,a,p=0):
        """Est-ce dans l'inventaire de l'item?"""
        for i,e in enumerate(self.metadata["biginv"]):
            if e.get("n",False)==a:
                if e["m"]+1<100 or p:
                    return i
            if e.get("n",None) is None:
                del self.metadata["biginv"][i]
        return "NotIn"

    def AddToInv(self,d):
        """Ajout dans l'inventaire"""
        m1Amount = 0#Quantité de m1 dans l'inventaire
        #Pour chaque slot du grand inventaire...
        for slot in self.metadata["biginv"]:
            #Si le slot contient du m1, on incrémente la quantité de m1 dans l'inventaire de la quantité de m1 dans le slot
            if slot["n"] == "M1":
                m1Amount += slot["m"]
                #Si la quantité de m1 accumulée dépasse la statistique de quantité maximale de m1 stockée...
        if m1Amount > Stats.GetStat("MaxStoredM1"):
            #On modifie la statistique
            Stats.SetStat("MaxStoredM1", m1Amount)
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
        """Récupère un item depuis l'inventaire"""
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
            if a == "Obstacle":
                a = "Obstacles/" + ("Bush" if SaveManager.GetEnvironmentType() == PlanetGenerator.PlanetTypes.EarthLike else "Rock") 
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
        if a == "Obstacle":
            a = "Obstacles/" + ("Bush" if SaveManager.GetEnvironmentType() == PlanetGenerator.PlanetTypes.EarthLike else "Rock") 
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
            elif random.randint(0,50*r)==50:
                if not (x,y) in SaveManager.mainData.clearedObstacles:
                    return "Obstacle"
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
     "Synthetron":{"c":{"NanoM1":50,"Copper":50}},
     "Coal":{"g":1},
     "Copper":{"g":2},
     "Gold":{"g":5},
     "M1":{"g":10},
     "MeltedCopper":{"g":8},
     "PlasmaGold":{"g":50}
     }

def getPrice(type):
    """Récupération du prix de création"""
    return list(doc.get(type,{}).get("c",{}).items())
