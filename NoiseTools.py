# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 09:11:39 2023

@author: sartre.thomas
"""

from PIL import Image

perlinTex = list(Image.open("Assets/precomputedNoise/perlinTexture.png").getdata())
craterTex = list(Image.open("Assets/precomputedNoise/craterTexture.png").getdata())


def perlinNoise(x:float, y:float)->float:
    return perlinTex[round(x*32)%1024+((round(y*32)%1024)*1024)][0] / 255

def FractalNoise(posX:float, posY:float, offset:tuple, octaves:int):

    value = 0
    maxValue = 0

    for i in range(octaves):
    
        frequency = 6.7**i
        amplitude = 0.28**i
        value += perlinNoise((posX * frequency) + offset[0], (posY * frequency) + offset[1]) * amplitude
        maxValue += amplitude
    
    return value / maxValue


def craterNoise(x:float, y:float)->float:
    return craterTex[round(x*256)%1024+((round(y*256)%1024)*1024)][0] / 256

def FractalCraterNoise(posX:float, posY:float, offset:tuple)->float:
    
    value = 0
    maxValue = 0

    for i in range(2):
    
        frequency = 2**i
        amplitude = 0.5**i
        value += craterNoise((posX * frequency) + offset[0], (posY * frequency) + offset[1]) * amplitude
        maxValue += amplitude
    
    return value / maxValue