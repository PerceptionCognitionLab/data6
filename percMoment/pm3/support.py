from psychopy import core, visual, sound, event, clock
import random
import numpy as np


correct1 = sound.Sound(500,secs = .1) # correct response
correct2 = sound.Sound(1000,secs = .2)
error1 = sound.Sound(value=300,secs=.5)

def feedback(correct):
        if correct == "correct":
                correct1.play()
                correct2.play()
        else:
            error1.play()

def initGlobals(gPar0):

        def makeCoord(size,spacing):
                x = []
                y = []
                for i in range(size*size):
                        result = divmod(i, size)
                        x.append(spacing * (result[0] - (size-1)/2))
                        y.append(spacing * (result[1] - (size-1)/2))
                return([x,y])

        def makeValidTarget(sizeIndicator):
                validTarget=[]
                size=len(sizeIndicator)
                for i in range(size*size):
                        result=divmod(i, size)
                        if sizeIndicator[result[0]] ==1 and sizeIndicator[result[1]] ==1:
                                validTarget.append(i)
                return(validTarget)

        gPar=gPar0
        gPar['size']=len(gPar['sizeIndicator'])
        [x,y]=makeCoord(gPar['size'],gPar['spacing'])
        gPar['x']=x
        gPar['y']=y
        gPar['validTarget']=makeValidTarget(gPar['sizeIndicator'])
        gPar['N']=len(x)
        return(gPar)


def mouseOnResp(x, y, mousePos, crit=20):
    dlc = []
    for i in range(len(x)):
        dist = np.linalg.norm([x[i], y[i]] - mousePos)
        dlc.append(dist < crit)
    S = sum(bool(x) for x in dlc)
    if S == 1:
        out = np.where(dlc)[0][0]
    else: 
        out = -1    
    return out

def mouseOnResp2(mousePos, crit=20):
    [x,y] = mousePos
    out = 2
    if 50 > x > -150:
        if y > 150:
              out = 0
        elif y < 150:
              out = 1
    else: 
        out = -1    
    return out

def mouseResponse2(mouse,win,frame):
        mousePress = False
        mouse.setVisible(True)
        mouse.setPos((0,0))
        #simult = (-88,-285) to (31,-278)
        #non-simult = (-92,239) to (59,239)
        while not mousePress:
                buttons = mouse.getPressed(getTime=False)
                resp = mouseOnResp2(mouse.getPos())
                frame.draw()
                win.flip()
                mousePress = any(buttons)
        mouse.setVisible(False)
        return(resp)

def mouseResponse(mouse,win,gPar,frame):
        [x,y]=[gPar['x'],gPar['y']]
        mousePress = False
        mouse.setVisible(True)
        mouse.setPos((300,0))
        while not mousePress:
                buttons = mouse.getPressed(getTime=False)
                resp = mouseOnResp(x, y, mouse.getPos())
                frame.draw()
                if resp > -1: 
                        respDot = visual.Circle(win, pos=(x[resp], y[resp]), fillColor=[1, 1, 1], radius=2)
                        respDot.draw()
                win.flip()
                mousePress = any(buttons)
        mouse.setVisible(False)
        return(resp)

def intDotIndex(gPar,target):
    s2=gPar['N']
    half=int((s2-1)/2)
    tot = np.array(range(s2))
    wot = np.delete(tot, target)
    index = np.array(range(s2-1))
    iA = np.sort(np.random.choice(index, half, replace=False))
    iB = np.delete(index, iA)
    return [wot[iA], wot[iB]]

def stairCase(soa,correct,correctPrevious,increment):
        if (correct and correctPrevious==1):
                soa+=increment
                cv=0
        if (correct and correctPrevious==0):
                cv=1   
        if (not correct):
                soa+= (-increment)
                cv=0
        if (soa==0):
                soa=1
        return ([soa,cv]) 

def instruct(win, message):
    visual.TextBox2(win, text=message, pos=(0, 0), size=(900, None), letterHeight=35, lineSpacing=1.2, alignment='center', anchor='center', padding=0).draw()


    win.flip()
    event.waitKeys(keyList=["space"])
    return 0
