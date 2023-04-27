# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 21:18:31 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

#Importation des bibliothèques nécessaires pour la génération
import pygame

import random
import math
from colorsys import hsv_to_rgb
import numpy

import NoiseTools
import FunctionUtils


#Les types de planète fournissent au générateur une direction globale dans sa manière de générer
class PlanetTypes:
    Random = 0
    Dead = 1
    Desertic = 2
    EarthLike = 3

#Paramètres généraux pour la génération des textures: taille de la texture, échelle de bruit, nombre d'octaves et vitesse de transition entre les biomes
TextureSize = 100
Scale = 3
octaves = 2
BiomeLerpSpeed = 0.3

#Paramètres pour la gestion de la lumière
CalculateLight = True
IsSunBehind = False
LightPos = (0.35, 0.35)

#Paramètres pour simuler la sphéricité de la planète en étirant le terrain (expérimental)
CalculateSphericity = False
SphericityFactor = 1


class PlanetaryConditions():
    """
    Permet de générer ou stocker des conditions planétaires pour les passer au générateur
    """
    def __init__(self, **kwargs):
        
        if kwargs.get("template", False):
            self.gravity = 1
            self.pressure = 1
            self.temperature = 15
            self.type = PlanetTypes.EarthLike
            return
        
        seed = kwargs.get("seed", None)
        if seed != None:
            random.seed(seed)
        
        self.gravity = kwargs.get("gravity", random.uniform(0.5, 1.5))
        self.pressure = kwargs.get("pressure", random.uniform(0, 2))
        self.temperature = kwargs.get("temperature", random.uniform(-50, 70))
        if (0.7 < self.gravity < 1.3 and 0.7 < self.pressure < 1.3 and -30 < self.temperature < 50):
            if (random.choice([True,False])):
                self.type = PlanetTypes.EarthLike
            else:
                self.type = PlanetTypes.Desertic
        else:
            self.type = PlanetTypes.Dead


