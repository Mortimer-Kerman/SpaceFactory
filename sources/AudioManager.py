# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 22:20:35 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame

import random
import os

import SettingsManager
import UiManager
import FunctionUtils
import SaveManager

#Évenements lié au son
MUSIC_ENDED = pygame.USEREVENT + 2
AMBIENCE_ENDED = pygame.USEREVENT + 3
SOUND_ENDED = pygame.USEREVENT + 4

lastRandomMusic = None#Variable stockant la dernière musique aléatoire jouée


loadedSounds = {}

def GetAllSoundsEvents():
    """
    Renvoie une liste avec tous les évenements de son
    """
    return [MUSIC_ENDED,AMBIENCE_ENDED] + [SOUND_ENDED + i for i in range(pygame.mixer.get_num_channels()-1)]

def Init():
    """
    Initialise le gestionnaire d'audio
    """
    LoadAllSounds()#On charge tous les sons
    
    pygame.mixer.set_num_channels(256)#Nombre de canaux sonores: 256
    
    pygame.mixer.music.set_endevent(MUSIC_ENDED)#si la musique s'arrête, lancer événement MUSIC_ENDED
    
    pygame.mixer.music.set_volume(0.7)#On règle le volume de la musique
    
    PlayRandomMusic()#Lancement de la musique
    
    audioChannels.append(pygame.mixer.Channel(0))#Création du canal audio 0, réservé au son d'ambiance
    
    audioChannels[0].set_endevent(AMBIENCE_ENDED)#Ajout de l'évenement de fin
    
    for i in range(pygame.mixer.get_num_channels()-1):#Pour i allant de 0 au nombre de canaux possibles...
        audioChannels.append(pygame.mixer.Channel(i+1))#On ajoute un nouveau canal à la liste
        audioChannels[i+1].set_endevent(SOUND_ENDED+i)#On lui ajoute un évenement de fin

audioChannels = []#Liste des canaux audio

def LoadAllSounds():
    """
    Charge tous les sons depuis les fichiers
    """
    global playlist
    
    soundsPath = './Assets/audio/'
    
    playlist = os.listdir(soundsPath + 'soundtrack/')#définition de notre playlist
    
    for subdir, dirs, files in os.walk(soundsPath):#on explore tous les fichiers dans le chemin des sons
        for file in files:#pour chaque fichier dans les fichiers
            if file.endswith(".mp3"):
                filepath = os.path.join(subdir, file)
                filename = filepath.replace(soundsPath, "").replace("\\","/")
                if not filename.startswith("soundtrack/"):
                    print("Loading " + filename)
                    loadedSounds[filename] = pygame.mixer.Sound(filepath)#chargement via pygame.mixer.Sound
    
    print("All sounds loaded!")


def Tick():
    """
    Met à jour le gestionnaire d'audio, notamment le lancement de nouvelles musiques si la précédente se coupe
    """
    if len(pygame.event.get(eventtype=MUSIC_ENDED)) != 0 or not pygame.mixer.music.get_busy():#Si un événement d'arrêt de musique est recensé ou si aucune musique n'est joué...
            PlayRandomMusic()#Nouvelle musique aléatoire
    if len(pygame.event.get(eventtype=AMBIENCE_ENDED)) != 0:#Si le son d'ambience s'est arrêté...
            BeginGameAmbience()#On le relance
    
    #Pour chaque canal audio (sauf le n°0)...
    for i in range(pygame.mixer.get_num_channels()-1):
        #Si ce canal audio s'est arrêté et qu'il était dans la liste des canaux utilisés...
        if len(pygame.event.get(eventtype=SOUND_ENDED+i)) != 0 and i+1 in usedChannels:
            usedChannels.remove(i+1)#On l'y retire

#Liste des canaux utilisés
usedChannels = [0]

def PlaySound(soundName,pos=None,volume=1):
    """
    Joue un son. Si une position dans le monde est donnée, le son sera spatialisé.
    """

    #On récupère le son à jouer
    sound = loadedSounds.get(soundName + ".mp3",None)
    
    #Si ce son n'existe pas, on annule l'exécution
    if sound == None:
        return

    #On parcourt les IDs de canaux audio possibles jusqu'a tomber sur un canal inutilisé
    channelID = 0
    while channelID in usedChannels:
        channelID += 1
    #Si le canal dont l'ID a été trouvé n'est pas un canal valide (hors de la liste des canaux ou égal à 0, celui réservé à l'ambience), on annule
    if channelID >= pygame.mixer.get_num_channels() or channelID == 0:
        return
    
    #On récupère le canal en question
    channel = audioChannels[channelID]
    
    #On récupère le volume de la musique entre 0 et 100
    gameVolume = SettingsManager.GetSetting("gameVolume")/100
    
    #Si une position d'origine a été spécifiée...
    if pos != None:
        #On récupère la position de la source à l'écran
        screenPos = UiManager.WorldPosToScreenPos(pos)
        
        #On calcule la "distance" brute entre la caméra et le monde en se basant sur le zoom
        bruteDistance = (150/SaveManager.GetZoom())
        
        #On calcule la position d'origine en fonction de la position sur l'écran
        sourcePos = (screenPos[0] / (UiManager.width/2) - 1, screenPos[1] / (UiManager.height/2) - 1, 0)
        
        #On calcule les position des oreilles gauche et droite
        leftEarPos = (-1,0,bruteDistance)
        rightEarPos = (1,0,bruteDistance)
        
        #On calcule le volume dans les oreilles gauche et droite: 1 divisé par la distance au carré (car le son diminue avec le carré de la distance) puis multiplé par le volume du jeu
        left = FunctionUtils.clamp01(1/(FunctionUtils.Distance(leftEarPos, sourcePos)**2)*gameVolume)
        right = FunctionUtils.clamp01(1/(FunctionUtils.Distance(rightEarPos, sourcePos)**2)*gameVolume)
        
        left = FunctionUtils.clamp01(left*volume)
        right = FunctionUtils.clamp01(right*volume)
        
        #Si le son dans les deux oreilles est très faible, il est inutile de jouer ce son
        if left < 0.05 and right < 0.05:
            return
        #On règle le son du canal audio
        channel.set_volume(left,right)
        
    else:
        #Si aucune position est spécifiée, le son n'est pas spatialisé, et le volume est réglé sur celui du jeu
        channel.set_volume(gameVolume)
        
    #On marque ce canal comme utilisé
    usedChannels.append(channelID)
    
    #On joue le son
    channel.play(sound)

def StopGameSounds():
    """
    Arrête tous les sons se jouant pendant une partie
    """
    pygame.mixer.stop()
    ClearUsedChannels()

def ClearUsedChannels():
    """
    Vide la liste des canaux utilisés
    """
    global usedChannels
    usedChannels = [0]

def BeginGameAmbience():
    """
    Démarre l'ambience sonore d'une partie
    """
    if not SaveManager.SaveLoaded():
        return
    sound = loadedSounds["ambience/ambiance2.mp3"]
    audioChannels[0].play(sound)

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
