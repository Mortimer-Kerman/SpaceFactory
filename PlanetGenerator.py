# -*- coding: utf-8 -*-
import random
import math
from colorsys import hsv_to_rgb
from perlin_noise import PerlinNoise
import matplotlib.pyplot as plt
import pygame
import numpy

class PlanetTypes:
    Random = 0
    EarthLike = 1
    Dead = 2
    GasGiant = 3

TextureSize = 100
Scale = 3

PoleCoverage = 0.3

DesertCoverage = 0.2

SandRedFactor = 0

SeaLevel = 0.5
BiomeLerpSpeed = 0.3
AtmosphereStrengh = 0.2
AtmosphereCoverage = 0.1

CloudsStrength = 0.5
CraterSize = 3

octaves = 2
lacunarity = 6.7
persistance = 0.28

PlanetType = PlanetTypes.Random

DeadPlanetColor = 0
AtmosphereColor = 0.5
GasGiantColor = 0
GasGiantBands = 1

Seed = 0
RandomSeed = True

CalculateLight = True
IsSunBehind = False
LightPos = (0.35, 0.35)

def Generate():
    global GasGiantColor
    global GasGiantBands
    global DeadPlanetColor
    global AtmosphereColor
    global AtmosphereCoverage
    global DesertCoverage
    global CloudsStrength
    global SandRedFactor
    global PlanetType
    global Seed
    """
    noise.SetNoiseType(FastNoiseLite.NoiseType.Cellular);
    noise.SetFrequency(0.020);
    noise.SetCellularDistanceFunction(FastNoiseLite.CellularDistanceFunction.EuclideanSq);
    noise.SetCellularReturnType(FastNoiseLite.CellularReturnType.Distance2Add);
    noise.SetCellularJitter(1.0);
    """
    if (RandomSeed):
        Seed = random.randint(-10000, 10000);
    random.seed(Seed)
    print(Seed)

    if (PlanetType == PlanetTypes.Random):
        PlanetType = random.randint(1, 3)
    PlanetType = PlanetTypes.EarthLike
    if (PlanetType == PlanetTypes.GasGiant):
    
        AtmosphereColor = random.uniform(0, 1)
        AtmosphereStrengh = 0.1
        AtmosphereCoverage = AtmosphereStrengh / 2
        GasGiantColor = random.uniform(0, 1)
        GasGiantBands = random.uniform(0.1, 3)
    
    elif(PlanetType == PlanetTypes.Dead):
    
        AtmosphereColor = random.uniform(0, 1)
        AtmosphereStrengh = random.uniform(0, 0.1) if random.randint(0, 3) == 0 else 0
        AtmosphereCoverage = AtmosphereStrengh / 2;
        DeadPlanetColor = random.uniform(0, 1)
    
    else:
    
        AtmosphereColor = 0.5
        AtmosphereStrengh = 0.2
        AtmosphereCoverage = AtmosphereStrengh / 2

        SeaLevel = random.uniform(0.2, 0.8)

        DesertCoverage = random.uniform(0, 1)

        CloudsStrength = (SeaLevel - 0.2) * 4 / 3

        SandRedFactor = random.uniform(0, 1)
    

    return Tex(TextureSize, (random.uniform(-TextureSize, TextureSize),random.uniform(-TextureSize, TextureSize)), (1 / TextureSize) * Scale)

def clamp(val:float,minv:float,maxv:float)->float:
    return max(min(val,maxv),minv)

def clamp01(val:float)->float:
    return clamp(val, 0, 1)

def lerp(a:float,b:float,t:float)->float:
    t = clamp01(t)
    return a * (1 - t) + (b * t)

def lerpcol(a:tuple,b:tuple,t:float)->tuple:
    return (lerp(a[0],b[0],t),lerp(a[1],b[1],t),lerp(a[2],b[2],t))

def add(a:tuple,b:tuple)->tuple:
    return(clamp01(a[0] + b[0]), clamp01(a[1] + b[1]), clamp01(a[2] + b[2]))

def multiply(c:tuple,v:float)->tuple:
    return (clamp01(c[0] * v),clamp01(c[1] * v),clamp01(c[2] * v))

