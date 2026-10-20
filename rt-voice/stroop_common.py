import csv
import random
from psychopy import visual, core, event, sound

COLOR_WORDS = ["red", "blue", "green"]   # 3 colors (yellow dropped)
COLOR_RGB = {"red": "red", "blue": "blue", "green": "green"}

TEXT_COLOR = "white"
ACCENT_COLOR = "white"

# Single CSV for both modalities. Columns not applicable to a given
# modality are left blank on that row.
CSV_FIELDNAMES = [
    "modality", "block", "trial", "word", "color", "congruent",
    "transition",  # ink color vs previous trial: repeat / alternate / first
    "rt_ms", "correct", "timed_out", "no_response",
    "recognized_text", "recognized_color_word",  # voice-only
    "response_key", "recognized_color",          # manual-only
]

PRACTICE_N = 5
MAX_PRACTICE_ATTEMPTS = 4  # if practice isn't passed clean within this many
                            # rounds of 5, the experiment aborts.


def show_welcome(win):
    text = (f"Welcome to the study.\n\n"
            f"Press SPACE to continue.")
    show_message(win, text)


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


def show_block_intro(win, instructions_text, block_idx, total_blocks):
    """Single combined screen: full instructions + block progress + start
    prompt, all together. Shown every time a block begins."""
    text = (f"{instructions_text}\n\n"
            f"Block {block_idx} of {total_blocks}\n\n"
            f"Press SPACE to start.")
    show_message(win, text)


def show_practice_prompt(win, modality_label):
    text = f"{modality_label} — Practice\n\nPress SPACE to begin practice."
    show_message(win, text)


def show_practice_fail(win, modality_label):
    text = (f"{modality_label} — Practice incorrect.\n\n"
            f"Practice will restart.\n\n"
            f"Press SPACE to start.")
    show_message(win, text)


def show_practice_complete(win, modality_label):
    text = (f"{modality_label} — Practice complete!\n\n"
            f"Real trial starting now.\n\n"
            f"Press SPACE to continue.")
    show_message(win, text)


def build_trial_list(n_trials=100, n_repeat=33, max_imbalance=3, max_tries=5000):
    """Full block with strictly fixed counts (defaults: 100 trials):

      * n_trials // 2 congruent, n_trials // 2 incongruent
      * 1 "first" trial (no predecessor, transition = "first")
      * n_repeat trials whose ink color == previous ink color ("repeat")
      * n_trials - 1 - n_repeat trials whose ink color != previous ("alternate")
        -> 100 trials = 1 first + 33 repeat + 66 alternate

    Congruency is split as evenly as possible inside repeat and alternate:
    alternate is 33 cong / 33 incong; repeat is 16/17 or 17/16 (the odd one
    out depends on whether the first trial is congruent, so the whole block
    is exactly 50/50).

    Colors/words are filled in sequentially from a shuffled list of
    (congruency, transition) cells:
      repeat    -> ink color == previous ink color
      alternate -> ink color != previous ink color (one of the other 2)
      congruent -> word == color; incongruent -> word != color
    The sequence is re-drawn until per-color and per-word counts are within
    `max_imbalance` of each other."""
    n_alt = n_trials - 1 - n_repeat
    n_cong_total = n_trials // 2
    assert n_trials % 2 == 0 and 0 <= n_repeat <= n_trials - 1

    def pick_word(color, congruent):
        if congruent:
            return color
        return random.choice([c for c in COLOR_WORDS if c != color])

    best = None
    for _ in range(max_tries):
        first_cong = random.random() < 0.5
        cong_left = n_cong_total - int(first_cong)   # congruent among the rest
        alt_cong = n_alt // 2
        rep_cong = cong_left - alt_cong
        assert 0 <= rep_cong <= n_repeat, "counts not satisfiable"
        cells = ([(True, "repeat")] * rep_cong
                 + [(False, "repeat")] * (n_repeat - rep_cong)
                 + [(True, "alternate")] * alt_cong
                 + [(False, "alternate")] * (n_alt - alt_cong))
        random.shuffle(cells)

        color = random.choice(COLOR_WORDS)
        trials = [{"word": pick_word(color, first_cong), "color": color,
                   "transition": "first"}]
        prev_color = color

        for cong, trans in cells:
            if trans == "repeat":
                color = prev_color
            else:
                color = random.choice([c for c in COLOR_WORDS if c != prev_color])
            trials.append({"word": pick_word(color, cong), "color": color,
                           "transition": trans})
            prev_color = color

        color_counts = [sum(t["color"] == c for t in trials) for c in COLOR_WORDS]
        word_counts = [sum(t["word"] == c for t in trials) for c in COLOR_WORDS]
        spread = max(max(color_counts) - min(color_counts),
                     max(word_counts) - min(word_counts))
        if best is None or spread < best[0]:
            best = (spread, trials)
        if spread <= max_imbalance:
            break
    return best[1]


def build_practice_list(n=PRACTICE_N):
    """Practice: each trial independently random congruent/incongruent
    (not a fixed split, per spec)."""
    trials = []
    for _ in range(n):
        word = random.choice(COLOR_WORDS)
        if random.random() < 0.5:
            color = word
        else:
            color = random.choice([c for c in COLOR_WORDS if c != word])
        trials.append({"word": word, "color": color})
    return trials


def make_tones():
    correct_tone = sound.Sound(value=880, secs=0.15)
    wrong_tone = sound.Sound(value=220, secs=0.15)
    no_response_tone = sound.Sound(value=140, secs=0.15)
    return correct_tone, wrong_tone, no_response_tone


def make_stims(win):
    stim_text = visual.TextStim(win, text="", height=0.2, font="Arial", bold=True)
    fixation = visual.TextStim(win, text="+", color=ACCENT_COLOR, height=0.08)
    return stim_text, fixation


def write_csv_row(data_path, row):
    with open(data_path, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=CSV_FIELDNAMES).writerow(row)
