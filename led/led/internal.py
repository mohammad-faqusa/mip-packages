from .driver import LED

class InternalLED(LED):
    def __init__(self, simulate=False):
        # On ESP32, internal LED is usually on GPIO2 and active high
        super().__init__(pin=2, active_high=True, simulate=simulate)
        print("[INIT] InternalLED initialized on pin 2")
