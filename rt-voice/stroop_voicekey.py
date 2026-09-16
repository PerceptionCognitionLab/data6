import os
import json
import queue
import csv
import random
import wave
from datetime import datetime
import numpy as np
import pyglet
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from psychopy import visual, core, event, gui, sound

VOSK_MODEL_PATH = "model/vosk-model-small-en-us-0.15"
SILENCE_TIMEOUT = 2.0
PRE_TRIAL_DISCARD_MARGIN = 0.0
COLOR_WORDS = ["red", "blue", "green", "yellow"]
COLOR_RGB = {"red": "red", "blue": "blue", "green": "green", "yellow": "yellow"}
N_BLOCKS = 4
TRIALS_PER_CONDITION = 25  # per block: 25 congruent + 25 incongruent
BG_COLOR = [-0.85, -0.85, -0.85]
TEXT_COLOR = "white"
ACCENT_COLOR = "white"
DATA_DIR = os.path.join("data", "voice")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

for hostapi in sd.query_hostapis():
    if "wasapi" in hostapi["name"].lower():
        DEVICE = hostapi.get("default_input_device", -1)
SAMPLE_RATE = int(round(sd.query_devices(DEVICE)["default_samplerate"]))
BLOCK_SIZE = int(SAMPLE_RATE/1000) # 1ms per block

def build_blocks():
    blocks = []
    for _ in range(N_BLOCKS):
        trials = []
        for _ in range(TRIALS_PER_CONDITION):
            word = random.choice(COLOR_WORDS)
            trials.append({"word": word, "color": word})
        for _ in range(TRIALS_PER_CONDITION):
            word = random.choice(COLOR_WORDS)
            color = random.choice([c for c in COLOR_WORDS if c != word])
            trials.append({"word": word, "color": color})
        random.shuffle(trials)
        blocks.append(trials)
    return blocks


class PersistentVoiceKey:
    def __init__(self, model_path, sample_rate=SAMPLE_RATE, grammar=None):
        self.model = Model(model_path)
        self.sample_rate = sample_rate
        self.grammar = json.dumps(grammar) if grammar else None
        self._audio_q = queue.Queue()
        self._stream = None
        self.block_size = None

    def start(self):
        self.block_size = BLOCK_SIZE
        self.sample_rate = SAMPLE_RATE
        self._stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            dtype="int16",
            channels=1,
            latency="low",
            device=DEVICE,
            callback=self._callback,
        )
        self._stream.start()
        print(f"[VoiceKey] mic stream open, sample_rate={self.sample_rate}")

    def stop(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def _callback(self, indata, frames, time_info, status):
        self._audio_q.put((bytes(indata), core.getTime()))

    def _make_recognizer(self):
        rec = (KaldiRecognizer(self.model, self.sample_rate, self.grammar)
               if self.grammar else KaldiRecognizer(self.model, self.sample_rate))
        rec.SetWords(True)
        return rec

    def listen_for_response(self, stim_onset_time, timeout=SILENCE_TIMEOUT):
        recognizer = self._make_recognizer()

        recognized_text = ""
        result_words = []
        chunks = []
        timed_out = False
        got_final = False
        first_block_start_time = None

        deadline = stim_onset_time + timeout

        while True:
            if core.getTime() > deadline:
                timed_out = True
                break

            try:
                data, block_time = self._audio_q.get(timeout=0.05)
            except queue.Empty:
                continue

            if block_time < stim_onset_time - PRE_TRIAL_DISCARD_MARGIN:
                continue

            chunks.append(data)
            if first_block_start_time is None:
                n_samples = len(data) // 2  # int16 = 2 bytes/sample
                first_block_start_time = block_time - n_samples / self.sample_rate

            if recognizer.AcceptWaveform(data):
                result_json = json.loads(recognizer.Result())
                recognized_text = result_json.get("text", "").strip()
                result_words = result_json.get("result", [])
                got_final = True
                break

        if not got_final:
            result_json = json.loads(recognizer.FinalResult())
            recognized_text = result_json.get("text", "").strip()
            result_words = result_json.get("result", [])

        # Use Vosk's own word-level timestamps to find where the recognized
        # color word starts, taking the LAST match (the participant's real
        # answer) in case a filler like "emmm" got misheard as an earlier
        # color word. If no color word was recognized, the trial is invalid
        # (no_response) — the wav is still saved for inspection.
        onset_time = None
        recognized_color_word = None
        for w in result_words:
            if w.get("word", "").lower() in COLOR_WORDS:
                onset_time = first_block_start_time + w["start"]
                recognized_color_word = w.get("word", "").lower()

        rt_ms = (onset_time - stim_onset_time) * 1000.0 if onset_time is not None else None
        audio_np = np.frombuffer(b"".join(chunks), dtype=np.int16)

        return {
            "rt_ms": rt_ms,
            "recognized_text": recognized_text,
            "recognized_color_word": recognized_color_word,
            "audio": audio_np,
            "timed_out": timed_out,
            "no_response": recognized_color_word is None,
        }


def save_wav(path, audio_np, sample_rate):
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_np.tobytes())


