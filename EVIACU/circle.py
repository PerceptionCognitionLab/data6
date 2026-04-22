from psychopy import monitors, visual, core, event, sound
import random
import math
import sys
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as el
import pandas as pd
import csv

seed = random.randrange(51)
expName = 'EVIACU'
refreshRate = 120
dbConf=el.beta              
el.setRefreshRate(refreshRate)
[pid,_,_]=el.startExp(expName,dbConf,pool=1,lockBox=True,refreshRate=refreshRate)
csv_path = f"E:/data6/EVIACU/Data/{pid}.csv"
data = pd.DataFrame(columns=["TrailNum", "Probability", "OnFrame", "OffFrame", "StartPos", "Truth", "Stimuli", "TerminateFrame", "Response"])
data.to_csv(csv_path, index=False)


#monitor setup
mon = monitors.Monitor("monitor")
mon.setWidth(29.5)
mon.setSizePix((1440,900))
mon.saveMon()   
win = visual.Window(fullscr=True, monitor=mon, units="cm", color=(-1,-1,-1))

#sound setup
CorrectSound = sound.Sound(value=880, secs=0.15)
WrongSound = sound.Sound(value=440, secs=0.15)

#circumference & fixation setup
Radius = 3.0 #cm
AngleDegree = [90, 45, 0, -45, -90, -135, 180, 135]
AngleSpot = len(AngleDegree)
spots = []
for a in AngleDegree:
    rad = math.radians(a)
    x = Radius * math.cos(rad)
    y = Radius * math.sin(rad)
    spots.append((x, y))
Circumference = visual.Circle(win, radius=Radius, lineColor=(1,1,1), fillColor=None, lineWidth=6)

Fixation = visual.TextStim(win, text="+", pos=(0, 0), height=1, color=(1, 1, 1), colorSpace="rgb")

def drawCircle():
    Circumference.draw()
    Fixation.draw()

#coin setup
Coin = 1.6 #cm
Head = visual.ImageStim(win, image="Stimulus/head.jpg", size=(Coin, Coin))
Tail = visual.ImageStim(win, image="Stimulus/tail.jpg", size=(Coin, Coin))
Proability = 0.65

#instruction setup
def showInstructions():
    headLabel = visual.TextStim(
        win,
        text="Head:",
        height=0.6,
        color=(1, 1, 1),
        pos=(-3, 5.5)
    )
    
    tailLabel = visual.TextStim(
        win,
        text="Tail:",
        height=0.6,
        color=(1, 1, 1),
        pos=(3, 5.5)
    )
    
    headDisplay = visual.ImageStim(win, image="Stimulus/head.jpg", size=(2, 2), pos=(-3, 3.5))
    tailDisplay = visual.ImageStim(win, image="Stimulus/tail.jpg", size=(2, 2), pos=(3, 3.5))
    
    instruction = visual.TextStim(
        win,
        text="There is two unfair coins, one is biased towards head and one is biased towards tail.\n"
             "You will see a sequence of coin flips and your task is to figure out which coin is being flipped.\n\n"
             "When you know your answer:\n"
             "Press H if you think the coin is biased towards HEADS\n"
             "Press T if you think the coin is biased towards TAILS\n"
             "Respond as quickly and accurately as possible.\n\n"
             "Press SPACE to begin.",
        height=0.5,
        color=(1, 1, 1),
        wrapWidth=15,
        alignText='left',
        pos=(0, -2)
    )
    
    waiting = True
    while waiting:
        keys = event.getKeys(keyList=['space', 'escape'])
        if keys:
            if 'escape' in keys:
                waiting = False
                win.close()
                core.quit()
            if 'space' in keys:
                waiting = False
        

        headLabel.draw()
        tailLabel.draw()
        headDisplay.draw()
        tailDisplay.draw()
        instruction.draw()
        win.flip()

#trial and stimulus setup 
Hz = 120
OnFrame = [24, 12, 6] #frames [200ms, 100ms, 50ms]
OffFrame = 3 #frames [25ms]
InterBreakFrames = 120 #frames [1000ms]
ShowingPerTrial = 20
Trial = 10
TotalTrials = Trial * len(OnFrame)

#startIdx setup
StartIdx = []
FullBlock = Trial // AngleSpot
Remainder = Trial % AngleSpot
for _ in range(FullBlock):
    block = list(range(AngleSpot))
    random.shuffle(block)
    StartIdx.extend(block)
if Remainder > 0:
    StartIdx.extend(random.sample(list(range(AngleSpot)), Remainder))

