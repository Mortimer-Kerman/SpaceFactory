# -*- coding: utf-8 -*-
import random
import pygame

import UiManager

class Ennemis:
    pass

class Events:
    def __init__(self):
        self.isEventHappening = False
        self.lastEvent=0
        self.runtime=0
        self.nextEvent = self.lastEvent + random.randint(990,998)
    def LaunchEvent(self):
        self.runtime+=1
        if self.nextEvent<self.runtime:
            self.nextEvent = self.nextEvent + random.randint(990,998)
            self.isEventHappening = True
            UiManager.Popup("text")