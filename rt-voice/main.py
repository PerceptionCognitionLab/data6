import sys
import random
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib
import os
from stroop_voicekey import run_voice
from stroop_manual import run_manual
from psychopy import visual

dbConf=exlib.beta
expName="rt-voice"
seed = None

nBlocks = 1
nTrials = 1
refreshRate=165
exlib.setRefreshRate(refreshRate)
pool = 3
[pid,_,_]=exlib.startExp(expName,dbConf,pool,lockBox=True,refreshRate=refreshRate)

run_voice(pid, nBlocks, nTrials)
run_manual(pid, nBlocks, nTrials)


BG_COLOR = [-0.85, -0.85, -0.85] 
win = visual.Window(fullscr=True,color=BG_COLOR,units="pix", allowGUI=False)
[resX,resY]=win.size
concern = exlib.getConcern(win)
win.close()
exlib.stopExp(pid, refreshRate, resX, resY, seed, dbConf, concern)