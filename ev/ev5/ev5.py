import pyxid2

#device setup
Device = pyxid2.get_xid_devices()
print(Device)
Dev = Device[0]
EscapeKey = 0
Resp1Key = 3
Resp0Key = 4
SpaceKey = 5
def getPadKeys(validKeys = None):
    Dev.poll_for_response()
    if Dev.has_response():
        keyResponse = Dev.get_next_response()
        if keyResponse['pressed']:
            key = keyResponse["key"]
            if key in validKeys:
                return key
    return None

def getPadKeysTime(validKeys = None):
    Dev.poll_for_response()
    if Dev.has_response():
        keyResponse = Dev.get_next_response()
        if keyResponse['pressed']:
            key = keyResponse["key"]
            if key in validKeys:
                return key, keyResponse["time"]
    return None, None

from psychopy import monitors, visual, core, sound
import random
import math
import pandas as pd
import csv
import numpy as np
import sys
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as el

seed = random.randrange(51)
rng = np.random.default_rng(seed)

#file setup
expName = 'ev5'
refreshRate = 120
dbConf=el.data6              
el.setRefreshRate(refreshRate)
[pid,sid,fname]=el.startExp(expName,dbConf,pool=3,lockBox=True,refreshRate=refreshRate)
csv_path = fname.removesuffix(".dat") + ".csv"
XCols = [f"x{i+1}" for i in range(50)]
data = pd.DataFrame(columns=["pid", "sid", "probHead", "trl",  "isHead", *XCols, "rt", "resp"])
data.to_csv(csv_path, index=False)


#monitor setup
mon = monitors.Monitor("monitor")
mon.setWidth(29.5)
mon.setSizePix((1440,900))
mon.saveMon()   
win = visual.Window(fullscr=True, monitor=mon, units="cm", color=(-1,-1,-1))

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

def drawFixation():
    Fixation.draw()
def drawCircle():
    Circumference.draw()

#coin setup
Coin = 1.6 #cm
Head = visual.ImageStim(win, image="Stimulus/head.jpg", size=(Coin, Coin))
Tail = visual.ImageStim(win, image="Stimulus/tail.jpg", size=(Coin, Coin))

#trial and stimulus setup 
OnFrame = [15, 15, 15, 15] #frames [125ms]
OffFrame = 3 #frames [25ms]
InterBreakFrames = 120 #frames [1000ms]
ShowingPerTrial = 50
Block = [50, 50, 50, 50]
TotalTrials = sum(Block)

#feedback setup
CorrectSound = sound.Sound(value=880, secs=0.15)
WrongSound = sound.Sound(value=440, secs=0.15)
Feedback = visual.TextStim(win, text="", pos=(0, 0), height=0.8, color=(1, 1, 1))

#instruction
def practiceInstruction():
    instruction = visual.TextStim(
        win,
        text="There is an anteater coin with its head and tail shown above.\n"
             "You will see one side of the coin shown at a random place on a circle.\n"
             "Press the button on the key pad accordingly.\n"
             "Press → to begin.",
        height=0.5,
        color=(1, 1, 1),
        wrapWidth=15,
        alignText='left',
        pos=(0, -2)
    )
    
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
    
    Dev.flush_serial_buffer()
    waiting = True
    while waiting:
        key = getPadKeys([SpaceKey, EscapeKey])
        if key == EscapeKey:
            win.close()
            core.quit()
        elif key == SpaceKey:
            waiting = False

        instruction.draw()
        headLabel.draw()
        tailLabel.draw()
        headDisplay.draw()
        tailDisplay.draw()
        win.flip()
        

def trialInstruction():
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
        text="One biased coin is being flipped many times.\n"
             "Your job is to determine which side the coin is biased towards based on the coin flips you see.\n"
             "When you know your answer, press the button on the key pad accordingly.\n"
             "Once you answer, a new biased coin will be flipped and the process repeats.\n\n"
             "Respond as quickly and accurately as possible.\n"
             "Press → to begin.",
        height=0.5,
        color=(1, 1, 1),
        wrapWidth=15,
        alignText='left',
        pos=(0, -2)
    )
    
    Dev.flush_serial_buffer()
    waiting = True
    while waiting:
        key = getPadKeys([SpaceKey, EscapeKey])
        if key == EscapeKey:
            win.close()
            core.quit()
        elif key == SpaceKey:
            waiting = False
        headLabel.draw()
        tailLabel.draw()
        headDisplay.draw()
        tailDisplay.draw()
        instruction.draw()
        win.flip()

