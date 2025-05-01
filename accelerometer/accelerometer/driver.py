import random

class MethodWrapper:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, args):
        if isinstance(args, (list, tuple)):
            return self.func(*args)  # Unpack!
        else:
            return self.func(args)



class MPU6050:
    def __init__(self, i2c=None, addr=0x68, simulate=True):
        self.simulate = simulate
        self.addr = addr
        self._accel = (0.0, 0.0, 0.0)
        self._gyro = (0.0, 0.0, 0.0)

        if not self.simulate:
            try:
                import mpu6050
                self._sensor = mpu6050.MPU6050(i2c, address=self.addr)
                self._sensor.wake()  # Make sure it's active
                print(f"[INIT] MPU6050 at 0x{addr:X} (real)")
            except Exception as e:
                print("[ERROR] Failed to init real MPU6050:", e)
                self.simulate = True
                
        def __getitem__(self, key):
                method = getattr(self, key)
                return MethodWrapper(method)
        
        if self.simulate:
            print(f"[INIT] Simulated MPU6050 (addr=0x{addr:X})")

    def read_accel(self):
        if self.simulate:
            self._accel = tuple(round(random.uniform(-2.0, 2.0), 2) for _ in range(3))
        else:
            self._accel = self._sensor.get_accel()
        print(f"[ACCEL] {self._accel}")
        return self._accel

    def read_gyro(self):
        if self.simulate:
            self._gyro = tuple(round(random.uniform(-250.0, 250.0), 1) for _ in range(3))
        else:
            self._gyro = self._sensor.get_gyro()
        print(f"[GYRO] {self._gyro}")
        return self._gyro

    def read_all(self):
        return {
            "accel": self.read_accel(),
            "gyro": self.read_gyro()
        }
