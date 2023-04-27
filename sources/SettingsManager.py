# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 17:51:59 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import json
import pygame_menu

import UiManager
import Localization

#Variable indiquant si des paramètres ont été changés
SettingsChanged = False

def DefaultSettingsInstance():
    """
    Instance par défaut des paramètres.
    """
    return {
        "musicVolume": 70,
        "gameVolume": 100,
        "niceBiomeBorders": True,
        "maxFps": 60,
        "keybinds": {
            "up": pygame.K_z,
            "down": pygame.K_s,
            "left": pygame.K_q,
            "right": pygame.K_d,
            "rotate": pygame.K_r,
            "inv": pygame.K_i,
            "buildMenu": pygame.K_c,
            "opportunities" : pygame.K_m,
            "tasks" : pygame.K_t
        }
    }

#Instance par défaut des paramètres
__mainSettings = DefaultSettingsInstance()

def GetSetting(name:str):
    """
    Permet de récupérer un paramètre avec son nom.
    Si le paramètre n'est pas trouvé, la fonction renvoie None
    Le fait que la fonction renvoie None peut aussi signifier que le paramètre est réglé sur None
    """
    return __mainSettings.get(name, None)

def SetSetting(name:str, value):
    """
    Permet de régler un paramètre avec son nom et sa valeur.
    Il n'est pas enregistré dans le disque dur, seulement dans la mémoire du jeu
    L'application des paramètres peut s'avérer nécessaire
    """
    __mainSettings[name] = value
    global SettingsChanged
    SettingsChanged = True

def GetKeybind(name:str):
    """
    Permet de récupérer l'identifiant d'une touche avec son nom
    Si la touche n'est pas trouvée, la fonction renvoie None
    Le fait que la fonction renvoie None peut aussi signifier que la touche est simplement désactivée par l'utilisateur
    """
    return __mainSettings["keybinds"].get(name, None)

def SetKeybind(name:str, value):
    """
    Permet de régler une touche avec son nom et son code.
    Elle n'est pas enregistrée dans le disque dur, seulement dans la mémoire du jeu
    L'application des paramètres peut s'avérer nécessaire
    """
    __mainSettings["keybinds"][name] = value
    global SettingsChanged
    SettingsChanged = True

def LoadSettings():
    """
    Charge les paramètres depuis le disque dur et les applique sur le jeu
    """
    global __mainSettings
    
    try:#On tente de charger les paramètres du jeu depuis le fichier de paramètres, puis on s'assure de leur validité et on les applique
        with open("Settings.json", "r") as f:
            __mainSettings = json.load(f)
        EnsureSettingsValidity()
        ApplySettings()
    except:#En cas d'erreur, on les réinitialise
        ResetSettings()
    #On marque que les paramètres n'ont pas changé
    global SettingsChanged
    SettingsChanged = False

def SaveSettings():
    """
    Sauvegarde les paramètres dans le disque dur et les applique au jeu
    """
    #On sauvegarde les paramètres sur le disque dur
    with open("Settings.json", "w") as f:
        f.write(json.dumps(__mainSettings, default=lambda o: o.__dict__, indent = 4))
    #On marque que les paramètres n'ont pas changé
    global SettingsChanged
    SettingsChanged = False
    #On applique les paramètres
    ApplySettings()

def ResetSettings():
    """
    Remet les paramètres à leur valeur de départ, les sauvegarde et les applique au jeu
    """
    global __mainSettings
    __mainSettings = DefaultSettingsInstance()
    SaveSettings()
    
def EnsureSettingsValidity():
    """
    Exécuter cette fonction lors du chargement des paramètres permet d'assurer la validité des paramètres en ajoutant les entrées manquantes
    """
    #Instance par défaut
    defaultInstance = DefaultSettingsInstance()
    #Pour chaque option de l'instance par défaut...
    for option in defaultInstance:
        #Si cette option n'est pas dans les paramètres, on l'y rajoute
        if not option in __mainSettings:
            __mainSettings[option] = defaultInstance[option]
    
    #Pour chaque paramètre de touche de l'instance par défaut...
    for keyBind in defaultInstance["keybinds"]:
        #Si cette touche n'est pas dans les paramètres, on l'y rajoute
        if not keyBind in __mainSettings["keybinds"]:
            __mainSettings["keybinds"][keyBind] = defaultInstance["keybinds"][keyBind]
    
