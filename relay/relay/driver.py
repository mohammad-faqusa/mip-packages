class Relay:
    def __init__(self, pin, active_high=True, simulate=True):
        self.pin = pin
        self.active_high = active_high
        self.simulate = simulate
        self._state = False  # OFF by default

        if not self.simulate:
            from machine import Pin
            self._relay = Pin(pin, Pin.OUT)

        print(f"[INIT] Relay on pin {pin} (active_high={active_high}, simulate={simulate})")

    def on(self):
        self._state = True
        if not self.simulate:
            self._relay.value(1 if self.active_high else 0)
        print("[RELAY] ON")

    def off(self):
        self._state = False
        if not self.simulate:
            self._relay.value(0 if self.active_high else 1)
        print("[RELAY] OFF")

    def toggle(self):
        if self._state:
            self.off()
        else:
            self.on()

    def is_on(self):
        return self._state
