import random
import time

class MethodWrapper:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, args):
        if isinstance(args, (list, tuple)):
            return self.func(*args)  # Unpack!
        else:
            return self.func(args)


class MotionSensor:
    def __init__(self, pin, simulate=True):
        self.pin = pin
        self.simulate = simulate
        self._motion_detected = False

        if not self.simulate:
            from machine import Pin
            self._pir = Pin(pin, Pin.IN)

        print(f"[INIT] MotionSensor on pin {pin} (simulate={simulate})")

    def __getitem__(self, key):
        method = getattr(self, key)
        return MethodWrapper(method)
    
    def read(self):
        if self.simulate:
            self._motion_detected = random.choice([True, False])
            print(f"[SIMULATED READ] Motion Detected: {self._motion_detected}")
        else:
            self._motion_detected = bool(self._pir.value())
            print(f"[READ] Motion Detected: {self._motion_detected}")

        return self._motion_detected

    def wait_for_motion(self, timeout=10):
        print(f"[WAIT] Waiting for motion for up to {timeout}s...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.read():
                print("[EVENT] Motion detected!")
                return True
            time.sleep(0.5)
        print("[TIMEOUT] No motion detected.")
        return False
