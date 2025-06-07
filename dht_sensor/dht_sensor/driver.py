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

class DHTSensor(DHTBase):
    def humidity(self):
        self.measure()
        return (self.buf[0] << 8 | self.buf[1]) * 0.1

    def temperature(self):
        self.measure()
        t = ((self.buf[2] & 0x7F) << 8 | self.buf[3]) * 0.1
        if self.buf[2] & 0x80:
            t = -t
        return t


__version__ = '0.1.0'


