import requests
import math
import time
import gc

from gc9a01 import GC9A01


# ============================================================
# SETTINGS
# ============================================================

CENTER_LAT = 52.7721
CENTER_LON = -1.2062

RADAR_RANGE_KM = 50

SCREEN_SIZE = 240
CENTER = 120

# Refresh rate
UPDATE_SECONDS = 2


# ============================================================
# RGB565 COLOURS
# ============================================================

BLACK = 0x0000
WHITE = 0xFFFF
GREEN = 0x07E0
RED = 0xF800
YELLOW = 0xFFE0
GREY = 0x7BEF


# ============================================================
# DISPLAY
# ============================================================

display = GC9A01(cs=8)


# ============================================================
# RGB565 PIXEL FUNCTIONS
# ============================================================

def set_pixel(buffer, x, y, colour):

    if x < 0 or x >= SCREEN_SIZE:
        return

    if y < 0 or y >= SCREEN_SIZE:
        return

    index = (y * SCREEN_SIZE + x) * 2

    buffer[index] = (colour >> 8) & 0xFF
    buffer[index + 1] = colour & 0xFF


def draw_circle(buffer, cx, cy, radius, colour):

    x = radius
    y = 0
    error = 1 - radius

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
            set_pixel(buffer, px, py, colour)

        y += 1

        if error < 0:
            error += 2 * y + 1
        else:
            x -= 1
            error += 2 * (y - x) + 1


def draw_line(buffer, x0, y0, x1, y1, colour):

    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)

    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    error = dx + dy

    while True:

        set_pixel(buffer, x0, y0, colour)

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * error

        if e2 >= dy:
            error += dy
            x0 += sx

        if e2 <= dx:
            error += dx
            y0 += sy


def draw_aircraft(buffer, x, y, colour):

    # Small aircraft/radar blip
    set_pixel(buffer, x, y, colour)
    set_pixel(buffer, x + 1, y, colour)
    set_pixel(buffer, x - 1, y, colour)
    set_pixel(buffer, x, y + 1, colour)
    set_pixel(buffer, x, y - 1, colour)

    # Extra pixels to make it easier to see
    set_pixel(buffer, x + 2, y, colour)
    set_pixel(buffer, x - 2, y, colour)
    set_pixel(buffer, x, y + 2, colour)
    set_pixel(buffer, x, y - 2, colour)


# ============================================================
# DISTANCE / BEARING
# ============================================================

def distance_and_bearing(lat1, lon1, lat2, lon2):

    R = 6371.0

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    distance = R * c

    y = math.sin(dlon) * math.cos(lat2)

    x = (
        math.cos(lat1) * math.sin(lat2)
        -
        math.sin(lat1)
        * math.cos(lat2)
        * math.cos(dlon)
    )

    bearing = math.degrees(
        math.atan2(y, x)
    )

    bearing = (bearing + 360) % 360

    return distance, bearing


# ============================================================
# RADAR POSITION
# ============================================================

def radar_position(distance_km, bearing):

    # Leave a small margin around the 50 km ring
    radar_radius_pixels = 105

    distance_pixels = (
        distance_km / RADAR_RANGE_KM
    ) * radar_radius_pixels

    angle = math.radians(bearing)

    # 0 degrees = North
    x = (
        CENTER
        + distance_pixels * math.sin(angle)
    )

    y = (
        CENTER
        - distance_pixels * math.cos(angle)
    )

    return int(x), int(y)


# ============================================================
# DRAW RADAR
# ============================================================

def draw_radar(buffer, aircraft):

    # Background
    buffer[:] = bytes(
        [BLACK >> 8, BLACK & 0xFF]
    ) * (SCREEN_SIZE * SCREEN_SIZE)

    # Radar rings
    draw_circle(
        buffer,
        CENTER,
        CENTER,
        115,
        GREEN
    )

    draw_circle(
        buffer,
        CENTER,
        CENTER,
        52,
        GREEN
    )

    draw_circle(
        buffer,
        CENTER,
        CENTER,
        21,
        GREEN
    )

    # Cardinal direction lines
    draw_line(
        buffer,
        CENTER,
        15,
        CENTER,
        225,
        GREEN
    )

    draw_line(
        buffer,
        15,
        CENTER,
        225,
        CENTER,
        GREEN
    )

    # Centre point = Loughborough
    draw_circle(
        buffer,
        CENTER,
        CENTER,
        3,
        WHITE
    )

    # Aircraft
    for plane in aircraft:

        x, y = radar_position(
            plane["distance"],
            plane["bearing"]
        )

        draw_aircraft(
            buffer,
            x,
            y,
            RED
        )


# ============================================================
# OPEN SKY
# ============================================================

def get_aircraft():

    url = "https://opensky-network.org/api/states/all"

    # Bounding box around Loughborough
    params = {
        "lamin": CENTER_LAT - 1.35,
        "lomin": CENTER_LON - 2.2,
        "lamax": CENTER_LAT + 1.35,
        "lomax": CENTER_LON + 2.2
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        if response.status_code != 200:

            print(
                "OpenSky error:",
                response.status_code
            )

            return []

        data = response.json()

        states = data.get(
            "states",
            []
        )

        aircraft = []

        for plane in states:

            latitude = plane[6]
            longitude = plane[5]

            if latitude is None or longitude is None:
                continue

            distance, bearing = distance_and_bearing(
                CENTER_LAT,
                CENTER_LON,
                latitude,
                longitude
            )

            # Only aircraft inside 50 km
            if distance <= RADAR_RANGE_KM:

                callsign = (
                    plane[1] or "UNKNOWN"
                ).strip()

                aircraft.append({
                    "callsign": callsign,
                    "icao": plane[0],
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": plane[7],
                    "speed": plane[9],
                    "heading": plane[10],
                    "distance": distance,
                    "bearing": bearing
                })

        return aircraft

    except Exception as e:

        print(
            "OpenSky connection error:",
            e
        )

        return []


# ============================================================
# MAIN LOOP
# ============================================================

try:

    print("Starting Loughborough radar...")
    print("Range:", RADAR_RANGE_KM, "km")

    buffer = bytearray(
        SCREEN_SIZE * SCREEN_SIZE * 2
    )

    while True:

        print()
        print("Updating aircraft...")

        aircraft = get_aircraft()

        print(
            "Aircraft within 50 km:",
            len(aircraft)
        )

        for plane in aircraft:

            print(
                plane["callsign"],
                "|",
                f"{plane['distance']:.1f} km",
                "|",
                f"{plane['bearing']:.0f}deg"
            )

        draw_radar(
            buffer,
            aircraft
        )

        display.show_buffer(
            buffer
        )

        gc.collect()

        time.sleep(
            UPDATE_SECONDS
        )


except KeyboardInterrupt:

    print("Stopping radar...")

    display.fill(BLACK)
    display.close()