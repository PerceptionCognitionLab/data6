
congruentDur =[50]
incongruentDur=[80]

def runBlock(blk,cong,nTrials):
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


otherTimes=[50,2,16,16,16]
pracOtherTimes=[100,100,100,16,16]
congOrder=[1,0,1,0,1,0,0,1]


intro()
#trainFR()
startExp()


numBlocks=3
for i in range(numBlocks): 
    runBlock(i,congOrder[i],,gPar.numTrials)

#hz=round(win.getActualFrameRate())
#[resX,resY]=win.size
win.close()
fptr.close
#el.stopExp(sid,hz,resX,resY,seed,dbConf)
core.quit()

frameDurations=[50,2,lPar.dur,16,16,16]
