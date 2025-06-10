class MethodWrapper:
    def __init__(self, func):
        self.func = func
        
     # NEW: make the wrapper itself callable
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __getitem__(self, args):
        if isinstance(args, (list, tuple)):
            return self.func(*args)  # Unpack!
        else:
            return self.func(args)



# encoder.py – rotary encoder helper for ESP32 / MicroPython
from machine import Pin
import micropython

class Encoder:
    """
    Increment/Decrement a bounded integer with a mechanical quadrature encoder.

    Args:
        pin_a      (int|Pin): GPIO number or pre-built Pin for channel A
        pin_b      (int|Pin): GPIO number or pre-built Pin for channel B
        min_pos          (int): lower bound (default 0)
        max_pos          (int): upper bound (default 180)
        pull        (Pin pull): Pin.PULL_UP or Pin.PULL_DOWN (default PULL_UP)
        callback        (func): optional user function(new_pos) → None
    """
    # Gray-code Δ-lookup table (16 entries)
    _DELTA = (
         0, +1, -1,  0,
        -1,  0,  0, +1,
        +1,  0,  0, -1,
         0, -1, +1,  0
    )

    def __init__(self,
                 pin_a,
                 pin_b,
                 *,
                 min_pos=0,
                 max_pos=180,
                 pull=Pin.PULL_UP,
                 callback=None):

        self._min  = min_pos
        self._max  = max_pos
        self._pos  = min_pos          # start at lower bound
        self._cb   = callback

        # Accept GPIO ints or already-created Pin objects
        self._pa = pin_a if isinstance(pin_a, Pin) else Pin(pin_a, Pin.IN, pull)
        self._pb = pin_b if isinstance(pin_b, Pin) else Pin(pin_b, Pin.IN, pull)

        # Internal state (last AB reading)
        self._state = (self._pa.value() << 1) | self._pb.value()

        # Prepare ISR safety nets
        micropython.alloc_emergency_exception_buf(100)

        # Attach interrupts on both edges of both channels
        trig = Pin.IRQ_RISING | Pin.IRQ_FALLING
        self._pa.irq(trigger=trig, handler=self._irq)
        self._pb.irq(trigger=trig, handler=self._irq)

    def __getitem__(self, key):
        method = getattr(self, key)
        return MethodWrapper(method)
    # --------------------------------------------------------------------- #
    # Public helpers
    # --------------------------------------------------------------------- #

    def get_position(self) -> int:
        """Return the current bounded position (0–180 by default)."""
        return self._pos

    def set_callback(self, func):
        """
        Register / replace a callback executed **outside** the IRQ context
        whenever the position value actually changes.

        func(new_position:int) → None
        """
        self._cb = func

    # --------------------------------------------------------------------- #
    # Internal methods
    # --------------------------------------------------------------------- #

    def _irq(self, pin):
        """
        Interrupt handler (runs at IRQ level – keep it tiny, no heap alloc).
        Schedules the user callback via micropython.schedule to execute in
        soft-IRQ / “background” context.
        """
        ab   = (self._pa.value() << 1) | self._pb.value()
        idx  = (self._state << 2) | ab
        self._state = ab

        delta = self._DELTA[idx]
        if not delta:
            return                              # noise or invalid step

        new_pos = self._pos + delta
        if new_pos < self._min:
            new_pos = self._min
        elif new_pos > self._max:
            new_pos = self._max

        if new_pos != self._pos:
            self._pos = new_pos
            if self._cb:
                # Schedule callback safely outside the hard IRQ.
                try:
                    micropython.schedule(self._schedule_trampoline, new_pos)
                except RuntimeError:
                    # schedule() queue full – skip this update
                    pass

    def _schedule_trampoline(self, new_pos):
        """Runs in soft-IRQ context; safe to allocate and call Python code."""
        if self._cb:
            try:
                self._cb(new_pos)
            except Exception as exc:
                # Prevent user callback exceptions from crashing schedule()
                print("Encoder callback error:", exc)


