import csv
import random
from psychopy import visual, core, event, sound

COLOR_WORDS = ["red", "blue", "green", "yellow"]
COLOR_RGB = {"red": "red", "blue": "blue", "green": "green", "yellow": "yellow"}

TEXT_COLOR = "white"
ACCENT_COLOR = "white"

# Single CSV for both modalities. Columns not applicable to a given
# modality are left blank on that row.
CSV_FIELDNAMES = [
    "modality", "block", "trial", "word", "color", "congruent",
    "rt_ms", "correct", "timed_out", "no_response",
    "recognized_text", "recognized_color_word", "audio_file",  # voice-only
    "response_key", "recognized_color",          # manual-only
]

PRACTICE_N = 5
MAX_PRACTICE_ATTEMPTS = 4  # if practice isn't passed clean within this many
                            # rounds of 5, the experiment aborts.

# Per-block trial counts. Combination-balanced (each congruent color, each
# incongruent word/color pair appears an equal number of times) AND
# sequence-balanced (an exact number of adjacent-same-color "repeat" trials).
N_CONGRUENT_PER_BLOCK = 48
N_INCONGRUENT_PER_BLOCK = 48
N_REPEATS_TARGET_PER_BLOCK = 24
REPEAT_BALANCE_MAX_ITERATIONS = 5000


def show_welcome(win):
    text = (f"Welcome to the study.\n\n"
            f"Press SPACE to continue.")
    show_message(win, text)


def show_loading(win, text="Loading, please wait..."):
    """No wait-for-space: draws once and returns immediately, so the caller
    can go do the slow work (e.g. loading the speech model) right after the
    flip, and the next screen shown afterwards is what makes this feel like
    an automatic transition."""
    stim = visual.TextStim(win, text=text, color=TEXT_COLOR, height=0.05,
                            wrapWidth=1.3, font="Arial")
    stim.draw()
    win.flip()


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
    """Single combined screen: block progress on top, full instructions
    below, start prompt at the bottom. Shown every time a block begins."""
    text = (f"Block {block_idx} of {total_blocks}\n\n"
            f"{instructions_text}\n\n"
            f"Press SPACE to start.")
    show_message(win, text)


def show_practice_prompt(win, modality_label):
    text = f"{modality_label} — Practice\n\nPress SPACE to begin practice."
    show_message(win, text)


def show_practice_fail(win, reminder_text):
    text = (f"Practice incorrect. Practice will restart.\n\n"
            f"{reminder_text}\n\n"
            f"Press SPACE to start.")
    show_message(win, text)


def show_practice_complete(win, modality_label):
    text = (f"{modality_label} — Practice complete!\n\n"
            f"Real trial starting now.\n\n"
            f"Press SPACE to continue.")
    show_message(win, text)


def build_trial_list(n_congruent=N_CONGRUENT_PER_BLOCK,
                      n_incongruent=N_INCONGRUENT_PER_BLOCK,
                      target_repeats=None):
    """Builds one block's trial sequence with two balance constraints:

      1. Combination balance: each congruent color, and each of the 12
         incongruent (word, color) pairs, appears an equal number of times.
      2. Repetition balance: the number of adjacent trials that share the
         same target color ("repeat" trials, per the repetition-effect
         definition: repeat iff trial[i].color == trial[i-1].color) is
         exactly target_repeats.

    n_congruent must be a multiple of len(COLOR_WORDS) (4).
    n_incongruent must be a multiple of the number of incongruent
    (word, color) combinations (12, for 4 colors).

    target_repeats defaults to ~25.3% of adjacent pairs (the ratio picked
    for the 48/48 case: 24 repeats out of 95 pairs), scaled to whatever
    n_congruent/n_incongruent are given so it doesn't need to be
    recomputed by hand if those change.
    """
    n_colors = len(COLOR_WORDS)
    incongruent_combos = [(w, c) for w in COLOR_WORDS for c in COLOR_WORDS if w != c]

    if n_congruent % n_colors != 0:
        raise ValueError(
            f"n_congruent ({n_congruent}) must be a multiple of {n_colors} colors."
        )
    if n_incongruent % len(incongruent_combos) != 0:
        raise ValueError(
            f"n_incongruent ({n_incongruent}) must be a multiple of "
            f"{len(incongruent_combos)} word/color combinations."
        )

    if target_repeats is None:
        n_pairs = n_congruent + n_incongruent - 1
        target_repeats = round(n_pairs / 4)

    trials = []

    per_congruent_color = n_congruent // n_colors
    for word in COLOR_WORDS:
        for _ in range(per_congruent_color):
            trials.append({"word": word, "color": word})

    per_incongruent_combo = n_incongruent // len(incongruent_combos)
    for word, color in incongruent_combos:
        for _ in range(per_incongruent_combo):
            trials.append({"word": word, "color": color})

    random.shuffle(trials)
    trials = _balance_repeats(trials, target_repeats)
    return trials


def _count_repeats(trials):
    """Number of adjacent pairs sharing the same target color."""
    return sum(1 for i in range(1, len(trials)) if trials[i]["color"] == trials[i - 1]["color"])


def _balance_repeats(trials, target_repeats, max_iterations=REPEAT_BALANCE_MAX_ITERATIONS):
    """Hill-climbs toward an exact repeat count by swapping pairs of trial
    positions (which changes adjacency but never the underlying combination
    counts, so combination balance is preserved automatically)."""
    trials = trials[:]
    n = len(trials)
    current = _count_repeats(trials)

    for _ in range(max_iterations):
        if current == target_repeats:
            return trials
        i, j = random.sample(range(n), 2)
        trials[i], trials[j] = trials[j], trials[i]
        new_count = _count_repeats(trials)
        if abs(new_count - target_repeats) < abs(current - target_repeats):
            current = new_count
        else:
            trials[i], trials[j] = trials[j], trials[i]  # revert the swap

    if current != target_repeats:
        raise RuntimeError(
            f"Could not balance repeat count to exactly {target_repeats} "
            f"within {max_iterations} iterations (best reached: {current})."
        )
    return trials


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
