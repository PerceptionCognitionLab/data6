import sys
import random
from psychopy import core, visual, event
from psychopy.hardware import keyboard

#from RunFrames tutorial
from psychopy import prefs
prefs.hardware['audioLib']=['PTB']
prefs.hardware['audioLatencyMode']=3
from psychopy import core, visual, sound, event
import numpy as np
import sys
sys.path.insert(0, 'E:/lib/data5')
import expLib51 as el



#NOTE: This below notes have absolutely nothing to do with adaptive stroop
# Steps we did to actually run the code
# create a new folder with the code in it
# Creating virtual enviornment: python -m venv venv
# Activate virtual environment: .venv\Scripts\activate
# Install psychopy: python -m pip install psychopy 
# Run with python example.py (or whatever the file name is)
# to deactivate virtual environment: deactivate

trialClock=core.Clock()

win=visual.Window(units= "pix", size=(1000, 1000), color=[-1,-1,-1], fullscr = False)

Adjust = 0

def run_trial(x,y):
    text = visual.TextStim(win,"Welcome to the experiment! Press key to start trial", height = 40, pos = (0,0))
    text.draw()
    win.flip()
    event.waitKeys()
    global Adjust
    
    
    list_letters = ["a","s","d","f","g", "h", "j", "k", "l"]
    rand_letters = random.sample(list_letters,4)
    
    
    #Draw the rectangles I actually want
    center_rectangle = visual.Rect(win, width = 100, height=100, fillColor = [1,1,1], pos = (0,0))
    #center_rectangle.draw()
    
    rectangle4 = visual.Rect(win, width=100, height=100, fillColor=[1,1,1], pos =(300,0))
    #rectangle4.draw()
    
    rectangle1 = visual.Rect(win, width=100, height=100, fillColor=[1,1,1], pos= (-300,0))
    #rectangle1.draw()
           
    rectangle2 = visual.Rect(win, width=100, height=100, fillColor= [1,1,1], pos=(-212, 212))
    #rectangle2.draw()
    
    rectangle3 = visual.Rect(win, width=100, height=100, fillColor= [1,1,1], pos=(212, 212))
    #rectangle3.draw()
    
    
    rectangles = [rectangle1, rectangle2, rectangle3, rectangle4]
    
    #selecting if it will be congruent or incongruent
    cond = random.randint(1,2)
    
    #congruent
    if cond == 1:
        rand_num = random.randint(1,4)
        mult_num = rand_num
        number = visual.TextStim(win, str(rand_num) * (rand_num), height= 40, color=[-1,-1,-1], pos = (0,0))
        number.draw()
        
    #incongruent
    else:
        
        rand_num = (random.randint(1,4))
        mult_num_option = [1,2,3,4]
        mult_num_option.remove(rand_num)
        mult_num = random.choice(mult_num_option)
        number = visual.TextStim(win, str(rand_num) * mult_num, height= 40, color=[-1,-1,-1], pos = (0,0))
        number.draw()
    
    
    
    
    letter1 = visual.TextStim(win, rand_letters[0],height= 40, color=[-1,-1,-1], pos = (-300,0))
    letter2 = visual.TextStim(win, rand_letters[1],height= 40, color=[-1,-1,-1], pos = (-212,212))
    letter3 = visual.TextStim(win, rand_letters[2],height= 40, color=[-1,-1,-1], pos = (212,212))
    letter4 = visual.TextStim(win, rand_letters[3],height= 40, color=[-1,-1,-1], pos = (300,0))
    
    
    
    correct_answer = rand_letters[mult_num-1]
    
    
    frames = []
    frameDurations= [x,25,y,25]
    
    frames.append(visual.BufferImageStim(win, stim=[ rectangle1,rectangle2, rectangle3, rectangle4, center_rectangle, number]))
    frames.append(visual.BufferImageStim(win, stim=[ rectangle1,rectangle2, rectangle3, rectangle4, center_rectangle]))
    frames.append(visual.BufferImageStim(win,stim=[ rectangle1,rectangle2, rectangle3, rectangle4, center_rectangle, letter1, letter2, letter3, letter4]))
    frames.append(visual.BufferImageStim(win,stim=[ rectangle1,rectangle2, rectangle3, rectangle4, center_rectangle]))    
    
    stamps=el.runFrames(win,frames,frameDurations,trialClock)
    
    prompt = visual.TextStim(win, "enter response",height= 40, color=[-1,-1,-1], pos = (0,0))
    prompt.draw()
    win.flip()
    
    keys = event.waitKeys(keyList = list_letters)
    
    print(keys)
    
    if cond == 1:
        Condition_text = visual.TextStim(win,"congruent", height= 40, color=[1,1,1], pos = (0,-60))
    elif cond ==2:
        Condition_text = visual.TextStim(win,"incongruent", height= 40, color=[1,1,1], pos = (0,-60))
        
    Condition_text.draw()
        
    if correct_answer in keys:
        correct_text =  visual.TextStim(win, "Correct!",height= 40, color=[0,1,0], pos = (0,0))
        correct_text.draw()
        Adjust = "correct"
       
    else:
        wrong_text = visual.TextStim(win, "Incorrect",height= 40, color=[1,0,0], pos = (0,0))
        wrong_text.draw()
        Adjust = "incorrect"
      
    
    win.flip()
    core.wait(3)
    print("Difference Between Time Stamps:\n",np.diff(stamps),"\n")
    print("Difference Between Frames:\n",el.actualFrameDurations(frameDurations,stamps))


#time the numbers stay on screen
num_time = 50
#time the letters stay on screen
let_time= 50

#for i in range(10):
#    run_trial(num_time, let_time)

for i in range(10):
    run_trial(num_time, let_time)
    
    if Adjust == "correct":
        num_time = int(num_time*0.5)
        let_time = int( let_time*0.5)

    elif Adjust == "incorrect":
        num_time = num_time*5
        let_time = let_time*5
        

win.close()

core.quit()
