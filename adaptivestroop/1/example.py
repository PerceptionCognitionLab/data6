from psychopy import core, visual

win=visual.Window(units= "pix", size=(1000, 1000), color=[-1,-1,-1], fullscr = False)

text = visual.TextStim(win,"Welcome to the experiment", height = 40, pos = (0,0))
text.draw()
win.flip()
core.wait(1)

rectangle = visual.Rect(win, width=100, height=100,fillColor=[1,1,1], pos = (0, 300))
rectangle.draw()
win.flip()
core.wait(1)

text.draw()
rectangle.draw()
win.flip()
core.wait(1)

win.close()
