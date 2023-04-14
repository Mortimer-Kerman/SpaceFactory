#chargement des bibliothèques
import pygame
import json
import random

import UiManager
import TextureManager
import SaveManager

class Drone:
    def __init__(self):
        self.pos=[UiManager.width//2,UiManager.height//2]
        self.texture = TextureManager.GetTexture("drone",50)
        self.speed = 0.005
        self.dest = list(pygame.mouse.get_pos())
    def show(self):
        timeDelta = SaveManager.clock.get_time() / 10
        
        self.pos[0] += self.speed * (self.dest[0]-self.pos[0]) * timeDelta
        self.pos[1] += self.speed * (self.dest[1]-self.pos[1]) * timeDelta
        UiManager.screen.blit(self.texture, self.pos)
    def update(self):
        self.dest = list(pygame.mouse.get_pos())
        self.dest[0] += random.randint(-100,100)
        self.dest[1] += random.randint(-100,100)
        if not 200 < self.pos[0] < UiManager.width-200:
            self.dest[0]=UiManager.width//2
        if not 200 < self.pos[1] < UiManager.height-200:
            self.dest[1]=UiManager.height//2