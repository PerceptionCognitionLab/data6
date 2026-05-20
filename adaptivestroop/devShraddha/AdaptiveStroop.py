import sys
import random
from psychopy import core, visual
from psychopy.hardware import keyboard

# Steps we did to actually run the code
# create a new folder with the code in it
# Creating virtual enviornment: python -m venv venv
# Activate virtual environment: .venv\Scripts\activate
# Install psychopy: python -m pip install psychopy 
# Run with python example.py (or whatever the file name is)
# to deactivate virtual environment: deactivate


win=visual.Window(units= "pix", size=(1000, 1000), color=[-1,-1,-1], fullscr = False)

text = visual.TextStim(win,"Welcome to the experiment", height = 40, pos = (0,0))
text.draw()
win.flip()
#Waits for 1 seconds before showing the rectangle
core.wait(1) 

#Draw rectangle example
rectangle = visual.Rect(win, width=100, height=100,fillColor=[1,1,1], pos = (0, 300))
rectangle.draw()
text.draw()
win.flip()
core.wait(1)



stimulus_time = 2
options_time = 2

list_letters = ["A","S","D","F","G", "H", "J", "K", "L"]
rand_letters = random.sample(list_letters,4)


#Draw the rectangles I actually want
center_rectangle = visual.Rect(win, width = 100, height=100, fillColor = [1,1,1], pos = (0,0))
#center_rectangle.draw()

rectangle2 = visual.Rect(win, width=100, height=100, fillColor=[1,1,1], pos =(300,0))
#rectangle2.draw()

rectangle3 = visual.Rect(win, width=100, height=100, fillColor=[1,1,1], pos= (-300,0))
#rectangle3.draw()

diag1_rectangle = visual.Rect(win, width=100, height=100, fillColor= [1,1,1], pos=(-212, 212))
#diag1_rectangle.draw()

diag2_rectangle = visual.Rect(win, width=100, height=100, fillColor= [1,1,1], pos=(212, 212))
#diag2_rectangle.draw()

def draw_rectangles():
    center_rectangle.draw()
    rectangle2.draw()
    rectangle3.draw()
    diag1_rectangle.draw()
    diag2_rectangle.draw()

draw_rectangles()

rand_num = str(random.randint(1,9))
mult_num = random.randint(1,4)
number = visual.TextStim(win, rand_num * mult_num, height= 40, color=[-1,-1,-1], pos = (0,0))
number.draw()

#why doesn't this wait?? It should wait for some time before showning letters
win.flip()
core.wait(stimulus_time)

draw_rectangles()

letter1 = visual.TextStim(win, rand_letters[0],height= 40, color=[-1,-1,-1], pos = (300,0))
letter2 = visual.TextStim(win, rand_letters[1],height= 40, color=[-1,-1,-1], pos = (-300,0))
letter3 = visual.TextStim(win, rand_letters[2],height= 40, color=[-1,-1,-1], pos = (-212,212))
letter4 = visual.TextStim(win, rand_letters[3],height= 40, color=[-1,-1,-1], pos = (212,212))

letter1.draw()
letter2.draw()
letter3.draw()
letter4.draw()

win.flip()
core.wait(options_time)


#trying to get participant response
kb = keyboard.Keyboard()
keys = kb.getKeys()

prompt = visual.TextStim(win, "Please Type Letter",height= 40, color=[-1,-1,-1], pos = (0,0))
prompt.draw()






win.close()

