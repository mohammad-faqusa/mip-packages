class MethodWrapper:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, args):
        if isinstance(args, (list, tuple)):
            return self.func(*args)  # Unpack!
        else:
            return self.func(args)



class LED:
    def __init__(self, pin, active_high=True, simulate=False):
        self.pin = pin
        self.active_high = active_high
        self.simulate = simulate
        self._state = False  # LED is initially off

        if not self.simulate:
            from machine import Pin
            self._led = Pin(pin, Pin.OUT)

        print(f"[INIT] LED on pin {pin} (active_high={active_high}, simulate={simulate})")

    def __getitem__(self, key):
        method = getattr(self, key)
        return MethodWrapper(method)
    
    def on(self):
        self._state = True
        if not self.simulate:
            self._led.value(1 if self.active_high else 0)
        print("[LED] ON")
        
    def switch(self, status):
            self._state = status
            if not self.simulate:
                self._led.value(1 if self._state else 0)
            print("[LED] ON")

    def off(self):
        self._state = False
        if not self.simulate:
            self._led.value(0 if self.active_high else 1)
        print("[LED] OFF")

    def toggle(self):
        if self._state:
            self.off()
        else:
            self.on()

    def is_on(self):
        return self._state
