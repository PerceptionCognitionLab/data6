from psychopy import prefs  
prefs.hardware['audioLib']=['PTB']
prefs.hardware['audioLatencyMode']=3
from psychopy import core, visual, sound, event
import numpy as np
from numpy import random
import sys
import math
sys.path.insert(0, '/home/exp/specl-exp/lib/data5/')
import expLib51 as el
from types import SimpleNamespace

pid=1
sid=1
fname="test"

#expName="dev2"
refreshRate=165
seed= -1

#dbConf=el.beta
#el.setRefreshRate(refreshRate)
#[pid,sid,fname]=el.startExp(expName,dbConf,pool=1,lockBox=False,refreshRate=refreshRate)

fptr=open(fname,"w")
rng = random.default_rng()

scale=400

trialClock=core.Clock()
correctSound1 = sound.Sound(500, secs=0.25)
correctSound2 = sound.Sound(1000, secs=0.25)
errorSound1 = sound.Sound(500, secs=0.5)
errorSound2 = sound.Sound(375, secs=0.5)

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

lParDict={"isCongruent":0,
          "target":0,
          "posTarg":0,          
          "dur":0}
lPar = SimpleNamespace(**lParDict)

def createStim():
    fixX=visual.TextStim(win,"+", height = 30)
    fixL=visual.Rect(win,pos=gPar.pos[0],fillColor=(-1,-1,-1),lineColor=(0,0,0),lineWidth=2,width=50,height=60)
    fixR=visual.Rect(win,pos=gPar.pos[1],fillColor=(-1,-1,-1),lineColor=(0,0,0),lineWidth=2,width=50,height=60)
    cXLR=visual.BufferImageStim(win,stim=(fixX,fixL,fixR))
    box=[fixL,fixR]
    targ=visual.TextStim(win, gPar.let[lPar.target],pos=gPar.pos[lPar.posTarg])
    mask1=visual.TextStim(win, gPar.mask[0],pos=gPar.pos[lPar.posTarg])
    mask2=visual.TextStim(win, gPar.mask[1],pos=gPar.pos[lPar.posTarg])
    return fixX,fixL,fixR,cXLR,box,targ,mask1,mask2

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



def runTrial(lPar,otherTimes):
    frames=[]
    frameDurations=[otherTimes[0],otherTimes[1],lPar.dur,otherTimes[2],otherTimes[3],otherTimes[4]]

    lPar.target = int(rng.integers(0,9,1))
    lPar.posTarg = int(rng.integers(0,2,1))  #0=left, 1=right
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
    stamps=el.runFrames(win,frames,frameDurations,trialClock)
    [resp,rt]=getResp()
    if (resp==lPar.target):
        correctSound1.play()
        correctSound2.play()
    else:
        errorSound1.play()
        errorSound2.play()

    return([resp,rt])

congruentDur =[50]
incongruentDur=[80]

def runBlock(blk,cong,otherTimes,nTrials):
    blockStart(blk,cong)
    lPar.isCongruent=cong

    if lPar.isCongruent==1:
        lPar.dur=congruentDur[-1]
    else:
        lPar.dur=incongruentDur[-1]
    
    numCor=0

    for trl in range(nTrials):
        [resp,rt]=runTrial(lPar,otherTimes)
        print(pid,sid,blk,trl,lPar.isCongruent,lPar.target,lPar.dur,resp,rt,sep=", ", file=fptr)
        print(pid,sid,blk,trl,lPar.isCongruent,lPar.target,lPar.dur,resp,rt)


        if (resp==lPar.target)&(numCor==0):
            numCor+=1
        elif (resp==lPar.target)&(numCor==1):
            if (blk==0) | (blk==1):
                lPar.dur = lPar.dur-5                   #staircase faster for first two blocks
            else:
                lPar.dur = lPar.dur-2
            if lPar.dur<0:
                lPar.dur=0
            numCor=0
        else:
            if (blk==0) | (blk==1):
                lPar.dur = lPar.dur+5
            else:
                lPar.dur = lPar.dur+2
            numCor=0

    if lPar.isCongruent==1:
        congruentDur.append(lPar.dur)
    else:
        incongruentDur.append(lPar.dur)
    
    print(congruentDur)
    print(incongruentDur)


