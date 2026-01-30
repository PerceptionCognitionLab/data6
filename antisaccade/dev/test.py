'''
from psychopy import prefs  
prefs.hardware['audioLib']=['PTB']
prefs.hardware['audioLatencyMode']=3
'''
from psychopy import core, visual, sound, event
import numpy as np
from numpy import random
import sys    
import math
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as el
from types import SimpleNamespace


pid=1
sid=1
fname="test"

#expName="dev3" mj jjkk99999jkl;  jj99
refreshRate=165
seed= -1

dbConf=el.beta
#el.setRefreshRate(refreshRate)
#[pid,sid,fname]=el.startExp(e      wxpName,dbConf,pool=1,lockBox=False,refreshRate=refreshRate)

fptr=open(fname,"w")
rng = random.default_rng()

scale=400

trialClock=core.Clock()
correctSound1 = sound.Sound(800, secs=0.15)
correctSound2 = sound.Sound(1200, secs=0.15)
errorSound1 = sound.Sound(500, secs=0.30)
errorSound2 = sound.Sound(375, secs=0.30)

win=visual.Window(units= "pix", 
                     allowGUI=False,
                     size=(2*scale,2*scale),
                     color=[-1,-1,-1],
                     fullscr = True)

gParDict={"let":['A','S','D','F','G','H','J','K','L'],
      "mask":['@','#'],
      "abortKey":'9',
      "keyList":['a','s','d','f','g','h','j','k','l','9'],
      "pos":[(-400,0),(400,0)],
      "numTrials":10}
gPar = SimpleNamespace(**gParDict)

targDur=2
lParDict={"isCongruent":0,
          "target":0,
          "posTarg":0,          
          "dur":[50,2,0,16,16,16]}
lPar = SimpleNamespace(**lParDict)

fixX=visual.TextStim(win,"+", height = 30)
fixL=visual.Rect(win,pos=gPar.pos[0],fillColor=(-1,-1,-1),lineColor=(0,0,0),lineWidth=2,width=50,height=60)
fixR=visual.Rect(win,pos=gPar.pos[1],fillColor=(-1,-1,-1),lineColor=(0,0,0),lineWidth=2,width=50,height=60)
cXLR=visual.BufferImageStim(win,stim=(fixX,fixL,fixR))
box=[fixL,fixR]


targ=visual.TextStim(win, gPar.let[lPar.target],pos=gPar.pos[lPar.posTarg])
mask1=visual.TextStim(win, gPar.mask[0],pos=gPar.pos[lPar.posTarg])
mask2=visual.TextStim(win, gPar.mask[1],pos=gPar.pos[lPar.posTarg])
    
    
def runTrial(frames):
    
    if lPar.isCongruent==1:
        posCue=lPar.posTarg
    else:
        posCue=1-lPar.posTarg
    box[posCue].lineColor=[1,1,1]
    box[posCue].lineWidth=10
    box[posCue].lineColor=[0,0,0]
    box[posCue].lineWidth=2
    stamps=el.runFrames(win,frames,lPar.dur,trialClock)
    el.endTrial()
    return


def intro():
    messageIntro=visual.TextStim(win,"Welcome to the experiment! \n\n We will start with some practice blocks." \
                                "\n\n Press any key to begin.",height=30)
    messageIntro.draw()
    win.flip()
    event.waitKeys()
     
intro()  
lPar.dur = [1,1,1,1,1,1]

 

for i in range(5):
    a = visual.BufferImageStim(win,stim=box+[fixX])
    b = visual.BufferImageStim(win,stim=(fixX,fixL,fixR,targ))
    c = visual.BufferImageStim(win,stim=(fixX,fixL,fixR,mask1))
    d = visual.BufferImageStim(win,stim=(fixX,fixL,fixR,mask2))
    frames = [cXLR, a, cXLR, b, c, d]
    runTrial(frames)
concern = el.getConcern(win)
[resX,resY]=win.size
win.close()
el.stopExp(sid,refreshRate,resX,resY,seed,dbConf, concern)
