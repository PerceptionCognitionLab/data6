# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 12:31:41 2026

@author: exp
"""

import sys
import random
from psychopy import core, visual, event
from psychopy.hardware import keyboard

#from RunFrames tutorial
from psychopy import prefs
prefs.hardware['audioLib']=['PTB']
prefs.hardware['audioLatencyMode']=3
from psychopy import core, visual, sound, event
import numpy as np
import sys
sys.path.insert(0, 'E:/lib/data5')
import expLib51 as el


#trialClock=core.Clock()

#win=visual.Window(units= "pix", size=(1000, 1000), color=[-1,-1,-1], fullscr = False)

#win.close()

#core.quit()

time = 10
symbols = []

for i in list(range (1,time)):
     if i % 3 == 0:
         symbols.append("!")
     elif i % 2 == 0:
         symbols.append("#")
     else:
         symbols.append("@")
         
print(symbols)
#text = visual.TextStim(win, symbols)
         