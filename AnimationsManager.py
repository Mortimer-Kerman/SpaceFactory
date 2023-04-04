#chargement des bibliothèques
import pygame
import json
import random

import UiManager
import TextureManager

class Drone:
    def __init__(self):
        self.pos=[UiManager.width//2,UiManager.height//2]
        self.texture = TextureManager.GetTexture("drone",50)
        self.speed = 0.001
        self.dest = [self.pos[0]+random.randint(-1000, 1000),self.pos[1]+random.randint(-1000, 1000)]
    def show(self):
        self.pos[0] += self.speed * (self.dest[0]-self.pos[0])
        self.pos[1] += self.speed * (self.dest[1]-self.pos[1])
        UiManager.screen.blit(self.texture, self.pos)
    def update(self):
        self.dest = [self.pos[0]+random.randint(-1000, 1000),self.pos[1]+random.randint(-1000, 1000)]
        if not 200 < self.pos[0] < UiManager.width-200:
            self.dest[0]=UiManager.width//2
        if not 200 < self.pos[1] < UiManager.height-200:
            self.dest[1]=UiManager.height//2