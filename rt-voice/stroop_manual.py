"""
Manual (Keyboard) Stroop Task (PsychoPy)
==========================================
Same trial structure, block structure, experiment flow, on-screen interface,
stimulus presentation, and data-storage convention as stroop_voicekey.py —
the only difference is the response modality: participants press D/F/J/K
instead of speaking. RT is measured with a simple polling loop using
event.getKeys() (lower precision than psychopy.hardware.keyboard, but
sufficient for most behavioral purposes and matches what was requested).

Design: 4 blocks x 50 trials (25 congruent / 25 incongruent each) = 200 trials.
Fullscreen. Press ESC at any time to quit.
"""

import os
import csv
import random
from datetime import datetime

import pyglet
from psychopy import visual, core, event, gui, sound

# ------------------------------------------------------------------
# Config — identical to stroop_voicekey.py except response-modality bits
# ------------------------------------------------------------------

COLOR_WORDS = ["red", "blue", "green", "yellow"]
COLOR_RGB = {"red": "red", "blue": "blue", "green": "green", "yellow": "yellow"}

# d/f/j/k -> color, left/right hand symmetric mapping
KEY_TO_COLOR = {"d": "red", "f": "blue", "j": "green", "k": "yellow"}

N_BLOCKS = 4
TRIALS_PER_CONDITION = 25   # per block: 25 congruent + 25 incongruent
RESPONSE_TIMEOUT = 2.0      # seconds, same as SILENCE_TIMEOUT in the voice version

BG_COLOR = [-0.85, -0.85, -0.85]     # near-black gray background
TEXT_COLOR = "white"
ACCENT_COLOR = "white"               # fixation cross etc — grayscale only;
                                      # only the stimulus word uses COLOR_RGB

DATA_DIR = os.path.join("data", "manual")  # separate from stroop_voicekey.py's "data/voice"
os.makedirs(DATA_DIR, exist_ok=True)


# ------------------------------------------------------------------
# Trial list — identical logic to stroop_voicekey.py's build_blocks()
# ------------------------------------------------------------------

def build_blocks():
    blocks = []
    for _ in range(N_BLOCKS):
        trials = []
        for _ in range(TRIALS_PER_CONDITION):
            word = random.choice(COLOR_WORDS)
            trials.append({"word": word, "color": word})  # congruent
        for _ in range(TRIALS_PER_CONDITION):
            word = random.choice(COLOR_WORDS)
            color = random.choice([c for c in COLOR_WORDS if c != word])
            trials.append({"word": word, "color": color})  # incongruent
        random.shuffle(trials)
        blocks.append(trials)
    return blocks


# ------------------------------------------------------------------
# Visual helpers — identical to stroop_voicekey.py
# ------------------------------------------------------------------

def get_screen_size():
    screen = pyglet.canvas.get_display().get_default_screen()
    return screen.width, screen.height


def make_window():
    # A borderless window sized to fill the screen, instead of fullscr=True —
    # exclusive fullscreen mode on Windows sometimes fails to grab OS keyboard
    # focus, so keys never register. This looks the same but stays a normal
    # focusable window.
    return visual.Window(fullscr=False, size=get_screen_size(), pos=(0, 0),
                          color=BG_COLOR, units="height", allowGUI=False)


def check_quit():
    if "escape" in event.getKeys(keyList=["escape"]):
        core.quit()


def show_message(win, text, wait_for_space=True, height=0.045):
    stim = visual.TextStim(win, text=text, color=TEXT_COLOR, height=height,
                            wrapWidth=1.3, font="Arial")
    stim.draw()
    win.flip()
    if wait_for_space:
        while True:
            keys = event.waitKeys(keyList=["space", "escape"])
            if "escape" in keys:
                core.quit()
            if "space" in keys:
                break


# ------------------------------------------------------------------
# Keyboard response collection
# ------------------------------------------------------------------

