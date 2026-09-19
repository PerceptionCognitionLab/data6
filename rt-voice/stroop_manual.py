from psychopy import core, event

from stroop_common import (
    COLOR_RGB, CSV_FIELDNAMES,
    check_quit, show_block_intro, show_practice_prompt,
    show_practice_fail, show_practice_complete,
    build_trial_list, build_practice_list, make_tones, make_stims,
    write_csv_row, MAX_PRACTICE_ATTEMPTS,
)

# d/f/j/k -> color, left/right hand symmetric mapping
KEY_TO_COLOR = {"d": "red", "f": "blue", "j": "green", "k": "yellow"}
RESPONSE_TIMEOUT = 2.0  # seconds, same as SILENCE_TIMEOUT in the voice version

INSTRUCTIONS_TEXT = (
    "In each trial, press the key matching the INK COLOR of the word "
    "as fast as you can (ignore what the word says).\n\n"
    "D = red      F = blue      J = green      K = yellow\n\n"
    "You will hear a tone after each response."
)

PRACTICE_REMINDER_TEXT = (
    "Remember: press the key matching the INK COLOR — "
    "D = red   F = blue   J = green   K = yellow"
)


def wait_for_keypress(stim_onset_time, timeout=RESPONSE_TIMEOUT):
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


class ManualModality:
    label = "Keyboard"
    key = "manual"

    def __init__(self, win, pid):
        self.win = win
        self.pid = pid
        self.correct_tone, self.wrong_tone, self.no_response_tone = make_tones()
        self.stim_text, self.fixation = make_stims(win)

    # no mic to manage, but keep the same interface as VoiceModality so
    # main.py can drive both uniformly
    def enter_block(self):
        pass

    def exit_block(self):
        pass

    def show_block_intro(self, block_idx, total_blocks):
        show_block_intro(self.win, INSTRUCTIONS_TEXT, block_idx, total_blocks)

    def _run_trial(self, trial, block_num, trial_num, record):
        word, color = trial["word"], trial["color"]
        congruent = (word == color)

        self.fixation.draw()
        self.win.flip()
        core.wait(0.5)

        event.clearEvents()  # drop stray keys pressed before stim onset
        self.stim_text.setText(word.upper())
        self.stim_text.setColor(COLOR_RGB[color])
        self.stim_text.draw()
        self.win.flip()
        stim_onset_time = core.getTime()

        result = wait_for_keypress(stim_onset_time)

        response_color = KEY_TO_COLOR.get(result["key"], "")
        is_correct = (response_color == color)
        no_response = result["timed_out"]

        self.win.flip()  # clear stimulus while tone plays
        if no_response:
            self.no_response_tone.play()
        elif is_correct:
            self.correct_tone.play()
        else:
            self.wrong_tone.play()
        core.wait(0.35)

        check_quit()

        if not record:
            return is_correct

        row = {fn: "" for fn in CSV_FIELDNAMES}
        row.update({
            "modality": "manual",
            "block": block_num,
            "trial": trial_num,
            "word": word,
            "color": color,
            "congruent": congruent,
            "rt_ms": round(result["rt_ms"], 1) if result["rt_ms"] else "",
            "correct": is_correct,
            "timed_out": result["timed_out"],
            "no_response": no_response,
            "response_key": result["key"] or "",
            "recognized_color": response_color,
        })
        return row, is_correct

    def run_practice(self, max_attempts=MAX_PRACTICE_ATTEMPTS):
        """Runs rounds of up to 5 practice trials (not saved to CSV). A
        round stops the moment a trial is wrong. Passes only on a clean
        round of all 5 correct; gives up after max_attempts rounds."""
        show_practice_prompt(self.win, self.label)
        for attempt in range(max_attempts):
            trials = build_practice_list()
            passed = True
            for i, trial in enumerate(trials, start=1):
                check_quit()
                is_correct = self._run_trial(trial, 0, i, record=False)
                if not is_correct:
                    passed = False
                    break  # stop this round immediately on the first error
            if passed:
                show_practice_complete(self.win, self.label)
                return True
            show_practice_fail(self.win, PRACTICE_REMINDER_TEXT)  # also doubles as the
            # "press space to start" prompt for the next round
        return False

    def run_block(self, block_num_total, n_trials, data_path):
        trials = build_trial_list(n_congruent=n_trials, n_incongruent=n_trials)
        for i, trial in enumerate(trials, start=1):
            check_quit()
            row, _ = self._run_trial(trial, block_num_total, i, record=True)
            write_csv_row(data_path, row)
