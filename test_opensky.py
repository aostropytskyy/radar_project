import requests
import math

url = "https://opensky-network.org/api/states/all"

# Loughborough
CENTER_LAT = 52.7721
CENTER_LON = -1.2062

# Radar range
RADIUS_KM = 50

# Bounding box around Loughborough
LAT_RANGE = 1.35
LON_RANGE = 2.2

params = {
    "lamin": CENTER_LAT - LAT_RANGE,
    "lomin": CENTER_LON - LON_RANGE,
    "lamax": CENTER_LAT + LAT_RANGE,
    "lomax": CENTER_LON + LON_RANGE
}

def radar_position(distance_km, bearing, radar_radius_pixels=115):
    """Convert distance and bearing into X/Y radar coordinates."""

    # Convert bearing to radians
    angle = math.radians(bearing)

    # Scale 50 km to the edge of the radar
    scale = radar_radius_pixels / RADIUS_KM

    distance_pixels = distance_km * scale

    # Bearing 0 = north
    x = distance_pixels * math.sin(angle)
    y = -distance_pixels * math.cos(angle)

    return x, y

def distance_and_bearing(lat1, lon1, lat2, lon2):
    """Calculate distance in km and bearing in degrees."""

    R = 6371.0

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine distance
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c

    # Bearing
    y = math.sin(dlon) * math.cos(lat2)

    x = (
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    )

    bearing = math.degrees(math.atan2(y, x))
    bearing = (bearing + 360) % 360

    return distance, bearing


response = requests.get(url, params=params, timeout=15)

print("HTTP status:", response.status_code)

if response.status_code == 200:

    data = response.json()

    aircraft = data.get("states", [])

    print(f"Aircraft found: {len(aircraft)}")
    print()

    for plane in aircraft:

        # OpenSky data
        callsign = (plane[1] or "UNKNOWN").strip()
        icao = plane[0]

        latitude = plane[6]
        longitude = plane[5]

        altitude = plane[7]
        speed = plane[9]
        heading = plane[10]

        # Ignore aircraft without a position
        if latitude is None or longitude is None:
            continue

        # Calculate distance and bearing from Loughborough
        distance, bearing = distance_and_bearing(
            CENTER_LAT,
            CENTER_LON,
            latitude,
            longitude
        )

        x, y = radar_position(distance, bearing)

        # Only display aircraft within our radar range
        if distance <= RADIUS_KM:

            print(
                f"Callsign: {callsign} | "
                f"ICAO: {icao} | "
                f"Lat: {latitude:.4f} | "
                f"Lon: {longitude:.4f} | "
                f"Altitude: {altitude} m | "
                f"Speed: {speed} m/s | "
                f"Heading: {heading}deg | "
                f"Distance: {distance:.1f} km | "
                f"Bearing: {bearing:.0f}deg"
                f"Radar X: {x:.1f} | "
                f"Radar Y: {y:.1f}"
            )

else:
    print("API request failed:")
    print(response.text)