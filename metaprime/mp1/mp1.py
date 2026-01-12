import sys
import random
from psychopy import visual, core, event
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib
import numpy as np

# region
refreshRate=165
exlib.setRefreshRate(refreshRate)
trialClock=core.Clock()
expName="metamask"
dbConf=exlib.data6
seed = random.randrange(1e6)
[pid,sid,fname]=exlib.startExp(expName,dbConf,pool=1,lockBox=True,refreshRate=refreshRate)
fptr = open(fname,'w')
# endregion

# Experiment settings
# region
num_blocks = 3
n_trials_per_condition = 3
ISI_frames = [0, 4, 8, 12, 16, 28]
# ISI_frames = [0, 2, 4, 6, 8, 10, 12] # Vorberg's
num_trials_per_block = 144
primeFrame = 2
maskFrame = 7   # to find dissociation
# maskFrame = 20
gap = 0.2
practice_num = 20
# endregion

# Define stimuli: primes, masks, text
#region
# Color
bg_color = np.array([1, 1, 1]) * 3/4
sti_color = np.array([-1, -1, -1]) * 3/4

# Set up the window
win = visual.Window(units="pix", size=(1920, 1080), color= bg_color, fullscr=True)

# Text stimuli
welcome_text1 = visual.TextStim(win, text='Welcome to the experiment! Press spacebar to continue.', pos = (0,0), color = sti_color)
welcome_text2 = visual.TextStim(win, text='The exerpiment contain two sessions. Each session has three blocks, which will last around 15 minutes.\n\nPress space bar to start the first session.', pos = (0,0), color = sti_color)
instruction_text1 = visual.TextStim(win, text='In this session, a flash arrow (shown as below) will be displayed on the screen. Your task is to identify the orientation of the arrow as soon as you see it.\n\nIf you think the arrow points to left. press "x", if you think the arrow points to right, press "m".\n\nPress spacebar to continue', pos = (0,0), color = sti_color)
rest_text=  visual.TextStim(win, text='Session 1 ends! You can have some rest before starting session 2.\n\nPress spacebar to start session 2.', pos = (0,0), color = sti_color)
instruction_text2 = visual.TextStim(win, text='You may have notice that there is a smaller arrow appears at the center of the main arrow (shown as below). In this session, you are required to identify the orientation of that smaller arrow as soon as you see it while neglecting the main arrow.\n\nIf you think the arrow points to left. press "x", if you think the arrow points to right, press "m".\n\nThis session is more difficult than the first session. Please try you best. Press spacebar to continue', pos = (0,0), color = sti_color)
goodbye_text = visual.TextStim(win, text='Experiment finished! Thank you for your participation.\n\nPress spacebar to exit', pos=(0, 0), color=sti_color)
start_practice_text = visual.TextStim(win, text='We will begin with some practice trials. We will provide feedback on correctness. Note that in the real experiment there will be no feedback.\n\nPress space to start the practice trials.', pos=(0, 0), color=sti_color)
end_practice_text = visual.TextStim(win, text='Practice finished.\n\nPress space to start the real experiment.', pos=(0, 0), color=sti_color)
# Fixation and blank
fixation = visual.TextStim(win, text='+', pos=(0, 0), color=sti_color, bold = True, height = 40)
blank =  visual.TextStim(win, text='', pos=(0, 0), color=sti_color, bold = True, height = 40)
# contour not touch

prime_left = visual.ShapeStim(
    win=win, vertices=[(-90,0),(-70,20),(80,20),(60,0),(80,-20),(-70,-20)],
    fillColor=sti_color, lineColor=sti_color, size=1)
prime_right = visual.ShapeStim(
    win=win, vertices=[(-60,0),(-80,20),(70,20),(90,0),(70,-20),(-80,-20)],
    fillColor=sti_color, lineColor=sti_color, size=1)


mask_outer_left = visual.ShapeStim(
    win=win, vertices=[(-165, 0), (-120, 45), (120, 45), (120, -45), (-120, -45)],
    fillColor=sti_color , lineColor=sti_color , size=1)
