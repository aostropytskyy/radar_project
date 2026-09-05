import spidev
import RPi.GPIO as GPIO
import time

WIDTH = 240
HEIGHT = 240

DC = 25
RST = 24
CS = 8


class GC9A01:

    def __init__(self):

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(DC, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RST, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(CS, GPIO.OUT, initial=GPIO.HIGH)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)

        # We control CS ourselves
        self.spi.no_cs = True

        self.spi.max_speed_hz = 2000000
        self.spi.mode = 0
        self.spi.lsbfirst = False
        self.spi.bits_per_word = 8

        self.reset()
        self.init_display()


    def command(self, value):

        GPIO.output(CS, GPIO.LOW)
        GPIO.output(DC, GPIO.LOW)

        self.spi.xfer2([value])

        GPIO.output(CS, GPIO.HIGH)


    def data(self, values):

        GPIO.output(CS, GPIO.LOW)
        GPIO.output(DC, GPIO.HIGH)

        if isinstance(values, int):
            values = [values]

        for i in range(0, len(values), 4096):
            self.spi.xfer2(values[i:i + 4096])

        GPIO.output(CS, GPIO.HIGH)


    def command_data(self, command, values):

        GPIO.output(CS, GPIO.LOW)

        GPIO.output(DC, GPIO.LOW)
        self.spi.xfer2([command])

        GPIO.output(DC, GPIO.HIGH)

        if isinstance(values, int):
            values = [values]

        self.spi.xfer2(values)

        GPIO.output(CS, GPIO.HIGH)


    def reset(self):

        GPIO.output(CS, GPIO.HIGH)

        GPIO.output(RST, GPIO.HIGH)
        time.sleep(0.05)

        GPIO.output(RST, GPIO.LOW)
        time.sleep(0.02)

        GPIO.output(RST, GPIO.HIGH)
        time.sleep(0.12)


    def init_display(self):

        self.reset()

        self.command(0x01)
        time.sleep(0.15)

        self.command(0xEF)

        self.command(0xEB)
        self.data(0x14)

        self.command(0xFE)

        self.command(0xEF)

        self.command(0xEB)
        self.data(0x14)

        self.command(0x84)
        self.data(0x40)

        self.command(0x85)
        self.data(0xFF)

        self.command(0x86)
        self.data(0xFF)

        self.command(0x87)
        self.data(0xFF)

        self.command(0x88)
        self.data(0x0A)

        self.command(0x89)
        self.data(0x21)

        self.command(0x8A)
        self.data(0x00)

        self.command(0x8B)
        self.data(0x80)

        self.command(0x8C)
        self.data(0x01)

        self.command(0x8D)
        self.data(0x01)

        self.command(0x8E)
        self.data(0xFF)

        self.command(0x8F)
        self.data(0xFF)

        self.command(0xB6)
        self.data([0x00, 0x20])

        self.command(0x36)
        self.data(0x08)

        self.command(0x3A)
        self.data(0x05)

        self.command(0x90)
        self.data([0x08, 0x08, 0x08, 0x08])

        self.command(0xBD)
        self.data(0x06)

        self.command(0xBC)
        self.data(0x00)

        self.command(0xFF)
        self.data([0x60, 0x01, 0x04])

        self.command(0xC3)
        self.data(0x13)

        self.command(0xC4)
        self.data(0x13)

        self.command(0xC9)
        self.data(0x22)

        self.command(0xBE)
        self.data(0x11)

        self.command(0xE1)
        self.data([0x10, 0x0E])

        self.command(0xDF)
        self.data([0x21, 0x0C, 0x02])

        self.command(0xF0)
        self.data([
            0x45, 0x09, 0x08,
            0x08, 0x26, 0x2A
        ])

        self.command(0xF1)
        self.data([
            0x43, 0x70, 0x72,
            0x36, 0x37, 0x6F
        ])

        self.command(0xF2)
        self.data([
            0x45, 0x09, 0x08,
            0x08, 0x26, 0x2A
        ])

        self.command(0xF3)
        self.data([
            0x43, 0x70, 0x72,
            0x36, 0x37, 0x6F
        ])

        self.command(0xED)
        self.data([0x1B, 0x0B])

        self.command(0xAE)
        self.data(0x77)

        self.command(0xCD)
        self.data(0x63)

        self.command(0x70)
        self.data([
            0x07, 0x07, 0x04,
            0x0E, 0x0F, 0x09,
            0x07, 0x08, 0x03
        ])

        self.command(0xE8)
        self.data(0x34)

        self.command(0x62)
        self.data([
            0x18, 0x0D, 0x71, 0xED,
            0x70, 0x70, 0x18, 0x0F,
            0x71, 0xEF, 0x70, 0x70
        ])

        self.command(0x63)
        self.data([
            0x18, 0x11, 0x71, 0xF1,
            0x70, 0x70, 0x18, 0x13,
            0x71, 0xF3, 0x70, 0x70
        ])

        self.command(0x64)
        self.data([
            0x28, 0x29, 0xF1,
            0x01, 0xF1, 0x00,
            0x07
        ])

        self.command(0x66)
        self.data([
            0x3C, 0x00, 0xCD,
            0x67, 0x45, 0x45,
            0x10, 0x00, 0x00
        ])

        self.command(0x67)
        self.data([
            0x00, 0x3C, 0x00,
            0x00, 0x00, 0x01,
            0x54, 0x10, 0x32, 0x98
        ])

        self.command(0x74)
        self.data([
            0x10, 0x85, 0x80,
            0x00, 0x00, 0x4E,
            0x00
        ])

        self.command(0x98)
        self.data([0x3E, 0x07])

        self.command(0x35)
        self.command(0x21)

        self.command(0x11)
        time.sleep(0.12)

        self.command(0x29)
        time.sleep(0.05)


    def set_window(self, x0, y0, x1, y1):

        GPIO.output(CS, GPIO.LOW)

        GPIO.output(DC, GPIO.LOW)
        self.spi.xfer2([0x2A])

        GPIO.output(DC, GPIO.HIGH)
        self.spi.xfer2([
            (x0 >> 8) & 0xFF,
            x0 & 0xFF,
            (x1 >> 8) & 0xFF,
            x1 & 0xFF
        ])

        GPIO.output(DC, GPIO.LOW)
        self.spi.xfer2([0x2B])

        GPIO.output(DC, GPIO.HIGH)
        self.spi.xfer2([
            (y0 >> 8) & 0xFF,
            y0 & 0xFF,
            (y1 >> 8) & 0xFF,
            y1 & 0xFF
        ])

        GPIO.output(DC, GPIO.LOW)
        self.spi.xfer2([0x2C])

        GPIO.output(DC, GPIO.HIGH)


    def fill(self, colour):

        high = (colour >> 8) & 0xFF
        low = colour & 0xFF

        block = bytearray()

        for _ in range(1024):
            block.append(high)
            block.append(low)

        self.set_window(0, 0, 239, 239)

        remaining = WIDTH * HEIGHT

        while remaining:

            pixels = min(1024, remaining)

            self.spi.xfer2(block[:pixels * 2])

            remaining -= pixels

        GPIO.output(CS, GPIO.HIGH)


    def show_buffer(self, buffer):

        self.set_window(0, 0, 239, 239)

        for i in range(0, len(buffer), 4096):
            self.spi.xfer2(buffer[i:i + 4096])

        GPIO.output(CS, GPIO.HIGH)

    def close(self):

        self.spi.close()
        GPIO.cleanup()
