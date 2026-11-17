import json
import os
import queue
import wave

import sounddevice as sd
from vosk import Model, KaldiRecognizer
from psychopy import core

from neutral_common import COLORS, RESPONSE_WINDOW

VOSK_MODEL_PATH = "model/vosk-model-small-en-us-0.15"
STABLE_MS = 60          # a colour word must stay in Vosk's partial result this long
SAVE_AUDIO = True       # one WAV per trial, starting at stimulus onset


class VoiceModality:
    """The trial ends as soon as Vosk has recognised the first colour word
    (no waiting for Vosk's end-of-speech detection)."""
    name = "voice"
    extra_delay = 0.0

    def __init__(self, pid):
        self.device = -1
        for api in sd.query_hostapis():
            if "wasapi" in api["name"].lower():
                self.device = api.get("default_input_device", -1)
        self.sr = int(round(sd.query_devices(self.device)["default_samplerate"]))
        self.model = Model(VOSK_MODEL_PATH)
        self.grammar = json.dumps(COLORS + ["[unk]"])
        self.pid = pid
        self.audio_dir = os.path.join("data", f"{pid}_audio")
        if SAVE_AUDIO:
            os.makedirs(self.audio_dir, exist_ok=True)

    def enter_block(self):                    # mic is open only during voice blocks
        self.q = queue.Queue()
        self.stream = sd.RawInputStream(
            samplerate=self.sr, blocksize=self.sr // 1000, dtype="int16", channels=1,
            latency="low", device=self.device,
            callback=lambda data, *_: self.q.put((bytes(data), core.getTime())))
        self.stream.start()

    def exit_block(self):
        self.stream.stop()
        self.stream.close()

    def begin(self, win):
        self.rec = KaldiRecognizer(self.model, self.sr, self.grammar)
        self.rec.SetWords(True)
        self.audio, self.audio_t0, self.text = [], None, ""
        self.cand, self.cand_ms, self.last_check = None, 0.0, 0.0
        self.too_late = False
        while not self.q.empty():             # drop audio recorded before this trial
            self.q.get_nowait()

    def check(self, t0):
        while not self.too_late:
            try:
                data, t = self.q.get_nowait()     # t = time at the end of this 1 ms block
            except queue.Empty:
                return None
            if t <= t0:                           # recorded before the stimulus
                continue
            if self.audio_t0 is None:
                self.audio_t0 = t - len(data) / 2 / self.sr
            self.audio.append(data)
            ms = len(self.audio) * len(data) / 2 / self.sr * 1000

            if self.rec.AcceptWaveform(data):     # Vosk closed an utterance by itself
                resp = self._first_color(self.rec.Result(), t0)
                if resp:
                    return resp
            elif ms - self.last_check >= 10:      # every 10 ms: read the partial result
                self.last_check = ms
                partial = json.loads(self.rec.PartialResult())["partial"].split()
                cand = next((w for w in partial if w in COLORS), None)
                if cand != self.cand:
                    self.cand, self.cand_ms = cand, ms
                elif cand and ms - self.cand_ms >= STABLE_MS:
                    resp = self._first_color(self.rec.FinalResult(), t0)   # word + onset time
                    if resp:
                        return resp
                    self.cand = None
        return None

    def _first_color(self, result, t0):
        result = json.loads(result)
        self.text = (self.text + " " + result.get("text", "")).strip()
        for w in result.get("result", []):
            if w["word"] in COLORS:
                rt = (self.audio_t0 + w["start"] - t0) * 1000
                if rt > RESPONSE_WINDOW * 1000:   # started too late: counts as no response
                    self.too_late = True
                    return None
                return dict(response=w["word"], color=w["word"], rt=rt)
        return None

    def after(self, tag):
        audio_file = ""
        if SAVE_AUDIO and self.audio:
            audio_file = f"{self.pid}_{tag}.wav"
            with wave.open(os.path.join(self.audio_dir, audio_file), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sr)
                wf.writeframes(b"".join(self.audio))
        return dict(recognized_text=self.text, audio_file=audio_file)
