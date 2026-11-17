from psychopy import core
from psychopy.hardware import keyboard

from neutral_common import KEYS, RESPONSE_WINDOW, KEYBOARD_EXTRA_DELAY


class ManualModality:
    name = "manual"
    extra_delay = KEYBOARD_EXTRA_DELAY        # trial ends this long after the key press

    def __init__(self, key_map):
        self.key_to_color = {k: c for c, k in key_map.items()}
        self.kb = keyboard.Keyboard()

    # nothing to open/close, but keep the same interface as the voice modality
    def enter_block(self):
        pass

    def exit_block(self):
        pass

    def begin(self, win):
        self.kb.clearEvents()
        win.callOnFlip(self.kb.clock.reset)   # rt = 0 at the next flip (stimulus onset)

    def check(self, t0):
        for k in self.kb.getKeys(keyList=KEYS + ["escape"], waitRelease=False):
            if k.name == "escape":
                core.quit()
            if 0 <= k.rt <= RESPONSE_WINDOW:  # ignore presses during the fixation
                return dict(response=k.name, color=self.key_to_color[k.name], rt=k.rt * 1000)
        return None

    def after(self, tag):
        return {}
