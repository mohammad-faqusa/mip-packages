# edge_detector.py
import machine, micropython
import time

class EdgeDetector:
    """
    Detect rising/falling edges on a GPIO pin and notify a watcher:
    Calls: watch_state(peripheral_name, { field_name: True/False })
    """

    def __init__(self, pin_num, *, pull=None, watch_state=None,
                 peripheral_name="device", field_name="state",
                 debounce_ms=0):
        self.pin = machine.Pin(pin_num, machine.Pin.IN, pull)
        self._watch_state = watch_state
        self._saved_watch_state = watch_state
        self._peripheral_name = peripheral_name
        self._field_name = field_name
        self._debounce_ms = debounce_ms
        self._last_evt_ms = 0
        self._last_level = None
        self._busy = 0

        micropython.alloc_emergency_exception_buf(100)

        self.pin.irq(
            trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING,
            handler=self._irq_handler,
        )

    def watch_state(self, fn):
        """Assign a function to receive state updates on edge events."""
        if not callable(fn):
            raise TypeError("watch_state must be callable")
        self._watch_state = fn
        self._saved_watch_state = fn

    def init_watch(self):
        """Reactivates the previously deactivated watch_state handler."""
        self._watch_state = self._saved_watch_state

    def deinit_watch(self):
        """Temporarily disables edge notifications (watch_state)."""
        self._saved_watch_state = self._watch_state
        self._watch_state = None

    # ───────── internal ─────────
    def _irq_handler(self, pin):
        level = pin.value()
        if self._busy == 0:
            self._busy = 1 if level else -1
            try:
                micropython.schedule(self._dispatch, level)
            except RuntimeError:
                # Schedule queue is full – drop this event
                self._busy = 0


    def _dispatch(self, level):
        self._busy = 0  # Ensure busy is cleared even on debounce
        now = time.ticks_ms()

        # Debounce
        if self._debounce_ms:
            if time.ticks_diff(now, self._last_evt_ms) < self._debounce_ms:
                return
            self._last_evt_ms = now

        # Skip same level if no debounce (for gas/PIR)
        if not self._debounce_ms and level == self._last_level:
            return

        self._last_level = level

        if self._watch_state:
            try:
                self._watch_state(self._peripheral_name, {
                    self._field_name: bool(level)
                })
            except Exception as exc:
                print(f"{self._peripheral_name} watch_state error:", exc)


