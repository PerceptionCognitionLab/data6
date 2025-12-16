from psychopy import core, visual, sound, event, clock
import numpy as np
from numpy import random
import sys
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as elib
import serial

# random
seed = 1234
rng = random.default_rng(seed)

# globals
abortKey = ['escape']
refreshRate = 60
expName = "ev3"
mu = 10
sd = 25
numDots = 30
dotY = 0
dotRadius = 5
dotInterval = 0.5 #seconds
potInterval = 0.1 #seconds
barX = 75
barY = -150
barWidth = 10 
alpha = 1 #loss/win
use_elib = False

# elib setup
if(use_elib):
    elib.setRefreshRate(refreshRate)
    expName="ev3"
    dbConf=elib.data5
    [pid,sid,fname]=elib.startExp(expName,dbConf,pool=1,lockBox=True,refreshRate=refreshRate)    
    froot=fname[:-4]
    resp_file=open(froot+".resp", "w")
    stim_file=open(froot+".stim", "w")
    summary_file=open(froot+".summary", "w")
else:  
    resp_file = open("test_resp", "w")
    stim_file=open("test_stim", "w")
    summary_file=open("test_summary", "w")

elib.setRefreshRate(refreshRate)

# serial setup
ser = serial.Serial(port='COM3', baudrate=9600, timeout= 1)
ser.reset_input_buffer()

# window
win = visual.Window(units="pix", size=(500, 500), color=[-1, -1, -1], fullscr=True)
screen_width = win.size[0]

# axes
xAxis = visual.Line(win, start=(-1000, 0), end=(1000, 0), lineColor=[255, 0, 0], lineWidth=0.5)
yAxis = visual.Line(win, start=(0, 1000), end=(0, 0), lineColor=[255, 0, 0], lineWidth=0.5)

# line objects
horizontal_line = visual.Line(win, start=(0, -150), end=(0, -200), lineColor="green", lineWidth=5)

top_left_bar = visual.Rect(win, pos = (-barX, barY), fillColor = 'green', width = barWidth+1, height = 0, anchor = 'bottom')
top_right_bar = visual.Rect(win, pos = (barX, barY), fillColor = 'green', width = barWidth+1, height = 0, anchor = 'bottom')
bottom_left_bar = visual.Rect(win, pos = (-barX,barY), fillColor = 'red', width = barWidth, height = 0, anchor = 'top')
bottom_right_bar = visual.Rect(win, pos = (barX,barY), fillColor = 'red', width = barWidth, height = 0, anchor = 'top')

# outline def
visual_limit = 250
top_max = visual_limit/2
bottom_max = top_max * alpha
total_outline_height = bottom_max + top_max
outline_center_y = barY + (top_max - bottom_max) / 2

outline_left = visual.Rect(
    win, pos=(-barX, outline_center_y), fillColor=None, lineColor='grey',
    width=barWidth + 5, lineWidth=2.5, height=total_outline_height, anchor='center'
)

outline_right = visual.Rect(
    win, pos=(barX, outline_center_y), fillColor=None, lineColor='grey',
    width=barWidth + 5, lineWidth=2.5, height=total_outline_height, anchor='center'
)


# sounds
correctSound1 = sound.Sound(500, secs=0.25)
correctSound2 = sound.Sound(1000, secs=0.25)
incorrectSound1 = sound.Sound(500, secs=0.5)
incorrectSound2 = sound.Sound(375, secs=0.5)

def playCorrectSound():
    correctSound1.play()
    core.wait(0.25)
    correctSound2.play()
    core.wait(0.25)

def playIncorrectSound():
    incorrectSound1.play()
    incorrectSound2.play()
    core.wait(0.5)

# feedback setup
last_feedback_text = None
last_feedback_color = 'white'
total_score = 0

