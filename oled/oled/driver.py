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


# oled_wrapper.py  ──────────────────────────────────────────────────────
from .ssd1306 import SSD1306_I2C as _Base       # official MicroPython driver
from machine   import I2C, Pin
import framebuf

class OLED(_Base):
    """SSD1306 128×64 OLED wrapper with normal & tiny fonts."""

    # ───────────────── constructor (no args) ──────────────────────────
    def __init__(self):
        i2c = I2C(0, scl=Pin(22), sda=Pin(21))        # edit pins if needed
        super().__init__(128, 64, i2c, addr=0x3C, external_vcc=False)

        # temp 8×8 buffer for downsizing characters to 4×6
        self._tmp_buf = bytearray(8)                  # 8×8 / 8 = 8 bytes
        self._tmp_fb  = framebuf.FrameBuffer1(self._tmp_buf, 8, 8)

    def __getitem__(self, key):
        method = getattr(self, key)
        return MethodWrapper(method)
    
    # ───────────────── low-level proxies ──────────────────────────────
    def fill_rect(self, x, y, w, h, col):
        self.framebuf.fill_rect(x, y, w, h, col)

    def clear(self):
        """Clear entire display and refresh."""
        self.fill(0)
        self.show()
    

    # ───────────────── tiny-font renderer ─────────────────────────────
    def _draw_char_tiny(self, ch, x, y, col=1):
        """Render a single character at (x,y) in 4×6 pixels."""
        self._tmp_fb.fill(0)
        self._tmp_fb.text(ch, 0, 0, col)          # draw 8×8 glyph
        # down-sample: take every 2nd column, first 6 rows
        for yy in range(6):
            for xx in range(4):
                if self._tmp_fb.pixel(xx * 2, yy):
                    self.pixel(x + xx, y + yy, col)

    # ───────────────── high-level helpers ─────────────────────────────
    def write_line(self, text, row, *, clear_line=True, col=1, tiny=True):
        """
        Write `text` on ROW.
        tiny=False → normal 8×8 font (16 chars / row, 8-px tall rows)  
        tiny=True  → tiny 4×6 font (32 chars / row, 6-px tall rows)
        """
        char_w, char_h = (4, 6) if tiny else (8, 8)
        max_rows       = self.height // char_h
        if not 0 <= row < max_rows:
            raise ValueError(f"row must be 0–{max_rows-1}")
        y = row * char_h

        if clear_line:
            self.fill_rect(0, y, self.width, char_h, 0)

        if tiny:
            for i, ch in enumerate(text[: self.width // char_w]):
                self._draw_char_tiny(ch, i * char_w, y, col)
        else:
            self.text(text[: self.width // char_w], 0, y, col)

        self.show()

    def write(self, text, row=0, *, col=1, tiny=True):
        """Clear screen, then write `text` on `row` with chosen font size."""
        self.clear()
        self.write_line(text, row, clear_line=False, col=col, tiny=tiny)


# ───────────────── quick demo ─────────────────────────────────────────
if __name__ == "__main__":
    oled = OLED()

    oled.write("Normal font demo", row=0)          # 8×8 font (16 chars)
    oled.write_line("Tiny font: 32 chars here ->", 2, tiny=True)
    oled.write_line("0123456789ABCDEF0123456789AB", 3, tiny=True)

