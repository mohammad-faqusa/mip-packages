class MethodWrapper:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __getitem__(self, args):
        if isinstance(args, (list, tuple)):
            return self.func(*args)
        else:
            return self.func(args)


from machine import Pin
import micropython

class Encoder:
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
                 watch_state=None,
                 ):

        self._min = min_pos
        self._max = max_pos
        self._pos = min_pos
        self._watch_state = watch_state
        self._saved_watch_state = watch_state
       

        self._pa = pin_a if isinstance(pin_a, Pin) else Pin(pin_a, Pin.IN, pull)
        self._pb = pin_b if isinstance(pin_b, Pin) else Pin(pin_b, Pin.IN, pull)

        self._state = (self._pa.value() << 1) | self._pb.value()

        micropython.alloc_emergency_exception_buf(100)
        trig = Pin.IRQ_RISING | Pin.IRQ_FALLING
        self._pa.irq(trigger=trig, handler=self._irq)
        self._pb.irq(trigger=trig, handler=self._irq)

    def __getitem__(self, key):
        method = getattr(self, key)
        return MethodWrapper(method)

    def get_position(self) -> int:
        return self._pos

    def watch_state(self, func):
        self._watch_state = func

    def _irq(self, pin):
        ab = (self._pa.value() << 1) | self._pb.value()
        idx = (self._state << 2) | ab
        self._state = ab

        delta = self._DELTA[idx]
        if not delta:
            return

        new_pos = self._pos + delta
        new_pos = max(self._min, min(self._max, new_pos))

        if new_pos != self._pos:
            self._pos = new_pos
            update = ("angle", self._pos)
            try:
                if self._watch_state:
                    self._watch_state("encoder", update)
              
            except Exception as exc:
                print("Encoder state change error:", exc)

    def init_watch(self):
        """Reactivate watch/triggers after deinit_watch."""
        self._watch_state = self._saved_watch_state

    def deinit_watch(self):
        """Disable watch/triggers without removing the encoder logic."""
        self._saved_watch_state = self._watch_state
        self._watch_state = None
