import time

from edge_detector import EdgeDetector
import machine

class GasSensor(EdgeDetector):
    """
    Basic push-button (normally open, pulled HIGH).
    Adds debounce and inverts logic so True = pressed.
    """
    PRESSED   = True
    RELEASED  = False

    def __init__(self, pin_num, *,
                 pull=machine.Pin.PULL_UP,
                 debounce_ms=20,
                 callback=None):
        self._debounce_ms = debounce_ms
        self._last_evt_ms = 0
        super().__init__(pin_num, pull=pull)          # rising + falling IRQ
        if callback:
            self.set_callback(callback)

    # Debounce by overriding the edge dispatcher
    def _dispatch(self, level):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_evt_ms) >= self._debounce_ms:
            self._last_evt_ms = now
            super()._dispatch(level)                  # let parent handle mapping
        else:
            # Too soon – drop the bounce and unlock the guard
            self._busy = 0

    # Invert logic: LOW (falling) = pressed, HIGH (rising) = released
    def on_rising(self, fn):
        if self._callback:
            self._callback(fn)

    def on_falling(self, fn):
        if self._callback:
            self._callback(fn)