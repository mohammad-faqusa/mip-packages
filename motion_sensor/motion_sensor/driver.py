# sensors.py
import machine, time
from .edge_detector import EdgeDetector


class PIRSensor(EdgeDetector):
    """
    Passive-infrared motion sensor.
    Delivers True on the HIGH pulse (motion) and False when it returns LOW.
    """
    MOTION = True
    IDLE   = False

    def __init__(self, pin_num, *, callback=None):
        # Most PIR modules use active-high output; no pull resistor needed.
        super().__init__(pin_num, pull=None)
        if callback:
            self.set_callback(callback)

    # Keep base dispatch, just map semantics for clarity
    def on_rising(self):
        if self._callback:
            self._callback(self.MOTION)

    def on_falling(self):
        if self._callback:
            self._callback(self.IDLE)



