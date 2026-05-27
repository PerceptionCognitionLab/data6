# -*- coding: utf-8 -*-
from psychopy import core, visual

win=visual.Window(units= "pix", size=(1000, 1000), color=[-1,-1,-1], fullscr = False)

text = visual.TextStim(win,"Welcome to the experiment", height = 40, pos = (0,0))
text.draw()
win.flip()
core.wait(1)

rectangle = visual.Rect(win, width=100, height=100,fillColor=[1,1,1], pos = (0, 300))
rectangle.draw()
win.flip()
core.wait(1)

text.draw()
rectangle.draw()
win.flip()
core.wait(1)

win.close()

from psychopy import prefs
prefs.hardware['audioLib']=['PTB']
prefs.hardware['audioLatencyMode']=3
from psychopy import core, visual, sound, event
import numpy as np
import sys
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as el



scale=400
trialClock=core.Clock()

win=visual.Window(units= "pix", 
                     allowGUI=False,
                     size=(2*scale,2*scale),
                     color=[-1,-1,-1],
                     fullscr = True)
                     
                     
rw=visual.Rect(win,width=100,height=100,fillColor=[1,1,1],pos=[870,200])

frames=[]
frameDurations=[200,200,200,200,200]

frames.append(visual.TextStim(win,"1"))
frames.append(visual.BufferImageStim(win,stim=[visual.TextStim(win,"2"),rw]))
frames.append(visual.TextStim(win,"3"))
frames.append(visual.BufferImageStim(win,stim=[visual.TextStim(win,"4"),rw]))
frames.append(visual.TextStim(win,"5"))

message=visual.TextStim(win,"Press x or m key to start")
message.draw()
win.flip()
keys = event.waitKeys(keyList=['x', 'm'])
stamps=el.runFrames(win,frames,frameDurations,trialClock)
win.close()
print(keys)
print("Difference Between Time Stamps:\n",np.diff(stamps),"\n")
print("Difference Between Frames:\n",el.actualFrameDurations(frameDurations,stamps))
core.quit()