#generate single trial event
def generateEvent(trialNum, probability, onFrames, offFrames, startIdx):
    if random.random() < 0.5:
        pHead = probability
        majorLabel = "head"
    else:
        pHead = 1 - probability
        majorLabel = "tail"

    events = []
    currentOnset = 0
    for i in range(ShowingPerTrial):
        onsetFrame = currentOnset
        offsetFrame = onsetFrame + onFrames

        spot = (startIdx + i) % AngleSpot
        position = spots[spot]

        if random.random() < pHead:
            stimulus = Head
            label = "head"
        else:
            stimulus = Tail
            label = "tail"

        events.append({
            "onsetFrame": onsetFrame,
            "offsetFrame": offsetFrame,
            "stimulus": stimulus,
            "position": position,
            "label": label,
            "spotId": spot + 1
        })

        currentOnset = offsetFrame + offFrames

    trialData = {
        "trialNum": trialNum,
        "probability": probability,
        "onFrame": onFrames,
        "offFrame": offFrames,
        "startPos": startIdx,
        "truth": majorLabel,
        "events": events,
        "terminateTrial": None,
        "response": None
    }
    return trialData

#run single trial and return trial data
def trial(trialNum, probability, onFrames, offFrames, startIdx):
    trialData = generateEvent(trialNum, probability, onFrames, offFrames, startIdx)
    events = trialData["events"]
    majorLabel = trialData["truth"]
    
    if events:
        trialFrames = events[-1]["offsetFrame"]
    else:
        trialFrames = 0
    
    #response setup
    response = None
    answered = False
    frameResponded = 20
    
    #trial event loop
    frame = 0
    while frame < trialFrames:
        keys = event.getKeys(keyList=['h','t','escape'])
        if keys:
            if 'escape' in keys:
                win.close()
                core.quit()
            if 'h' in keys:
                response = 'head'
                answered = True
                frameResponded = frame
                break
            if 't' in keys:
                response = 'tail'
                answered = True
                frameResponded = frame
                break
        
        now = frame
        drawCircle()

        #draw stimulus
        for e in events:
            if e["onsetFrame"] <= now < e["offsetFrame"]:
                e["stimulus"].pos = e["position"]
                e["stimulus"].draw()
        win.flip()
        frame += 1
    
    #append response data
    trialData["terminateTrial"] = frameResponded
    trialData["response"] = response

    #sound feedback
    if answered:
        if (response == 'head' and majorLabel == 'head') or (response == 'tail' and majorLabel == 'tail'):
            CorrectSound.play()
        else:
            WrongSound.play()
    else:
        WrongSound.play()
    
    #inter-trial break
    for _ in range(InterBreakFrames):
        drawCircle()
        win.flip()
    
    return trialData

#60 seconds break between trial blocks
def trialBreak():
    BreakTimeText = visual.TextStim(win, text="Break time", height=1, color=(1, 1, 1), wrapWidth=20)
    CountdownText = visual.TextStim(win, text="", height=1.5, color=(1, 1, 1), wrapWidth=20)
    ContinueText = visual.TextStim(win, text="Press SPACE to continue", height=1, color=(1, 1, 1), wrapWidth=20)
    
    #"break time" 120 frames (1secs)
    for frame in range(240):
        BreakTimeText.draw()
        win.flip()
    
    #60secs countdown 720 frames
    countdownFrames = 720
    for frame in range(countdownFrames):
        remainingTime = (countdownFrames - frame) / Hz
        countdownDisplay = f"{remainingTime:.0f}"
        CountdownText.text = countdownDisplay
        
        CountdownText.draw()
        win.flip()
    
    #"press space to continue"
    event.clearEvents(eventType='keyboard')
    waiting = True
    while waiting:
        keys = event.getKeys(keyList=['space', 'escape'])
        if keys:
            if 'escape' in keys:
                win.close()
                core.quit()
            if 'space' in keys:
                waiting = False
        
        ContinueText.draw()
        win.flip()
        

#------
#main
#------
event.clearEvents(eventType='keyboard')

#instruction
showInstructions()

#trials
# print("TrailNum, Probability, OnFrame, OffFrame, StartPos, Truth, Stimuli, TerminateFrame, Response")
for t in range(TotalTrials):
    event.clearEvents(eventType='keyboard')
    
    #fixation
    drawCircle()
    win.flip()
    core.wait(1)

    #determine OnFrame group
    onFrameGroupIndex = t // Trial
    currentOnFrames = OnFrame[onFrameGroupIndex]
    currentOffFrames = OffFrame
    trialIndex = t % len(StartIdx)
    
    trialData = trial(t+1, Proability, currentOnFrames, currentOffFrames, StartIdx[trialIndex])
    stimulusStr = "".join([e["label"][0].upper() for e in trialData["events"]])
    
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([trialData['trialNum'],trialData['probability'],trialData['onFrame'], trialData['offFrame'], trialData['startPos'], trialData['truth'], stimulusStr, trialData['terminateTrial'], trialData['response']])
        f.close()
    # print(f"{trialData['trialNum']}, {trialData['probability']}, {trialData['onFrame']}, {trialData['offFrame']}, {trialData['startPos']}, {trialData['truth']}, {stimulusStr}, {trialData['terminateTrial']}, {trialData['response']}")
    
    #break after each trial block
    if (t + 1) % Trial == 0 and t + 1 < TotalTrials:
        trialBreak()

win.close()
        


