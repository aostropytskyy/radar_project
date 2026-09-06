import spidev
import RPi.GPIO as GPIO
import time


class GC9A01:

    WIDTH = 240
    HEIGHT = 240

    # Shared pins
    DC = 25
    RST = 24

    def __init__(self, cs=8, reset_display=True):

        # Allow each display to have its own CS pin
        self.cs = cs

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.cs, GPIO.OUT)
        GPIO.setup(self.DC, GPIO.OUT)
        GPIO.setup(self.RST, GPIO.OUT)

        GPIO.output(self.cs, GPIO.HIGH)

        # SPI
        self.spi = spidev.SpiDev()

        # Use SPI bus 0, device 0
        # CS is controlled manually, so both displays can use
        # the same SPI device configuration.
        self.spi.open(0, 0)

        self.spi.no_cs = True
        self.spi.max_speed_hz = 2000000
        self.spi.mode = 0
        self.spi.lsbfirst = False
        self.spi.bits_per_word = 8

        if reset_display:
            self.reset()

        self.init_display()


    # ---------------------------------------------------------
    # Reset
    # ---------------------------------------------------------

    def reset(self):

        GPIO.output(self.RST, GPIO.HIGH)
        time.sleep(0.1)

        GPIO.output(self.RST, GPIO.LOW)
        time.sleep(0.1)

        GPIO.output(self.RST, GPIO.HIGH)
        time.sleep(0.1)

    # ---------------------------------------------------------
    # SPI command
    # ---------------------------------------------------------

    def command(self, cmd):

        GPIO.output(self.cs, GPIO.LOW)
        GPIO.output(self.DC, GPIO.LOW)

        self.spi.xfer2([cmd])

        GPIO.output(self.cs, GPIO.HIGH)

    # ---------------------------------------------------------
    # SPI data
    # ---------------------------------------------------------

    def data(self, data):

        GPIO.output(self.cs, GPIO.LOW)
        GPIO.output(self.DC, GPIO.HIGH)

        if isinstance(data, int):
            data = [data]

        self.spi.xfer2(data)

        GPIO.output(self.cs, GPIO.HIGH)

    # ---------------------------------------------------------
    # Command + data
    # ---------------------------------------------------------

    def command_data(self, cmd, data):

        GPIO.output(self.cs, GPIO.LOW)

        # Command
        GPIO.output(self.DC, GPIO.LOW)
        self.spi.xfer2([cmd])

        # Data
        GPIO.output(self.DC, GPIO.HIGH)

        if isinstance(data, int):
            data = [data]

        self.spi.xfer2(data)

        GPIO.output(self.cs, GPIO.HIGH)

    # ---------------------------------------------------------
    # Display initialisation
    # ---------------------------------------------------------

    def init_display(self):

        self.command(0xEF)

        self.command_data(0xEB, [0x14])

        self.command(0xFE)
        self.command(0xEF)

        self.command_data(0x84, [0x40])
        self.command_data(0x85, [0xFF])
        self.command_data(0x86, [0xFF])
        self.command_data(0x87, [0xFF])
        self.command_data(0x88, [0x0A])
        self.command_data(0x89, [0x21])
        self.command_data(0x8A, [0x00])
        self.command_data(0x8B, [0x80])
        self.command_data(0x8C, [0x01])
        self.command_data(0x8D, [0x01])
        self.command_data(0x8E, [0xFF])
        self.command_data(0x8F, [0xFF])

        self.command_data(0xB6, [0x00, 0x20])

        # Memory access control
        self.command_data(0x36, [0x08])

        # RGB565
        self.command_data(0x3A, [0x05])

        self.command_data(
            0x90,
            [0x08, 0x08, 0x08, 0x08]
        )

        self.command_data(
            0xBD,
            [0x06]
        )

        self.command_data(
            0xBC,
            [0x00]
        )

        self.command_data(
            0xFF,
            [0x60, 0x01, 0x04]
        )

        self.command_data(
            0xC3,
            [0x13]
        )

        self.command_data(
            0xC4,
            [0x13]
        )

        self.command_data(
            0xC9,
            [0x22]
        )

        self.command_data(
            0xBE,
            [0x11]
        )

        self.command_data(
            0xE1,
            [0x10, 0x0E]
        )

        self.command_data(
            0xDF,
            [0x21, 0x0C, 0x02]
        )

        # Power / gamma settings
        self.command_data(
            0xF0,
            [0x45, 0x09, 0x08, 0x08, 0x26, 0x2A]
        )

        self.command_data(
            0xF1,
            [0x43, 0x70, 0x72, 0x36, 0x37, 0x6F]
        )

        self.command_data(
            0xF2,
            [0x45, 0x09, 0x08, 0x08, 0x26, 0x2A]
        )

        self.command_data(
            0xF3,
            [0x43, 0x70, 0x72, 0x36, 0x37, 0x6F]
        )

        self.command_data(
            0xED,
            [0x1B, 0x0B]
        )

        self.command_data(
            0xAE,
            [0x77]
        )

        self.command_data(
            0xCD,
            [0x63]
        )

        self.command_data(
            0x70,
            [0x07, 0x07, 0x04, 0x0E, 0x0F, 0x09, 0x07, 0x08, 0x03]
        )

        self.command_data(
            0xE8,
            [0x34]
        )

        self.command_data(
            0x62,
            [0x18, 0x0D, 0x71, 0xED, 0x70, 0x70, 0x18, 0x0F, 0x71, 0xEF, 0x70, 0x70]
        )

        self.command_data(
            0x63,
            [0x18, 0x11, 0x71, 0xF1, 0x70, 0x70, 0x18, 0x13, 0x71, 0xF3, 0x70, 0x70]
        )

        self.command_data(
            0x64,
            [0x28, 0x29, 0xF1, 0x01, 0xF1, 0x00, 0x07]
        )

        self.command_data(
            0x66,
            [0x3C, 0x00, 0xCD, 0x67, 0x45, 0x45, 0x10, 0x00, 0x00, 0x00]
        )

        self.command_data(
            0x67,
            [0x00, 0x3C, 0x00, 0x00, 0x00, 0x01, 0x54, 0x10, 0x32, 0x98]
        )

        self.command_data(
            0x74,
            [0x10, 0x85, 0x80, 0x00, 0x00, 0x4E, 0x00]
        )

        self.command_data(
            0x98,
            [0x3E, 0x07]
        )

        # Frame rate / porch
        self.command_data(
            0x35,
            [0x00]
        )

        # Display inversion ON
        self.command(0x21)

        # Sleep out
        self.command(0x11)
        time.sleep(0.12)

        # Display ON
        self.command(0x29)
        time.sleep(0.05)

    # ---------------------------------------------------------
    # Set drawing window
    # ---------------------------------------------------------

    def set_window(self, x0, y0, x1, y1):

        # Column address
        self.command_data(
            0x2A,
            [
                (x0 >> 8) & 0xFF,
                x0 & 0xFF,
                (x1 >> 8) & 0xFF,
                x1 & 0xFF
            ]
        )

        # Row address
        self.command_data(
            0x2B,
            [
                (y0 >> 8) & 0xFF,
                y0 & 0xFF,
                (y1 >> 8) & 0xFF,
                y1 & 0xFF
            ]
        )

        # Memory write
        self.command(0x2C)

    # ---------------------------------------------------------
    # Fill entire display with RGB565 colour
    # ---------------------------------------------------------

    def fill(self, colour):

        high = (colour >> 8) & 0xFF
        low = colour & 0xFF

        # 240 x 240 pixels
        pixel_count = self.WIDTH * self.HEIGHT

        # Build chunks to avoid excessive memory usage
        chunk_pixels = 2048

        chunk = bytearray()

        for _ in range(chunk_pixels):
            chunk.append(high)
            chunk.append(low)

        self.set_window(
            0,
            0,
            self.WIDTH - 1,
            self.HEIGHT - 1
        )

        GPIO.output(self.cs, GPIO.LOW)
        GPIO.output(self.DC, GPIO.HIGH)

        remaining = pixel_count

        while remaining > 0:

            pixels = min(remaining, chunk_pixels)

            self.spi.xfer2(
                chunk[:pixels * 2]
            )

            remaining -= pixels

        GPIO.output(self.cs, GPIO.HIGH)

    # ---------------------------------------------------------
    # Send complete framebuffer
    # ---------------------------------------------------------

    def show_buffer(self, buffer):

        if len(buffer) != self.WIDTH * self.HEIGHT * 2:
            raise ValueError(
                "Buffer must be exactly "
                f"{self.WIDTH * self.HEIGHT * 2} bytes"
            )

        self.set_window(
            0,
            0,
            self.WIDTH - 1,
            self.HEIGHT - 1
        )

        GPIO.output(self.cs, GPIO.LOW)
        GPIO.output(self.DC, GPIO.HIGH)

        # Send in chunks because spidev's buffer is limited
        for i in range(0, len(buffer), 4096):
            self.spi.xfer2(
                buffer[i:i + 4096]
            )

        GPIO.output(self.cs, GPIO.HIGH)

    # ---------------------------------------------------------
    # Close display
    # ---------------------------------------------------------

    def close(self):

        GPIO.output(self.cs, GPIO.HIGH)

        self.spi.close()

        GPIO.cleanup()