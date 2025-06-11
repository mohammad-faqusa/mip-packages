
class MethodWrapper:
    def __init__(self, func):
        self.func = func
        
     # NEW: make the wrapper itself callable
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __getitem__(self, args):
        if isinstance(args, (list, tuple)):
            return self.func(*args)  # Unpack!
        else:
            return self.func(args)


from machine import Pin, PWM

class Servo:
    def __init__(self,
                 pin: int | Pin,
                 freq: int = 50,
                 min_us: int = 500,
                 max_us: int = 2500,
                 angle_range: int = 180):

        self._pwm = PWM(pin if isinstance(pin, Pin) else Pin(pin), freq=freq)

        # cached constants for quick math
        self._period_us   = 1_000_000 // freq          # 20 000 µs at 50 Hz
        self._min_us      = min_us
        self._max_us      = max_us
        self._angle_range = angle_range
        self._us_per_deg  = (max_us - min_us) / angle_range
        self._duty_max    = 1023                       # ESP32 → 10-bit PWM

        self._current_deg = angle_range // 2           # default start
        self.angle(self._current_deg)

    def __getitem__(self, key):
        method = getattr(self, key)
        return MethodWrapper(method)
    # ---------- low-level helper ---------- #
    def write_us(self, us: int) -> None:
        """Directly set the high-time in microseconds."""
        us = max(self._min_us, min(self._max_us, us))
        duty = int(us * self._duty_max / self._period_us)
        self._pwm.duty(duty)

    # ---------- high-level helpers ---------- #
    def angle(self, degrees: float | int) -> None:
        """Move servo to `degrees` (0 → angle_range)."""
        degrees = max(0, min(degrees, self._angle_range))
        us = int(self._min_us + degrees * self._us_per_deg)
        self.write_us(us)
        self._current_deg = degrees                    # remember the target

    def get_angle(self) -> float:
        """Return the last angle value passed to `angle()` (degrees)."""
        return self._current_deg

    def deinit(self) -> None:
        """Release the PWM peripheral when finished."""
        self._pwm.deinit()