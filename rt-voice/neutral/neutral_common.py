import csv
import random
from types import SimpleNamespace

from psychopy import visual, core, event, sound

# ---------------- settings ----------------
COLORS = ["red", "green", "blue", "yellow"]          # all colours in the study
COLOR_RGB = {"red": (235, 45, 45), "green": (40, 190, 70),
             "blue": (70, 120, 255), "yellow": (240, 215, 30)}
KEYS = ["f", "j", "d", "k"]      # 2 colours -> F J, 4 colours -> F J D K
SET_SIZES = [2, 4]
STIM_TEXT = "#####"

TRIALS_PER_BLOCK = 100           # 1 first + 33 repeat + 66 alternate
REPEAT_PROP = 1 / 3              # proportion of colour repeats, same for 2 and 4 colours
PRACTICE_TRIALS = 8
PRACTICE_PASS = 7                # correct out of PRACTICE_TRIALS
MAX_PRACTICE_ROUNDS = 4

FIXATION = 0.5
RESPONSE_WINDOW = 2.0            # response must start within this (s)
NO_RESPONSE_END = 2.5            # trial ends here if nothing was detected
KEYBOARD_EXTRA_DELAY = 0.40      # keyboard waits this long after the press (to match
                                 # Vosk's recognition time); set from the pilot
ITI = 0.35                       # blank after the trial ends (tone plays here)

CSV_FIELDNAMES = ["modality", "set_size", "block", "trial", "color", "target_key",
                  "transition", "responded", "response", "correct", "rt_ms",
                  "end_lag_ms", "rsi_ms", "recognized_text", "audio_file"]

INSTRUCTIONS = {
    "manual": "Press the key for the COLOR of the symbols as fast and as accurately as you can.",
    "voice": "Say the COLOR of the symbols out loud as fast and as accurately as you can.\n"
             "Say the color word once.",
}


def rgb(color):
    return [v / 127.5 - 1 for v in COLOR_RGB[color]]


