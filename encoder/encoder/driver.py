class Encoder:
    def __init__(self, pin_a, pin_b, simulate=True):
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.simulate = simulate
        self._position = 0

        if not self.simulate:
            from machine import Pin
            self._a = Pin(pin_a, Pin.IN)
            self._b = Pin(pin_b, Pin.IN)
            self._a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._update_position)
            print(f"[INIT] Encoder initialized on pins {pin_a}, {pin_b}")
        else:
            print(f"[INIT] Simulated Encoder (manual position control)")

    def _update_position(self, pin):
        a_val = self._a.value()
        b_val = self._b.value()
        if a_val == b_val:
            self._position += 1
        else:
            self._position -= 1
        print(f"[ENCODER] Position updated: {self._position}")

    def get_position(self):
        return self._position

    def reset(self):
        self._position = 0
        print(f"[ENCODER] Position reset.")

    # Only for simulate=True
    def simulate_step(self, steps):
        if self.simulate:
            self._position += steps
            print(f"[SIMULATE] Encoder position changed by {steps} → {self._position}")
