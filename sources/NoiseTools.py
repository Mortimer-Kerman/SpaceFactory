# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 09:11:39 2023

@author: Thomas Sartre et François Patinec-Haxel
"""
#importation de PIL pour la lecture des images
from PIL import Image
import numpy as np
#récupération des deux textures sous forme d'arrays de couelurs

perlinTex = list(Image.open("Assets/precomputedNoise/perlinTexture.png").getdata())
craterTex = list(Image.open("Assets/precomputedNoise/craterTexture.png").getdata())

def perlinNoise(x:float, y:float)->float:
    """
    Le bruit de perlin permet de générer des cartes de valeurs aléatoires entre 0 et 1 avec des transitions douces entre les valeurs adjacentes.
    """
    return perlinTex[round(x*32)%1024+((round(y*32)%1024)*1024)][0] / 255
		




def FractalNoise(posX:float, posY:float, offset:tuple, octaves:int, lacunarity:float=6.7, persistance:float=0.28):
    """
    Le bruit fractal combine plusieurs cartes de bruit de perlin pour augmenter le niveau de détail.
    """
    frequency = lacunarity ** np.arange(octaves)
    amplitude = persistance ** np.arange(octaves)

    # Création d'un tableau de valeurs de bruit de Perlin pour chaque octave
    perlin_octaves = np.zeros(octaves)
    for i in range(octaves):
        perlin_octaves[i] = perlinNoise((posX * frequency[i]) + offset[0], (posY * frequency[i]) + offset[1])

    # Calcul de la valeur finale en combinant les valeurs de chaque octave
    value = np.sum(perlin_octaves * amplitude)

    # Normalisation de la valeur entre 0 et 1
    value = value / np.sum(amplitude)

    return value



def craterNoise(x:float, y:float)->float:
    """
    Ce bruit de cratère est une variante du bruit cellulaire qui est utilisée dans ce cas pour l'affichage de cratères.
    """
    return craterTex[round(x*256)%1024+((round(y*256)%1024)*1024)][0] / 256

def FractalCraterNoise(posX:float, posY:float, offset:tuple)->float:
    """
    Le bruit fractal combine plusieurs cartes de bruit de cratère pour augmenter le niveau de détail.
    """
    value = 0
    maxValue = 0
    
    #Deux octaves suffisent dans ce cas.
    for i in range(2):
    
        frequency = 2**i
        amplitude = 0.5**i
        #L'idée est d'empiler des cartes de plus en plus petites et ayant une influence de plus en plus faible sur le résultat final.
        value += craterNoise((posX * frequency) + offset[0], (posY * frequency) + offset[1]) * amplitude
        #on garde trace de la valeur maximale pour pouvoir ajuster la valeur entre 0 et 1
        maxValue += amplitude
    
    return value / maxValue