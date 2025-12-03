from psychopy import visual, core, event
import random
import csv
import sys
import os
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib

# =========================
# Config & Globals
# =========================
WIN_SIZE = (1920, 1080)
FULLSCR = True
UNITS = "pix"
BG_COLOR = (0,0,0)

FIELD_W, FIELD_H = 900, 600
DOT_RADIUS = 14
DOT_MIN_DIST = 2*DOT_RADIUS + 6
GREEN_RANGE = (3, 9)
YELLOW_RANGE = (3, 9)
PRACTICE_SET_SIZES = [2, 2]   # added practice sets
CSPAN_SET_SIZES = [3, 4,5,6,7]      # main task sizes
SETS_PER_SIZE = 1
FEEDBACK_DURATION = 2.0

# File paths
refreshRate = 165
exlib.setRefreshRate(refreshRate)
pool = 3
dbConf=exlib.data6
expName="indSVT"
[pid,sid,fname]=exlib.startExp(expName,dbConf,pool=pool,lockBox=True,refreshRate=refreshRate)
triallog_path = os.path.abspath(f"Data/{pid}_CSpan.csv")
summary_path = os.path.abspath(f"Data_summary/{pid}_CSpan_summary.csv")

# =========================
# Window & IO
# =========================
win = visual.Window(size=WIN_SIZE, units=UNITS, fullscr=FULLSCR, color=BG_COLOR)
mouse = event.Mouse(win=win, visible=True)
text_kwargs = dict(color='white', height=32, alignText='center', wrapWidth=1500)
small_text_kwargs = dict(color='white', height=24, alignText='center', wrapWidth=1600)
msg = visual.TextStim(win, text='', **text_kwargs)
msg_small = visual.TextStim(win, text='', **small_text_kwargs)

# =========================
# Utilities
# =========================
def check_escape():
    if 'escape' in event.getKeys(['escape']):
        win.close(); core.quit()