def instructions():
    instruction0 = visual.TextStim(win, text="Welcome!", height=40, pos=(0,300))
    instruction1 = visual.TextStim(win, text="You're on a game show! In this challenge, a drunk person is trying to shoot at one of two invisible targets on either side of the screen.", height=20, color='white', pos=(0, 200))
    instruction2 = visual.TextStim(win, text="You can't see the targets, but you can see where each shot lands. Your job is to bet on which side the shooter is aiming at on each trial.", height=20, color='white', pos=(0, 100))
    instruction3 = visual.TextStim(win, text="Place your bet by turning the knob left or right based on which side the target is on.", height=20, color='white', pos=(0, 0))
    instruction4 = visual.TextStim(win, text="You'll start with 10 practice rounds then move on to the main game, which has 50 rounds. Feel free to take a break at any time between rounds.", height=20, color='white', pos=(0, -100))
    instruction5 = visual.TextStim(win, text="Press any key to continue.", height=20, color='white', pos=(0, -200))

    while True:
        instruction0.draw()
        instruction1.draw()
        instruction2.draw()
        instruction3.draw()
        instruction4.draw()
        instruction5.draw()

        win.flip()
        keys = event.getKeys()
        if keys:
            if 'escape' in keys:
                core.quit()
            break

def updateBars(x_offset):
    if x_offset >= 0:
        top_right_bar.height = x_offset / 2
        bottom_right_bar.height = top_right_bar.height * alpha
        top_left_bar.height = 0
        bottom_left_bar.height = 0
    else:
        top_left_bar.height = -x_offset / 2
        bottom_left_bar.height = top_left_bar.height * alpha
        top_right_bar.height = 0
        bottom_right_bar.height = 0

def showBlockStartScreen(text):
    message = visual.TextStim(win, text=text, height=30, color='white', pos=(0, 0))
    instruction = visual.TextStim(win, text="Press any key to start", height=20, color='white', pos=(0, -40))
    while True:
        message.draw()
        instruction.draw()
        win.flip()
        keys = event.getKeys()
        if keys:
            if 'escape' in keys:
                core.quit()
            break

