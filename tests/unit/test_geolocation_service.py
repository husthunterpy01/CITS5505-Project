from unittest.mock import MagicMock, patch
from urllib.error import URLError

import pytest

from app.service.geolocationservice import GeoLocationService


class TestNormalizeText:
    def test_normalize_text_collapses_whitespace_and_lowercases(self):
        assert GeoLocationService._normalize_text("  Perth\t WA  ") == "perth wa"

    def test_normalize_text_none_yields_empty_string(self):
        assert GeoLocationService._normalize_text(None) == ""

    def test_normalize_text_empty_string(self):
        assert GeoLocationService._normalize_text("") == ""


class TestIsWesternAustraliaResult:
    def test_rejects_non_dict_payload(self):
        assert GeoLocationService._is_western_australia_result([]) is False

    def test_rejects_non_australia_country_code(self):
        payload = {"country_code": "NZ", "state": "Western Australia"}
        assert GeoLocationService._is_western_australia_result(payload) is False

    def test_accepts_australia_with_wa_state_name(self):
        payload = {"country_code": "AU", "state": "Western Australia"}
        assert GeoLocationService._is_western_australia_result(payload) is True

    def test_accepts_australia_with_wa_state_code(self):
        payload = {"country_code": "AU", "state_code": "WA"}
        assert GeoLocationService._is_western_australia_result(payload) is True

    def test_rejects_australia_without_wa_identifier(self):
        payload = {"country_code": "AU", "state": "Victoria"}
        assert GeoLocationService._is_western_australia_result(payload) is False


class TestNormalizeLocationResult:
    def test_returns_none_for_non_dict(self):
        assert GeoLocationService._normalize_location_result("x") is None

    def test_returns_none_when_coordinates_missing(self):
        payload = {"country_code": "AU", "state": "WA", "name": "Perth"}
        assert GeoLocationService._normalize_location_result(payload) is None

    def test_returns_none_when_outside_wa(self):
        payload = {
            "country_code": "AU",
            "state": "Victoria",
            "name": "Melbourne",
            "lon": 144.9631,
            "lat": -37.8136,
        }
        assert GeoLocationService._normalize_location_result(payload) is None

    def test_returns_expected_shape_for_wa_payload(self):
        payload = {
            "country_code": "AU",
            "state": "Western Australia",
            "name": "Fremantle",
            "lon": 115.7439,
            "lat": -32.0569,
        }
        out = GeoLocationService._normalize_location_result(payload)
        assert out == {
            "name": "Fremantle",
            "state": "Western Australia",
            "label": "Fremantle, Western Australia",
            "longitude": 115.7439,
            "latitude": -32.0569,
        }


class TestCalculateDistance:
    def test_same_coordinates_yield_zero_kilometers(self):
        d = GeoLocationService.calculate_distance(115.86, -31.95, 115.86, -31.95)
        assert d == pytest.approx(0.0, abs=1e-9)

    def test_distance_is_symmetric_in_point_order(self):
        lon1, lat1 = 115.7439, -32.0569
        lon2, lat2 = 115.8575, -31.9523
        assert GeoLocationService.calculate_distance(
            lon1, lat1, lon2, lat2
        ) == pytest.approx(
            GeoLocationService.calculate_distance(lon2, lat2, lon1, lat1),
            rel=1e-6,
        )

    def test_fremantle_to_perth_cbd_is_plausible_range_km(self):
        """Approximate sanity check for two known WA coordinates."""
        perth_lon, perth_lat = 115.8613, -31.9523
        freo_lon, freo_lat = 115.7439, -32.0569
        km = GeoLocationService.calculate_distance(perth_lon, perth_lat, freo_lon, freo_lat)
        assert 10.0 < km < 25.0


