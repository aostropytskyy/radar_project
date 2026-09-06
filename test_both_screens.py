import time
import math

from gc9a01 import GC9A01


WIDTH = 240
HEIGHT = 240


# ---------------------------------------------------------
# Colours
# ---------------------------------------------------------

BLACK = 0x0000
WHITE = 0xFFFF
GREEN = 0x07E0
YELLOW = 0xFFE0
CYAN = 0x07FF
GREY = 0x8410
RED = 0xF800


# ---------------------------------------------------------
# Basic drawing functions
# ---------------------------------------------------------

def pixel(buffer, x, y, colour):

    if 0 <= x < WIDTH and 0 <= y < HEIGHT:

        pos = (y * WIDTH + x) * 2

        buffer[pos] = (colour >> 8) & 0xFF
        buffer[pos + 1] = colour & 0xFF


def draw_line(buffer, x1, y1, x2, y2, colour):

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    err = dx - dy

    while True:

        pixel(buffer, x1, y1, colour)

        if x1 == x2 and y1 == y2:
            break

        e2 = 2 * err

        if e2 > -dy:
            err -= dy
            x1 += sx

        if e2 < dx:
            err += dx
            y1 += sy


def draw_circle(buffer, cx, cy, radius, colour):

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
            (cx + x, cy - y),
        ]

        for px, py in points:
            pixel(buffer, px, py, colour)

        y += 1

        if decision <= 0:
            decision += 2 * y + 1
        else:
            x -= 1
            decision += 2 * (y - x) + 1


# ---------------------------------------------------------
# Tiny font
# ---------------------------------------------------------

