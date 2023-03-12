# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 21:13:26 2023

@author: Thomas Sartre et François Patinec-Haxel
"""

def clamp(val:float,minv:float,maxv:float)->float:
    return max(min(val,maxv),minv)

def clamp01(val:float)->float:
    return clamp(val, 0, 1)

def lerp(a:float,b:float,t:float)->float:
    t = clamp01(t)
    return a * (1 - t) + (b * t)

def lerpcol(a:tuple,b:tuple,t:float)->tuple:
    return (lerp(a[0],b[0],t),lerp(a[1],b[1],t),lerp(a[2],b[2],t))

def addcol(a:tuple,b:tuple)->tuple:
    return(clamp01(a[0] + b[0]), clamp01(a[1] + b[1]), clamp01(a[2] + b[2]))

def multiplycol(c:tuple,v:float)->tuple:
    return (clamp01(c[0] * v),clamp01(c[1] * v),clamp01(c[2] * v))

def ZeroOneToHexa(c:tuple)->tuple:
    return (c[0] * 255, c[1] * 255, c[2] * 255)