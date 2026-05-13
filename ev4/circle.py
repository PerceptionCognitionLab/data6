from psychopy import monitors, visual, core, event, sound
import random
import math
import sys
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as el
import pandas as pd
import csv
import numpy as np
import pyxid2
import time

seed = random.randrange(51)
rng = np.random.default_rng(seed)

#file setup
expName = 'EVIACU'
refreshRate = 120
dbConf=el.beta              
el.setRefreshRate(refreshRate)
[pid,sid,fname]=el.startExp(expName,dbConf,pool=1,lockBox=True,refreshRate=refreshRate)
csv_path = f"E:/data6/ev4/Data/ev4p{pid}s{sid}.csv"
XCols = [f"x{i+1}" for i in range(20)]
data = pd.DataFrame(columns=["pid", "sid", "trl", "cond", "start", "isHead", *XCols, "rt", "resp"])
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
OnFrame = [18, 12, 9] #frames [150ms, 100ms, 75ms]
OffFrame = 3 #frames [25ms]
InterBreakFrames = 120 #frames [1000ms]
ShowingPerTrial = 20
Trial = 1
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
def generateEvent(trialCount, onFrames, startIdx):
    if random.random() < 0.5:
        pHead = Proability
        isHead = 1
    else:
        pHead = 1 - Proability
        isHead = 0

    events = []
    currentOnset = 0
    for i in range(ShowingPerTrial):
        onsetFrame = currentOnset
        offsetFrame = onsetFrame + onFrames

        spot = (startIdx + i) % AngleSpot
        position = spots[spot]

        if random.random() < pHead:
            stimulus = Head
            label = 1
        else:
            stimulus = Tail
            label = 0

        events.append({
            "onsetFrame": onsetFrame,
            "offsetFrame": offsetFrame,
            "stimulus": stimulus,
            "position": position,
            "label": label,
            "spotId": spot + 1
        })

        currentOnset = offsetFrame + OffFrame

    trialData = {
        "trial": trialCount,
        "startPos": startIdx,
        "isHead": isHead,
        "events": events,
        "terminateTrial": None,
        "response": None
    }
    return trialData

#get stimulus at terminate frame
def getStimulus(events, frame):
    for idx, e in enumerate(events):
        if e["onsetFrame"] <= frame <= e["offsetFrame"]:
            return idx + 1
    return 20

#run single trial and return trial data
def trial(trialCount, onFrames, startIdx):
    trialData = generateEvent(trialCount, onFrames, startIdx)
    events = trialData["events"]
    isHead = trialData["isHead"]
    
    if events:
        trialFrames = events[-1]["offsetFrame"]
    else:
        trialFrames = 0
    
    #response setup
    response = None
    answered = False
    stimulusResponded = None
    
    #trial event loop
    frame = 0
    while frame < trialFrames:
        keys = event.getKeys(keyList=['h','t','escape'])
        if keys:
            if 'escape' in keys:
                win.close()
                core.quit()
            if 'h' in keys:
                response = 1
                answered = True
                stimulusResponded = getStimulus(events, frame)
                break
            if 't' in keys:
                response = 0
                answered = True
                stimulusResponded = getStimulus(events, frame)
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
    trialData["terminateStimulus"] = stimulusResponded
    trialData["response"] = response

    #sound feedback
    if answered:
        if (response == 1 and isHead == 1) or (response == 0 and isHead == 0):
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
    BreakTimeText = visual.TextStim(win, text="Break Time", height=1, color=(1, 1, 1), wrapWidth=20)
    CountdownText = visual.TextStim(win, text="", height=1.5, color=(1, 1, 1), wrapWidth=20)
    ContinueText = visual.TextStim(win, text="Press SPACE to continue", height=1, color=(1, 1, 1), wrapWidth=20)
    
    #breaktime 120 frames (1secs)
    for frame in range(120):
        BreakTimeText.draw()
        win.flip()
    
    #60secs countdown 7200 frames
    countdownFrames = 1
    for frame in range(countdownFrames):
        remainingTime = (countdownFrames - frame) / refreshRate
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
        
def getConcern():
    thankyou = visual.TextStim(win, text="Experiment ends. \nPlease contact the experimenter!", height=1, color=(1, 1, 1), wrapWidth=20)
    thankyou.draw()
    win.flip()
    event.waitKeys(keyList=["space"])
    
    question = visual.TextStim(win, text="Experimenter notes: ", pos=(0, 5), height=1, color=(1, 1, 1), wrapWidth=20)
    answer = visual.TextStim(win, text="", height=1, color=(1, 1, 1), wrapWidth=20)

    typedAnswer = ""

    while True:
        keys = event.getKeys()
        for key in keys:
            if 'escape' in keys:
                win.close()
                core.quit()
            elif key == "return":
                break
            elif key == "backspace":
                typedAnswer = typedAnswer[:-1]
            elif key == "space":
                typedAnswer += " "
            elif len(key) == 1:
                typedAnswer += key
        if "return" in keys:
            break
        answer.text = typedAnswer
        question.draw()
        answer.draw()
        win.flip()
    
    concernText = typedAnswer
    return concernText


#------
#main
#------
event.clearEvents(eventType='keyboard')

#instruction
showInstructions()

#trials
condition = []
for t in range(TotalTrials):
    event.clearEvents(eventType='keyboard')
    
    #fixation
    drawCircle()
    win.flip()
    core.wait(1)

    #determine OnFrame group
    onFrameGroupIndex = t // Trial
    currentOnFrames = OnFrame[onFrameGroupIndex]
    trialIndex = t % len(StartIdx)
    
    #determine condition group
    if currentOnFrames not in condition:
        condition.append(currentOnFrames)
    conditionCount = condition.index(currentOnFrames) + 1
    
    trialData = trial(t+1, currentOnFrames, StartIdx[trialIndex])
    stimulusStr = [e["label"] for e in trialData["events"]]
    
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([pid, sid, trialData['trial'], conditionCount, trialData['startPos']+1, trialData['isHead'], *stimulusStr, trialData['terminateStimulus'], trialData['response']])
        f.close()
    
    #break after each trial block
    if (t + 1) % Trial == 0 and t + 1 < TotalTrials:
        trialBreak()

concern = getConcern()
[resX,resY]=win.size
win.close()
el.stopExp(sid, refreshRate, resX, resY, seed, dbConf, concern)
core.quit()
        
