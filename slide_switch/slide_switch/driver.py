class SlideSwitch:
    def __init__(self, pin, simulate=True):
        self.pin = pin
        self.simulate = simulate
        self._state = False  # False = OFF, True = ON

        if not self.simulate:
            from machine import Pin
            self._switch = Pin(pin, Pin.IN, Pin.PULL_UP)

        print(f"[INIT] SlideSwitch on pin {pin} (simulate={simulate})")

    def set_simulated_state(self, state: bool):
        """Set simulated position (True = ON, False = OFF)"""
        if self.simulate:
            self._state = state
            print(f"[SIM SET] SlideSwitch state set to: {'ON' if state else 'OFF'}")

    def read(self):
        if self.simulate:
            return self._state
        else:
            return not self._switch.value()  # Active LOW assumed

    @property
    def state(self):
        """Return current switch state."""
        return self.read()