def displayDots(mu, sd, endChance, dotY, dotRadius, dotInterval, numTrials):
    global last_feedback_text, last_feedback_color, total_score

    resp = []
    stim = []
    summary = []

    inside_threshold = 25
    max_offset = screen_width / 2 - 50
    visual_limit = 250

    moved_outside = False
    while True:
        if "escape" in event.getKeys():
            return resp, stim, summary            

        line = None
        while ser.in_waiting:
            try:
                raw = ser.readline().decode("utf-8", errors="ignore").strip()
                if raw:
                    line = raw
            except Exception:
                continue

        if line and line.isdigit():
            if(line == None):
                line = 0
            val = int(line)
            norm_val = -(val - 512) / 512.0
            x_offset = norm_val * max_offset
            x_offset = max(-visual_limit, min(visual_limit, x_offset))

            horizontal_line.start = (x_offset,-150)
            horizontal_line.end = (x_offset,-200)

            # end inside threshold edge case
            if abs(x_offset) <= inside_threshold:
                horizontal_line.lineColor = 'green'
            else:
                horizontal_line.lineColor = 'red'

            if not moved_outside:
                if abs(x_offset) > inside_threshold:
                    moved_outside = True
            else:
                if abs(x_offset) <= inside_threshold:
                    break

        reset_text = visual.TextStim(win, text="Please move the knob outside the green zone, then back inside to start.", height=25, color='yellow', pos=(0, 0))
        reset_text.draw()

        horizontal_line.draw()
        win.flip()

    trial = 0
    trial_score = None
    while(trial < numTrials):
        dotNum = 0

        correct = -1 if rng.integers(0, 2) == 0 else 1
        coordinates = np.round(rng.normal(mu * correct, sd, 20))
        circ = visual.Circle(win, pos=(coordinates[dotNum], dotY),
                             fillColor=[1, 1, 1], radius=dotRadius)

        inside_time = None

        # ready check before trial
        while True:
            if "escape" in event.getKeys():
                return resp, stim, summary

            # serial
            line = None
            while ser.in_waiting:
                try:
                    raw = ser.readline().decode("utf-8", errors="ignore").strip()
                    if raw:
                        line = raw
                except Exception:
                    continue

            if line and line.isdigit():
                if(line == None):
                    line = 0
                val = int(line)
                norm_val = -(val - 512) / 512.0
                x_offset = norm_val * max_offset

                # +- 250 pixel clamp
                x_offset = max(-visual_limit, min(visual_limit, x_offset))

                horizontal_line.start = (x_offset,-150)
                horizontal_line.end = (x_offset,-200)

                updateBars(x_offset)

                #feedback
                if abs(x_offset) <= inside_threshold:
                    horizontal_line.lineColor = 'green'
                else:
                    horizontal_line.lineColor = 'red'

            if last_feedback_text:
                feedback_stim = visual.TextStim(win, text=last_feedback_text, height=30, color=last_feedback_color, pos=(0, 110))
                feedback_stim.draw()

                if(trial_score == None):
                    trial_score = 0
                trial_score_stim = visual.TextStim(win, text=f"Trial score: {int(trial_score)}", height=30, color=last_feedback_color, pos=(0, 80))
                trial_score_stim.draw()

                if(total_score == None):
                    total_score = 0
                score_stim = visual.TextStim(win, text=f"Total score: {int(total_score)}", height=30, color=last_feedback_color, pos=(0, 50))
                score_stim.draw()

                progress_percent = int((trial / numTrials) * 100)
                progress_text = visual.TextStim(win, text=f"Progress: {progress_percent}%", height=15, color='white', pos=(0, 500))
                progress_text.draw()
            
            # ready phase draw
            ready_text = visual.TextStim(win, text="Ready? Move the knob to the middle to continue.", height=30, color='white', pos=(0, 0))
            ready_text.draw()
            horizontal_line.draw()
            win.flip()

            # check if line is centered
            if abs(x_offset) <= inside_threshold:
                if inside_time is None:
                    inside_time = core.getTime()
                elapsed = core.getTime() - inside_time
            else:
                inside_time = None
                elapsed = 0

            if(elapsed >= 1):
                break

        # trial dots loop
        frame_in_trial = 0
        outline_right.lineColor = 'grey'
        outline_left.lineColor = 'grey'

        while True:
            if "escape" in event.getKeys():
                return resp, stim, summary

            # serial
            line = None
            while ser.in_waiting:
                try:
                    raw = ser.readline().decode("utf-8", errors="ignore").strip()
                    if raw:
                        line = raw
                except Exception:
                    continue

            if line and line.isdigit():
                if(line == None):
                    line = 0
                val = int(line)
                norm_val = -(val - 512) / 512.0
                x_offset = norm_val * max_offset
                x_offset = max(-visual_limit, min(visual_limit, x_offset))

                updateBars(x_offset)

            # update pot reading every potInterval seconds
            if frame_in_trial % (potInterval*refreshRate) == 0:
                resp.append([trial, frame_in_trial/refreshRate, x_offset])

            # update dots every dotInterval seconds
            if frame_in_trial % (dotInterval*refreshRate) == 0:
                dotNum += 1
                if dotNum >= len(coordinates):
                    dotNum = 0
                circ.pos = (coordinates[dotNum], dotY)
                stim.append([trial, frame_in_trial/refreshRate, coordinates[dotNum]])
                if dotNum > 3:
                    if ((rng.random() < endChance) or dotNum > 9):
                        final_side = np.sign(x_offset)
                        # end in middle edge case
                        if final_side == 0:
                            final_side = 1

                        # feedback
                        if final_side == correct:
                            last_feedback_text = "Correct!"
                            playCorrectSound()
                            last_feedback_color = 'green'
                            trial_score = top_right_bar.height * 2/5 if correct == 1 else top_left_bar.height * 2/5
                        else:
                            last_feedback_text = "Incorrect"
                            playIncorrectSound()
                            last_feedback_color = 'red'
                            trial_score = -bottom_right_bar.height * 2/5 if bottom_right_bar.height != 0 else -bottom_left_bar.height * 2/5

                        total_score += trial_score
                        
                        if(trial_score == None):
                            trial_score = 0
                        summary.append([trial, dotNum, correct, x_offset, int(trial_score)])
                        trial += 1

                        moved_outside = False
                        while True:
                            if "escape" in event.getKeys():
                                return resp, stim, summary

                            line = None
                            while ser.in_waiting:
                                try:
                                    raw = ser.readline().decode("utf-8", errors="ignore").strip()
                                    if raw:
                                        line = raw
                                except Exception:
                                    continue

                            if line and line.isdigit():
                                if(line == None):
                                    line = 0
                                val = int(line)
                                norm_val = -(val - 512) / 512.0
                                x_offset = norm_val * max_offset
                                x_offset = max(-visual_limit, min(visual_limit, x_offset))

                                horizontal_line.start = (x_offset,-150)
                                horizontal_line.end = (x_offset,-200)

                                updateBars(x_offset)

                                if abs(x_offset) <= inside_threshold:
                                    horizontal_line.lineColor = 'green'
                                else:
                                    horizontal_line.lineColor = 'red'

                                if not moved_outside:
                                    if abs(x_offset) > inside_threshold:
                                        moved_outside = True
                                else:
                                    if abs(x_offset) <= inside_threshold:
                                        break

                            if last_feedback_text:
                                feedback_stim = visual.TextStim(win, text=last_feedback_text, height=30, color=last_feedback_color, pos=(0, 110))
                                feedback_stim.draw()

                                if(trial_score == None):
                                    trial_score = 0
                                trial_score_stim = visual.TextStim(win, text=f"Trial score: {int(trial_score)}", height=30, color=last_feedback_color, pos=(0, 80))
                                trial_score_stim.draw()

                                if(total_score == None):
                                    total_score = 0
                                score_stim = visual.TextStim(win, text=f"Total score: {int(total_score)}", height=30, color=last_feedback_color, pos=(0, 50))
                                score_stim.draw()

                                progress_percent = int((trial / numTrials) * 100)
                                progress_text = visual.TextStim(win, text=f"Progress: {progress_percent}%", height=15, color='white', pos=(0, 500))
                                progress_text.draw()


                            reset_text = visual.TextStim(win, text="Please move the knob outside the green zone, then back inside to continue.", height=25, color='yellow', pos=(0, 0))
                            reset_text.draw()

                            horizontal_line.draw()
                            win.flip()

                        break

            circ.draw()
            xAxis.draw()
            yAxis.draw()
            top_left_bar.draw()
            top_right_bar.draw()
            bottom_left_bar.draw()
            bottom_right_bar.draw()
            outline_left.draw()
            outline_right.draw()
            win.flip()

            frame_in_trial += 1

    return resp, stim, summary

