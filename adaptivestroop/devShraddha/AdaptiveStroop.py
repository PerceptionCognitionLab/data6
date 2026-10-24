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
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as el



#NOTE: This below notes have absolutely nothing to do with adaptive stroop
# Steps we did to actually run the code
# create a new folder with the code in it
# Creating virtual enviornment: python -m venv venv
# Activate virtual environment: .venv\Scripts\activate
# Install psychopy: python -m pip install psychopy 
# Run with python example.py (or whatever the file name is)
# to deactivate virtual environment: deactivate

refreshRate=165
trialClock=core.Clock()
el.setRefreshRate(refreshRate)

win=visual.Window(units= "pix", size=(1000, 1000), color=[-1,-1,-1], fullscr = False)

Adjust = 0

def run_trial(x):
    text = visual.TextStim(win,"Welcome to the experiment! Press key to start trial", height = 40, pos = (0,-100))
    text.draw()
    win.flip()
    event.waitKeys()
    global Adjust
    
    
    list_letters = ["A","S","D","F","G", "H", "J", "K", "L"]
    
    rand_letters = random.sample(list_letters,4)
   
    #Draw the rectangles I actually want
    center_rectangle = visual.Rect(win, width = 100, height=100, fillColor = 'black', lineColor = 'white', lineWidth = 4, pos = (0,-100))
    rectangle1 = visual.Rect(win, width=100, height=100, fillColor = 'black', lineColor = 'white', lineWidth = 4, pos= (-283,183))
    rectangle2 = visual.Rect(win, width=100, height=100, fillColor = 'black', lineColor = 'white', lineWidth = 4, pos=(-104, 286))
    rectangle3 = visual.Rect(win, width=100, height=100, fillColor = 'black', lineColor = 'white', lineWidth = 4, pos=(283, 183))
    rectangle4 = visual.Rect(win, width=100, height=100, fillColor = 'black', lineColor = 'white', lineWidth = 4, pos =(104,286))
    rectangles = [rectangle1, rectangle2, rectangle3, rectangle4, center_rectangle]
    
    #selecting if it will be congruent or incongruent
    cond = random.randint(1,2)
    
    #congruent
    if cond == 1:
        rand_num = random.randint(1,4)
        mult_num = rand_num
        number = visual.TextStim(win, str(rand_num) * (rand_num), height= 40, color=[1,1,1], pos = (0,-100))
        number.draw()
        
    #incongruent
    else:
        
        rand_num = (random.randint(1,4))
        mult_num_option = [1,2,3,4]
        mult_num_option.remove(rand_num)
        mult_num = random.choice(mult_num_option)
        number = visual.TextStim(win, str(rand_num) * mult_num, height= 40, color=[1,1,1], pos = (0,-100))
        number.draw()
    
    
    
    
    letter1 = visual.TextStim(win, rand_letters[0],height= 40, color='white', pos = (-283,183))
    letter2 = visual.TextStim(win, rand_letters[1],height= 40, color='white', pos = (-104,286))
    letter3 = visual.TextStim(win, rand_letters[2],height= 40, color='white', pos = (104,286))
    letter4 = visual.TextStim(win, rand_letters[3],height= 40, color='white', pos = (283,183))
    letters = [letter1, letter2, letter3, letter4]

    ### Feedback sounds ##
    correctSound1 = sound.Sound(800, secs=0.15)
    correctSound2 = sound.Sound(1200, secs=0.15)
    errorSound1 = sound.Sound(500, secs=0.30)
    errorSound2 = sound.Sound(375, secs=0.30)
    
    correct_answer = rand_letters[mult_num-1]
    
    
    frames = []
    #We are changing the third one. The last five are masks
    frameDurations=  [100, 30, x, 20, 5, 5, 5, 5, 5]
    
    frames.append(visual.BufferImageStim(win,stim = rectangles))
    frames.append(visual.BufferImageStim(win, stim= rectangles + [number]))
    frames.append(visual.BufferImageStim(win, stim= rectangles))
    frames.append(visual.BufferImageStim(win,stim= rectangles + letters))
    
    for i in ["!", "@", "#", "$", "%"]:
            frames.append(visual.BufferImageStim(win, stim= rectangles + [visual.TextStim(win, i,color=[1,1,1], height= 40, pos = (-283,183)), 
                                                                          visual.TextStim(win, i, color=[1,1,1], height= 40, pos = (-104,286)),
                                                                          visual.TextStim(win, i, color=[1,1,1], height= 40,  pos = (283,183)),
                                                                          visual.TextStim(win, i, color=[1,1,1], height= 40, pos = (104,286))]))
    
    
    stamps=el.runFrames(win,frames,frameDurations,trialClock)
    
    prompt = visual.TextStim(win, "enter response",height= 40, color=[-1,-1,-1], pos = (0,-100))
    prompt.draw()
    win.flip()
    
    #keys = event.waitKeys(keyList = list_letters)
    keys = event.waitKeys(keyList=[l.lower() for l in list_letters])
    
    print(keys)
    
    if cond == 1:
        Condition_text = visual.TextStim(win,"congruent", height= 40, color=[1,1,1], pos = (0,-160))
    elif cond ==2:
        Condition_text = visual.TextStim(win,"incongruent", height= 40, color=[1,1,1], pos = (0,-160))
        
    Condition_text.draw()
        
    if correct_answer.lower() in keys:
        correct_text =  visual.TextStim(win, "Correct!",height= 40, color=[0,1,0], pos = (0,-100))
        correct_text.draw()
        Adjust = "correct"
        correctSound1.play()
        core.wait(0.1)
        correctSound2.play()

       
    else:
        wrong_text = visual.TextStim(win, "Incorrect",height= 40, color=[1,0,0], pos = (0,-100))
        wrong_text.draw()
        Adjust = "incorrect"
        errorSound1.play()
        core.wait(0.1)
        errorSound2.play()
      
    
    win.flip()
    core.wait(3)
    print("Difference Between Time Stamps:\n",np.diff(stamps),"\n")
    print("Difference Between Frames:\n",el.actualFrameDurations(frameDurations,stamps))


#time the numbers stay on screen
wait_time = 30 


#for i in range(10):
#    run_trial(wait_time, let_time)

for i in range(5):
    run_trial(wait_time)
    if 'escape' in event.getKeys():
        print("Experiment aborted by user.")
        win.close()
    if Adjust == "correct":
        wait_time = int(wait_time*0.3)


    elif Adjust == "incorrect":
        wait_time = wait_time*3

        

win.close()

core.quit()
