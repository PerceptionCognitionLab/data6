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
expName="pm3Test"
dbConf=elib.beta
[pid,sid,fname]=elib.startExp(expName,dbConf,pool=1,lockBox=True,refreshRate=refreshRate)
#[pid,sid,fname]=[1,1,'test']
fptr=open(fname,"w")


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
    stim.append(visual.Circle(win, pos=(-136,0.0), fillColor=[1, 1, 1], radius=4))
    stim.append(visual.Circle(win, pos=(96,0.0), fillColor=[1, 1, 1], radius=4))
    both=visual.BufferImageStim(win,stim=stim)
    stim.append(both)
    blank = visual.TextStim(win, '', pos = (0.0,0.0))
    option = []
    #option.append(visual.TextBox2(win, text = "Different", size=(1.8,.1), pos=(-120,240)))
    #option.append(visual.TextBox2(win, text = "Same", size=(1.8,.1), pos=(-100,-280)))
    option.append(visual.TextBox2(win, text = "Different", size=(800,400), pos=(300,240), letterHeight=30))
    option.append(visual.TextBox2(win, text = "Same", size=(800,400), pos=(330,-280), letterHeight=30))
    options=visual.BufferImageStim(win,stim=option)

    frames = [fix, blank, stim[stimCode], blank, both, options]
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
def runSimult(trialNum, prac=False):
    if not prac:
        header=["trialNum", "dur", "stim", "resp"]
        print(*header, sep=' ', file=fptr)
    counter = 0
    dur = 6
    for i in range(trialNum):
        trialNum = i
        stim = random.choice([0,2])
        if stim == 0:
            stim = random.choice([0,1])
        resp=runTrial(dur,stim)
        #print(resp)
        info=[trialNum, dur, stim, resp]
        if info[2]==2:
            info[2] = 1
        else:
            info[2] = 0
        print(*info, sep=' ', file=fptr)
        # staircase
        if (info[2]==info[3])&(counter==0):
            counter+=1
            support.feedback("correct")
            if prac:
                feedback_text = 'Correct!'
                visual.TextStim(win, text=feedback_text, pos=(0, 0)).draw()
                win.flip()
                core.wait(1)  # Display feedback for 1 second
        elif (info[2]==info[3])&(counter==1):
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

def runInteg(trialNum, prac=False):
    counter = 0
    soa = 6
    for i in range(trialNum):
        trialNum = i
        resp=integrationTrial(soa,gPar)
        #print("target,resp,correct",resp[0],resp[1],resp[2])
        info=[trialNum, soa, resp[2]]
        print(*info, sep=' ', file=fptr)
        # staircase
        if (info[2]==True)&(counter==0):
            support.feedback("correct")
            counter+=1
            if prac:
                feedback_text = 'Correct!'
                visual.TextStim(win, text=feedback_text, pos=(0, 0)).draw()
                win.flip()
                core.wait(1)  # Display feedback for 1 second
        elif (info[2]==True)&(counter==1):
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
            if soa<0:
                soa=0
            counter=0
            if prac:
                feedback_text = 'Inorrect!'
                visual.TextStim(win, text=feedback_text, pos=(0, 0)).draw()
                win.flip()
                core.wait(1)  # Display feedback for 1 second
        

#############

# Easy Practice Trials
def practiceInteg(soa):
    for i in range(2):
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
        
practiceInteg(2)

'''
#############

# Experiment and Instructions

#Task 1: Integration
support.instruct(win,"Welcome to the experiment! \n\nPress spacebar to continue.")
support.instruct(win,"In this session, a gird of white dots will appear in two seperate flashes. Your task is to identify the dot that is missing.\n\nWhen all of the dots turn red, click the dot that you think was missing.\n\nPress spacebar to continue")
support.instruct(win,"Let's begin with some practice. We will provide feedback on correctness.\n\nPress space to start the practice trials.")
runInteg(5, prac=True ) #turn this into a practice trial
support.instruct(win,"Practice finished.\n\nPress space to start the trials.")
runInteg(5)
support.instruct(win,"Session 1 finished! You can have some rest before starting session 2.\n\nPress spacebar to start session 2.")

#Task 2: Simultaneous
support.instruct(win,"In this session, two white dots will appear side by side. Your task is to identify if both dots appeared at the same time or if one appeared before the other.\n\nIf you think they appeared at the same time. press 'same'. If you think one of them appeared first, press 'different'.\n\nPress spacebar to continue")
support.instruct(win,"Let's begin with some practice. We will provide feedback on correctness.\n\nPress space to start the practice trials.")
runSimult(5, prac=True) #turn this into a practice trial
support.instruct(win,"Practice finished.\n\nPress space to start the trials.")
runSimult(5)

support.instruct(win,"Experiment finished. Thank you for your participation! :) \n\nPress spacebar to exit")
'''

fptr.close()
win.close()
core.quit()