FONT = {
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    "B": ["11110","10001","10001","11110","10001","10001","11110"],
    "C": ["01111","10000","10000","10000","10000","10000","01111"],
    "D": ["11110","10001","10001","10001","10001","10001","11110"],
    "E": ["11111","10000","10000","11110","10000","10000","11111"],
    "F": ["11111","10000","10000","11110","10000","10000","10000"],
    "G": ["01111","10000","10000","10111","10001","10001","01111"],
    "H": ["10001","10001","10001","11111","10001","10001","10001"],
    "I": ["11111","00100","00100","00100","00100","00100","11111"],
    "J": ["00111","00010","00010","00010","10010","10010","01100"],
    "K": ["10001","10010","10100","11000","10100","10010","10001"],
    "L": ["10000","10000","10000","10000","10000","10000","11111"],
    "M": ["10001","11011","10101","10101","10001","10001","10001"],
    "N": ["10001","11001","10101","10011","10001","10001","10001"],
    "O": ["01110","10001","10001","10001","10001","10001","01110"],
    "P": ["11110","10001","10001","11110","10000","10000","10000"],
    "Q": ["01110","10001","10001","10001","10101","10010","01101"],
    "R": ["11110","10001","10001","11110","10100","10010","10001"],
    "S": ["01111","10000","10000","01110","00001","00001","11110"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
    "U": ["10001","10001","10001","10001","10001","10001","01110"],
    "V": ["10001","10001","10001","10001","10001","01010","00100"],
    "W": ["10001","10001","10001","10101","10101","11011","10001"],
    "X": ["10001","10001","01010","00100","01010","10001","10001"],
    "Y": ["10001","10001","01010","00100","00100","00100","00100"],
    "Z": ["11111","00001","00010","00100","01000","10000","11111"],

    "0": ["01110","10001","10011","10101","11001","10001","01110"],
    "1": ["00100","01100","00100","00100","00100","00100","01110"],
    "2": ["01110","10001","00001","00010","00100","01000","11111"],
    "3": ["11110","00001","00001","01110","00001","00001","11110"],
    "4": ["00010","00110","01010","10010","11111","00010","00010"],
    "5": ["11111","10000","10000","11110","00001","00001","11110"],
    "6": ["01110","10000","10000","11110","10001","10001","01110"],
    "7": ["11111","00001","00010","00100","01000","01000","01000"],
    "8": ["01110","10001","10001","01110","10001","10001","01110"],
    "9": ["01110","10001","10001","01111","00001","00001","01110"],

    ":": ["00000","00100","00100","00000","00100","00100","00000"],
    "-": ["00000","00000","00000","11111","00000","00000","00000"],
    ".": ["00000","00000","00000","00000","00000","00110","00110"],
    " ": ["00000","00000","00000","00000","00000","00000","00000"],
}


def draw_char(buffer, char, x, y, scale, colour):

    char = char.upper()

    if char not in FONT:
        return

    pattern = FONT[char]

    for row, line in enumerate(pattern):

        for col, value in enumerate(line):

            if value == "1":

                for sy in range(scale):
                    for sx in range(scale):

                        pixel(
                            buffer,
                            x + col * scale + sx,
                            y + row * scale + sy,
                            colour
                        )


def draw_text(buffer, text, x, y, scale, colour):

    for char in text.upper():

        draw_char(
            buffer,
            char,
            x,
            y,
            scale,
            colour
        )

        x += 6 * scale


def centred_text(buffer, text, y, scale, colour):

    width = len(text) * 6 * scale

    x = (WIDTH - width) // 2

    draw_text(
        buffer,
        text,
        x,
        y,
        scale,
        colour
    )


# ---------------------------------------------------------
# Radar
# ---------------------------------------------------------

planes = [
    {
        "angle": 25,
        "distance": 55,
        "speed": 0.20,
        "callsign": "BA142",
        "selected": True
    },

    {
        "angle": 115,
        "distance": 82,
        "speed": -0.12,
        "callsign": "EZY21",
        "selected": False
    },

    {
        "angle": 205,
        "distance": 43,
        "speed": 0.08,
        "callsign": "RYR67",
        "selected": False
    },

    {
        "angle": 310,
        "distance": 98,
        "speed": -0.16,
        "callsign": "KLM31",
        "selected": False
    }
]


def create_radar(angle):

    buffer = bytearray(WIDTH * HEIGHT * 2)

    # Black background
    for i in range(0, len(buffer), 2):
        buffer[i] = 0
        buffer[i + 1] = 0

    cx = 120
    cy = 120

    # Radar circles
    draw_circle(buffer, cx, cy, 30, GREEN)
    draw_circle(buffer, cx, cy, 60, GREEN)
    draw_circle(buffer, cx, cy, 90, GREEN)
    draw_circle(buffer, cx, cy, 115, GREEN)

    # Crosshair
    draw_line(buffer, 5, cy, 235, cy, GREEN)
    draw_line(buffer, cx, 5, cx, 235, GREEN)

    # Diagonal guides
    draw_line(buffer, 38, 38, 202, 202, GREY)
    draw_line(buffer, 202, 38, 38, 202, GREY)

    # Sweep
    sweep_rad = math.radians(angle)

    sweep_x = int(
        cx + 115 * math.sin(sweep_rad)
    )

    sweep_y = int(
        cy - 115 * math.cos(sweep_rad)
    )

    draw_line(
        buffer,
        cx,
        cy,
        sweep_x,
        sweep_y,
        YELLOW
    )

    # Aircraft
    for plane in planes:

        a = math.radians(plane["angle"])

        x = int(
            cx +
            plane["distance"] *
            math.sin(a)
        )

        y = int(
            cy -
            plane["distance"] *
            math.cos(a)
        )

        colour = YELLOW if plane["selected"] else CYAN

        # Target
        draw_circle(
            buffer,
            x,
            y,
            4,
            colour
        )

        # Aircraft heading line
        heading_rad = math.radians(
            plane["angle"] + 90
        )

        hx = int(
            x + 9 * math.cos(heading_rad)
        )

        hy = int(
            y + 9 * math.sin(heading_rad)
        )

        draw_line(
            buffer,
            x,
            y,
            hx,
            hy,
            colour
        )

    # Centre
    draw_circle(
        buffer,
        cx,
        cy,
        3,
        YELLOW
    )

    return buffer


# ---------------------------------------------------------
# Flight information
# ---------------------------------------------------------

flight = {
    "callsign": "BA142",
    "airline": "BRITISH",
    "altitude": 12500,
    "speed": 420,
    "heading": 275,
    "origin": "LHR",
    "destination": "BFS"
}


def create_info_screen():

    buffer = bytearray(WIDTH * HEIGHT * 2)

    # Black background
    for i in range(0, len(buffer), 2):
        buffer[i] = 0
        buffer[i + 1] = 0

    # Border
    draw_line(buffer, 8, 8, 231, 8, GREEN)
    draw_line(buffer, 231, 8, 231, 231, GREEN)
    draw_line(buffer, 231, 231, 8, 231, GREEN)
    draw_line(buffer, 8, 231, 8, 8, GREEN)

    # Callsign
    centred_text(
        buffer,
        flight["callsign"],
        18,
        3,
        YELLOW
    )

    # Airline
    centred_text(
        buffer,
        flight["airline"],
        45,
        2,
        CYAN
    )

    # Separator
    draw_line(
        buffer,
        25,
        68,
        215,
        68,
        GREY
    )

    # Altitude
    centred_text(
        buffer,
        "ALTITUDE",
        80,
        2,
        WHITE
    )

    centred_text(
        buffer,
        str(flight["altitude"]) + " FT",
        100,
        3,
        GREEN
    )

    # Speed
    centred_text(
        buffer,
        "SPEED",
        133,
        2,
        WHITE
    )

    centred_text(
        buffer,
        str(flight["speed"]) + " KMH",
        153,
        2,
        GREEN
    )

    # Heading
    centred_text(
        buffer,
        "HDG",
        181,
        2,
        WHITE
    )

    centred_text(
        buffer,
        str(flight["heading"]) + " DEG",
        201,
        2,
        GREEN
    )

    return buffer


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

print("Starting displays...")

# Display 1 = radar
radar_display = GC9A01(cs=8, reset_display=True)

# Display 2 = information
info_display = GC9A01(cs=7, reset_display=False)

print("Both displays initialised.")


try:

    # Draw initial information screen
    info_buffer = create_info_screen()
    info_display.show_buffer(info_buffer)

    angle = 0

    while True:

        # Update radar
        radar_buffer = create_radar(angle)

        radar_display.show_buffer(
            radar_buffer
        )

        # Move sweep
        angle += 5

        if angle >= 360:
            angle = 0

        time.sleep(0.08)


except KeyboardInterrupt:

    print("\nStopping...")


finally:

    radar_display.close()
    info_display.close()

    print("Displays closed.")