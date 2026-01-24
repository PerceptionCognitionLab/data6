from psychopy import core, visual, event
import numpy as np
from numpy import random
import random as rd
import sys
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib

seed = rd.randrange(1e6)
expName="dev2" 
refreshRate=165


dbConf=exlib.beta
exlib.setRefreshRate(refreshRate)
[pid,sid,fname]=exlib.startExp(expName,dbConf,pool=1,lockBox=True,refreshRate=refreshRate)

win = visual.Window(size=(800, 800), color=[-1, -1, -1], units="pix", fullscr=False)

bar = visual.Rect(
    win,
    width=100,
    height=100,
    pos=(0, 0),)
bar.draw()
win.flip()
core.wait(0.5)

[resX,resY]=win.size
concernText = exlib.getConcern(win)
exlib.stopExp(sid,refreshRate,resX,resY,seed,dbConf,concernText)
# ---- Cleanup ----
win.close()
core.quit()