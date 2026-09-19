import os
import json
import queue
import wave
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from psychopy import core

from stroop_common import (
    COLOR_WORDS, COLOR_RGB, CSV_FIELDNAMES,
    check_quit, show_block_intro, show_practice_prompt,
    show_practice_fail, show_practice_complete,
    build_trial_list, build_practice_list, make_tones, make_stims,
    write_csv_row, MAX_PRACTICE_ATTEMPTS,
)

VOSK_MODEL_PATH = "model/vosk-model-small-en-us-0.15"
SILENCE_TIMEOUT = 2.0
PRE_TRIAL_DISCARD_MARGIN = 0.0
AUDIO_DIR = os.path.join("data", "voice_audio")

INSTRUCTIONS_TEXT = (
    "In each trial, say the INK COLOR of the word out loud as fast as you can "
    "(ignore what the word says).\n\n"
    "You will hear a tone after each response."
)

PRACTICE_REMINDER_TEXT = (
    "Remember: say the INK COLOR of the word out loud, not the word itself."
)


def _get_device():
    device = -1
    for hostapi in sd.query_hostapis():
        if "wasapi" in hostapi["name"].lower():
            device = hostapi.get("default_input_device", -1)
    return device


class PersistentVoiceKey:
    """Mic stream + recognizer. start()/stop() can be called repeatedly
    across the experiment (once per voice block) — the model is loaded
    once in __init__, only the audio stream is opened/closed per call."""

    def __init__(self, model_path, sample_rate, device, block_size, grammar=None):
        self.model = Model(model_path)
        self.sample_rate = sample_rate
        self.device = device
        self.block_size = block_size
        self.grammar = json.dumps(grammar) if grammar else None
        self._audio_q = queue.Queue()
        self._stream = None

    def start(self):
        # fresh queue on every (re)start so nothing stale from a previous
        # block (or from time spent idle during a keyboard block) leaks in
        self._audio_q = queue.Queue()
        self._stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            dtype="int16",
            channels=1,
            latency="low",
            device=self.device,
            callback=self._callback,
        )
        self._stream.start()
        print(f"[VoiceKey] mic stream open, sample_rate={self.sample_rate}")

    def stop(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            print("[VoiceKey] mic stream closed")

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


class VoiceModality:
    label = "Voice"
    key = "voice"

    def __init__(self, win, pid):
        self.win = win
        self.pid = pid

        device = _get_device()
        sample_rate = int(round(sd.query_devices(device)["default_samplerate"]))
        block_size = int(sample_rate / 1000)  # 1ms per block

        self.voice_key = PersistentVoiceKey(
            VOSK_MODEL_PATH, sample_rate, device, block_size, grammar=COLOR_WORDS
        )
        self.correct_tone, self.wrong_tone, self.no_response_tone = make_tones()
        self.stim_text, self.fixation = make_stims(win)

        self.subj_audio_dir = os.path.join(AUDIO_DIR, f"{pid}")
        os.makedirs(self.subj_audio_dir, exist_ok=True)

    # --- mic lifecycle, called by main.py around each voice block ---
    def enter_block(self):
        self.voice_key.start()

    def exit_block(self):
        self.voice_key.stop()

    # --- screens ---
    def show_block_intro(self, block_idx, total_blocks):
        show_block_intro(self.win, INSTRUCTIONS_TEXT, block_idx, total_blocks)

    # --- trial execution ---
    def _run_trial(self, trial, block_num, trial_num, record):
        word, color = trial["word"], trial["color"]
        congruent = (word == color)

        self.fixation.draw()
        self.win.flip()
        core.wait(0.5)

        self.stim_text.setText(word.upper())
        self.stim_text.setColor(COLOR_RGB[color])
        self.stim_text.draw()
        self.win.flip()
        stim_onset_time = core.getTime()

        result = self.voice_key.listen_for_response(stim_onset_time)

        recognized_text = result["recognized_text"].lower().strip()
        recognized = result["recognized_color_word"] or ""
        is_correct = (recognized == color)

        self.win.flip()
        if result["no_response"]:
            self.no_response_tone.play()
        elif is_correct:
            self.correct_tone.play()
        else:
            self.wrong_tone.play()
        core.wait(0.35)

        check_quit()

        if not record:
            return is_correct

        # audio_file is named by the total block number (across both
        # modalities), matching how block_num is written to the CSV.
        audio_path = os.path.join(
            self.subj_audio_dir, f"block{block_num}_trial{trial_num:03d}.wav"
        )
        if result["audio"].size > 0:
            save_wav(audio_path, result["audio"], sample_rate=self.voice_key.sample_rate)
        else:
            audio_path = ""

        row = {fn: "" for fn in CSV_FIELDNAMES}
        row.update({
            "modality": "voice",
            "block": block_num,
            "trial": trial_num,
            "word": word,
            "color": color,
            "congruent": congruent,
            "rt_ms": round(result["rt_ms"], 1) if result["rt_ms"] else "",
            "correct": is_correct,
            "timed_out": result["timed_out"],
            "no_response": result["no_response"],
            "recognized_text": recognized_text,
            "recognized_color_word": recognized,
            "audio_file": audio_path,
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
