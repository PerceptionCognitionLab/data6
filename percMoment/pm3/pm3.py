# Imports
from psychopy import core, visual, sound, event, clock
import math 
import random
import decimal
import sys
import numpy as np  
import os
import time   
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as elib
import support


# Housekeeping
abortKey=['9']
refreshRate=165
elib.setRefreshRate(refreshRate)
expName="pm3"
dbConf=elib.data6
[pid,sid,fname]=elib.startExp(expName,dbConf,pool=1,lockBox=True,refreshRate=refreshRate)
# [pid,sid,fname]=[1,1,'test']
fptr=open(fname,"w")
header=["pid", "block", "taskType", "trialNum", "soa", "stim", "resp", "correct"]
print(*header, sep=' ', file=fptr)
block = 0


win = visual.Window(units="pix", size=(500, 500), color=[-1, -1, -1], fullscr=True)
mouse = event.Mouse(visible=False, newPos=[0,0], win=win) 
trialClock=core.Clock()
correctSound1=sound.Sound(value=500,secs=.1)
correctSound2=sound.Sound(value=1000,secs=.2)
errorSound=sound.Sound(value=300,secs=.5)
seed = random.randrange(1e6)
random.seed(seed)

fix = visual.TextStim(win, "+")  # fixation cross
gPar0={
	'spacing' : 48,
	'sizeIndicator' : [0,1,1,1,0],
	'increment': [1,-1]
}  
gPar=support.initGlobals(gPar0)  # adds x, y, validTarget, N to structure
fix = visual.TextStim(win, "+")  # fixation cross
blank = visual.TextStim(win, "")  # blank window
int_trial = 3



#############
# simultaneous task trial
#############

def runTrial(dur, stimCode):
    stim=[]
    #stim.append(visual.Circle(win, pos=(-136,0.0), fillColor=[1, 1, 1], radius=4))
    stim.append(visual.Circle(win, pos=(-96,0.0), fillColor=[1, 1, 1], radius=7.5))
    stim.append(visual.Circle(win, pos=(96,0.0), fillColor=[1, 1, 1], radius=7.5))
    both=visual.BufferImageStim(win,stim=stim)
    stim.append(both)
    blank = visual.TextStim(win, '', pos = (0.0,0.0))
    option = []
    #option.append(visual.TextBox2(win, text = "Different", size=(1.8,.1), pos=(-120,240)))
    #option.append(visual.TextBox2(win, text = "Same", size=(1.8,.1), pos=(-100,-280)))
    option.append(visual.TextBox2(win, text = "Different", size=(800,400), pos=(330,240), letterHeight=30))
    option.append(visual.TextBox2(win, text = "Same", size=(800,400), pos=(350,-280), letterHeight=30))
    options=visual.BufferImageStim(win,stim=option)

    frames = [fix, blank, stim[stimCode], blank, both, options] # wait a sec before mouse appears
    frameTimes = [60,60, 1, dur, 1, 1]

    stamps=elib.runFrames(win,frames,frameTimes,trialClock)
    critTime=elib.actualFrameDurations(frameTimes,stamps)[3]
    critPass=(np.absolute(dur/refreshRate-critTime)<.001)
    resp=support.mouseResponse2(mouse,win,frames[5])
    return(resp)
    
    '''
    stamps=elib.runFrames(win, frames, frameTimes, trialClock, addBlank=False)
    event.waitKeys()
    #exit(1)
    keys = event.waitKeys(timeStamped=trialClock, 
                          keyList=['x', 'm', '9'])
    resp=1
    if keys[0][0]=='x':
        resp=0
    return(resp)
    # resp "1/m" means same and "0/x" is different
    '''

#############
# fusion task trial
#############