#############
#practice
#############

def fixiateFrame(frame):
    frame[-1].draw()
    win.flip() 

def cuePractice():
    fixX,fixL,fixR,cXLR,box,targ,mask1,mask2=createStim()
    frame = []
    frameTimes=[1,3]
    box[0].lineColor = [1,1,1]
    box[0].lineWidth=10
    cue = visual.BufferImageStim(win, stim=box + [fixX])
    box[0].lineColor = [0,0,0]
    box[0].lineWidth = 2
    frame.append(cue)
    frame.append(visual.BufferImageStim(win,stim=[fixX,fixL,fixR]))
    el.runFrames(win, frame, frameTimes, trialClock)
    fixiateFrame(frame)

def trainFR():
    fixX,fixL,fixR,cXLR,box,targ,mask1,mask2=createStim()

    #start practice
    frame=[]
    frameTimes=[1]
    startP= visual.TextStim(win,"Let's practice walking through the expreiment" \
                            "\n\nPress a key to continue",height=30)
    frame.append(startP)
    el.runFrames(win,frame,frameTimes,trialClock)
    fixiateFrame(frame)
    event.waitKeys()

    #fixation 
    frame = []
    frameTimes=[1]
    text1= visual.TextStim(win,"This is the start screen. " \
                            "This will appear at the start of each trial",pos=(0,200),height=20)
    text2= visual.TextStim(win,"First, one of the boxes will flash white. " \
                            "\nThis is the cue. \n\nClick to see the cue", pos=(0,-200),height=20)
    frame.append(visual.BufferImageStim(win,stim=[text1,text2,fixL,fixR,fixX]))
    el.runFrames(win,frame,frameTimes,trialClock)
    fixiateFrame(frame)
    event.waitKeys()

    #cue 
    cuePractice()
    text3=visual.TextStim(win, "That was the cue." \
                          "Do you want to see it again? (Click Y for yes or N for no)", pos=(0,200),height=20)
    frame.append(visual.BufferImageStim(win,stim=[text3,fixL,fixR,fixX]))
    el.runFrames(win,frame,frameTimes,trialClock)
    fixiateFrame(frame)
    event.waitKeys()


    
###################
###################
###################    



def blockStart(blk,cong):
    if (cong):
        cond = "Same side"
    else:
        cond = "Opposite side"
    message=visual.TextStim(win,f"Block {blk+1}  \n{cond} \n\nPress key to start",height=30)
    message.draw()
    win.flip()
    event.waitKeys()

def startExp():
    message=visual.TextStim(win,"Feeling ready? \n\nNow we will start the experiment blocks. " \
                            "\n\nPress a key to continue.",height=30)
    message.draw()
    win.flip()
    event.waitKeys()

def intro():
    messageIntro=visual.TextStim(win,"Welcome to the experiment! \n\n We will start with some practice blocks." \
                                "\n\n Press any key to begin practicing.",height=30)
    messageIntro.draw()
    win.flip()
    event.waitKeys()


congOrder=[1,0,1,0,0,1]
pracCongOrder=[1,0]
otherTimes=[50,2,16,16,16]
pracOtherTimes=[100,100,100,16,16]
intro()
#trainFR()
startExp()

runBlock(-99,1,pracOtherTimes,10)

blocks=[0,1,2,3,4,5]
for i in range(int(len(blocks))): 
    runBlock(i,congOrder[i],otherTimes,gPar.numTrials)

#hz=round(win.getActualFrameRate())
#[resX,resY]=win.size
win.close()
fptr.close
#el.stopExp(sid,hz,resX,resY,seed,dbConf)
core.quit()

frameDurations=[50,2,lPar.dur,16,16,16]