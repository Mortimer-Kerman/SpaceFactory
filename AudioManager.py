# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 22:20:35 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import random

MUSIC_ENDED = pygame.USEREVENT#MUSIC_ENDED est un événement

playlist=["theme","Genesis","LostInSpace","buran-voskresenie"]#définition de notre playlist

lastRandomMusic = None#Variable stockant la dernière musique aléatoire jouée

def Init():
    pygame.mixer.music.set_endevent(MUSIC_ENDED)#si la musique s'arrête, lancer événement MUSIC_ENDED
    
    pygame.mixer.music.set_volume(0.7)#On règle le volume de la musique
    
    PlayRandomMusic()#Lancement de la musique

def Tick():
    """
    Met à jour le gestionnaire d'audio, nottament le lancement de nouvelles musique si la précédente se coupe
    """
    if len(pygame.event.get(eventtype=MUSIC_ENDED)) != 0:#Si un évenement d'arrêt de musique est recensé
            PlayRandomMusic()#Nouvelle musique aléatoire

def PlayRandomMusic():
    """
    Lance une musique aléatoire différente de la dernière musique aléatoire
    """
    global lastRandomMusic
    
    #On récupère une musique aléatoire
    music = random.choice(playlist)
    
    #Tant que cette musique est la dernière musique aléatoire prise, on la change
    while music == lastRandomMusic:
        music = random.choice(playlist)
    
    lastRandomMusic = music
    PlayMusic(music)#on lance la musique
    
def PlayMusic(musicName:str):
    """
    Lance une musique d'après son nom
    """
    pygame.mixer.music.load("./Assets/audio/" + musicName + ".mp3")#on charge une nouvelle musique
    pygame.mixer.music.play(start=0.0, fade_ms=200)#lancement de la lecture de la musique