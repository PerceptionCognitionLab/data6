from psychopy import prefs
prefs.hardware['audioLib']=['PTB']
prefs.hardware['audioLatencyMode']=3
from psychopy import core, visual, sound, event
import numpy as np
import sys
sys.path.insert(0, '/home/exp/specl-exp/lib/data5/')
import expLib51 as el



scale=400

trialClock=core.Clock()

win=visual.Window(units= "pix", 
                     allowGUI=False,
                     size=(2*scale,2*scale),
                     color=[-1,-1,-1],
                     fullscr = True)
                     
                     
rw=visual.Rect(win,width=100,height=100,fillColor=[1,1,1],pos=[870,200])

frames=[]
frameDurations=[20,2,2,20,10]

frames.append(visual.TextStim(win,"1"))
frames.append(visual.BufferImageStim(win,stim=[visual.TextStim(win,"2"
),rw]))
frames.append(visual.TextStim(win,"3"))
frames.append(visual.BufferImageStim(win,stim=[visual.TextStim(win,"4"
),rw]))
frames.append(visual.TextStim(win,"5"))


message=visual.TextStim(win,"Press a key to start")
message.draw()
win.flip()
event.waitKeys()

stamps=el.runFrames(win,frames,frameDurations,trialClock)

event.waitKeys()
win.close()

print("Difference Between Time Stamps:\n",np.diff(stamps),"\n")
print("Difference Between Frames:\n",el.actualFrameDurations(frameDurations,stamps))
core.quit()