# ---------------- participant setup ----------------
def setup_participant(pid):
    """Colour->key map and block order, both fixed by the pid.
    Block order: A(sizes) B(sizes) | B(reversed) A(reversed)."""
    pid = int(pid)
    rng = random.Random(pid)
    colors = COLORS[:]
    rng.shuffle(colors)                       # colors[:2] are used in the 2-colour blocks
    key_map = dict(zip(colors, KEYS))         # colour -> key
    a, b = ("manual", "voice") if pid % 2 == 0 else ("voice", "manual")
    sizes = SET_SIZES if (pid // 2) % 2 == 0 else SET_SIZES[::-1]
    order = ([(a, n) for n in sizes] + [(b, n) for n in sizes]
             + [(b, n) for n in sizes[::-1]] + [(a, n) for n in sizes[::-1]])
    return colors, key_map, order, rng


def build_trials(colors, rng):
    """Colour sequence for one block: exactly REPEAT_PROP colour repeats,
    colour counts within 2 of each other."""
    n = TRIALS_PER_BLOCK
    n_rep = round(REPEAT_PROP * (n - 1))
    while True:
        repeats = [True] * n_rep + [False] * (n - 1 - n_rep)
        rng.shuffle(repeats)
        seq = [rng.choice(colors)]
        for rep in repeats:
            seq.append(seq[-1] if rep else rng.choice([c for c in colors if c != seq[-1]]))
        counts = [seq.count(c) for c in colors]
        if max(counts) - min(counts) <= 2:
            return seq


# ---------------- screens ----------------
def make_stims(win):
    return SimpleNamespace(
        stim=visual.TextStim(win, STIM_TEXT, height=0.2, font="Arial", bold=True),
        fixation=visual.TextStim(win, "+", height=0.08),
        tones=dict(correct=sound.Sound(880, secs=0.15), wrong=sound.Sound(220, secs=0.15),
                   none=sound.Sound(140, secs=0.15)))


def show(win, text, mapping=()):
    """Text, optional coloured mapping lines, wait for SPACE."""
    visual.TextStim(win, text, pos=(0, 0.22), height=0.035, wrapWidth=1.4).draw()
    for i, (label, color) in enumerate(mapping):
        visual.TextStim(win, label, pos=(0, -0.02 - 0.07 * i), height=0.05,
                        color=rgb(color), bold=True).draw()
    visual.TextStim(win, "Press SPACE to continue.", pos=(0, -0.4), height=0.03).draw()
    win.flip()
    if "escape" in event.waitKeys(keyList=["space", "escape"]):
        core.quit()


def mapping_lines(modality, colors, key_map):
    if modality == "manual":                  # left to right on the keyboard: D F J K
        by_key = {key_map[c]: c for c in colors}
        return [(f"{k.upper()} = {by_key[k]}", by_key[k]) for k in "dfjk" if k in by_key]
    return [(c, c) for c in colors]


# ---------------- one trial ----------------
def run_trial(win, S, mod, color, tag):
    S.fixation.draw()
    win.flip()
    fix_on = core.getTime()
    mod.begin(win)                            # clear keys / new recogniser, during the fixation
    core.wait(max(0.0, fix_on + FIXATION - core.getTime()))

    S.stim.setColor(rgb(color))
    S.stim.draw()
    win.flip()
    t0 = core.getTime()                       # stimulus onset; RT is measured from here

    resp = None
    while resp is None and core.getTime() - t0 < NO_RESPONSE_END:
        resp = mod.check(t0)                  # None until a response is complete
        if event.getKeys(["escape"]):
            core.quit()
        core.wait(0.001, hogCPUperiod=0)

    if resp is not None:                      # keyboard only: wait extra_delay after the press
        core.wait(max(0.0, t0 + resp["rt"] / 1000 + mod.extra_delay - core.getTime()))
    win.flip()                                # stimulus off = end of the trial
    t_end = core.getTime()

    correct = resp is not None and resp["color"] == color
    S.tones["none" if resp is None else "correct" if correct else "wrong"].play()
    extra = mod.after(tag)                    # voice: save the audio, recognised text
    core.wait(max(0.0, t_end + ITI - core.getTime()))
    return dict(resp=resp, correct=correct, t0=t0, t_end=t_end, extra=extra)


# ---------------- blocks ----------------
def write_header(path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, CSV_FIELDNAMES).writeheader()


def run_block(win, S, mod, block_num, colors, key_map, rng, path):
    prev_color = prev_resp_time = None
    lags = []
    for i, color in enumerate(build_trials(colors, rng), start=1):
        r = run_trial(win, S, mod, color, f"b{block_num}_t{i}")
        resp = r["resp"]
        rt = resp["rt"] if resp else None
        row = dict(modality=mod.name, set_size=len(colors), block=block_num, trial=i,
                   color=color, target_key=key_map[color],
                   transition=("first" if prev_color is None
                               else "repeat" if color == prev_color else "alternate"),
                   responded=resp is not None, response=resp["response"] if resp else "",
                   correct=r["correct"], rt_ms=round(rt, 1) if resp else "",
                   end_lag_ms=round((r["t_end"] - r["t0"]) * 1000 - rt, 1) if resp else "",
                   rsi_ms=round((r["t0"] - prev_resp_time) * 1000, 1) if prev_resp_time else "",
                   **r["extra"])
        with open(path, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, CSV_FIELDNAMES).writerow(row)
        if resp:
            lags.append(row["end_lag_ms"])
        prev_color = color
        prev_resp_time = r["t0"] + rt / 1000 if resp else None
    if mod.name == "voice" and lags:
        lags.sort()
        print(f"[voice] median recognition lag this block: {lags[len(lags) // 2]:.0f} ms "
              f"(KEYBOARD_EXTRA_DELAY is {KEYBOARD_EXTRA_DELAY * 1000:.0f} ms)")


def run_practice(win, S, mod, colors, key_map, rng):
    """Rounds of PRACTICE_TRIALS (not saved). Pass = PRACTICE_PASS correct."""
    for rnd in range(MAX_PRACTICE_ROUNDS):
        seq = (colors * PRACTICE_TRIALS)[:PRACTICE_TRIALS]
        rng.shuffle(seq)
        n_correct = sum(run_trial(win, S, mod, c, f"practice{rnd + 1}_t{j}")["correct"]
                        for j, c in enumerate(seq, start=1))
        if n_correct >= PRACTICE_PASS:
            show(win, f"Practice complete ({n_correct} of {PRACTICE_TRIALS} correct).\n\n"
                      f"The real block starts next.")
            return True
        show(win, f"{n_correct} of {PRACTICE_TRIALS} correct (need {PRACTICE_PASS}).\n\n"
                  f"Let's practice once more.", mapping_lines(mod.name, colors, key_map))
    return False
