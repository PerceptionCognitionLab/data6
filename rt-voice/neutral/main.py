import os
import sys

sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib
from psychopy import visual

from neutral_common import (INSTRUCTIONS, setup_participant, make_stims, show,
                            mapping_lines, write_header, run_practice, run_block)
from neutral_manual import ManualModality
from neutral_voicekey import VoiceModality

dbConf = exlib.beta
expName = "rt-voice"
refreshRate = 165
exlib.setRefreshRate(refreshRate)
pool = 3

[pid, _, _] = exlib.startExp(expName, dbConf, pool, lockBox=True, refreshRate=refreshRate)

colors, key_map, order, rng = setup_participant(pid)
print(f"[pid {pid}] keys: {key_map}  order: {order}")

os.makedirs("data", exist_ok=True)
data_path = os.path.join("data", f"{pid}.csv")
write_header(data_path)

BG_COLOR = [-0.85, -0.85, -0.85]
win = visual.Window(fullscr=True, color=BG_COLOR, units="height", allowGUI=False)
S = make_stims(win)
show(win, "Welcome to the study.")

modalities = {"manual": ManualModality(key_map), "voice": VoiceModality(pid)}
practiced = set()
aborted = False

for block_num, (modality, n) in enumerate(order, start=1):
    mod = modalities[modality]
    block_colors = colors[:n]
    mapping = mapping_lines(modality, block_colors, key_map)
    mod.enter_block()
    show(win, f"{INSTRUCTIONS[modality]}\n\nBlock {block_num} of {len(order)}", mapping)

    if (modality, n) not in practiced:   # practice the first time each condition appears
        show(win, "First a short practice.", mapping)
        if not run_practice(win, S, mod, block_colors, key_map, rng):
            mod.exit_block()
            aborted = True
            break
        practiced.add((modality, n))

    run_block(win, S, mod, block_num, block_colors, key_map, rng, data_path)
    mod.exit_block()

show(win, "Practice was not passed. Please tell the experimenter." if aborted
     else "All blocks are done. Thank you!")
win.close()

# --- end-of-experiment concern/questionnaire window (unchanged from original) ---
concern_win = visual.Window(fullscr=True, color=BG_COLOR, units="pix", allowGUI=False)
resX, resY = concern_win.size
concern = exlib.getConcern(concern_win)
concern_win.close()

exlib.stopExp(pid, refreshRate, resX, resY, int(pid), dbConf, concern)
