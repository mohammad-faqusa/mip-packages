class MethodWrapper:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, args):
        if isinstance(args, (list, tuple)):
            return self.func(*args)  # Unpack!
        else:
            return self.func(args)

class Relay:
    def __init__(self, pin, active_high=True, simulate=False):
        self.pin = pin
        self.active_high = active_high
        self.simulate = simulate
        self._state = False  # Relay is initially off
        self._on_change = None  # NEW: callback for state changes

        if not self.simulate:
            from machine import Pin
            self._relay = Pin(pin, Pin.OUT)

        print(f"[INIT] Relay on pin {pin} (active_high={active_high}, simulate={simulate})")

    def __getitem__(self, key):
        method = getattr(self, key)
        return MethodWrapper(method)
    
    def on(self):
        self._trigger_if_changed(True)

    def off(self):
        self._trigger_if_changed(False)

    def switch(self, status):
        self._trigger_if_changed(bool(status))

    def toggle(self):
        self._trigger_if_changed(not self._state)

    def is_on(self):
        return self._state

    def watch_state(self, callback):
        """Set a callback to trigger when Relay state changes."""
        self._on_change = callback

    def _trigger_if_changed(self, new_state):
        if new_state != self._state:
            self._state = new_state
            if not self.simulate:
                self._relay(1 if self._state == self.active_high else 0)
            if self._on_change:
                self._on_change("relay", ("state", self._state))
            print(f"[Relay] {'ON' if self._state else 'OFF'} (triggered)")