# ------------------------------------------------------------------
# Visual helpers
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
# Main experiment
# ------------------------------------------------------------------

def run_experiment():
    info = {"Subject ID": "", "Session": "001"}
    dlg = gui.DlgFromDict(info, title="Voice-Key Stroop")
    if not dlg.OK:
        core.quit()

    subj_id = info["Subject ID"] or "test"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_path = os.path.join(DATA_DIR, f"{subj_id}_{timestamp}.csv")
    subj_audio_dir = os.path.join(AUDIO_DIR, f"{subj_id}_{timestamp}")
    os.makedirs(subj_audio_dir, exist_ok=True)

    voice_key = PersistentVoiceKey(VOSK_MODEL_PATH, grammar=COLOR_WORDS)
    win = None

    try:
        voice_key.start()

        correct_tone = sound.Sound(value=880, secs=0.15)
        wrong_tone = sound.Sound(value=220, secs=0.15)
        no_response_tone = sound.Sound(value=140, secs=0.15)

        win = make_window()
        stim_text = visual.TextStim(win, text="", height=0.2, font="Arial", bold=True)
        fixation = visual.TextStim(win, text="+", color=ACCENT_COLOR, height=0.08)

        show_message(
            win,
            "In each trial, say the INK COLOR of the word out loud as fast as you can "
            "(ignore what the word says).\n\n"
            "You will hear a tone after each response.\n\n"
            "Press SPACE to begin."
        )

        blocks = build_blocks()

        fieldnames = [
            "block", "trial", "word", "color", "congruent",
            "rt_ms", "recognized_text", "recognized_color_word", "correct",
            "timed_out", "no_response", "audio_file",
        ]
        with open(data_path, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=fieldnames).writeheader()

        for b, block_trials in enumerate(blocks, start=1):
            show_message(win, f"Block {b} of {N_BLOCKS}\n\nPress SPACE to start.")

            for i, trial in enumerate(block_trials, start=1):
                check_quit()
                word, color = trial["word"], trial["color"]
                congruent = (word == color)

                fixation.draw()
                win.flip()
                core.wait(0.5)

                stim_text.setText(word.upper())
                stim_text.setColor(COLOR_RGB[color])
                stim_text.draw()
                win.flip()
                stim_onset_time = core.getTime()

                result = voice_key.listen_for_response(stim_onset_time)

                recognized_text = result["recognized_text"].lower().strip()
                recognized = result["recognized_color_word"] or ""
                is_correct = (recognized == color)

                win.flip()
                if result["no_response"]:
                    no_response_tone.play()
                elif is_correct:
                    correct_tone.play()
                else:
                    wrong_tone.play()
                core.wait(0.35)

                audio_path = os.path.join(subj_audio_dir, f"block{b}_trial{i:03d}.wav")
                if result["audio"].size > 0:
                    save_wav(audio_path, result["audio"], sample_rate=voice_key.sample_rate)
                else:
                    audio_path = ""

                with open(data_path, "a", newline="", encoding="utf-8") as f:
                    csv.DictWriter(f, fieldnames=fieldnames).writerow({
                        "block": b,
                        "trial": i,
                        "word": word,
                        "color": color,
                        "congruent": congruent,
                        "rt_ms": round(result["rt_ms"], 1) if result["rt_ms"] else "",
                        "recognized_text": recognized_text,
                        "recognized_color_word": recognized,
                        "correct": is_correct,
                        "timed_out": result["timed_out"],
                        "no_response": result["no_response"],
                        "audio_file": audio_path,
                    })

                check_quit()
        show_message(win, "Experiment complete. Thank you!", wait_for_space=False)
        core.wait(2.0)
    finally:
        voice_key.stop()
        if win is not None:
            win.close()
    core.quit()

if __name__ == "__main__":
    run_experiment()