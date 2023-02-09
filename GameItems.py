# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 18:05:51 2023

@author: 29ray
"""
import SaveManager
import UiManager
import TextureManager

class Item:
    def __init__(self,name:str,pos:tuple,texture:str="no",metadata=None):
        self.name=name
        self.pos=pos
        self.texture=texture
        self.metadata=metadata
    def ReadDictRepresentation(DictRepresentation:dict):
        item = Item(None,None)
        item.__dict__ = DictRepresentation
        return item
    def Display(self):
        cam = SaveManager.GetCamPos()
        cam = [cam[0],cam[1]]
        zoom = SaveManager.GetZoom()
        cam[0] += UiManager.width / 2
        cam[1] += UiManager.height / 2
        if not (-cam[0]+UiManager.width+200>=self.pos[0]*zoom>=-cam[0]-200 and -cam[1]+UiManager.height+200>=self.pos[1]*zoom>=-cam[1]-200):
            return
        print("displayin")
        UiManager.screen.blit(TextureManager.GetTexture(self.texture, zoom), (self.pos[0]*zoom+cam[0], self.pos[1]*zoom+cam[1]))