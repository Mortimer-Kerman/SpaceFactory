# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 21:18:31 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

#Importation des bibliothèques nécessaires pour la génération
import random
import math
from colorsys import hsv_to_rgb
import numpy
import NoiseTools
import FunctionUtils

import pygame

#Les types de planète fournissent au générateur une direction globale dans sa manière de générer
class PlanetTypes:
    Random = 0
    EarthLike = 1
    Dead = 2

#Paramètres généraux pour la génération des textures: taille de la texture, échelle de bruit, nombre d'octaves et vitesse de transition entre les biomes
TextureSize = 100
Scale = 3
octaves = 2
BiomeLerpSpeed = 0.3

#Paramètres pour la gestion de la lumière
CalculateLight = True
IsSunBehind = False
LightPos = (0.35, 0.35)

CalculateSphericity = False
SphericityFactor = 1


class PlanetaryConditions():
    """
    Permet de générer ou stocker des conditions planétaires pour les passer au générateur
    """
    def __init__(self, **kwargs):
        self.gravity = kwargs.get("gravity", random.uniform(0.5, 1.5))
        self.pressure = kwargs.get("pressure", random.uniform(0, 2))
        self.temperature = kwargs.get("temperature", random.uniform(-50, 70))
        self.type = PlanetTypes.EarthLike if (0.7 < self.gravity < 1.3
                                          and 0.7 < self.pressure < 1.3
                                          and -30 < self.temperature < 50) else PlanetTypes.Dead


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
    DeadPlanetColor = 0
    AtmosphereColor = 0.5
    AtmosphereCoverage = 0.1
    AtmosphereStrengh = 0.2
    DesertCoverage = 0.2
    CloudsStrength = 0.5
    SandRedFactor = 0
    SeaLevel = 0.5
    PoleCoverage = 0.3
    
    #On récupère le type de planète depuis les conditions
    PlanetType = conditions.type
    
    if PlanetType == PlanetTypes.Dead:
    
        AtmosphereColor = random.uniform(0, 1)
        AtmosphereStrengh = random.uniform(0, 0.1) if random.randint(0, 2) == 0 else 0
        AtmosphereCoverage = AtmosphereStrengh / 2;
        DeadPlanetColor = random.uniform(0, 1)
        
        SeaLevel = random.uniform(0.2, 0.8)
    
    else:
    
        AtmosphereColor = 0.5
        AtmosphereStrengh = 0.2
        AtmosphereCoverage = AtmosphereStrengh / 2

        SeaLevel = 0.5#random.uniform(0.2, 0.8)

        DesertCoverage = random.uniform(0, 1)

        CloudsStrength = (SeaLevel - 0.2) * 4 / 3

        SandRedFactor = random.uniform(0, 1)
    
    Offset = (random.uniform(-TextureSize, TextureSize),random.uniform(-TextureSize, TextureSize))
    
    scale = (1 / TextureSize) * Scale
    
    pix = []

    for y in range(TextureSize):
        row = []
        for x in range(TextureSize):
            
            xCoord = x * scale;
            yCoord = y * scale;

            distanceToC = DistanceToCenter(x, y)

            c = (0,0,0)
            if distanceToC < 0.99:
            
                if PlanetType == PlanetTypes.EarthLike:
                
                    depth = FractalNoise(xCoord, yCoord, Offset, octaves, distanceToC)
                    
                    ocean = (0, 0, depth + SeaLevel)
                    grass = (0, depth, 0)
                    desert = FunctionUtils.lerpcol(((depth * 1) + 0.2, (depth * 0.92) + 0.2, 0.2), (depth, depth / 4, 0), SandRedFactor)
                    poles = (depth + 0.3, depth + 0.3, depth + 0.3)

                    Latitude = abs((x - (TextureSize / 2)) / (TextureSize / 2))

                    grass = FunctionUtils.lerpcol(desert, grass, FunctionUtils.clamp01((FractalNoise(xCoord, yCoord, (Offset[0] * 2, Offset[1] * 2), 1, distanceToC) - DesertCoverage) / (1 - DesertCoverage)) / BiomeLerpSpeed)

                    grass = FunctionUtils.lerpcol(grass, poles, FunctionUtils.clamp01((Latitude - (1 - PoleCoverage)) / PoleCoverage) / BiomeLerpSpeed)

                    if depth < SeaLevel:
                        c = ocean
                    else:
                        c = grass
                
                if PlanetType == PlanetTypes.Dead:
                
                    depth = FractalNoise(xCoord, yCoord, Offset, octaves, distanceToC)
                    
                    if depth < SeaLevel:
                        depth = depth / 2 + 0.5 + (FractalCraterNoise(xCoord*4, yCoord*4, Offset, distanceToC) / 8)
                    else:
                        depth = depth / 2 + 0.25 + FractalCraterNoise(xCoord, yCoord, Offset, distanceToC)
                    c = hsv_to_rgb(0.08, DeadPlanetColor, depth/2)
            
            atm = (0,0,0)
            if (distanceToC < 1 and AtmosphereCoverage != 0): 
            
                density = (distanceToC - (1 - AtmosphereCoverage)) / AtmosphereCoverage
                if (density < AtmosphereStrengh):
                    density = AtmosphereStrengh
                atm = FunctionUtils.multiplycol(hsv_to_rgb(AtmosphereColor, 1, 1), density);
            

            clouds = (0,0,0)
            if (distanceToC < 1):
            
                if (PlanetType == PlanetTypes.EarthLike):
                
                    density = (FractalNoise(xCoord, yCoord, (Offset[0] * 3, Offset[1] * 3), octaves, distanceToC) * 2) - 1 - (0.5 - CloudsStrength)
                    if (density < 0):
                        density = 0
                    clouds = (density, density, density)
            
            light = 1
            if (distanceToC < 1 and CalculateLight):
            
                light = (DistanceToLightSource(x, y) - 0.6) if IsSunBehind else (-DistanceToLightSource(x, y) + 0.8)
                if (light < 0):
                    light = 0
                light *= 2
            
            col = FunctionUtils.multiplycol(FunctionUtils.addcol(FunctionUtils.addcol(c, atm), clouds), light)
            row.append(FunctionUtils.ZeroOneToHexa(col))
        pix.append(row)
    
    texture = pygame.Surface((TextureSize,TextureSize))
    pygame.surfarray.blit_array(texture, numpy.array(pix))
    
    return texture







def DistanceToCenter(x:float, y:float):

    return Distance((x, y), (TextureSize / 2, TextureSize / 2)) / (TextureSize / 2)

def Distance(a:tuple,b:tuple):
    return math.sqrt(((b[0]-a[0])**2) + ((b[1]-a[1])**2))

def DistanceToLightSource(x:float, y:float):

    return Distance((x, y), (LightPos[0] * TextureSize, LightPos[1] * TextureSize)) / (TextureSize / 1.2)

def DistanceToCenterElliptical(x:float, y:float):

    return (math.pow(x - (TextureSize / 2), 2) / math.pow(TextureSize / 2, 2)) + (math.pow(y - (TextureSize / 2), 2) / math.pow(TextureSize / 6, 2))




def FractalNoise(posX:float, posY:float, offset:tuple, octaves:int, DistanceToC:float):
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
    if CalculateSphericity:
        offX = DistanceToC * SphericityFactor
        if posX > TextureSize/2:
            offX = -offX
        offY = DistanceToC * SphericityFactor
        if posY > TextureSize/2:
            offY = -offY
        offset = (offset[0] + offX, offset[1] + offY)
    return NoiseTools.FractalCraterNoise(posX, posY, offset)


#Generate(Seed = 100)