from machine import Pin
import time

class LEDController:
    def __init__(self, pin_num):
        self.led = Pin(pin_num, Pin.OUT)

    def on(self):
        self.led.value(1)

    def off(self):
        self.led.value(0)

    def blink(self, times=5, interval=0.5):
        for _ in range(times):
            self.on()
            time.sleep(interval)
            self.off()
            time.sleep(interval)