def Generate(conditions = None, Seed = None):
    """
    Génère une texture d'une planète vue depuis l'orbite à partir de conditions spécifiées en entrée
    """
    
    #Si aucune graine n'est donnée en entrée, il faut en prendre une aléatoire
    if Seed == None:
        Seed = random.randint(-10000, 10000)
    
    #On règle le générateur d'aléatoire sur cette graine
    random.seed(Seed)
    
    #Si les conditions planétaires ne sont pas spécifiées, il faut en prendre des aléatoires
    if conditions == None:
        conditions = PlanetaryConditions()
    
    #Préparation de plusieurs variables décrivant des caractéristiques de l'apparence de la planète: Apparence de l'atmosphère, niveau de la mer, taille des calottes polaires...
    DeadPlanetColor = 0#Facteur de couleur des planètes mortes
    AtmosphereColor = 0.5#Teinte HSV de la couleur des atmosphères
    AtmosphereStrengh = 0.2#Force de l'effet d'atmosphère, définit une valeur minimale sous laquelle la visibilité de l'atmosphère ne peut pas descendre
    AtmosphereCoverage = 0.1#Couverture atmosphérique, dit à quelle vitesse l'atmosphère devient visible sur les bords de la planète
    DesertCoverage = 0.2#Couverture du désert. Une valeur de 0 indique une planète sans déserts et une valeur tendant vers 1 recouvre la planète de déserts. Une valeur de 1 provoque des divisions par 0, mais ça n'est jamais choisi par le générateur.
    CloudsStrength = 0.5#Force de l'effet de nuages. Plus la valeur s'approche de 1, plus les nuages sont visibles et étendus.
    SandRedFactor = 0#Facteur de couleur du sable. Une valeur proche de 0 indique un sable jaune/blanc et une valeur proche de 1 indique un sable rouge/orange.
    SeaLevel = 0.5#Niveau de la mer. A 0, aucune mer visible, et à 1, la planète est recouverte d'océans. Sur les planètes mortes, elle définit la taille des mers lunaires.
    PoleCoverage = 0.3#Taille des pôles. Une valeur de 0 ne permet aucune calotte glaciaire, et à 1, les glaces se rejoignent à l'équateur.
    
    #On récupère le type de planète depuis les conditions
    PlanetType = conditions.type
    
    #Si c'est une planète morte...
    if PlanetType == PlanetTypes.Dead:
        #On règle des paramètres de manière aléatoire
        AtmosphereColor = random.uniform(0, 1)
        #Une chance sur deux que la planète possède une atmosphère
        AtmosphereStrengh = random.uniform(0, 0.1) if random.randint(0, 2) == 0 else 0
        DeadPlanetColor = random.uniform(0, 1)
        SeaLevel = random.uniform(0.2, 0.8)
    #Sinon...  
    else:
        #L'atmosphère et le niveau de la mer ne change pas
        AtmosphereColor = 0.5
        AtmosphereStrengh = 0.2
        SeaLevel = 0.5
        #Paramètres aléatoires pour le désert
        DesertCoverage = random.uniform(0, 0.6)
        SandRedFactor = random.uniform(0, 1)
    
    #Si la  planète est désertique...
    if PlanetType == PlanetTypes.Desertic:
        #On règle les paramètres pour simuler un monde désertique
        SeaLevel = random.uniform(0.4, 0.5)
        DesertCoverage = 0.9
        #Explications: Dans ce code, une planète désertique est juste une planète semblable à la terre, mais couverte de déserts.
        #Le même code est donc utilisé pour les deux types, la seule différence réside dans les paramètres du générateur.
        PlanetType = PlanetTypes.EarthLike 
    
    #La force des nuages est proportionelle au niveau de la mer
    CloudsStrength = (SeaLevel - 0.2) * 4 / 3
    #La couverture atmosphérique est proportionelle à la force de l'atmosphère
    AtmosphereCoverage = AtmosphereStrengh / 2
    
    #On calcule un décalage aléatoire. Sans lui, toutes les planètes auraient le même terrain.
    Offset = (random.uniform(-TextureSize, TextureSize),random.uniform(-TextureSize, TextureSize))
    
    #Création d'un facteur pour convertir une position sur la texture en position dans le bruit
    scale = (1 / TextureSize) * Scale
    
    #Ce tableau contiendra la texture de la planète
    pix = []

    #Pour chaque colonne de la texture...
    for y in range(TextureSize):
        #Création d'un tableau pour la colonne
        row = []
        #Pour chaque ligne de la texture...
        for x in range(TextureSize):
            #On calcule la position dans le bruit
            xCoord = x * scale
            yCoord = y * scale
            
            #Distance au centre de la texture entre 0 et 1
            distanceToC = DistanceToCenter(x, y)
            
            #Couleur pour le fond de l'image
            c = (0,0,0)
            
            #Si la distance au centre est inférieure à 0,99...
            if distanceToC < 0.99:
                
                #On calcule la valeur de bruit à cet emplacement
                depth = FractalNoise(xCoord, yCoord, Offset, octaves, distanceToC)
                
                #Si la planète est semblable à la Terre...
                if PlanetType == PlanetTypes.EarthLike:
                    
                    #Calcul de certaines couleurs
                    
                    #Océan: Bleu, et plus l'océan est profond plus le bleu devient noir
                    ocean = (0, 0, depth + SeaLevel)
                    #Herbe: Vert, et plus l'altitude est haute plus le vert est intense
                    grass = (0, depth, 0)
                    #Désert: Interpolation linéaire entre un jaune et un rouge en fonction du facteur de rouge du sable
                    desert = FunctionUtils.lerpcol(((depth * 1) + 0.2, (depth * 0.92) + 0.2, 0.2), (depth, depth / 4, 0), SandRedFactor)
                    #Pôles: Blancheur proportionelle à l'altitude
                    poles = (depth + 0.3, depth + 0.3, depth + 0.3)
                    
                    #Calcul de la distance à l'équateur sur l'image avec 1 aux pôles et 0 à l'équateur. Pour que ça soit vraiment la latitude il ne faudrait pas que la valeur soit absolue.
                    Latitude = abs((x - (TextureSize / 2)) / (TextureSize / 2))

                    #Interpolation linéaire entre le désert et l'herbe d'après une carte de bruit avec un décalage différent et une seule octave, dont les proportions sont régulées par la couverture désertique pour que ses valeurs tendent vers 0 en cas de forte couverture désertique et 1 en cas de faible couverture désertique
                    grass = FunctionUtils.lerpcol(desert, grass, FunctionUtils.clamp01((FractalNoise(xCoord, yCoord, (Offset[0] * 2, Offset[1] * 2), 1, distanceToC) - DesertCoverage) / (1 - DesertCoverage)) / BiomeLerpSpeed)

                    #Interpolation linéaire entre le terrain obtenu et les pôles pour que globalement, plus on est proche des pôles, plus le terrain est blanc
                    grass = FunctionUtils.lerpcol(grass, poles, FunctionUtils.clamp01((Latitude - (1 - PoleCoverage)) / PoleCoverage) / BiomeLerpSpeed)
                    
                    #Si l'altitude est inférieure au niveau de la mer, la couleur de fond devient celle des océans, sinon elle devient celle des terres émergées
                    if depth < SeaLevel:
                        c = ocean
                    else:
                        c = grass
                
                #Si la planète est morte...
                if PlanetType == PlanetTypes.Dead:
                    
                    #Si l'altitude est inférieure au niveau de la mer...
                    if depth < SeaLevel:
                        #On recalcule l'altitude selon une carte de bruit de cratère petite et avec une faible influence
                        depth = depth / 2 + 0.5 + (FractalCraterNoise(xCoord*4, yCoord*4, Offset, distanceToC) / 8)
                    else:
                        #Sinon, on recalcule avec une grande carte de bruit de cratère avec une forte influence
                        depth = depth / 2 + 0.25 + FractalCraterNoise(xCoord, yCoord, Offset, distanceToC)
                    
                    #On définit la couleur en fonction de l'altitude, et du facteur de couleur de la planète morte
                    c = hsv_to_rgb(0.08, DeadPlanetColor, depth/2)
            
            #Couleur pour l'atmosphère
            atm = (0,0,0)
            
            #Si la distance au centre est inférieure à 1 et que la planète a bien une atmosphère...
            if (distanceToC < 1 and AtmosphereCoverage != 0): 
                
                #On calcule la densité locale de l'atmosphère en fonction de la couverture de l'atmosphère et de la distance au centre
                density = (distanceToC - (1 - AtmosphereCoverage)) / AtmosphereCoverage
                #On s'assure qu'elle ne soit pas inférieure à la force de l'atmosphère
                if (density < AtmosphereStrengh):
                    density = AtmosphereStrengh
                #On calcule la couleur finale de l'atmosphère en multipliant la couleur générale de l'atmosphère par la densité locale
                atm = FunctionUtils.multiplycol(hsv_to_rgb(AtmosphereColor, 1, 1), density)
            
            #Couleur pour les nuages
            clouds = (0,0,0)
            
            #Si la distance au centre est inférieure à 1 et que la planète est semblable à la Terre...
            if (distanceToC < 1 and PlanetType == PlanetTypes.EarthLike):
                
                #On calcule la densité locale des nuages selon une petite carte de bruit et la force des nuages
                density = (FractalNoise(xCoord, yCoord, (Offset[0] * 3, Offset[1] * 3), octaves, distanceToC) * 2) - 1 - (0.5 - CloudsStrength)
                #On s'assure que la densité ne passe pas en dessous de 0
                if (density < 0):
                    density = 0
                #La couleur des nuages est simplement un blanc proportionnel à la densité
                clouds = (density, density, density)
            
            #Puissance locale de la lumière
            light = 1
            
            #Si la distance au centre est inférieure à 1 et qu'il faut calculer la lumière...
            if (distanceToC < 1 and CalculateLight):
                #On calcule pour qu'elle soit proportionellle à la distance à la source lumineuse si le soleil est derrière la planète, sinon, inversement proportionelle.
                light = (DistanceToLightSource(x, y) - 0.6) if IsSunBehind else (-DistanceToLightSource(x, y) + 0.8)
                #On s'assure que la puissance de la lumière ne passe pas sous 0
                if (light < 0):
                    light = 0
                #Dernière touche finale
                light *= 2
            #On calcule la couleur finale du pixel: La couleur du terrain plus la couleur de l'atmosphère plus la couleur des nuages, le tout multiplié par la puissance de la lumière
            col = FunctionUtils.multiplycol(FunctionUtils.addcol(FunctionUtils.addcol(c, atm), clouds), light)
            #On ajoute la couleur à la ligne après l'avoir convertie d'un format 0-1 à un format 0-255
            row.append(FunctionUtils.ZeroOneToHexa(col))
        
        #On ajoute la ligne au tableau de l'image
        pix.append(row)
    
    #On crée une nouvelle texture dans laquelle on vient stocker le tableau de pixel (conversion via numpy nécessaire)
    texture = pygame.Surface((TextureSize,TextureSize))
    pygame.surfarray.blit_array(texture, numpy.array(pix))
    
    #On renvoie la texture
    return texture