# main

instructions()
endChance = 0.15
numTrials = 10
total_score = 0
showBlockStartScreen("Tutorial Block")
resp, stim, summary = displayDots(mu, sd, endChance, dotY, dotRadius, dotInterval, numTrials)
numTrials = 50
total_score = 0
showBlockStartScreen("Main Block")
resp, stim, summary = displayDots(mu, sd, endChance, dotY, dotRadius, dotInterval, numTrials)

# data writing
resp_file.write("trial\ttime\tpot_val\n")
for row in resp:
    resp_file.write(f"{row[0]}\t{row[1]}\t{row[2]}\n")

stim_file.write("trial\ttime\tstim_coord\n")
for row in stim:
    stim_file.write(f"{row[0]}\t{row[1]}\t{row[2]}\n")

summary_file.write("trial\tpoints_drawn\tcorrect\tfinal_pot_val\ttrial_score\n")
for row in summary:
    summary_file.write(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\t{row[4]}\n")

# final screen
final_score_text = visual.TextStim(win, text=f"Final Total Score:\n{int(total_score)}", height=30, color='white', pos=(0, 40))
exit_text = visual.TextStim(win, text="Press ESCAPE to exit", height=30, color='white', pos=(0, -40))

while True:
    final_score_text.draw()
    exit_text.draw()
    win.flip()

    if 'escape' in event.getKeys():
        break

hz=round(win.getActualFrameRate())
[resX,resY]=win.size
if(use_elib):
    elib.stopExp(sid,hz,resX,resY,seed,dbConf)
win.close()
ser.close()
core.quit()
