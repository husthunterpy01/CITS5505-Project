import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.models import Location, Product


class GeoLocationService:
    """Resolve location names to coordinates using Geapify batch geocoding."""

    BASE_URL = "https://api.geoapify.com/v1/batch/geocode/search"
    MAX_POLL_ATTEMPTS = 10
    POLL_INTERVAL_SECONDS = 1
    def __init__(self):
        pass
    
    @classmethod
    def _api_key(cls):
        return os.getenv("GEOAPIFY_API_KEY", "").strip()

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
        """
        Two-step Geapify flow:
        1) POST batch job
        2) GET job result URL

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

        api_key = cls._api_key()
        if not api_key:
            print("GEOAPIFY_API_KEY is not set. Falling back to default coordinates.")
            return {}

        query = urlencode({"apiKey": api_key})
        create_job_url = f"{cls.BASE_URL}?{query}"

        try:
            create_result = cls._request_json(
                create_job_url,
                method="POST",
                payload=unique_locations,
            )
            result_url = (create_result or {}).get("url")
            if not result_url:
                print("Geapify batch job did not return a result URL.")
                return {}

            result_payload = None
            for _ in range(cls.MAX_POLL_ATTEMPTS):
                result_payload = cls._request_json(result_url, method="GET")
                if not isinstance(result_payload, dict):
                    break

                status = str(result_payload.get("status", "")).lower()
                if status not in {"pending", "running", "processing"}:
                    break
                time.sleep(cls.POLL_INTERVAL_SECONDS)
        except (HTTPError, URLError, TimeoutError, ValueError) as error:
            print(f"Geolocation lookup failed: {error}")
            return {}

        resolved = {}

        items = []
        if isinstance(result_payload, list):
            items = result_payload
        elif isinstance(result_payload, dict):
            if isinstance(result_payload.get("results"), list):
                items = result_payload.get("results", [])
            elif isinstance(result_payload.get("features"), list):
                items = result_payload.get("features", [])

        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue

            properties = item.get("properties") if isinstance(item.get("properties"), dict) else item
            lon = properties.get("lon")
            lat = properties.get("lat")
            if lon is None or lat is None:
                continue

            raw_query = None
            query_node = properties.get("query")
            if isinstance(query_node, dict):
                raw_query = query_node.get("text")
            if not raw_query and isinstance(item.get("query"), str):
                raw_query = item.get("query")

            # Keep the primary key as the original input value used by seed.
            input_location = unique_locations[index] if index < len(unique_locations) else None
            if not input_location:
                continue

            coordinates = {
                "longitude": float(lon),
                "latitude": float(lat),
            }

            resolved[input_location] = coordinates
            if raw_query:
                resolved[raw_query] = coordinates

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