def DistanceToCenter(x:float, y:float):
    """
    Renvoie la distance au centre de l'image entre 0 et 1
    """
    return FunctionUtils.Distance((x, y), (TextureSize / 2, TextureSize / 2)) / (TextureSize / 2)

def DistanceToLightSource(x:float, y:float):
    """
    Renvoie la distance à la source de lumière entre 0 et 1
    """
    return FunctionUtils.Distance((x, y), (LightPos[0] * TextureSize, LightPos[1] * TextureSize)) / (TextureSize / 1.2)

def DistanceToCenterElliptical(x:float, y:float):
    """
    Retourne la distance au centre selon un ellipse, utile pour dessiner des anneaux
    """
    return (math.pow(x - (TextureSize / 2), 2) / math.pow(TextureSize / 2, 2)) + (math.pow(y - (TextureSize / 2), 2) / math.pow(TextureSize / 6, 2))


def FractalNoise(posX:float, posY:float, offset:tuple, octaves:int, DistanceToC:float):
    """
    Permet de calculer une valeur de bruit fractal avec si besoin un calcul de la sphéricité
    """
    if CalculateSphericity:
        offX = DistanceToC * SphericityFactor
        if posX > TextureSize/2:
            offX = -offX
        offY = DistanceToC * SphericityFactor
        if posY > TextureSize/2:
            offY = -offY
        offset = (offset[0] + offX, offset[1] + offY)
    return NoiseTools.FractalNoise(posX, posY, offset, octaves)


