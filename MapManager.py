# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 15:26:04 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame

import SettingsManager
import SaveManager
import UiManager
import FunctionUtils
import NoiseTools
import numpy

worldMap = pygame.image.load("Assets/background.png")

def OpenMap():
    
    worldMap = CalculateWorldMap()
    
    zoom = 4
    lastZoom = zoom
    camPos = [0,0]
    
    scaledMap = pygame.transform.scale(worldMap,(UiManager.width * zoom,UiManager.height * zoom))
    
    while True:
        
        UiManager.screen.blit(scaledMap, camPos)
        
        pygame.display.update()
        
        #action du clavier
        keys = pygame.key.get_pressed()#On stocke les touches pressées
        
        if keys[SettingsManager.GetKeybind("up")]:#si touche up
            camPos[1]+=SaveManager.clock.get_time() / 2
        if keys[SettingsManager.GetKeybind("down")]:#si touche down
            camPos[1]-=SaveManager.clock.get_time() / 2
        if keys[SettingsManager.GetKeybind("right")]:#si touche right
            camPos[0]-=SaveManager.clock.get_time() / 2
        if keys[SettingsManager.GetKeybind("left")]:#si touche left
            camPos[0]+=SaveManager.clock.get_time() / 2    
        
        camPos[0] = FunctionUtils.clamp(camPos[0], -UiManager.width*(zoom-1), 0)
        camPos[1] = FunctionUtils.clamp(camPos[1], -UiManager.height*(zoom-1), 0)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            
            if event.type == pygame.MOUSEWHEEL:#si un changement molette survient
                zoom = FunctionUtils.clamp(zoom+(event.y / 10), 1, 4)#on ajoute le y du changement de molette en s'assurant de garder le niveau de zoom entre 10 et 150
                if zoom != lastZoom:
                    lastZoom = zoom
                    scaledMap = pygame.transform.scale(worldMap,(UiManager.width * zoom,UiManager.height * zoom))
        
        SaveManager.clock.tick()#on mets à jour l'horloge des FPS

import matplotlib.pyplot as plt

def CalculateWorldMap():
    pix = []
    
    Offset = (1,1)
    DesertCoverage = 0.5
    PoleCoverage = 0.2
    SandRedFactor = 0.25
    BiomeLerpSpeed = 0.2
    SeaLevel = 0.5
    
    for y in range(200):
        row = []
        for x in range(100):
            
            xCoord = x / 50
            yCoord = y / 50
            
            depth = NoiseTools.FractalNoise(xCoord, yCoord, Offset, 2)
            
            col = (depth,depth,depth)
            
            variationMap = (depth - SeaLevel) / 2
            
            ocean = (0, 0.21, 0.35)
            grass = (0.28 + variationMap, 0.52 + variationMap, 0.07 + variationMap)
            desert = FunctionUtils.lerpcol(((depth * 1) + 0.2, (depth * 0.92) + 0.2, 0.2), (depth, depth / 4, 0), SandRedFactor)
            poles = (depth + 0.3, depth + 0.3, depth + 0.3)
            
            Latitude = abs((x - 50) / 50)
            
            biomeMap = NoiseTools.FractalNoise(xCoord, yCoord, (Offset[0] * 2, Offset[1] * 2), 2)# * 2 + 1
            
            biomeMap = round(biomeMap + 0.5 - DesertCoverage)#FunctionUtils.clamp01(((biomeMap+factor)/(abs(biomeMap+factor)+0.1)+1)/2)
            
            grass = FunctionUtils.lerpcol(desert, grass, biomeMap)

            grass = FunctionUtils.lerpcol(grass, poles, FunctionUtils.clamp01((Latitude - (1 - PoleCoverage)) / PoleCoverage) / BiomeLerpSpeed)

            if depth < SeaLevel:
                col = ocean
            else:
                col = grass
            
            #row.append(col)
            row.append(FunctionUtils.ZeroOneToHexa(col))
        pix.append(row)
    
    plt.imshow(pix)
    
    texture = pygame.Surface((200,100))
    pygame.surfarray.blit_array(texture, numpy.array(pix))
    
    return texture

CalculateWorldMap()