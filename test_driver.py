from gc9a01 import GC9A01
import time

display = GC9A01()

try:

    display.fill(0xF800)
    time.sleep(2)

    display.fill(0x07E0)
    time.sleep(2)

    display.fill(0x001F)
    time.sleep(2)

    display.fill(0xFFFF)
    time.sleep(2)

    display.fill(0x0000)
    time.sleep(2)

finally:

    display.close()