def integrationTrial(soa,gPar):
	[x,y]=[gPar['x'],gPar['y']]
	target= random.choice(gPar['validTarget'])
	[aDots, bDots]=support.intDotIndex(gPar,target)
	dots=[]
	for i in range(gPar['N']):
		dots.append(visual.Circle(win, pos=(x[i],y[i]), fillColor=[0, -1, -1], radius=2.5))
	allRed=visual.BufferImageStim(win,stim=dots)
	adots=[]
	alldots=[]
	for i in range(len(aDots)):
		adots.append(visual.Circle(win, pos=(x[aDots[i]],y[aDots[i]]), fillColor=[1, 1, 1], radius=5))
		alldots.append(visual.Circle(win, pos=(x[aDots[i]],y[aDots[i]]), fillColor=[1, 1, 1], radius=5))
	a=visual.BufferImageStim(win,stim=adots)
	bdots=[]
	for i in range(len(bDots)):
		bdots.append(visual.Circle(win, pos=(x[bDots[i]],y[bDots[i]]), fillColor=[1, 1, 1], radius=5))
		alldots.append(visual.Circle(win, pos=(x[bDots[i]],y[bDots[i]]), fillColor=[1, 1, 1], radius=5))
	b=visual.BufferImageStim(win,stim=bdots)
	frame = [fix, blank, a, blank, b, blank, allRed]
	frameDurations = [120, 60, 5, soa, 5, 60, 1]

	stamps=elib.runFrames(win,frame,frameDurations,trialClock)
	critTime=elib.actualFrameDurations(frameDurations,stamps)[3]
	critPass=(np.absolute(soa/refreshRate-critTime)<.001)
	resp=support.mouseResponse(mouse,win,gPar,frame[6])
	correct=target==resp
	#support.feedback("correct")
	return([target,resp,correct,np.round(critTime,4),critPass])


#############
# staircase
#############

def runSimult(trialNum, block, prac=False):
    counter = 0
    dur = 6
    for i in range(trialNum):
        trialNum = i
        stim = random.choice([0,2])
        if stim == 0:
            stim = random.choice([0,1])
        resp=runTrial(dur,stim)
        #print(resp)
        info=[pid, block, 'Simult', trialNum+1,  dur, stim, resp]
        if info[5]==2:
            info[5] = 1
        else:
            info[5] = 0
        if info[5]==info[6]:
            correct = True
        else:
            correct = False
        info.append(correct)
        if not prac:
            print(*info, sep=' ', file=fptr)
        # staircase
        if (correct)&(counter==0): #simplify this now?
            counter+=1
            support.feedback("correct")
            if prac:
                feedback_text = 'Correct!'
                visual.TextStim(win, text=feedback_text, pos=(0, 0)).draw()
                win.flip()
                core.wait(1)  # Display feedback for 1 second
        elif (correct)&(counter==1):
            support.feedback("correct")
            dur = dur-2
            if dur<0:
                dur=0
            counter=0
            if prac:
                feedback_text = 'Correct!'
                visual.TextStim(win, text=feedback_text, pos=(0, 0)).draw()
                win.flip()
                core.wait(1)  # Display feedback for 1 second
        else:
            support.feedback("incorrect")
            dur = dur+2
            if dur>8:
                dur=8
            counter=0
            if prac:
                feedback_text = 'Inorrect!'
                visual.TextStim(win, text=feedback_text, pos=(0, 0)).draw()
                win.flip()
                core.wait(1)  # Display feedback for 1 second

