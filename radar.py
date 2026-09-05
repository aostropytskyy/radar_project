import math
import time

from gc9a01 import GC9A01


WIDTH = 240
HEIGHT = 240

CX = 120
CY = 120

# RGB565 colours
BLACK = 0x0000
GREEN = 0x07E0
DARK_GREEN = 0x0320
BRIGHT_GREEN = 0x07FF
WHITE = 0xFFFF
YELLOW = 0xFFE0
RED = 0xF800


# ------------------------------------------------------------
# RGB565 helpers
# ------------------------------------------------------------

def put_pixel(buffer, x, y, colour):

    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return

    pos = (y * WIDTH + x) * 2

    buffer[pos] = (colour >> 8) & 0xFF
    buffer[pos + 1] = colour & 0xFF


# ------------------------------------------------------------
# Line drawing
# ------------------------------------------------------------

def line(buffer, x0, y0, x1, y1, colour):

    x0 = int(x0)
    y0 = int(y0)
    x1 = int(x1)
    y1 = int(y1)

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    err = dx - dy

    while True:

        put_pixel(buffer, x0, y0, colour)

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * err

        if e2 > -dy:
            err -= dy
            x0 += sx

        if e2 < dx:
            err += dx
            y0 += sy


# ------------------------------------------------------------
# Circle
# ------------------------------------------------------------

def circle(buffer, cx, cy, radius, colour):

    x = radius
    y = 0
    decision = 1 - radius

    while x >= y:

        points = [
            (cx + x, cy + y),
            (cx + y, cy + x),
            (cx - y, cy + x),
            (cx - x, cy + y),
            (cx - x, cy - y),
            (cx - y, cy - x),
            (cx + y, cy - x),
            (cx + x, cy - y)
        ]

        for px, py in points:
            put_pixel(buffer, px, py, colour)

        y += 1

        if decision <= 0:
            decision += 2 * y + 1
        else:
            x -= 1
            decision += 2 * (y - x) + 1


# ------------------------------------------------------------
# Filled circle
# ------------------------------------------------------------

def filled_circle(buffer, cx, cy, radius, colour):

    for y in range(-radius, radius + 1):

        width = int(math.sqrt(radius * radius - y * y))

        for x in range(-width, width + 1):

            put_pixel(
                buffer,
                cx + x,
                cy + y,
                colour
            )


# ------------------------------------------------------------
# Aircraft
# ------------------------------------------------------------

def aircraft(buffer, angle, distance, selected=False):

    # Radar angle:
    # 0 degrees = north
    radians = math.radians(angle)

    radius = distance

    x = int(
        CX +
        math.sin(radians) * radius
    )

    y = int(
        CY -
        math.cos(radians) * radius
    )

    colour = YELLOW if selected else GREEN

    # Target dot
    filled_circle(
        buffer,
        x,
        y,
        3 if selected else 2,
        colour
    )

    # Aircraft heading indicator
    heading_length = 7

    hx = int(
        x +
        math.sin(radians) * heading_length
    )

    hy = int(
        y -
        math.cos(radians) * heading_length
    )

    line(
        buffer,
        x,
        y,
        hx,
        hy,
        colour
    )

    # Small cross
    line(
        buffer,
        x - 4,
        y,
        x + 4,
        y,
        colour
    )

    line(
        buffer,
        x,
        y - 4,
        x,
        y + 4,
        colour
    )


# ------------------------------------------------------------
# Radar graphics
# ------------------------------------------------------------

def draw_radar(buffer, sweep_angle, aircraft_list):

    # Radar boundary
    circle(
        buffer,
        CX,
        CY,
        116,
        GREEN
    )

    # Range rings
    for radius in [30, 60, 90]:

        circle(
            buffer,
            CX,
            CY,
            radius,
            DARK_GREEN
        )

    # Outer ring
    circle(
        buffer,
        CX,
        CY,
        115,
        GREEN
    )

    # Crosshair
    line(
        buffer,
        CX - 115,
        CY,
        CX + 115,
        CY,
        DARK_GREEN
    )

    line(
        buffer,
        CX,
        CY - 115,
        CX,
        CY + 115,
        DARK_GREEN
    )

    # Diagonal guides
    line(
        buffer,
        CX - 82,
        CY - 82,
        CX + 82,
        CY + 82,
        DARK_GREEN
    )

    line(
        buffer,
        CX + 82,
        CY - 82,
        CX - 82,
        CY + 82,
        DARK_GREEN
    )

    # Sweep
    sweep_length = 113

    radians = math.radians(sweep_angle)

    sx = int(
        CX +
        math.sin(radians) * sweep_length
    )

    sy = int(
        CY -
        math.cos(radians) * sweep_length
    )

    line(
        buffer,
        CX,
        CY,
        sx,
        sy,
        BRIGHT_GREEN
    )

    # Aircraft
    for i, plane in enumerate(aircraft_list):

        aircraft(
            buffer,
            plane["angle"],
            plane["distance"],
            i == plane["selected"]
        )

    # Centre
    filled_circle(
        buffer,
        CX,
        CY,
        2,
        WHITE
    )


# ------------------------------------------------------------
# Simulated aircraft
# ------------------------------------------------------------

planes = [

    {
        "angle": 25,
        "distance": 55,
        "speed": 0.20,
        "selected": 0
    },

    {
        "angle": 115,
        "distance": 82,
        "speed": -0.12,
        "selected": 0
    },

    {
        "angle": 205,
        "distance": 43,
        "speed": 0.08,
        "selected": 0
    },

    {
        "angle": 310,
        "distance": 98,
        "speed": -0.16,
        "selected": 0
    }
]


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

display = GC9A01()

try:

    sweep = 0

    while True:

        # New framebuffer
        buffer = bytearray(
            WIDTH * HEIGHT * 2
        )

        # Move aircraft slightly
        for plane in planes:

            plane["angle"] += plane["speed"]

            if plane["angle"] >= 360:
                plane["angle"] -= 360

            if plane["angle"] < 0:
                plane["angle"] += 360

        # Draw radar
        draw_radar(
            buffer,
            sweep,
            planes
        )

        # Send complete frame
        display.show_buffer(buffer)

        # Sweep rotation
        sweep += 5

        if sweep >= 360:
            sweep -= 360

        time.sleep(0.08)


except KeyboardInterrupt:

    print("Radar stopped")


finally:

    display.close()