def Tex(TextureSize:int, Offset:tuple, scale:float = 1):

    pix = []

    for y in range(TextureSize):
        row = []
        for x in range(TextureSize):
        
            xCoord = x * scale;
            yCoord = y * scale;

            c = (0,0,0);
            if (DistanceToCenter(x, y) < 0.99):
            
                if (PlanetType == PlanetTypes.EarthLike):
                
                    depth = FractalNoise(xCoord, yCoord, Offset)
                    
                    ocean = (0, 0, depth + SeaLevel)
                    grass = (0, depth, 0)
                    desert = lerpcol(((depth * 1) + 0.2, (depth * 0.92) + 0.2, 0.2), (depth, depth / 4, 0), SandRedFactor)
                    poles = (depth + 0.3, depth + 0.3, depth + 0.3)

                    Latitude = abs((y - (TextureSize / 2)) / (TextureSize / 2))

                    grass = lerpcol(desert, grass, clamp01((perlinNoise(xCoord + (Offset[0] * 2), yCoord + (Offset[1] * 2)) - DesertCoverage) / (1 - DesertCoverage)) / BiomeLerpSpeed)

                    grass = lerpcol(grass, poles, clamp01((Latitude - (1 - PoleCoverage)) / PoleCoverage) / BiomeLerpSpeed)

                    if (depth < SeaLevel):
                        c = ocean
                    else:
                        c = grass
                
                if (PlanetType == PlanetTypes.Dead):
                
                    depth = FractalNoise(xCoord, yCoord, Offset);

                    depth = depth / 2 + 0.25 #+ CraterNoise(xCoord, yCoord, Offset, CraterSize)
                    c = hsv_to_rgb(0.08, DeadPlanetColor, depth/2)
                
                if (PlanetType == PlanetTypes.GasGiant):
                
                    depth = clamp01(perlinNoise(0, yCoord * GasGiantBands + Offset[0]) + (perlinNoise(xCoord * 5, yCoord * 5) / 20))

                    c = add(hsv_to_rgb(AtmosphereColor, 1, depth * 0.7), hsv_to_rgb(GasGiantColor, 1, 1 - depth))
                
                
            """
            atm = (0,0,0)
            if (DistanceToCenter(x, y) < 1): 
            
                density = (DistanceToCenter(x, y) - (1 - AtmosphereCoverage)) / AtmosphereCoverage
                if (density < AtmosphereStrengh) density = AtmosphereStrengh;
                atm = Color.HSVToRGB(AtmosphereColor, 1, 1) * density;
            

            Color clouds = Color.clear;
            if (DistanceToCenter(x, y) < 1) 
            {
                if (PlanetType.Equals(PlanetTypes.EarthLike))
                {
                    float density = (FractalNoise(xCoord, yCoord, Offset * 3) * 2) - 1 - (0.5f - CloudsStrength);
                    if (density < 0) density = 0;
                    clouds = Color.white * density;
                }
            }

            
            pix[(int)y * TextureSize + (int)x] = (c + atm + clouds) * light;
            """
            
            
            atm = (0,0,0)
            if (DistanceToCenter(x, y) < 1 and AtmosphereCoverage != 0): 
            
                density = (DistanceToCenter(x, y) - (1 - AtmosphereCoverage)) / AtmosphereCoverage
                if (density < AtmosphereStrengh):
                    density = AtmosphereStrengh
                atm = multiply(hsv_to_rgb(AtmosphereColor, 1, 1), density);
            

            clouds = (0,0,0)
            if (DistanceToCenter(x, y) < 1):
            
                if (PlanetType == PlanetTypes.EarthLike):
                
                    density = (FractalNoise(xCoord, yCoord, (Offset[0] * 3, Offset[1] * 3)) * 2) - 1 - (0.5 - CloudsStrength)
                    if (density < 0):
                        density = 0
                    clouds = (density, density, density)
            
            light = 1
            if (DistanceToCenter(x, y) < 1 and CalculateLight):
            
                light = (DistanceToLightSource(x, y) - 0.6) if IsSunBehind else (-DistanceToLightSource(x, y) + 1)
                if (light < 0):
                    light = 0
                light *= 1.5
            
            col = multiply(add(add(c, atm), clouds), light)
            col = (col[0] * 255,
            col[1] * 255,
            col[2] * 255)
            row.append(col)
        pix.append(row)
    
    return numpy.array(pix)
    #plt.imshow(pix)
    #plt.show()


def DistanceToCenter(x:float, y:float):

    return Distance((x, y), (TextureSize / 2, TextureSize / 2)) / (TextureSize / 2)

def Distance(a:tuple,b:tuple):
    return math.sqrt(((b[0]-a[0])**2) + ((b[1]-a[1])**2))

def DistanceToLightSource(x:float, y:float):

    return Distance((x, y), (LightPos[0] * TextureSize, LightPos[1] * TextureSize)) / (TextureSize / 1.2)


def FractalNoise(posX:float, posY:float, offset:tuple):

    value = 0
    maxValue = 0

    for i in range(octaves):
    
        frequency = lacunarity**i
        amplitude = persistance**i
        value += perlinNoise((posX * frequency) + offset[0], (posY * frequency) + offset[0]) * amplitude;
        maxValue += amplitude;
    
    return value / maxValue;

noise = PerlinNoise(octaves=1, seed=1)

def perlinNoise(x,y):
    return noise([x,y]) + 0.5

def DistanceToCenterElliptical(x:float, y:float):

    return (math.pow(x - (TextureSize / 2), 2) / math.pow(TextureSize / 2, 2)) + (math.pow(y - (TextureSize / 2), 2) / math.pow(TextureSize / 6, 2))


#noise = new FastNoiseLite()
"""
public float CraterNoise(float posX, float posY, Vector2 offset, float craterSize)
{
    float CraterNoise = (noise.GetNoise(posX / craterSize + offset.x, posY / craterSize + offset.y) - 1) / -2;

    CraterNoise -= 0.9f;

    CraterNoise /= 0.1f;

    CraterNoise = Mathf.Clamp01(CraterNoise);

    CraterNoise /= 2;

    if (CraterNoise > 0.4f)
    {
        CraterNoise -= 0.4f;
    }
    else if (CraterNoise > 0.2f)
    {
        CraterNoise -= 0.2f;
        CraterNoise *= -1;
        CraterNoise += 0.2f;
    }
    return CraterNoise;
}
"""


Generate()