mask_outer_right = visual.ShapeStim(
    win=win, vertices=[(-120, 45), (120, 45), (165,0), (120, -45), (-120, -45)],
    fillColor=sti_color , lineColor=sti_color , size=1)
mask_inner = visual.ShapeStim(
    win=win, vertices=[(-105,30),(105,30),(90,15),(105,0),(90,-15),(105,-30),(-105,-30),(-90,-15),(-105,0),(-90,15)],
    fillColor=bg_color, lineColor=bg_color, size=1)
#endregion

# Define a function for a single trial
def run_trial(block_num, trial_num, prime_direction, mask_direction, ISI, position, provide_feedback=False, goal = None): 
    # Set goal of the trial
    true = mask_direction  if goal == 'mask' else prime_direction
    position = (0, 130) if position == 'top' else (0, -130)

    prime = prime_left if prime_direction == 'left' else prime_right
    mask_outer = mask_outer_left if mask_direction == 'left' else mask_outer_right
        
    prime.pos = position
    mask_outer.pos = position
    mask_inner.pos = position
        
    mask = visual.BufferImageStim(win, stim = [mask_outer, mask_inner])
            
    # Run frames
    if ISI != 0:
        frames = [fixation, prime, blank, mask]
        frameDurations = [120, primeFrame, ISI, maskFrame]
        stamps = exlib.runFrames(win, frames, frameDurations, trialClock)
        critTime = exlib.actualFrameDurations(frameDurations, stamps)[2]
        critPass = (np.absolute((ISI/refreshRate) - critTime) < .001)
        if not critPass:
            print('Critical pass fail at trial ' + str(trial_num) + ' : while critical time is ' + str(np.round(critTime, 4)) +
                  ', actual time is ' + str(np.round(ISI/refreshRate, 4)))
    else:
        frames = [fixation, prime, mask]
        frameDurations = [120, primeFrame, maskFrame] 
        stamps = exlib.runFrames(win, frames, frameDurations, trialClock)

    # Record the reaction time and wait for response for at most 1.5s
    trialClock.reset()
    blank.draw()
    win.flip()
    keys = event.waitKeys(maxWait=5, timeStamped=trialClock, keyList=['x', 'm'])

    # Check if the response was correct
    if keys:
        key, rt = keys[0]
        response = 'left' if key == 'x' else 'right'
        correctness = (response == true)
    else:
        response, rt, correctness = None, None, False  # No response is considered incorrect

    # Provide feedback if it's a practice trial
    if provide_feedback:
        feedback_text = 'Correct!' if correctness else 'Incorrect!'
        feedback = visual.TextStim(win, text=feedback_text, pos=(0, 0), color=sti_color)
        feedback.draw()
        win.flip()
        core.wait(1)  # Display feedback for 1 second

    # 1-second break before the next fixation point
    else:
        win.flip()  # Clear the screen
        core.wait(0.2) # Display feedback for 0.2 second

    # Return trial result
    output = [pid,
              sid,
              goal,
              (block_num - 1) * num_trials_per_block + trial_num,
              block_num,
              trial_num,
              prime_direction, 
              mask_direction, 
              prime_direction == mask_direction,
              np.round(ISI * 0.006, 3), 
              position, 
              response, 
              np.round(rt, 3) if rt is not None else rt, 
              correctness]
    if provide_feedback == False:
        print(output)
        print(*output, sep=',', file=fptr)
    
    exlib.endTrial()
        
# Define a function for a practice trial
def run_practice_block(n_trials=practice_num, goal = None):
    # Start the practice block
    start_practice_text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    # Generate practice trial conditions (randomized)
    conditions = []
    for _ in range(n_trials):
        ISI = random.choice(ISI_frames)
        position = random.choice(['top', 'bottom'])
        prime_direction = random.choice(['left', 'right'])
        mask_direction = random.choice(['left', 'right'])
        conditions.append({'prime': prime_direction, 'mask': mask_direction, 'ISI': ISI, 'position': position})
    random.shuffle(conditions)

    # Run each trial in the practice block
    for trial_num, trial in enumerate(conditions):
        # Check for escape key to quit
        if 'escape' in event.getKeys():
            return True  # Signal to quit

        # Run the trial with feedback enabled
        run_trial(
            block_num=0,  # Block 0 for practice
            trial_num=trial_num + 1,
            prime_direction=trial['prime'],
            mask_direction=trial['mask'],
            ISI=trial['ISI'],
            position=trial['position'],
            provide_feedback=True,  # Enable feedback for practice
            goal = goal
        )

    # Show practice end message
    end_practice_text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    return False  # Continue to the main experiment

