import machine
import time

class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin):
        self.trig = machine.Pin(trig_pin, machine.Pin.OUT)
        self.echo = machine.Pin(echo_pin, machine.Pin.IN)
        self.trig.off()

    def get_distance(self):
        self.trig.off()
        time.sleep_us(2)
        self.trig.on()
        time.sleep_us(10)
        self.trig.off()

        while self.echo.value() == 0:
            pulse_start = time.ticks_us()

        while self.echo.value() == 1:
            pulse_end = time.ticks_us()

        duration = time.ticks_diff(pulse_end, pulse_start)
        distance = (duration / 2) * 0.0343  # in cm
        return distance