class TestSuggestWaLocations:
    def test_short_query_returns_empty_without_calling_api(self):
        with patch.object(GeoLocationService, "_request_json") as req:
            assert GeoLocationService.suggest_wa_locations("ab") == []
            req.assert_not_called()

    def test_missing_api_key_returns_empty(self, monkeypatch):
        monkeypatch.delenv("GEOAPIFY_API_KEY", raising=False)
        with patch.object(GeoLocationService, "_request_json") as req:
            assert GeoLocationService.suggest_wa_locations("Perth") == []
            req.assert_not_called()

    def test_network_error_returns_empty_list(self, monkeypatch):
        monkeypatch.setenv("GEOAPIFY_API_KEY", "test-key")
        with patch.object(
            GeoLocationService,
            "_request_json",
            side_effect=URLError("network"),
        ):
            assert GeoLocationService.suggest_wa_locations("Perth") == []

    def test_deduplicates_results_by_normalized_name(self, monkeypatch):
        monkeypatch.setenv("GEOAPIFY_API_KEY", "test-key")
        payload = {
            "results": [
                {
                    "country_code": "AU",
                    "state": "WA",
                    "name": "Perth",
                    "lon": 115.86,
                    "lat": -31.95,
                },
                {
                    "country_code": "AU",
                    "state": "WA",
                    "name": "Perth",
                    "lon": 115.87,
                    "lat": -31.96,
                },
            ]
        }
        with patch.object(GeoLocationService, "_request_json", return_value=payload):
            locs = GeoLocationService.suggest_wa_locations("Perth", limit=5)
        assert len(locs) == 1
        assert locs[0]["name"] == "Perth"

    def test_filters_out_non_wa_results(self, monkeypatch):
        monkeypatch.setenv("GEOAPIFY_API_KEY", "test-key")
        payload = {
            "results": [
                {
                    "country_code": "AU",
                    "state": "Victoria",
                    "name": "Melbourne",
                    "lon": 144.96,
                    "lat": -37.81,
                },
                {
                    "country_code": "AU",
                    "state": "WA",
                    "name": "Albany",
                    "lon": 117.88,
                    "lat": -34.93,
                },
            ]
        }
        with patch.object(GeoLocationService, "_request_json", return_value=payload):
            locs = GeoLocationService.suggest_wa_locations("alb", limit=5)
        assert [x["name"] for x in locs] == ["Albany"]


class TestResolveWaLocation:
    def test_empty_query_returns_none(self):
        assert GeoLocationService.resolve_wa_location("   ") is None

    def test_exact_name_match_prefers_matching_suggestion(self, monkeypatch):
        monkeypatch.setenv("GEOAPIFY_API_KEY", "x")
        suggestions = [
            {
                "name": "Albany",
                "state": "Western Australia",
                "label": "Albany, Western Australia",
                "longitude": 117.88,
                "latitude": -34.93,
            },
            {
                "name": "Perth",
                "state": "Western Australia",
                "label": "Perth, Western Australia",
                "longitude": 115.86,
                "latitude": -31.95,
            },
        ]
        with patch.object(
            GeoLocationService,
            "suggest_wa_locations",
            return_value=suggestions,
        ):
            pick = GeoLocationService.resolve_wa_location("Perth")
        assert pick["name"] == "Perth"

    def test_falls_back_to_first_suggestion_when_no_partial_match(self, monkeypatch):
        monkeypatch.setenv("GEOAPIFY_API_KEY", "x")
        first = {
            "name": "Albany",
            "state": "Western Australia",
            "label": "Albany, Western Australia",
            "longitude": 117.88,
            "latitude": -34.93,
        }
        with patch.object(
            GeoLocationService,
            "suggest_wa_locations",
            return_value=[first],
        ):
            pick = GeoLocationService.resolve_wa_location("Unknown Place XYZ")
        assert pick is first


class TestGeocodeBatch:
    def test_empty_and_none_inputs_return_empty_dict(self):
        assert GeoLocationService.geocode_batch(None) == {}
        assert GeoLocationService.geocode_batch([]) == {}

    def test_skips_blank_strings_and_deduplicates(self):
        with patch.object(
            GeoLocationService,
            "resolve_wa_location",
            return_value={
                "name": "Perth",
                "longitude": 115.86,
                "latitude": -31.95,
            },
        ) as resolve:
            out = GeoLocationService.geocode_batch(["", "  Perth ", "Perth"])
        resolve.assert_called()
        assert out["Perth"] == {"longitude": 115.86, "latitude": -31.95}

    def test_unresolved_location_is_omitted(self):
        with patch.object(GeoLocationService, "resolve_wa_location", return_value=None):
            assert GeoLocationService.geocode_batch(["Nowhere"]) == {}


class TestRequestJson:
    def test_parses_json_from_mock_response(self):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"ok": true}'
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_resp
        mock_cm.__exit__.return_value = False

        with patch("app.service.geolocationservice.urlopen", return_value=mock_cm):
            data = GeoLocationService._request_json("http://example.test/x")
        assert data == {"ok": True}
