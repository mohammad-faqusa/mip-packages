# sensors.py
import machine
from .edge_detector import EdgeDetector

class PIRSensor(EdgeDetector):
    """
    Passive-infrared motion sensor.
    Calls watch_state("pir", {"motion": True}) on motion detected,
    and {"motion": False} when motion ends.
    """
    MOTION = True
    IDLE = False

    def __init__(self, pin_num, *, watch_state=None):
        # PIR modules typically output active-high and don't need internal pull resistors
        super().__init__(pin_num, pull=None, watch_state=watch_state)

    def _dispatch(self, level):
        if self._watch_state:
            try:
                self._watch_state("pir", {"motion": bool(level)})
            except Exception as exc:
                print("PIRSensor watch_state error:", exc)