def wait_for_keypress(stim_onset_time, timeout=RESPONSE_TIMEOUT):
    """
    Poll for a d/f/j/k keypress. RT is measured from stim_onset_time to
    the moment event.getKeys() reports the key (same clock: core.getTime(),
    consistent with the timing approach used in stroop_voicekey.py).

    Note: event.getKeys() timing precision is limited by how often this
    loop polls (not tied to display refresh), typically within a few ms
    on a modern machine, but psychopy.hardware.keyboard would give more
    precise, hardware-timestamped RTs if higher precision is needed later.
    """
    deadline = stim_onset_time + timeout
    while True:
        now = core.getTime()
        if now > deadline:
            return {"key": None, "rt_ms": None, "timed_out": True}

        keys = event.getKeys(keyList=list(KEY_TO_COLOR.keys()) + ["escape"])
        if keys:
            key = keys[0]
            if key == "escape":
                core.quit()
            rt_ms = (core.getTime() - stim_onset_time) * 1000.0
            return {"key": key, "rt_ms": rt_ms, "timed_out": False}


# ------------------------------------------------------------------
# Main experiment
# ------------------------------------------------------------------

def run_experiment():
    info = {"Subject ID": "", "Session": "001"}
    dlg = gui.DlgFromDict(info, title="Keyboard Stroop")
    if not dlg.OK:
        core.quit()

    subj_id = info["Subject ID"] or "test"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_path = os.path.join(DATA_DIR, f"{subj_id}_{timestamp}.csv")

    correct_tone = sound.Sound(value=880, secs=0.15)
    wrong_tone = sound.Sound(value=220, secs=0.25)
    no_response_tone = sound.Sound(value=140, secs=0.35)

    win = make_window()
    stim_text = visual.TextStim(win, text="", height=0.2, font="Arial", bold=True)
    fixation = visual.TextStim(win, text="+", color=ACCENT_COLOR, height=0.08)

    show_message(
        win,
        "In each trial, press the key matching the INK COLOR of the word "
        "as fast as you can (ignore what the word says).\n\n"
        "D = red      F = blue      J = green      K = yellow\n\n"
        "You will hear a tone after each response.\n\n"
        "Press SPACE to begin."
    )

    blocks = build_blocks()

    fieldnames = [
        "block", "trial", "word", "color", "congruent",
        "rt_ms", "response_key", "recognized_color", "correct",
        "timed_out", "no_response",
    ]
    with open(data_path, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=fieldnames).writeheader()

    try:
        for b, block_trials in enumerate(blocks, start=1):
            show_message(
                win,
                f"Block {b} of {N_BLOCKS}\n\nPress SPACE to start.",
            )

            for i, trial in enumerate(block_trials, start=1):
                check_quit()
                word, color = trial["word"], trial["color"]
                congruent = (word == color)

                fixation.draw()
                win.flip()
                core.wait(0.5)

                event.clearEvents()  # drop stray keys pressed before stim onset
                stim_text.setText(word.upper())
                stim_text.setColor(COLOR_RGB[color])
                stim_text.draw()
                win.flip()
                stim_onset_time = core.getTime()

                result = wait_for_keypress(stim_onset_time)

                response_color = KEY_TO_COLOR.get(result["key"], "")
                is_correct = (response_color == color)
                no_response = result["timed_out"]

                win.flip()  # clear stimulus while tone plays
                if no_response:
                    no_response_tone.play()
                    core.wait(0.35)
                elif is_correct:
                    correct_tone.play()
                    core.wait(0.15)
                else:
                    wrong_tone.play()
                    core.wait(0.25)

                with open(data_path, "a", newline="", encoding="utf-8") as f:
                    csv.DictWriter(f, fieldnames=fieldnames).writerow({
                        "block": b,
                        "trial": i,
                        "word": word,
                        "color": color,
                        "congruent": congruent,
                        "rt_ms": round(result["rt_ms"], 1) if result["rt_ms"] else "",
                        "response_key": result["key"] or "",
                        "recognized_color": response_color,
                        "correct": is_correct,
                        "timed_out": result["timed_out"],
                        "no_response": no_response,
                    })

                check_quit()

        show_message(win, "Experiment complete. Thank you!", wait_for_space=False)
        core.wait(2.0)
    finally:
        win.close()

    core.quit()


if __name__ == "__main__":
    run_experiment()