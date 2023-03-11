# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 17:51:59 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

import pygame
import json
import pygame_menu

import UiManager

SettingsChanged = False

def DefaultSettingsInstance():
    """
    Instance par défaut des paramètres.
    """
    return {
        "musicVolume": 70,
        "keybinds": {
            "up": pygame.K_z,
            "down": pygame.K_s,
            "left": pygame.K_q,
            "right": pygame.K_d,
            "rotate": pygame.K_r
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
        __mainSettings = json.load(open("Settings.json", "r"))
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
    open("Settings.json", "w").write(json.dumps(__mainSettings, default=lambda o: o.__dict__, indent = 4))
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


SettingsMenu = None


def OpenSettings(background):
    global SettingsMenu
    if SettingsMenu != None:
        SettingsMenu.disable()
    SettingsMenu = pygame_menu.Menu('Options', 800, 600, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    def TryLeave():
        if not SettingsChanged:
            LoadSettings()
            SettingsMenu.disable()
            return
        UiManager.WarnUser("Attention", "Cetains paramètres ne sont pas sauvegardés.\nVoulez-vous quand même quitter?\n", lambda:(LoadSettings(), SettingsMenu.disable()), None)
        
        
    topBar = SettingsMenu.add.frame_h(800,50)
    topBar.relax(True)
    topBar.pack(SettingsMenu.add.button('Retour', TryLeave), align=pygame_menu.locals.ALIGN_LEFT)
    topBar.pack(SettingsMenu.add.button('Enregistrer', SaveSettings), align=pygame_menu.locals.ALIGN_RIGHT)
    
    SettingsMenu.add.vertical_margin(20)
    
    SettingsMenu.add.range_slider('Volume de la musique', GetSetting("musicVolume"), (0, 100), 1, value_format=lambda x: str(int(x)), onchange=lambda x:(pygame.mixer.music.set_volume(int(x)/100),SetSetting("musicVolume", int(x))), align=pygame_menu.locals.ALIGN_LEFT)
    
    SettingsMenu.add.vertical_margin(20)
    
    SettingsMenu.add.label("Touches", align=pygame_menu.locals.ALIGN_LEFT)
    
    SettingsMenu.add.vertical_margin(20)
    
    bindings = GetSetting("keybinds")
    
    for key in bindings.keys():
        frame = SettingsMenu.add.frame_h(300, 50, padding=0, align=pygame_menu.locals.ALIGN_LEFT)
        frame.relax(True)
        frame.pack(SettingsMenu.add.label(key))
        
        name = pygame.key.name(bindings[key])
        leak = int((10 - len(name))/2)
        for i in range(leak):
            name = " " + name + " "
        
        button = SettingsMenu.add.button(name)
        frame.pack(button, align=pygame_menu.locals.ALIGN_RIGHT)
        button.set_onreturn(lambda btn=button,kname=key:ChangeKey(btn,kname,background))
    
    SettingsMenu.add.vertical_margin(20)
    
    SettingsMenu.add.button('Réinitialiser les paramètres', lambda:UiManager.WarnUser("Attention","Voulez-vous vraiment remettre\ntous vos paramètres à leurs valeurs d'origine?",lambda:(ResetSettings(),OpenSettings(background)),None,background))
    
    SettingsMenu.mainloop(UiManager.screen, background)

def ChangeKey(KeyButton,KeyId,background):
    keyName = KeyButton.get_title().strip()
    
    KeyChanger = pygame_menu.Menu('Changer la touche', 400, 300, theme=pygame_menu.themes.THEME_DARK)#le thème du menu
    
    KeyChanger.add.label(KeyId)
    KeyChanger.add.label("Touche actuelle: " + keyName)
    
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





    
    
    
    
    