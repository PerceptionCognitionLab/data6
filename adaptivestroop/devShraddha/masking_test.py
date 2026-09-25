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



trialClock=core.Clock()

win=visual.Window(units= "pix", size=(1000, 1000), color=[-1,-1,-1], fullscr = False)


time = 10
symbols = []

for i in list(range (1,time+1)):
     if i % 3 == 0:
         symbols.append("!")
     elif i % 2 == 0:
         symbols.append("#")
     else:
         symbols.append("@")
         



frames = []
frameDurations= []



#text = visual.TextStim(win, symbols)
for i in symbols:
    frameDurations.append(10)
    frames.append(visual.TextStim(win, i, pos = (-300,0)))
    #frames.append(visual.BufferImageStim(win, stim=[visual.TextStim(win, rand_letters[0], pos = (-300,0))]))

stamps=el.runFrames(win,frames,frameDurations,trialClock)

win.flip()

win.close()

core.quit()