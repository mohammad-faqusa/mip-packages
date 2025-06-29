# edge_detector.py
import machine, micropython

class EdgeDetector:
    """
    Detect rising/falling edges on a GPIO pin and notify a watcher:
        watch_state("button", {"pressed": True})   on rising edge
        watch_state("button", {"pressed": False})  on falling edge
    """

    def __init__(self, pin_num, *, pull=None, watch_state=None):
        self.pin = machine.Pin(pin_num, machine.Pin.IN, pull)
        self._busy = 0
        self._watch_state = watch_state
        self._saved_watch_state = watch_state  # for init/deinit toggle

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
            micropython.schedule(self._dispatch, level)

    def _dispatch(self, level):
        """Abstract method to handle debounced edge transitions."""
        raise NotImplementedError("_dispatch() must be implemented in subclasses.")