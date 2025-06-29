from .edge_detector import EdgeDetector
import machine

class PushButton(EdgeDetector):
    def __init__(self, pin_num, *, debounce_ms=20, watch_state=None):
        super().__init__(pin_num,
                         pull=machine.Pin.PULL_UP,
                         watch_state=watch_state,
                         peripheral_name="button",
                         field_name="pressed",
                         debounce_ms=debounce_ms)

