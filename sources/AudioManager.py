# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 22:20:35 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame

import random
import os

MUSIC_ENDED = pygame.USEREVENT#MUSIC_ENDED est un événement
AMBIENCE_ENDED = pygame.USEREVENT + 1

lastRandomMusic = None#Variable stockant la dernière musique aléatoire jouée

def Init():
    global playlist
    playlist = os.listdir('./Assets/audio/soundtrack/')#définition de notre playlist
    
    pygame.mixer.music.set_endevent(MUSIC_ENDED)#si la musique s'arrête, lancer événement MUSIC_ENDED
    
    pygame.mixer.music.set_volume(0.7)#On règle le volume de la musique
    
    PlayRandomMusic()#Lancement de la musique
    
    pygame.mixer.Channel(0).set_endevent(AMBIENCE_ENDED)

def Tick():
    """
    Met à jour le gestionnaire d'audio, nottament le lancement de nouvelles musique si la précédente se coupe
    """
    if len(pygame.event.get(eventtype=MUSIC_ENDED)) != 0:#Si un évenement d'arrêt de musique est recensé
            PlayRandomMusic()#Nouvelle musique aléatoire
    if len(pygame.event.get(eventtype=AMBIENCE_ENDED)) != 0:#Si un évenement d'arrêt de musique est recensé
            BeginGameAmbience()
        
def StopGameSounds():
    """
    Arrête tous les jeux se jouant pendant une partie
    """
    for i in range(pygame.mixer.get_num_channels()):
        pygame.mixer.Channel(i).stop()
        
def BeginGameAmbience():
    """
    Démarre l'ambience sonore d'une partie
    """
    sound = pygame.mixer.Sound("./Assets/audio/ambiance2.mp3")
    pygame.mixer.Channel(0).play(sound)

def PlayRandomMusic():
    """
    Lance une musique aléatoire différente de la dernière musique aléatoire
    """
    global lastRandomMusic
    global playlist
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
    pygame.mixer.music.load("./Assets/audio/soundtrack/" + musicName)#on charge une nouvelle musique
    pygame.mixer.music.play(start=0.0, fade_ms=200)#lancement de la lecture de la musique