import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.models import Location, Product


class GeoLocationService:
    """Resolve location names to coordinates using Geapify batch geocoding."""

    AUTOCOMPLETE_URL = "https://api.geoapify.com/v1/geocode/autocomplete"
    WA_FILTER = "rect:112.8,-35.2,129.1,-13.4"
    
    @classmethod
    def _api_key(cls):
        return os.getenv("GEOAPIFY_API_KEY", "").strip()

    @staticmethod
    def _normalize_text(value):
        return " ".join((value or "").strip().split()).lower()

    @classmethod
    def _is_western_australia_result(cls, payload):
        if not isinstance(payload, dict):
            return False

        country = str(payload.get("country_code") or payload.get("country") or "").strip().lower()
        if country and country != "au":
            return False

        state = cls._normalize_text(payload.get("state"))
        state_code = cls._normalize_text(payload.get("state_code"))
        admin1 = cls._normalize_text(payload.get("county"))

        return any(
            token in {"wa", "western australia"}
            for token in (state, state_code, admin1)
        )

    @classmethod
    def _normalize_location_result(cls, payload):
        if not isinstance(payload, dict):
            return None

        suburb = payload.get("name") or payload.get("suburb") or payload.get("city")
        lon = payload.get("lon")
        lat = payload.get("lat")

        if not suburb or lon is None or lat is None:
            return None

        if not cls._is_western_australia_result(payload):
            return None

        state = payload.get("state")
        return {
            "name": suburb.strip(),
            "state": state,
            "label": f"{suburb.strip()}, {state}" if state else suburb.strip(),
            "longitude": float(lon),
            "latitude": float(lat),
        }

    @classmethod
    def suggest_wa_locations(cls, query, limit=5):
        clean_query = (query or "").strip()
        if len(clean_query) < 3:
            return []

        api_key = cls._api_key()
        if not api_key:
            return []

        params = {
            "text": clean_query,
            "filter": cls.WA_FILTER,
            "limit": limit,
            "format": "json",
            "apiKey": api_key,
        }
        url = f"{cls.AUTOCOMPLETE_URL}?{urlencode(params)}"

        try:
            payload = cls._request_json(url, method="GET")
        except (HTTPError, URLError, TimeoutError, ValueError):
            return []

        locations = []
        seen = set()
        for result in payload.get("results", []):
            location = cls._normalize_location_result(result)
            if not location:
                continue

            key = cls._normalize_text(location["name"])
            if key in seen:
                continue

            seen.add(key)
            locations.append(location)

        return locations[:limit]

    @classmethod
    def resolve_wa_location(cls, query):
        clean_query = (query or "").strip()
        if not clean_query:
            return None

        locations = cls.suggest_wa_locations(clean_query, limit=10)
        if not locations:
            return None

        normalized_query = cls._normalize_text(clean_query)
        for location in locations:
            normalized_name = cls._normalize_text(location["name"])
            normalized_label = cls._normalize_text(location["label"])
            if normalized_query in {normalized_name, normalized_label}:
                return location

        for location in locations:
            normalized_name = cls._normalize_text(location["name"])
            if normalized_query in normalized_name or normalized_name in normalized_query:
                return location

        return locations[0]

    @staticmethod
    def _request_json(url, method="GET", payload=None):
        data = None
        headers = {}

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(url=url, data=data, headers=headers, method=method)
        with urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))

    @classmethod
    def geocode_batch(cls, location_names):
        """Resolve location names to WA-only coordinates.

        Returns: {location_name: {"longitude": float, "latitude": float}}
        """
        unique_locations = []
        seen = set()
        for name in location_names or []:
            clean_name = (name or "").strip()
            if clean_name and clean_name not in seen:
                seen.add(clean_name)
                unique_locations.append(clean_name)

        if not unique_locations:
            return {}

        resolved = {}

        for input_location in unique_locations:
            match = cls.resolve_wa_location(input_location)
            if not match:
                continue

            resolved[input_location] = {
                "longitude": match["longitude"],
                "latitude": match["latitude"],
            }
            resolved[match["name"]] = {
                "longitude": match["longitude"],
                "latitude": match["latitude"],
            }

        return resolved

    @classmethod
    def calculate_distance(cls, lon1, lat1, lon2, lat2):
        """
        Haversine formula to calculate distance between two points in kilometers.
        """
        from math import radians, cos, sin, asin, sqrt

        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  
        return c * r
    
    @classmethod
    def nearest_products(cls, user_lat, user_lon, limit=10):
        """Return products sorted by distance from the user's location."""
        products = Product.query.join(Location).filter(Product.status == 'available').all()
        with_dist = [
            (p, cls.calculate_distance(user_lon, user_lat, p.location.longitude, p.location.latitude))
            for p in products
        ]
        with_dist.sort(key=lambda x: x[1])
        return with_dist[:limit]