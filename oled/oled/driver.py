# oled_wrapper.py
from .ssd1306 import SSD1306_I2C as _Base          # official driver
from machine   import I2C, Pin


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


class OLED(_Base):
    """SSD1306 128×64 OLED with simple text helpers.

    Example
    -------
    >>> from oled_wrapper import OLED
    >>> oled = OLED()                 # no parameters needed
    >>> oled.write("Hello OLED!")     # clear + write on first row
    >>> oled.write_line("Row 3", 3)   # write on row 3
    """

    # ── constructor with built-in I²C init ────────────────────────────
    def __init__(self):
        # Default ESP32 I²C pins (change here if your wiring differs)
        i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        super().__init__(128, 64, i2c, addr=0x3C, external_vcc=False)
    
    def __getitem__(self, key):
        method = getattr(self, key)
        return MethodWrapper(method)

    # ── small framebuffer proxies ─────────────────────────────────────
    def fill_rect(self, x, y, w, h, col):
        self.framebuf.fill_rect(x, y, w, h, col)

    def clear(self):
        """Clear the entire display and refresh."""
        self.fill(0)
        self.show()

    # ── convenience helpers ───────────────────────────────────────────
    def write_line(self, text, row, *, clear_line=True, col=1):
        """
        Render `text` on ROW (0–7).  
        Set `clear_line=False` to overwrite without erasing that row.
        """
        if not 0 <= row < 8:                       # 64 px / 8 px per row
            raise ValueError("row must be 0–7")
        y = row * 8
        if clear_line:
            self.fill_rect(0, y, self.width, 8, 0)
        self.text(text, 0, y, col)
        self.show()

    def write(self, text, row=0, *, col=1):
        """Clear full screen, then write `text` on `row` (default = 0)."""
        self.clear()
        self.write_line(text, row, clear_line=False, col=col)

