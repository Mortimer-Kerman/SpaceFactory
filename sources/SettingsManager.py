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
            "opportunities" : pygame.K_m,
            "tasks" : pygame.K_t
        }
    }

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
    
    try:
        with open("Settings.json", "r") as f:
            __mainSettings = json.load(f)
        EnsureSettingsValidity()
        ApplySettings()
    except:
        ResetSettings()
    global SettingsChanged
    SettingsChanged = False

def SaveSettings():
    """
    Sauvegarde les paramètres dans le disque dur et les applique au jeu
    """
    with open("Settings.json", "w") as f:
        f.write(json.dumps(__mainSettings, default=lambda o: o.__dict__, indent = 4))
    global SettingsChanged
    SettingsChanged = False
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
    defaultInstance = DefaultSettingsInstance()
    for option in defaultInstance:
        if not option in __mainSettings:
            __mainSettings[option] = defaultInstance[option]
    
    for keyBind in defaultInstance["keybinds"]:
        if not keyBind in __mainSettings["keybinds"]:
            __mainSettings["keybinds"][keyBind] = defaultInstance["keybinds"][keyBind]
    
def ApplySettings():
    """
    Applique les paramètres au jeu
    """
    pygame.mixer.music.set_volume(GetSetting("musicVolume")/100)
    pygame.mixer.Channel(0).set_volume(GetSetting("gameVolume")/150)

SettingsMenu = None


def OpenSettings(background):
    global SettingsMenu
    if SettingsMenu != None:
        SettingsMenu.disable()
    SettingsMenu = pygame_menu.Menu(Localization.GetLoc('Settings.Title'), 800, 600, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    def TryLeave():
        if not SettingsChanged:
            LoadSettings()
            SettingsMenu.disable()
            return
        UiManager.WarnUser(Localization.GetLoc('Game.Warning'), Localization.GetLoc('Settings.NotSaved'), lambda:(LoadSettings(), SettingsMenu.disable()), None, background)
        
        
    topBar = SettingsMenu.add.frame_h(780,50)
    topBar.relax(True)
    topBar.pack(SettingsMenu.add.button(Localization.GetLoc('Game.Back'), TryLeave), align=pygame_menu.locals.ALIGN_LEFT)
    topBar.pack(SettingsMenu.add.button(Localization.GetLoc('Settings.Save'),  lambda : (SaveSettings(),TryLeave())), align=pygame_menu.locals.ALIGN_RIGHT)
    
    SettingsMenu.add.vertical_margin(20)
    
    SettingsMenu.add.range_slider(Localization.GetLoc('Settings.MusicVolume'), GetSetting("musicVolume"), (0, 100), 1, value_format=lambda x: str(int(x)), onchange=lambda x:(pygame.mixer.music.set_volume(int(x)/100),SetSetting("musicVolume", int(x))), align=pygame_menu.locals.ALIGN_LEFT)
    SettingsMenu.add.range_slider(Localization.GetLoc('Settings.GameVolume'), GetSetting("gameVolume"), (0, 100), 1, value_format=lambda x: str(int(x)), onchange=lambda x:(pygame.mixer.Channel(0).set_volume(int(x)/150),SetSetting("gameVolume", int(x))), align=pygame_menu.locals.ALIGN_LEFT)
    
    SettingsMenu.add.toggle_switch(Localization.GetLoc('Settings.NiceBiomeBorders'), GetSetting("niceBiomeBorders"), state_text=(Localization.GetLoc('Settings.NiceBiomeBorders.False'), Localization.GetLoc('Settings.NiceBiomeBorders.True')), onchange=lambda x:(SetSetting("niceBiomeBorders", x),UiManager.ForceBackgroundRefresh()),align=pygame_menu.locals.ALIGN_LEFT)
    
    SettingsMenu.add.range_slider(Localization.GetLoc('Settings.MaxFps'), GetSetting("maxFps"), (30, 201), 1, value_format=lambda x: str(int(x)) if int(x) < 201 else Localization.GetLoc('Settings.MaxFps.Unlimited'), onchange=lambda x:SetSetting("maxFps", int(x)), align=pygame_menu.locals.ALIGN_LEFT)
    
    SettingsMenu.add.vertical_margin(20)
    
    SettingsMenu.add.label(Localization.GetLoc('Settings.Keys.Title'), align=pygame_menu.locals.ALIGN_LEFT)
    
    SettingsMenu.add.vertical_margin(20)
    
    bindings = GetSetting("keybinds")
    
    for key in bindings.keys():
        frame = SettingsMenu.add.frame_h(300, 50, padding=0, align=pygame_menu.locals.ALIGN_LEFT)
        frame.relax(True)
        frame.pack(SettingsMenu.add.label(Localization.GetLoc('Settings.Keys.'+key)))
        
        name = pygame.key.name(bindings[key])
        leak = int((10 - len(name))/2)
        for i in range(leak):
            name = " " + name + " "
        
        button = SettingsMenu.add.button(name,background_color=(50,50,50)).resize(100, 50)
        frame.pack(button, align=pygame_menu.locals.ALIGN_RIGHT)
        button.set_onreturn(lambda btn=button,kname=key:ChangeKey(btn,kname,background))
    
    SettingsMenu.add.vertical_margin(20)
    
    SettingsMenu.add.button(Localization.GetLoc('Settings.Reset'), lambda:UiManager.WarnUser(Localization.GetLoc('Game.Warning'),Localization.GetLoc('Settings.Reset.Message'),lambda:(ResetSettings(),OpenSettings(background)),None,background))
    
    SettingsMenu.add.vertical_margin(20)
    
    SettingsMenu.mainloop(UiManager.screen, background)

def ChangeKey(KeyButton,KeyId,background):
    keyName = KeyButton.get_title().strip()
    
    KeyChanger = pygame_menu.Menu(Localization.GetLoc('Settings.EditKey'), 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    KeyChanger.add.label(Localization.GetLoc('Settings.Keys.'+KeyId))
    KeyChanger.add.label(Localization.GetLoc('Settings.EditKey.Current',keyName))
    
    def kLoop():
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key != pygame.K_ESCAPE:
                    SetKeybind(KeyId, event.key)
                    name = pygame.key.name(event.key)
                    leak = int((10 - len(name))/2)
                    for i in range(leak):
                        name = " " + name + " "
                    KeyButton.set_title(name)
                KeyChanger.disable()
    
    KeyChanger.mainloop(UiManager.screen, lambda:(background(),kLoop()))