# Define a function to run a block of trials
def run_block(block_num, n_trials_per_condition, ISI_frames, goal = None):
    # Generate trial conditions
    conditions = []
    # Count on trial number
    trial_num = 0
    #Collect all conditions and shuffle
    for ISI in ISI_frames:
        for position in ['top', 'bottom']:
            conditions.append({'prime': 'left', 'mask': 'left', 'ISI': ISI, 'position': position})
            conditions.append({'prime': 'right', 'mask': 'right', 'ISI': ISI, 'position': position})
            conditions.append({'prime': 'left', 'mask': 'right', 'ISI': ISI, 'position': position})
            conditions.append({'prime': 'right', 'mask': 'left', 'ISI': ISI, 'position': position})

    # Shuffle and repeat trials for each condition
    trial_list = conditions * n_trials_per_condition
    random.shuffle(trial_list)

    # Run each trial in the block
    for trial in trial_list:
        # Check for escape key to quit
        if 'escape' in event.getKeys():
            return True  # Return results and signal to quit
        trial_num += 1
        # Run the trial and collect results
        run_trial(
            block_num = block_num,
            trial_num = trial_num,
            prime_direction=trial['prime'],
            mask_direction=trial['mask'],
            ISI=trial['ISI'],
            position=trial['position'],
            goal = goal
        )

    return False  # Return results and signal to continue

# Define a function to run the full experiment with multiple blocks
def run_experiment(num_blocks, n_trials_per_condition, ISI_frames, goal = None):
    # Run the practice block first
    print("Running Practice Block...")
    quit_experiment = run_practice_block(goal = goal)
    if quit_experiment:
        print("Experiment quit by user during practice.")
        return

    # Run the main experimental blocks
    for block_num in range(1, num_blocks + 1):
        print(f"Running Block {block_num}...")

        # Run a block of trials
        quit_experiment = run_block(block_num, n_trials_per_condition, ISI_frames, goal = goal)
        if quit_experiment:
            print("Experiment quit by user.")
            break  # Stop experiment if quit signal received

        # Pause between blocks (except last one)
        if block_num < num_blocks:
            break_text = visual.TextStim(win, text=f'Block {block_num} finished\nPress space to continue to the next block', pos=(0, 0), color=sti_color)
            break_text.draw()
            win.flip()
            event.waitKeys(keyList=['space'])

# The experiment skeleton
# region
# welcome1
welcome_text1.draw()
win.flip()
event.waitKeys(keyList=['space'])

# welcome2
welcome_text2.draw()
win.flip()
event.waitKeys(keyList=['space'])

# instruction1
mask_outer_left.pos = (0,-300)
mask_inner.pos = (0,-300)
mask_outer_left.draw()
mask_inner.draw()
instruction_text1.draw()
win.flip()
event.waitKeys(keyList=['space'])

# Run the mask experiment
all_results = run_experiment(num_blocks, n_trials_per_condition, ISI_frames, goal = 'mask')

# rest
rest_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

# instruction2
prime_right.pos = (0,-300)
mask_outer_left.pos = (0,-300)
mask_inner.pos = (0,-300)
mask_outer_left.draw()
mask_inner.draw()
instruction_text2.draw()
prime_right.draw()
win.flip()
event.waitKeys(keyList=['space'])

# Run the prime experiment
all_results = run_experiment(num_blocks, n_trials_per_condition, ISI_frames, goal = 'prime')

# Show goodbye screen
goodbye_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

# Record settings and close the window
[resX,resY]=win.size
fptr.flush()
win.close()
core.quit()