#generate probabilities for each block
def generateProbabilities():
    probs = []
    for b, blockSize in enumerate(Block):
        initial = (
            [0.65] * 5 +
            [0.35] * 5
        )
        random.shuffle(initial)
        probs.extend(initial)
        if blockSize > 10:
            extra = (
                #[0.50] * int(blockSize * 0.2) +
                [0.00] * 1 +
                [1.00] * 1
            )
            remainder = blockSize - len(initial) - len(extra)
            extra.extend(
                [0.65] * (remainder // 2) +
                [0.35] * (remainder // 2)
            )
            if remainder % 2:
                extra.append(random.choice([0.65, 0.35]))
            random.shuffle(extra)
            probs.extend(extra)
    return probs

#generate spots for each trial
def generateSpots(nTrials):
    spotOrder = []
    while len(spotOrder) < nTrials:
        block = list(range(AngleSpot))
        random.shuffle(block)
        spotOrder.extend(block)
    return spotOrder[:nTrials]

#generate showing for each trial
def generateShowings(trialCount, onFrames, pHead):
    positionOrder = generateSpots(ShowingPerTrial)
    events = []
    currentOnset = 0
    for i in range(ShowingPerTrial):
        onsetFrame = currentOnset
        offsetFrame = onsetFrame + onFrames
        spot = positionOrder[i]
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

    if pHead == 0.65 or pHead == 1:
        isHead = 1
    elif pHead == 0.35 or pHead == 0:
        isHead = 0
    else:
        isHead = 0.5
    trialData = {
        "trial": trialCount,
        "probHead": pHead,
        "isHead": isHead,
        "events": events,
        "terminateStimulus": None,
        "response": None
    }
    return trialData

#get stimulus at terminate frame
def getStimulus(events, responseTime):
    for idx, e in enumerate(events):
        onset = e["onsetFrame"] / refreshRate * 1000
        offset = e["offsetFrame"] / refreshRate * 1000
        if onset <= responseTime <= offset:
            return idx + 1
        if responseTime < onset:
            return idx
    return len(events)

def generateFeedback(trialData, response):
    probHead = trialData["probHead"]
    events = trialData["events"]
    terminateStimulus = trialData["terminateStimulus"]

    correct = None
    # biased coin
    if probHead > 0.5 or probHead < 0.5:
        if probHead > 0.5:
            correctAnswer = 1
        else:
            correctAnswer = 0
        if response == correctAnswer:
            correct = True
    # fair coin (NEED DISCUSSION)
    elif probHead == 0.5:
        evidence = 0
        for i in range(terminateStimulus):
            if events[i]["label"] == 1:
                evidence += 1
            else:
                evidence -= 1
        if evidence > 0:
            correctAnswer = 1
        elif evidence < 0:
            correctAnswer = 0
        else:
            correctAnswer = None
        if correctAnswer is not None and response == correctAnswer:
            correct = True

    if correct:
        Feedback.text = "✓"
        Feedback.color = (0, 1, 0)
        CorrectSound.play()

    else:
        Feedback.text = "X"
        Feedback.color = (1, 0, 0)
        WrongSound.play()

#pratice trial to test response time
def practice(nTrials=20):
    practiceSpots = generateSpots(nTrials)
    for _ in range(InterBreakFrames):
        drawFixation()
        drawCircle()
        win.flip()
    
    for p in range(nTrials):
        if random.random() < 0.5:
            stimulus = Head
            correctResponse = 1
        else:
            stimulus = Tail
            correctResponse = 0
        spot = practiceSpots[p]
        position = spots[spot]

        Dev.flush_serial_buffer()
        Dev.reset_timer()
        for frame in range(15):
            drawCircle()
            drawFixation()
            stimulus.pos = position
            stimulus.draw()
            win.flip()
          
        responded = False
        response = None
        responseTime = None
        while not responded:
            key, responseTime = getPadKeysTime([EscapeKey, Resp1Key, Resp0Key])
            if key == EscapeKey:
                win.close()
                core.quit()
            elif key == Resp1Key:
                response = 1
                responded = True
            elif key == Resp0Key:
                response = 0
                responded = True
            drawCircle()
            drawFixation()
            win.flip()
        if response == correctResponse:
            Feedback.text = "✓"
            Feedback.color = (0, 1, 0)
            CorrectSound.play()
        else:
            Feedback.text = "X"
            Feedback.color = (1, 0, 0)
            WrongSound.play()
        for _ in range(InterBreakFrames):
            drawCircle()
            Feedback.draw()
            win.flip()

        stimulusStr = [""] * 50

        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                pid,
                sid,
                -0.5,
                p + 1,
                correctResponse,
                *stimulusStr,
                responseTime, # keypad ms
                response
            ])

