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

import psutil, os

process = psutil.Process(os.getpid())

def log_ram(i):
    mem = process.memory_info().rss / 1024**2
    print(f"Trial {i}: RAM = {mem:.1f} MB")
    
    
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
    return


def intro():
    messageIntro=visual.TextStim(win,"Welcome to the experiment! \n\n We will start with some practice blocks." \
                                "\n\n Press any key to begin.",height=30)
    messageIntro.draw()
    win.flip()
    event.waitKeys()
     
intro()  
lPar.dur = [1,1,1,1,1,1]

 
a = visual.BufferImageStim(win,stim=box+[fixX])
b = visual.BufferImageStim(win,stim=(fixX,fixL,fixR,targ))
c = visual.BufferImageStim(win,stim=(fixX,fixL,fixR,mask1))
d = visual.BufferImageStim(win,stim=(fixX,fixL,fixR,mask2))
for i in range(500):
    frames = [cXLR, a, cXLR, b, c, d]
    runTrial(frames)
    log_ram(i)
win.close()
'''
def getResp():
    keys=event.getKeys(keyList=gPar.keyList,timeStamped=trialClock)
    if len(keys)==0:
        keys=event.waitKeys(keyList=gPar.keyList,timeStamped=trialClock)
    resp=keys[0][0]
    rt=keys[0][1]
    if resp==gPar.abortKey:
        fptr.close()
        win.close()
        core.quit()   
    resp = gPar.keyList.index(resp)
    return([resp,round(rt,3)])

def runTrial():
    frames=[]

    if lPar.isCongruent==1:
        posCue=lPar.posTarg
    else:
        posCue=1-lPar.posTarg
    
    fixX,fixL,fixR,cXLR,box,targ,mask1,mask2=createStim()
    frames.append(cXLR)
    box[posCue].lineColor=[1,1,1]
    box[posCue].lineWidth=10
    frames.append(visual.BufferImageStim(win,stim=box+[fixX]))
    box[posCue].lineColor=[0,0,0]
    box[posCue].lineWidth=2
    frames.append(cXLR)
    frames.append(visual.BufferImageStim(win,stim=(fixX,fixL,fixR,targ)))
    frames.append(visual.BufferImageStim(win,stim=(fixX,fixL,fixR,mask1)))
    frames.append(visual.BufferImageStim(win,stim=(fixX,fixL,fixR,mask2)))
    stamps=el.runFrames(win,frames,lPar.dur,trialClock)
    [resp,rt]=getResp()
    if (resp==lPar.target):
        correctSound1.play()
        correctSound2.play()
    else:
        errorSound1.play()
        errorSound2.play()

    return([resp,rt])
    

def runBlock(blk,cong,nTrials,increment):
    txt(blk)
    blockStart(blk,cong)
    lPar.isCongruent=cong
    numCor=0
    
    for trl in range(nTrials):
        print(trl)
        lPar.target = int(rng.integers(0,9,1))
        lPar.posTarg = int(rng.integers(0,2,1))  #0=left, 1=right
        [resp,rt]=runTrial()
        print(pid,sid,blk,trl,lPar.isCongruent,lPar.target,lPar.dur[targDur],resp,rt,sep=", ", file=fptr)
        print(pid,sid,blk,trl,lPar.isCongruent,lPar.target,lPar.dur[targDur],resp,rt)
    
        if (resp==lPar.target)&(numCor==0):
            numCor+=1
        elif (resp==lPar.target)&(numCor==1):
            lPar.dur[targDur] = lPar.dur[targDur]-increment
            if lPar.dur[targDur]<1:
                lPar.dur[targDur]=1
            numCor=0
        else:
            lPar.dur[targDur]=lPar.dur[targDur]+increment
            numCor=0

    return(lPar.dur[targDur])

def blockStart(blk,cong):
    if (cong==1):
        cond = "Same side"
    else:
        cond = "Opposite side"
    message=visual.TextStim(win,f"Block {blk+1}  \n{cond} \n\nPress key to start",height=30)
    message.draw()
    win.flip()
    event.waitKeys()

def intro():
    messageIntro=visual.TextStim(win,"Welcome to the experiment! \n\n We will start with some practice blocks." \
                                "\n\n Press any key to begin.",height=30)
    messageIntro.draw()
    win.flip()
    event.waitKeys()


def txt(blk):
    if (blk==0):
        text=visual.TextStim(win,"In this experiemnt, you will see two squares on either side of the screen." \
                          " One of the squares will light up (the cue). Then a letter (the target) will appear in either the same square" \
                            " or the opposite square. Your job is to type what the letter was." \
                            "\n\n\nFirst, let's see what it looks like when the cue and the target are on the same side." \
                            "\n\n\nPress any key to continue", height=30)
        text.draw()
        win.flip()
        event.waitKeys()
        
    if (blk==1):
        text=visual.TextStim(win,"Great job!\n\n\nNext, let's see what it looks like when the cue and the target are on opposite sides." \
                            "\n\n\nPress any key to continue", height=30)
        text.draw()
        win.flip()
        event.waitKeys()
        
    if (blk==2):
        text=visual.TextStim(win, "Nice job!\n That's what the objects in the experiment will look like." \
                             "\n\nNow we will do another practice, a little faster this time." \
                                 "\n\n\nPress any key to continue", height = 30)
        text.draw()
        win.flip()
        event.waitKeys()
        
    if (blk==3):
        text=visual.TextStim(win, "Great work! It's OK if it feels harder as it gets faster." \
                             "\n\nNow, we'll practice again, but the letter will be in the box opposite the cue." \
                             "\n\n\nPress any key to continue", height =30)
        text.draw()
        win.flip()
        event.waitKeys()
        
    if (blk==4):
        text=visual.TextStim(win, "Great job!\n\nThe last set of practice will be at the same speed as the experiment," \
                             "which is a little faster than before.\n\n\nPress any key to continue", height=30)
        text.draw()
        win.flip()
        event.waitKeys()

    if (blk==6):
        text=visual.TextStim(win,"Feeling ready? \n\nNow we will start the experiment blocks." \
                             "\n\nYou may take breaks between blocks. Remember to stay focused and do your best." \
                            "\n\n\nPress a key to start the experiment  ",height=30) 
        text.draw()
        win.flip()
        event.waitKeys()  



########################
#### RUN EXPERIMENT ####
########################

intro()

#########################
#### PRACTICE BLOCKS ####
#########################

last=[90,70]
nTrials=5
increment=5
#Block 0 - congruent practice 1 (slow)
blk=0
cong=1
lPar.dur=[60,12,last[cong],22,16,16]
last[cong]=runBlock(blk,cong,nTrials,increment)

#Block 1 - incongruent practice (slow)
blk=1
cong=0
lPar.dur=[60,12,last[cong],22,16,16]
last[cong]=runBlock(blk,cong,nTrials,increment)


last=[75,55]
nTrials=10
increment=2
#Block 2 - congruent practice (slighely faster, more trials)
blk=2
cong=1
lPar.dur=[60,6,last[cong],19,16,16]
last[cong]=runBlock(blk,cong,nTrials,increment)

#Block 3 - incongruent practice (slightly faster, more trials)
blk=3
cong=0
lPar.dur=[60,6,last[cong],19,16,16]
last[cong]=runBlock(blk,cong,nTrials,increment)


last=[60,40]
nTrials=15
increment=2
#Block 4 - congrent practice (at speed)
blk=4
cong=1
lPar.dur=[60,2,last[cong],16,16,16]
last[cong]=runBlock(blk,cong,nTrials,increment)

#Block 5 - incongruent practice (at speed)
blk=5
cong=0
lPar.dur=[60,2,last[cong],16,16,16]
last[cong]=runBlock(blk,cong,nTrials,increment)



#############################
#### EXPERIMENTAL BLOCKS ####
#############################

#startExp()
last=[60,40]
nTrials=60
increment=5
#Block 6 - congruent 1
blk=6
cong=1
lPar.dur=[60,2,last[cong],16,16,16]
last[cong]=runBlock(blk,cong,nTrials,increment)

#Block 7 - incongruent 2
blk=7
cong=0
lPar.dur=[60,2,last[cong],16,16,16]
last[cong]=runBlock(blk,cong,nTrials,increment)
                                             
increment=2
#Block 8 - congruent 2
blk=8
cong=1
lPar.dur=[60,2,last[cong],16,16,16]
last[cong]=runBlock(blk,cong,nTrials,increment)

#Block 9 -incongruent 2
blk=9
cong=0
lPar.dur=[60,2,last[cong],16,16,16]
last[cong]=runBlock(blk,cong,nTrials,increment)

increment=1                                             #decreasing increment
#Block 10 - incongruent 3
blk=10
cong=0
lPar.dur=[60,2,last[cong],16,16,16]
last[cong]=runBlock(blk,cong,nTrials,increment)

#Block 11 - congruent 3
blk=11
cong=1
lPar.dur=[60,2,last[cong],16,16,16]
last[cong]=runBlock(blk,cong,nTrials,increment)



#hz=round(win.getActualFrameRate())
#[resX,resY]=win.size
win.close()
fptr.close()
#el.st  opExp(sid,hz,resX,resY,seed,dbConf)
core.quit()

'''