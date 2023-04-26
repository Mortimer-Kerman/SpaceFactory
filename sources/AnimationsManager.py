#chargement des bibliothèques
import pygame
import random

import UiManager
import TextureManager
import SaveManager

class Drone:
    """
    Gère le drone qui suit la souris
    """
    def __init__(self):
        self.pos=[UiManager.width//2,UiManager.height//2]#On initialise sa position au centre de l'écran
        self.speed = 0.005#Vitesse de base du drone
        self.dest = list(pygame.mouse.get_pos())#Première destination : La position de la souris
    def show(self):
        """
        Affichage du drone
        """
        timeDelta = SaveManager.clock.get_time() / 10
        #On déplace le drone vers la cible de manière constante par rapport au pas de temps et on l'affiche
        self.pos[0] += self.speed * (self.dest[0]-self.pos[0]) * timeDelta
        self.pos[1] += self.speed * (self.dest[1]-self.pos[1]) * timeDelta
        UiManager.screen.blit(TextureManager.GetTexture("drone",max(50,SaveManager.GetZoom()/1.5)), self.pos)
    def update(self):
        """
        Mise à jour du drone
        """
        #Mise à jour de la position avec un décalage aléatoire
        self.dest = list(pygame.mouse.get_pos())
        self.dest[0] += random.randint(-100,100)
        self.dest[1] += random.randint(-100,100)
        #Si le drone s'approche trop du bord de l'écran, on le pousse à s'approcher du centre
        if not 200 < self.pos[0] < UiManager.width-200:
            self.dest[0]=UiManager.width//2
        if not 200 < self.pos[1] < UiManager.height-200:
            self.dest[1]=UiManager.height//2