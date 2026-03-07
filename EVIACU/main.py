#source ../.venv/bin/activate
#python3 circle.py

from psychopy import monitors, visual, core, event, sound
import random
import math
import sys
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as el

seed = random.randrange(51)
expName = 'EVIACU'
refreshRate = 165
dbConf=el.beta              
el.setRefreshRate(refreshRate)
[pid,sid,fname]=el.startExp(expName,dbConf,pool=1,lockBox=True,refreshRate=refreshRate)

#monitor setup
mon = monitors.Monitor("monitor")
mon.setWidth(29.5)
mon.setSizePix((1440,900))
mon.saveMon()   
win = visual.Window(fullscr=True, monitor=mon, units="cm", color=(-1,-1,-1))

#circumference setup
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
#fixation setup
Fixation = visual.TextStim(win, text="+", pos=(0, 0), height=1, color=(1, 1, 1), colorSpace="rgb")

def draw_circle():
    Circumference.draw()
    Fixation.draw()

#coin setup
Coin = 1.6 #cm
Head = visual.ImageStim(win, image="Stimulus/head.jpg", size=(Coin, Coin))
Tail = visual.ImageStim(win, image="Stimulus/tail.jpg", size=(Coin, Coin))
Proability = 0.65

#sound setup
CorrectSound = sound.Sound(value=880, secs=0.15)
WrongSound = sound.Sound(value=220, secs=0.15)

#trial and stimulus setup
#400/250, 250/150
Duration = 0.400 #milisec
Overlap = 0.250 #milisec
InterBreak = 2 #seconds
ShowingPerTrial = 20
Trial = 10

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

#trial event setup
def trialShowing(StartIdx):
    #randomness
    if random.random() < 0.5:
        pHead = Proability
        majorLabel = "head"
    else:
        pHead = 1 - Proability
        majorLabel = "tail"

    event = []
    for i in range(ShowingPerTrial):
        onset = i * Overlap
        offset = onset + Duration

        spot = (StartIdx + i) % AngleSpot
        position = spots[spot]

        if random.random() < pHead:
            stimulus = Head
            label = "head"
        else:
            stimulus = Tail
            label = "tail"
            
        event.append({
            "onset": onset,
            "offset": offset,
            "stimulus": stimulus,
            "position": position,
            "label": label,
            "spot_id": spot + 1
        })
    return event, StartIdx, majorLabel
        

#------
#main
#------
draw_circle()
win.flip()
core.wait(1)

for t in range(Trial):
    events, start, majorLabel = trialShowing(StartIdx[t])
    print(f"Trial {t+1}: startIdx={start}, major={majorLabel}")

    #current trial setup
    event.clearEvents(eventType='keyboard')
    trialClock = core.Clock()
    trialEnd = (ShowingPerTrial - 1) * Overlap + Duration

    #response setup
    response = None
    isCorrect = False
    answered = False

    #trial event
    while trialClock.getTime() < trialEnd:
        keys = event.getKeys(keyList=['f','j','escape'])
        if keys:
            if 'escape' in keys:
                win.close()
                core.quit()
            if 'f' in keys:
                response = 'f'
                answered = True
                isCorrect = (majorLabel == 'head')
                break
            if 'j' in keys:
                response = 'j'
                answered = True
                isCorrect = (majorLabel == 'tail')
                print("response received:", keys[0])
                break
        
        now = trialClock.getTime()
        draw_circle()

        #draw stimulus
        for e in events:
            if e["onset"] <= now < e["offset"]:
                e["stimulus"].pos = e["position"]
                e["stimulus"].draw()

        win.flip()

    #feedback
    if answered:
        if isCorrect:
            CorrectSound.play()
            print(f"Trial {t+1}: response={response}, correct")
        else:
            WrongSound.play()
            print(f"Trial {t+1}: response={response}, wrong")
    else:
        WrongSound.play()
        print(f"Trial {t+1}: no response, wrong")
    
    #inter-trial break
    draw_circle()
    win.flip()
    core.wait(InterBreak)



[resX,resY]=win.size
win.close()
el.stopExp(sid, refreshRate, resX, resY, seed, dbConf, 'NA')
        
print(pid)
print(sid)
print(fname)
