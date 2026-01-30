from psychopy import prefs
prefs.hardware['audioLib']=['PTB']
#prefs.hardware['audioLatencyMode']=3
from psychopy import core, visual, sound, event, clock
import numpy as np
import sys
sys.path.insert(0, '/home/exp/specl-exp/lib/data5/')
import expLib51 as el



scale=400

win=visual.Window(units= "pix", 
                     allowGUI=False,
                     size=(2*scale,2*scale),
                     color=[-1,-1,-1],
                     fullscr = True)

message=visual.TextStim(win,text="Hello World",
                        pos=(0,0),
                        height=20,bold=True,
                        anchorVert="bottom")
                        

     

message.draw()
win.flip()

beep=sound.Sound("A",secs=1)
beep.play()

event.waitKeys()

win.close()
core.quit()
