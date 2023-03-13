# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 22:20:35 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import random

MUSIC_ENDED = pygame.USEREVENT#MUSIC_ENDED est un événement

playlist=["theme.mp3","Genesis.mp3","buran-voskresenie.mp3"]#définition de notre playlist

def Init():
    pygame.mixer.music.set_endevent(MUSIC_ENDED)#si la musique s'arrête, lancer événement MUSIC_ENDED
    
    #Lancement de la musique
    pygame.mixer.music.load("./Assets/audio/" + random.choice(playlist))#on chargte une nouvelle musique
    
    pygame.mixer.music.set_volume(0.7)#On règle le volume de la musique
    pygame.mixer.music.play(start=0.0, fade_ms=200)#lancement de la lecture de la musique