import random

class DHTSensor:
    def __init__(self, pin, sensor_type="DHT22", simulate=True):
        self.pin = pin
        self.sensor_type = sensor_type
        self.simulate = simulate
        self._temp = 0.0
        self._humidity = 0.0

        if not self.simulate:
            import dht
            from machine import Pin
            sensor_class = dht.DHT22 if self.sensor_type == "DHT22" else dht.DHT11
            self._sensor = sensor_class(Pin(self.pin))

        print(f"[INIT] {sensor_type} on pin {pin} (simulate={simulate})")

    def measure(self):
        if self.simulate:
            self._temp = round(random.uniform(20.0, 30.0), 1)       # Simulated temp
            self._humidity = round(random.uniform(40.0, 60.0), 1)   # Simulated humidity
            print(f"[MEASURE] Simulated: {self._temp}°C, {self._humidity}%")
        else:
            self._sensor.measure()
            self._temp = self._sensor.temperature()
            self._humidity = self._sensor.humidity()
            print(f"[MEASURE] Real: {self._temp}°C, {self._humidity}%")

    def temperature(self):
        return self._temp

    def humidity(self):
        return self._humidity
