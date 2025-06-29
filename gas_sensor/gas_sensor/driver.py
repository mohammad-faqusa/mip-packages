import time

from .edge_detector import EdgeDetector
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
                 ):
        self._debounce_ms = debounce_ms
        self._last_evt_ms = 0
        super().__init__(pin_num, pull=pull)          # rising + falling IRQ
    
    def _dispatch(self, level):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_evt_ms) < self._debounce_ms:
            return  # Ignore bouncing
        self._last_evt_ms = now

        if self._watch_state:
            try:
                self._watch_state("gas", {"detected": True})
            except Exception as exc:
                print("PushButton watch_state error:", exc)