def ApplySettings():
    """
    Applique les paramètres au jeu
    """
    #On r-gle le volume des canaux de musique et de son d'ambiance
    pygame.mixer.music.set_volume(GetSetting("musicVolume")/100)
    pygame.mixer.Channel(0).set_volume(GetSetting("gameVolume")/150)

#Instance du menu de paramètres
SettingsMenu = None

def OpenSettings(background):
    """
    Ouvre le menu des paramètres avec le fond actuel
    """
    global SettingsMenu
    #Si un menu de paramètres existe déjà, on le désactive
    if SettingsMenu != None:
        SettingsMenu.disable()
    
    #Création du menu
    SettingsMenu = pygame_menu.Menu(Localization.GetLoc('Settings.Title'), 800, 600, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    #Fonction temporaire pour s'assurer que les paramètres sont sauvegardés avant de quitter le menu
    def TryLeave():
        #Si les paramètres ne sont pas modifiés ou que l'utilisateur donne sa confirmation pour quitter sans sauvegarder...
        if not SettingsChanged or UiManager.WarnUser(Localization.GetLoc('Game.Warning'), Localization.GetLoc('Settings.NotSaved'), None, None, background):
            LoadSettings()#On recharge les paramètres
            SettingsMenu.disable()#On désactive le menu
    
    #Barre contenant les boutons du haut
    topBar = SettingsMenu.add.frame_h(780,50)
    topBar.relax(True)
    #Bouton de retour
    topBar.pack(SettingsMenu.add.button(Localization.GetLoc('Game.Back'), TryLeave), align=pygame_menu.locals.ALIGN_LEFT)
    #Bouton de sauvegarde
    topBar.pack(SettingsMenu.add.button(Localization.GetLoc('Game.Save'),  lambda : (SaveSettings(),TryLeave())), align=pygame_menu.locals.ALIGN_RIGHT)
    
    SettingsMenu.add.vertical_margin(20)
    
    #Paramètres de volume de la musique et de volume du jeu
    SettingsMenu.add.range_slider(Localization.GetLoc('Settings.MusicVolume'), GetSetting("musicVolume"), (0, 100), 1, value_format=lambda x: str(int(x)), onchange=lambda x:(pygame.mixer.music.set_volume(int(x)/100),SetSetting("musicVolume", int(x))), align=pygame_menu.locals.ALIGN_LEFT)
    SettingsMenu.add.range_slider(Localization.GetLoc('Settings.GameVolume'), GetSetting("gameVolume"), (0, 100), 1, value_format=lambda x: str(int(x)), onchange=lambda x:(pygame.mixer.Channel(0).set_volume(int(x)/150),SetSetting("gameVolume", int(x))), align=pygame_menu.locals.ALIGN_LEFT)
    
    #Paramètre pour les transitions douces entre les biomes
    SettingsMenu.add.toggle_switch(Localization.GetLoc('Settings.NiceBiomeBorders'), GetSetting("niceBiomeBorders"), state_text=(Localization.GetLoc('Settings.NiceBiomeBorders.False'), Localization.GetLoc('Settings.NiceBiomeBorders.True')), onchange=lambda x:(SetSetting("niceBiomeBorders", x),UiManager.ForceBackgroundRefresh()),align=pygame_menu.locals.ALIGN_LEFT)
    
    #Paramètre pour les FPS max
    SettingsMenu.add.range_slider(Localization.GetLoc('Settings.MaxFps'), GetSetting("maxFps"), (30, 201), 1, value_format=lambda x: str(int(x)) if int(x) < 201 else Localization.GetLoc('Settings.MaxFps.Unlimited'), onchange=lambda x:SetSetting("maxFps", int(x)), align=pygame_menu.locals.ALIGN_LEFT)
    
    SettingsMenu.add.vertical_margin(20)
    
    #Label annonçant les réglages de touches
    SettingsMenu.add.label(Localization.GetLoc('Settings.Keys.Title'), align=pygame_menu.locals.ALIGN_LEFT)
    
    SettingsMenu.add.vertical_margin(20)
    
    #On récupère les réglages de touches
    bindings = GetSetting("keybinds")
    
    #Pour chaque clé des réglages...
    for key in bindings.keys():
        #On crée un cadre pour contenir les infos sur la touche
        frame = SettingsMenu.add.frame_h(500, 50, padding=0, align=pygame_menu.locals.ALIGN_LEFT)
        frame.relax(True)
        #On ajoute le nom traduit du réglage
        frame.pack(SettingsMenu.add.label(Localization.GetLoc('Settings.Keys.'+key)))
        
        #On récupère le nom de la touche utilisée
        name = pygame.key.name(bindings[key])
        #On récupère une valeur correspondant entre la différence entre 10 et la longueur du nom de la touche, divisé par 2
        leak = int((10 - len(name))/2)
        #On rajoute des espaces devant et derrière le nom afin de pouvoir élargir la taille du bouton sans étirer le texte dedans
        for i in range(leak):
            name = " " + name + " "
        
        #Création du bouton pour changer la touche
        button = SettingsMenu.add.button(name,background_color=(50,50,50)).resize(100, 50)
        frame.pack(button, align=pygame_menu.locals.ALIGN_RIGHT)
        #On permet au bouton de régler la touche
        button.set_onreturn(lambda btn=button,kname=key:ChangeKey(btn,kname,background))
    
    SettingsMenu.add.vertical_margin(20)
    
    #Bouton de réinitialisation, demande la confirmation à l'utilisateur avant de réinitialiser
    SettingsMenu.add.button(Localization.GetLoc('Settings.Reset'), lambda:UiManager.WarnUser(Localization.GetLoc('Game.Warning'),Localization.GetLoc('Settings.Reset.Message'),lambda:(ResetSettings(),OpenSettings(background)),None,background))
    
    SettingsMenu.add.vertical_margin(20)
    
    #Boucle du menu
    SettingsMenu.mainloop(UiManager.screen, background)

def ChangeKey(KeyButton,KeyId,background):
    """
    Permet de modifier une touche dans les paramètres avec un menu contextuel
    """
    #On récupère le titre du bouton de changement et on retire tous les espaces avant et après
    keyName = KeyButton.get_title().strip()
    
    #Création d'un menu
    KeyChanger = pygame_menu.Menu(Localization.GetLoc('Settings.EditKey'), 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    #On ajoute des labels avec le nom du paramètre modifié et la touche actuellement modifiée
    KeyChanger.add.label(Localization.GetLoc('Settings.Keys.'+KeyId))
    KeyChanger.add.label(Localization.GetLoc('Settings.EditKey.Current',keyName))
    
    #Fonction temporaire pour gérer la boucle de mise à jour du menu (désactive la mise à jour par défaut du menu)
    def kLoop():
        #Pour chaque event pygame...
        for event in pygame.event.get():
            #Si une touche est pressée...
            if event.type == pygame.KEYDOWN:
                #Si la touche pressée n'est pas la touche echap...
                if event.key != pygame.K_ESCAPE:
                    #On règle le paramètre modifié avec la touche choisie
                    SetKeybind(KeyId, event.key)
                    #On met à jour le nom affiché
                    name = pygame.key.name(event.key)
                    #On récupère une valeur correspondant entre la différence entre 10 et la longueur du nom de la touche, divisé par 2
                    leak = int((10 - len(name))/2)
                    #On rajoute des espaces devant et derrière le nom afin de pouvoir élargir la taille du bouton sans étirer le texte dedans
                    for i in range(leak):
                        name = " " + name + " "
                    #On remet ce nom dans le bouton du menu de paramètres
                    KeyButton.set_title(name)
                #On ferme le menu
                KeyChanger.disable()
    
    #Boucle du menu
    KeyChanger.mainloop(UiManager.screen, lambda:(background(),kLoop()))
