import sys
import machine

if hasattr(machine, "dht_readinto"):
    from machine import dht_readinto
elif sys.platform.startswith("esp"):
    from esp import dht_readinto
elif sys.platform == "pyboard":
    from pyb import dht_readinto
else:
    dht_readinto = __import__(sys.platform).dht_readinto

del machine

class MethodWrapper:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, args):
        if isinstance(args, (list, tuple)):
            return self.func(*args)  # Unpack!
        else:
            return self.func(args)


class DHTBase:
    def __init__(self, pin):
        self.pin = pin
        self.buf = bytearray(5)
    
    def __getitem__(self, key):
        method = getattr(self, key)
        return MethodWrapper(method)

    def measure(self):
        buf = self.buf
        dht_readinto(self.pin, buf)
        if (buf[0] + buf[1] + buf[2] + buf[3]) & 0xFF != buf[4]:
            raise Exception("checksum error")

import uasyncio as asyncio

class DHTSensor(DHTBase):
    def __init__(self, pin):
        super().__init__(pin)
        self._last_values = {"temperature": None, "humidity": None}
        self._on_state_change = None
        self._watching = False
        self._watch_task = None

    def humidity(self):
        return (self.buf[0] << 8 | self.buf[1]) * 0.1

    def temperature(self):
        t = ((self.buf[2] & 0x7F) << 8 | self.buf[3]) * 0.1
        if self.buf[2] & 0x80:
            t = -t
        return t

    def _trigger_on_change(self, key, value):
        if self._last_values.get(key) != value:
            self._last_values[key] = value
            if self._on_state_change:
                self._on_state_change("dht_sensor", {key: value})

    def watch_state(self, callback, interval=5):
        """Set the callback and start the watch loop."""
        self._on_state_change = callback
        self.init_watch(interval)

    def init_watch(self, interval=5):
        """Start the background async loop."""
        if not self._watching:
            self._watching = True
            self._watch_task = asyncio.create_task(self._watch_loop(interval))

    def deinit_watch(self):
        """Stop the background async loop."""
        self._watching = False
        self._watch_task = None

    async def _watch_loop(self, interval):
        while self._watching:
            try:
                self.measure()
                self._trigger_on_change("temperature", self.temperature())
                self._trigger_on_change("humidity", self.humidity())
            except Exception as e:
                print("DHT read error:", e)
            await asyncio.sleep(interval)

__version__ = '0.1.0'