def FractalCraterNoise(posX:float, posY:float, offset:tuple, DistanceToC:float)->float:
    """
    Permet de calculer une valeur de bruit de cratère avec si besoin un calcul de la sphéricité
    """
    if CalculateSphericity:
        offX = DistanceToC * SphericityFactor
        if posX > TextureSize/2:
            offX = -offX
        offY = DistanceToC * SphericityFactor
        if posY > TextureSize/2:
            offY = -offY
        offset = (offset[0] + offX, offset[1] + offY)
    return NoiseTools.FractalCraterNoise(posX, posY, offset)

def RandomSaveName()->str:   

    length = random.randint(4,10)
    consonants = [ "b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "l", "n", "p", "q", "r", "s", "sh", "zh", "t", "v", "w", "x" ]
    vowels = [ "a", "e", "i", "o", "u", "ae", "y" ]
    Name = ""
    b = 0
    while b < length:
    
        Name += random.choice(consonants)
        b += 1
        if b == length:
            break
        Name += random.choice(vowels)
        b += 1
    
    
    suffixes = [ "I", "II", "III", "IV", "V", "Prime", "Alpha", "Beta", "Delta", "Zeta", "Omega", "Sigma", "Minoris", "Majoris" ]
    
    if random.choice((True,False)):
        Name += " " + random.choice(suffixes)
    
    Name = Name[0].upper() + Name[1:]
    
    return Name

