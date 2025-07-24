# geolocation.py

from io import BytesIO
from PIL import Image
import exifread
from geopy.geocoders import Nominatim
from langchain.agents import Tool

def fetch_geolocation(image_bytes: bytes) -> str:
    """
    1. Read GPS EXIF tags from the uploaded image bytes.
    2. Convert them to decimal lat/lon.
    3. Reverse‑geocode to a human address.
    """
    # 1) Load EXIF
    img = BytesIO(image_bytes)
    tags = exifread.process_file(img, details=False)
    if not tags.get("GPS GPSLatitude"):
        return "Unknown location"

    def to_decimal(values, ref):
        deg, min, sec = [float(x.num) / float(x.den) for x in values]
        dec = deg + (min / 60.0) + (sec / 3600.0)
        return -dec if ref in ["S", "W"] else dec

    lat = to_decimal(tags["GPS GPSLatitude"].values,
                     tags["GPS GPSLatitudeRef"].values)
    lon = to_decimal(tags["GPS GPSLongitude"].values,
                     tags["GPS GPSLongitudeRef"].values)

    # 2) Reverse geocode
    geolocator = Nominatim(user_agent="road-damage-app")
    location = geolocator.reverse((lat, lon), exactly_one=True, timeout=10)
    return location.address if location else f"{lat:.6f}, {lon:.6f}"

class GeoLocationTool(Tool):
    def __init__(self):
        super().__init__(
            name="GeoLocation",
            func=fetch_geolocation,
            description=(
                "Given image bytes, extract GPS EXIF and return a human-readable location."
            )
        )