#run single trial and return trial data
def trial(trialCount, onFrames, pHead):
    trialData = generateShowings(trialCount, onFrames, pHead)
    events = trialData["events"]
    
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
    Dev.flush_serial_buffer()
    Dev.reset_timer()
    while frame < trialFrames:
        key, responseTime = getPadKeysTime([EscapeKey, Resp1Key, Resp0Key])
        if key == EscapeKey:
            win.close()
            core.quit()
        if key == Resp1Key:
            response = 1
            answered = True
            stimulusResponded = getStimulus(events, responseTime)
            break
        if key == Resp0Key:
            response = 0
            answered = True
            stimulusResponded = getStimulus(events, responseTime)
            break    
        now = frame
        drawCircle()
        drawFixation()

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
       generateFeedback(trialData, response)
    else:
        Feedback.text = "X"
        Feedback.color = (1, 0, 0)
        WrongSound.play()
    
    #inter-trial break
    for _ in range(InterBreakFrames):
        drawCircle()
        Feedback.draw()
        win.flip()
    
    return trialData

#60 seconds break between trial blocks
def trialBreak():
    BreakTimeText = visual.TextStim(win, text="Break Time", height=1, color=(1, 1, 1), wrapWidth=20)
    CountdownText = visual.TextStim(win, text="", height=1.5, color=(1, 1, 1), wrapWidth=20)
    ContinueText = visual.TextStim(win, text="Continue →", height=1, color=(1, 1, 1), wrapWidth=20)
    
    #breaktime 120 frames (1secs)
    for frame in range(120):
        BreakTimeText.draw()
        win.flip()
    
    #60secs countdown 7200 frames
    countdownFrames = 7200
    for frame in range(countdownFrames):
        remainingTime = (countdownFrames - frame) / refreshRate
        countdownDisplay = f"{remainingTime:.0f}"
        CountdownText.text = countdownDisplay
        
        CountdownText.draw()
        win.flip()
    
    Dev.flush_serial_buffer()
    waiting = True
    while waiting:
        key = getPadKeys([SpaceKey, EscapeKey])
        if key == EscapeKey:
            win.close()
            core.quit()
        if key == SpaceKey:
            waiting = False
        ContinueText.draw()
        win.flip()
        
def getConcern():
    thankyou = visual.TextStim(win, text="Experiment ends. \nPlease contact the experimenter!", height=1, color=(1, 1, 1), wrapWidth=20)
#    thankyou.draw()
#    win.flip()
#    event.waitKeys(keyList=["space"])
    
#    question = visual.TextStim(win, text="Experimenter notes: ", pos=(0, 5), height=1, color=(1, 1, 1), wrapWidth=20)
#    answer = visual.TextStim(win, text="", height=1, color=(1, 1, 1), wrapWidth=20)

    typedAnswer = ""

#    while True:
#        keys = event.getKeys()
#        for key in keys:
#            if 'escape' in keys:
#                win.close()
#                core.quit()
#            elif key == "return":
#                break
#            elif key == "backspace":
#                typedAnswer = typedAnswer[:-1]
#            elif key == "space":
#                typedAnswer += " "
#            elif len(key) == 1:
#                typedAnswer += key
#        if "return" in keys:
#            break
#        answer.text = typedAnswer
#        question.draw()
#        answer.draw()
#        win.flip()
    

    Dev.flush_serial_buffer()
    waiting = True
    while waiting:
        key = getPadKeys([SpaceKey, EscapeKey])
        if key == EscapeKey:
            win.close()
            core.quit()
        if key == SpaceKey:
            waiting = False
        thankyou.draw()
        win.flip()
    concernText = typedAnswer
    return concernText


#------
#main
#------
Dev.flush_serial_buffer()
win.mouseVisible = False
#pratice
practiceInstruction()
practice()
#trials
trialInstruction()
Probabilities = generateProbabilities()
cumulativeTrials = np.cumsum(Block)
for t in range(TotalTrials):
    Dev.flush_serial_buffer()
    
    #fixation
    drawCircle()
    drawFixation()
    win.flip()
    core.wait(1)

    #determine OnFrame group
    onFrameGroupIndex = np.searchsorted(cumulativeTrials, t, side="right")
    currentOnFrames = OnFrame[onFrameGroupIndex]
    
    currentPHead = Probabilities[t]
    trialData = trial(t+1, currentOnFrames, currentPHead)
    stimulusStr = [e["label"] for e in trialData["events"]]
    
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([pid, sid, trialData['probHead'], trialData['trial'], trialData['isHead'], *stimulusStr, trialData['terminateStimulus'], trialData['response']])
        f.close()
    
    #break after each trial block
    if (t + 1) in cumulativeTrials[:-1]:
        trialBreak()
#pratice
practiceInstruction()
practice()

concern = getConcern()
[resX,resY]=win.size

Dev.con.flush()
Dev.con.close()
win.close()
el.stopExp(sid, refreshRate, resX, resY, seed, dbConf, concern)
core.quit()
        
