# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 16:13:46 2023

@author: Thomas Sartre et François Patinec-Haxel
"""
#importation des bibliothèques
import pygame
import pygame_menu

import random

import TextureManager
import SaveManager
import UiManager
import GameItems

pygame.init()#initialisation pygame

UiManager.Init()#initialisation du l'UiManager

pygame.display.set_caption('SpaceFactory')#Définition du tire de la fenêtre

TextureManager.LoadAllTextures()#chargement des textures

def Play():
    """
    Lance le jeu
    """
    pygame.key.set_repeat(10)#on réduit le temps de détéction de répétition de touche
    SaveManager.Load(str(saveFileSelect.get_value()))#Chargement de la sauvegarde

    GameItems.Minerais.SpawnAllScreen()#Spawn des minerais

    while SaveManager.SaveLoaded():#tant que la sauvegarde est chargée
        
        UiManager.UpdateBackground()#mise à jour du fond

        for m in GameItems.current:#pour chaque minerais dans GameItems.current
            GameItems.Minerais.PlaceFromCurrent(m)#placement du minerais

        for item in SaveManager.GetItems():#pour chaque item dans SaveManager.GetItems()
            item.Display()#Afficher l'item
            item.Give()

        for index,popup in enumerate(UiManager.UIPopup):#pour index , popup dans UiManager.UIPopup
            popup.show(index)
            UiManager.UIelements["popup_area"]=pygame.Rect(UiManager.width-500,50,500,205*(index+1)).collidepoint(pygame.mouse.get_pos())#on stocke la zone de popup

        UiManager.DisplayUi()#Afficher l'Interface Utilisateur
        
        pygame.display.update()#Mise à jour de l'affichage Pygame
        
        #action du clavier
        keys = pygame.key.get_pressed()#On stocke les touches pressées
        
        camOffset = [0,0]#Définition de l'offset de la caméra
        if keys[pygame.K_UP]:#si touche up
            camOffset[1]+=5
        if keys[pygame.K_DOWN]:#si touche down
            camOffset[1]-=5
        if keys[pygame.K_RIGHT]:#si touche right
            camOffset[0]-=5
        if keys[pygame.K_LEFT]:#si touche left
            camOffset[0]+=5
        SaveManager.TranslateCam(camOffset)#On applique les changements de caméra
        
        if camOffset != [0,0]:#si un déplacement a eu lieu
            GameItems.Minerais.SpawnBorder(camOffset)#on spawn les minerais aux bordures
        
        if keys[pygame.K_ESCAPE]:#Si la touche Esc est pressée
            SaveManager.Unload()#Décharger la sauvegarde
            return#on quitte la fonction Play()
        
        for event in pygame.event.get():
            #en cas de fermeture du jeu (sert à ne pas provoquer de bug)
            if event.type == pygame.QUIT:#en cas de Alt+F4 ou de fermeture via la croix de la fenêtre
                SaveManager.Unload()#Décharger la sauvegarde
                return#on quitte la fonction Play()
            
            #action de molette de souris
            if event.type == pygame.MOUSEWHEEL:#si un changement molette survient
                zoom = SaveManager.mainData.zoom#on récupère le zoom 
                zoom+=event.y if event.y+zoom>1 else 0#on ajoute le y du changement de molette (uniquement si le niveau de zoom restera supérieur à 1)
                SaveManager.mainData.zoom = zoom#on change le zoom dans le SaveManager
                TextureManager.RefreshZoom()#On mets à jour le zoom
                GameItems.Minerais.SpawnBorder(camOffset)#On spawn les minerais aux bordures
                
            if event.type == pygame.MOUSEBUTTONDOWN:#en cas de clic
                if event.button == 1: # 1 == left button
                    if not UiManager.IsClickOnUI():#si ce n'est pas un clic sur UI
                        if not SaveManager.IsItemHere(UiManager.GetMouseWorldPos()):
                            SaveManager.PlaceItem(GameItems.Item(SaveManager.GetSelectedItem(), UiManager.GetMouseWorldPos(),{}))#Placer item
                        else:
                            UiManager.Popup("Vous ne pouvez pas placer d'éléments ici, cet emplacement est déjà occupé")
                    elif UiManager.UIelements.get("select",False):#Si l'élément d'UI cliqué est l'élément stocké à UiManager.UIelements["select"], alors
                        UiManager.showMenu["select"]=1-UiManager.showMenu.get("select",0)#montrer le menu "select"
                    elif UiManager.UIelements.get("menu_icon",False):#Si l'élément d'UI cliqué est l'élément stocké à UiManager.UIelements["menu_icon"], alors
                        SaveManager.Unload()#Décharger la sauvegarde
                        return#on quitte la fonction Play()
                    elif UiManager.UIelements.get("select2",False):
                        for i in GameItems.menuElements:
                            if UiManager.UIelements.get("selectElements_"+i,False):
                                SaveManager.SetSelectedItem(i)
                    elif UiManager.UIelements.get("popup_area",False):
                        for index,popup in enumerate(UiManager.UIPopup):
                            if UiManager.UIelements.get("popup_"+str(index),False):
                                popup.close(index)
                if event.button == 3: # 3 == right button
                    if not UiManager.IsClickOnUI():#si ce n'est pas un clic sur UI
                        clickedItem = SaveManager.GetItemAtPos(UiManager.GetMouseWorldPos())
                        if clickedItem != None:
                            UiManager.Popup(clickedItem.name+"\n"+str(clickedItem.metadata)+"\n"+str(clickedItem.pos)+"\n"+str(GameItems.Minerais.Type(*UiManager.GetMouseWorldPos()))+str(GameItems.Minerais.Type(*clickedItem.pos)))
            
            if event.type == MUSIC_ENDED:#Si la musique s'arrête
                pygame.mixer.music.load("./Assets2/audio/" + random.choice(playlist))#on charge une nouvelle musique
                pygame.mixer.music.play(start=0.0, fade_ms=200)#on lance la lecture de la nouvelle musique
        
        
        SaveManager.clock.tick()#on mets à jour l'horloge des FPS
        

   

MUSIC_ENDED = pygame.USEREVENT#MUSIC_ENDED est un événement
pygame.mixer.music.set_endevent(MUSIC_ENDED)#si la musique s'arrête, lancer événement MUSIC_ENDED
playlist=["theme.mp3","Genesis.mp3","jake-chudnow-moon-men.mp3","buran-voskresenie.mp3"]#définition de notre playlist
#Lancement de la musique
pygame.mixer.music.load("./Assets2/audio/" + random.choice(playlist))#on chargte une nouvelle musique

pygame.mixer.music.set_volume(0.7)#On règle le volume de la musique
pygame.mixer.music.play(start=0.0, fade_ms=200)#lancement de la lecture de la musique

#Définition du Menu (ici, le menu est généré via le module pygame_menu)
menu = pygame_menu.Menu('Bienvenue', 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
bg=pygame_menu.baseimage.BaseImage("./Assets2/background.png", drawing_mode=101, drawing_offset=(0, 0), drawing_position='position-northwest', load_from_file=True, frombase64=False, image_id='')#on définit le fond du menu
saveFileSelect=menu.add.text_input('Fichier :', default='save',maxchar=10)#zone de texte du menu (sert au choix de la sauvegarde)

menu.add.button('Jouer', Play)#Boutton pour lancer le jeu
menu.add.button('Quitter', pygame_menu.events.EXIT)#Quitter le jeu

menu.mainloop(UiManager.screen, lambda : (bg.draw(UiManager.screen),pygame.key.set_repeat(1000)))#Boucle principale du Menu