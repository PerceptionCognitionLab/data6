import sys
import os
import csv
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib
from psychopy import visual

from stroop_common import CSV_FIELDNAMES, show_welcome, show_loading
from stroop_voicekey import VoiceModality
from stroop_manual import ManualModality

dbConf = exlib.beta
expName = "rt-voice"
seed = None

nBlocks = 4          
nTrials = 48 # must be multiple of 12

assert nTrials % 12 == 0, f"nTrials ({nTrials}) must be divisible by 12."
refreshRate = 165
exlib.setRefreshRate(refreshRate)
pool = 3

[pid, _, _] = exlib.startExp(expName, dbConf, pool, lockBox=True, refreshRate=refreshRate)

BG_COLOR = [-0.85, -0.85, -0.85]
win = visual.Window(fullscr=True, color=BG_COLOR, units="height", allowGUI=False)

show_welcome(win)

# --- modality order: odd pid -> voice first, even pid -> keyboard first ---
first_key = "voice" if int(pid) % 2 == 1 else "manual"
second_key = "manual" if first_key == "voice" else "voice"

modality_sequence = []
for _ in range(nBlocks):
    modality_sequence.append(first_key)
    modality_sequence.append(second_key)
TOTAL_BLOCKS = len(modality_sequence)  # 8 with default nBlocks=4

# --- single CSV covering both modalities ---
os.makedirs("data", exist_ok=True)
data_path = os.path.join("data", f"{pid}.csv")
with open(data_path, "w", newline="", encoding="utf-8") as f:
    csv.DictWriter(f, fieldnames=CSV_FIELDNAMES).writeheader()

# Loading the voice recognizer model (inside VoiceModality.__init__) takes
# tens of seconds, so show a "please wait" screen first; whatever screen
# comes next (the first block's intro) replaces it automatically once
# loading finishes, with no keypress needed in between.
show_loading(win)
voice_mod = VoiceModality(win, pid)
manual_mod = ManualModality(win, pid)
modalities = {"voice": voice_mod, "manual": manual_mod}

aborted = False

for block_idx, modality_key in enumerate(modality_sequence, start=1):
    mod = modalities[modality_key]
    mod.enter_block()  # opens the mic if this is a voice block, no-op otherwise

    mod.show_block_intro(block_idx, TOTAL_BLOCKS)  # combined instructions + "Block N of 8" + start prompt

    # practice runs at the start of every block (not just the first time a
    # modality appears)
    passed = mod.run_practice()
    if not passed:
        mod.exit_block()
        aborted = True
        break

    mod.run_block(block_idx, nTrials, data_path)
    mod.exit_block()  # closes the mic if this was a voice block

win.close()

# --- end-of-experiment concern/questionnaire window (unchanged from original) ---
concern_win = visual.Window(fullscr=True, color=BG_COLOR, units="pix", allowGUI=False)
resX, resY = concern_win.size
concern = exlib.getConcern(concern_win)
concern_win.close()

exlib.stopExp(pid, refreshRate, resX, resY, seed, dbConf, concern)
