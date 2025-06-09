# edge_detector.py
import machine, micropython

class EdgeDetector:
    """
    Detect rising/falling edges on a GPIO pin and invoke a user callback:
        cb(True)   on rising edge
        cb(False)  on falling edge
    """

    def __init__(self, pin_num, *, pull=None):
        self.pin = machine.Pin(pin_num, machine.Pin.IN, pull)
        self._callback = None            # user-supplied fn(bool)
        self._busy = 0                   # re-entrancy guard
        micropython.alloc_emergency_exception_buf(100)

        # Fire on both edges
        self.pin.irq(
            trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING,
            handler=self._irq_handler,    # runs in hard-IRQ context
        )

    def set_callback(self, fn):
        if not callable(fn):
            raise TypeError("callback must be callable")
        self._callback = fn

    def deinit(self):
        self.pin.irq(handler=None)
        self._callback = None

    # ───────── internal plumbing ─────────
    def _irq_handler(self, pin):
        level = pin.value()               # 1=rising, 0=falling
        if self._busy == 0:               # drop duplicates while queued
            self._busy = 1 if level else -1
            micropython.schedule(self._dispatch, level)

    def _dispatch(self, level):
        self._busy = 0
        if self._callback:
            self._callback(bool(level))