def show_instructions(text):
    mouse.clickReset()
    while True:
        check_escape()
        msg.text = text
        msg.draw()
        msg_small.text = "Click to continue"
        msg_small.pos = (0, -win.size[1]//2 + 100)
        msg_small.draw()
        win.flip()
        if mouse.getPressed()[0]:
            core.wait(0.15)
            return
        core.wait(0.01)

class Button:
    def __init__(self, win, text, pos, size=(220,70)):
        self.rect = visual.Rect(win, width=size[0], height=size[1], pos=pos,
                                fillColor=(-0.2,-0.2,-0.2), lineColor=(0.7,0.7,0.7))
        self.label = visual.TextStim(win, text=text, pos=pos, color='white', height=28)
    def draw(self): self.rect.draw(); self.label.draw()
    def contains(self, mouse): return self.rect.contains(mouse)

# =========================
# Dot field generation
# =========================
def _random_position(bounds_w, bounds_h):
    return (random.uniform(-bounds_w/2.0, bounds_w/2.0),
            random.uniform(-bounds_h/2.0, bounds_h/2.0))

def _far_enough(pt, pts, min_dist):
    for (x,y) in pts:
        if (pt[0]-x)**2 + (pt[1]-y)**2 < (min_dist**2):
            return False
    return True

def generate_dot_positions(n_total, radius=DOT_RADIUS, field_w=FIELD_W, field_h=FIELD_H,
                           min_dist=DOT_MIN_DIST, max_tries=5000):
    positions, tries = [], 0
    while len(positions) < n_total and tries < max_tries:
        tries += 1
        p = _random_position(field_w, field_h)
        if _far_enough(p, positions, min_dist):
            positions.append(p)
    return positions

def draw_dot_field(win, green_positions, yellow_positions, radius=DOT_RADIUS):

    dim_yellow = (0.4, 0.4, 0)    

    for (x, y) in yellow_positions:
        visual.Circle(win, radius=radius, pos=(x, y), 
                      fillColor=dim_yellow, lineColor=dim_yellow).draw()
    for (x, y) in green_positions:
        visual.Circle(win, radius=radius, pos=(x, y), 
                      fillColor='green', lineColor='green').draw()


# =========================
# Task elements
# =========================
def show_card_and_wait(green_pos, yellow_pos):
    mouse.clickReset()
    while True:
        check_escape()
        msg.text = "Count the GREEN dots. Ignore YELLOW.\n\nClick to continue after counting."
        msg.pos = (0, 400); msg.draw(); msg.pos = (0, 0)
        draw_dot_field(win, green_pos, yellow_pos)
        win.flip()
        if mouse.getPressed()[0]:
            rt = core.getTime()
            core.wait(0.15)
            return rt
        core.wait(0.01)

def recall_counts_ui(set_size):
    nums = [str(i) for i in range(10)]
    cols = 5; row_h = 90; col_w = 120
    origin_x = - (cols-1)/2 * col_w
    origin_y = + 40
    num_buttons = []
    for idx, t in enumerate(nums):
        r = idx//cols; c = idx%cols
        pos = (origin_x + c*col_w, origin_y - r*row_h)
        num_buttons.append(Button(win, t, pos, size=(100,60)))
    blank_btn = Button(win, "blank", pos=(-200, -240))
    clear_btn = Button(win, "clear", pos=(0, -240))
    exit_btn  = Button(win, "Exit",  pos=(200, -240))
    recalled = []
    mouse.clickReset()
    while True:
        check_escape()
        msg_small.text = f"Recall the GREEN counts (remaining: {set_size - len(recalled)})"
        msg_small.pos = (0, 300); msg_small.draw()
        for b in num_buttons: b.draw()
        for b in [blank_btn, clear_btn, exit_btn]: b.draw()
        prev = " ".join([str(x) if x is not None else "_" for x in recalled])
        msg.text = prev; msg.pos = (0, 200); msg.draw(); msg.pos = (0, 0)
        win.flip()
        if mouse.getPressed()[0]:
            if blank_btn.contains(mouse):
                if len(recalled) < set_size: recalled.append(None)
            elif clear_btn.contains(mouse):
                recalled = []
            elif exit_btn.contains(mouse):
                break
            else:
                for i, b in enumerate(num_buttons):
                    if b.contains(mouse) and len(recalled) < set_size:
                        recalled.append(int(nums[i]))
                        break
            while mouse.getPressed()[0]:
                core.wait(0.01)
            core.wait(0.05)
        if len(recalled) >= set_size:
            break
        core.wait(0.01)
    while len(recalled) < set_size:
        recalled.append(None)
    return recalled

def feedback_screen(n_correct_in_set, set_size):
    t_end = core.getTime() + FEEDBACK_DURATION
    while core.getTime() < t_end:
        check_escape()
        msg.text = f"You recalled {n_correct_in_set}/{set_size} correctly."
        msg.draw(); win.flip()

# =========================
# Logging & saving
# =========================
def log_set_rows(trial_rows, block_type, set_index, set_size,
                 green_counts, yellow_counts, card_rts, recalled):
    for i in range(set_size):
        trial_rows.append(dict(
            block_type=block_type,
            set_index=set_index,
            set_size=set_size,
            trial_in_set=i+1,
            stim_green=green_counts[i],
            stim_yellow=yellow_counts[i],
            rt_display=card_rts[i],
            recall_value="" if recalled[i] is None else recalled[i]
        ))

def save_triallog(trial_rows, path):
    fieldnames = ['block_type','set_index','set_size','trial_in_set',
                  'stim_green','stim_yellow','rt_display','recall_value']
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader(); writer.writerows(trial_rows)

def save_summary(summary_dict, path):
    fieldnames = ['abs_perfect_sum','total_correct_positions','average_rt_display']
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader(); writer.writerow(summary_dict)

# =========================
# Instructions
# =========================
show_instructions(
    "Welcome!\n\nIn this task, you'll see many dots displayed on the screen. You need to count and remember the number of GREEN dots on each display."
    "After a few displays, you need to recall the number of green dots on each display in order."
)

# =========================
# Practice block
# =========================
trial_rows = []
set_counter = 0
for set_size in PRACTICE_SET_SIZES:
    set_counter += 1
    green_counts = [random.randint(GREEN_RANGE[0], GREEN_RANGE[1]) for _ in range(set_size)]
    yellow_counts = [random.randint(YELLOW_RANGE[0], YELLOW_RANGE[1]) for _ in range(set_size)]
    green_positions_seq, yellow_positions_seq = [], []
    for i in range(set_size):
        n_g, n_y = green_counts[i], yellow_counts[i]
        pos = generate_dot_positions(n_g + n_y)
        green_positions_seq.append(pos[:n_g]); yellow_positions_seq.append(pos[n_g:])
    card_rts = []
    for i in range(set_size):
        rt = show_card_and_wait(green_positions_seq[i], yellow_positions_seq[i])
        card_rts.append(rt)
    recalled = recall_counts_ui(set_size)
    correct_positions = sum(1 for i in range(set_size) if recalled[i] == green_counts[i])
    feedback_screen(correct_positions, set_size)
    log_set_rows(trial_rows, 'practice', set_counter, set_size,
                 green_counts, yellow_counts, card_rts, recalled)

# =========================
# Main CSPAN block
# =========================
show_instructions(
    "Main task\n\nYou'll complete 15 tasks."
    "In each task, you need to count and remember the number of GREEN dots on each display. After a few displays, you need to recall the number of green dots on each display in order."
)

all_correct_positions = 0
all_rts = []
perfect_by_size = {s: [] for s in CSPAN_SET_SIZES}

for set_size in CSPAN_SET_SIZES:
    set_counter += 1
    green_counts = [random.randint(GREEN_RANGE[0], GREEN_RANGE[1]) for _ in range(set_size)]
    yellow_counts = [random.randint(YELLOW_RANGE[0], YELLOW_RANGE[1]) for _ in range(set_size)]
    green_positions_seq, yellow_positions_seq = [], []
    for i in range(set_size):
        n_g, n_y = green_counts[i], yellow_counts[i]
        pos = generate_dot_positions(n_g + n_y)
        green_positions_seq.append(pos[:n_g]); yellow_positions_seq.append(pos[n_g:])
    card_rts = []
    for i in range(set_size):
        rt = show_card_and_wait(green_positions_seq[i], yellow_positions_seq[i])
        card_rts.append(rt)
        all_rts.append(rt)
    recalled = recall_counts_ui(set_size)
    correct_positions = sum(1 for i in range(set_size) if recalled[i] == green_counts[i])
    all_correct_positions += correct_positions
    perfect_by_size[set_size].append(correct_positions == set_size)
    feedback_screen(correct_positions, set_size)
    log_set_rows(trial_rows, 'cspan_main', set_counter, set_size,
                 green_counts, yellow_counts, card_rts, recalled)

# =========================
# Compute summary
# =========================
abs_perfect_sum = sum(s for s in CSPAN_SET_SIZES for ok in perfect_by_size[s] if ok)
total_correct_positions = all_correct_positions
average_rt_display = sum(all_rts)/len(all_rts) if len(all_rts)>0 else 0.0

summary = dict(
    abs_perfect_sum=abs_perfect_sum,
    total_correct_positions=total_correct_positions,
    average_rt_display=round(average_rt_display,3)
)

save_triallog(trial_rows, triallog_path)
save_summary(summary, summary_path)

show_instructions(
    f"Task complete!\n\n"
    f"All-perfect set length sum: {abs_perfect_sum}\n"
    f"Total correct positions: {total_correct_positions}\n"
    f"Average RT (display): {average_rt_display:.2f} ms\n\nClick to finish."
)

win.close()
core.quit()
#exlib.stopExp(sid,hz,resX,resY,seed,dbConf)