import random

class GasSensor:
    def __init__(self, pin, analog=True, simulate=True):
        self.pin = pin
        self.analog = analog
        self.simulate = simulate
        self._gas_level = 0

        if not self.simulate and not analog:
            from machine import Pin
            self._sensor = Pin(pin, Pin.IN)
        elif not self.simulate and analog:
            from machine import ADC, Pin
            self._sensor = ADC(Pin(pin))

        print(f"[INIT] GasSensor on pin {pin} (analog={analog}, simulate={simulate})")

    def read(self):
        if self.simulate:
            self._gas_level = random.randint(0, 1023) if self.analog else random.choice([0, 1])
            print(f"[SIMULATED READ] Gas Level: {self._gas_level}")
        else:
            self._gas_level = self._sensor.read() if self.analog else self._sensor.value()
            print(f"[READ] Gas Level: {self._gas_level}")

        return self._gas_level