def runInteg(trialNum, block, prac=False):
    counter = 0
    soa = 6
    for i in range(trialNum):
        trialNum = i
        resp=integrationTrial(soa,gPar)
        #print("target,resp,correct",resp[0],resp[1],resp[2])
        info=[pid, block, 'Integ', trialNum+1,  soa, resp[0], resp[1], resp[2]]
        if not prac:
            print(*info, sep=' ', file=fptr)
        # staircase
        if (info[7]==True)&(counter==0):
            support.feedback("correct")
            counter+=1
            if prac:
                feedback_text = 'Correct!'
                visual.TextStim(win, text=feedback_text, pos=(0, 0)).draw()
                win.flip()
                core.wait(1)  # Display feedback for 1 second
        elif (info[7]==True)&(counter==1):
            support.feedback("correct")
            soa = soa+2
            if soa>8:
                soa=8
            counter=0
            if prac:
                feedback_text = 'Correct!'
                visual.TextStim(win, text=feedback_text, pos=(0, 0)).draw()
                win.flip()
                core.wait(1)  # Display feedback for 1 second
        else:
            support.feedback("incorrect")
            soa = soa-1
            if soa<1:
                soa=1
            counter=0
            if prac:
                feedback_text = 'Inorrect!'
                visual.TextStim(win, text=feedback_text, pos=(0, 0)).draw()
                win.flip()
                core.wait(1)  # Display feedback for 1 second
        

#############

# Easy Practice Trials
def practiceInteg(soa):
    for i in range(4):
        resp=integrationTrial(soa,gPar)
        if (resp[2]==True):
            support.feedback("correct")
            feedback_text = 'Correct!'
            visual.TextStim(win, text=feedback_text, pos=(0, 0)).draw()
            win.flip()
            core.wait(1)  # Display feedback for 1 second
       # Display feedback for 1 second
        else:
            support.feedback("incorrect")
            feedback_text = 'Inorrect!'
            visual.TextStim(win, text=feedback_text, pos=(0, 0)).draw()
            win.flip()
            core.wait(1)  # Display feedback for 1 second
            
def practiceSimult(soa):
    for i in range(4):
        stim = random.choice([0,2])
        if stim == 0:
            stim = random.choice([0,1])
        resp=runTrial(soa,stim)
        if stim ==2:
            stim = 1
        else:
            stim = 0
        # staircase
        if (stim==resp):
            support.feedback("correct")
            feedback_text = 'Correct!'
            visual.TextStim(win, text=feedback_text, pos=(0, 0)).draw()
            win.flip()
            core.wait(1)  # Display feedback for 1 second
        else:
            support.feedback("incorrect")
            feedback_text = 'Inorrect!'
            visual.TextStim(win, text=feedback_text, pos=(0, 0)).draw()
            win.flip()
            core.wait(1)  # Display


#############
# Experiment and Instruction

support.instruct(win,"Welcome to the experiment! \n\nPress spacebar to continue.")
# practice trials
support.instruct(win,"Let's begin with some practice. We will provide feedback on correctness.\n\nPress space to start the practice trials.")
practiceInteg(1)
practiceInteg(3)
support.instruct(win,"Good, now the practice will get a little bit harder. \n\nPress spacebar to continue.")
runInteg(6, 0, prac=True)
support.instruct(win,"Now we will practice the second task. \n\nPress spacebar to continue.")
practiceSimult(8)
practiceSimult(6)
support.instruct(win,"Good, now the practice will get a little bit harder again. \n\nPress spacebar to continue.")
runSimult(6, 0, prac=True)
# start trials
support.instruct(win,"Practice finished.\n\nPress space to start the first trial.")
runInteg(50, 1)
support.instruct(win,"Great. Now we'll start the second trial. \n\nPress space to start the trials.")
runSimult(50, 2)
support.instruct(win,"Session 1 finished! You can have some rest before starting session 2.\n\nPress spacebar to start session 2.")
support.instruct(win,"Press space to start the next trial.")
runInteg(50, 3)
support.instruct(win,"Great. Now we'll start the next trial. \n\nPress space to start the trials.")
runSimult(50, 4)
support.instruct(win,"Session 2 finished! You can have some rest before starting the last session.\n\nPress spacebar to start session 3.")
support.instruct(win,"Press space to start the next trial.")
runInteg(50, 5)
support.instruct(win,"Great. Now we'll start the last trial. \n\nPress space to start.")
runSimult(50,6)


fptr.close()
concern = elib.getConcern(win)
[resX,resY]=win.size
win.close()
elib.stopExp(sid, refreshRate, resX, resY, seed, dbConf, concern)
core.quit()
