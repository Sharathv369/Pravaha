"""Comprehensive automated test suite for the PRAVAHA FastAPI backend."""

import math
import unittest
import pandas as pd
from starlette.testclient import TestClient

from src.api.main import app
from src.api import config


class TestPravahaAPI(unittest.TestCase):
    """Test cases covering all endpoints, data integrity, and error conditions."""

    @classmethod
    def setUpClass(cls):
        """Instantiate the test client once for the suite."""
        cls.client = TestClient(app)

    # -----------------------------------------------------------------------
    # Helper assertion methods
    # -----------------------------------------------------------------------
    def assert_no_nan_or_inf(self, obj, path=""):
        """Recursively assert that a JSON structure contains no NaN or Infinity floats."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                self.assert_no_nan_or_inf(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                self.assert_no_nan_or_inf(item, f"{path}[{idx}]")
        elif isinstance(obj, float):
            self.assertFalse(math.isnan(obj), f"Found NaN float at {path}")
            self.assertFalse(math.isinf(obj), f"Found Inf float at {path}")

    # -----------------------------------------------------------------------
    # 1. Health Endpoint Tests
    # -----------------------------------------------------------------------
    def test_health_endpoint_healthy(self):
        """Test GET /health returns HTTP 200, status 'healthy', and complete dataset breakdown."""
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assert_no_nan_or_inf(data)

        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["api_title"], "PRAVAHA API")
        self.assertEqual(data["api_version"], "1.0.0")
        self.assertTrue(data["backend_ready"])
        self.assertEqual(data["verified_station_count"], 38)
        self.assertEqual(data["validation_sample_count"], 24088)

        datasets = data["datasets"]
        self.assertTrue(datasets["train_labelled"])
        self.assertTrue(datasets["station_catalog"])
        self.assertTrue(datasets["river_system_grouping"])
        self.assertTrue(datasets["catchment_provenance"])
        self.assertTrue(datasets["lorso_predictions"])
        self.assertTrue(datasets["lorso_results"])

    def test_root_endpoint(self):
        """Test GET / returns API metadata and documentation links."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["title"], "PRAVAHA API")
        self.assertIn("/health", data["endpoints"])
        self.assertIn("/api/stations", data["endpoints"])

    # -----------------------------------------------------------------------
    # 2. Station Endpoints Tests
    # -----------------------------------------------------------------------
    def test_list_stations_all(self):
        """Test GET /api/stations returns all 38 verified candidate stations."""
        res = self.client.get("/api/stations")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assert_no_nan_or_inf(data)

        self.assertEqual(data["total_count"], 38)
        self.assertEqual(data["filtered_count"], 38)
        self.assertEqual(len(data["stations"]), 38)

        # Verify leading zero retention on every station ID string
        for st in data["stations"]:
            self.assertIsInstance(st["station_id"], str)
            self.assertGreaterEqual(len(st["station_id"]), 8)
            self.assertTrue(st["station_id"].isdigit())

    def test_search_station_by_id_and_name(self):
        """Test searching stations by partial station ID and river name."""
        # Search by partial ID
        res_id = self.client.get("/api/stations?search=01646500")
        self.assertEqual(res_id.status_code, 200)
        data_id = res_id.json()
        self.assertEqual(data_id["filtered_count"], 1)
        self.assertEqual(data_id["stations"][0]["station_id"], "01646500")

        # Search by river name
        res_name = self.client.get("/api/stations?search=potomac")
        self.assertEqual(res_name.status_code, 200)
        data_name = res_name.json()
        self.assertGreaterEqual(data_name["filtered_count"], 1)
        self.assertTrue(any("POTOMAC" in s["station_name"] for s in data_name["stations"]))

    def test_filter_by_river_system(self):
        """Test filtering stations by river system grouping."""
        res = self.client.get("/api/stations?river_system=Potomac%20River")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["filtered_count"], 1)
        self.assertEqual(data["stations"][0]["station_id"], "01646500")

    def test_station_pagination(self):
        """Test limit and offset pagination parameters."""
        res = self.client.get("/api/stations?limit=5&offset=0")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["stations"]), 5)
        self.assertEqual(data["total_count"], 38)

    def test_get_station_detail_success(self):
        """Test GET /api/stations/{station_id} for a verified core station."""
        res = self.client.get("/api/stations/01646500")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assert_no_nan_or_inf(data)

        self.assertEqual(data["station_id"], "01646500")
        self.assertEqual(data["state"], "MD")
        self.assertEqual(data["state_cd"], 24)
        self.assertAlmostEqual(data["drainage_area_sqmi"], 11564.57, places=2)
        self.assertEqual(data["drainage_area_verification_status"], "VERIFIED")
        self.assertEqual(data["data_quality_status"], "VERIFIED_BENCHMARK_READY")
        self.assertTrue(data["has_validation_predictions"])

        # Check flow percentiles
        thresholds = data["flow_thresholds_cfs"]
        self.assertEqual(thresholds["q50_median_cfs"], 7240.0)
        self.assertEqual(thresholds["q90_threshold_cfs"], 25500.0)
        self.assertEqual(thresholds["max_recorded_cfs"], 192000.0)

    def test_get_station_detail_leading_zero_normalization(self):
        """Test that 7-digit ID '1646500' normalizes to '01646500'."""
        res = self.client.get("/api/stations/1646500")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["station_id"], "01646500")

    def test_get_station_detail_not_found(self):
        """Test GET /api/stations/{station_id} for an unknown station returns HTTP 404."""
        res = self.client.get("/api/stations/99999999")
        self.assertEqual(res.status_code, 404)
        self.assertIn("was not found", res.json()["detail"])

    # -----------------------------------------------------------------------
    # 3. Hydrograph Endpoint Tests
    # -----------------------------------------------------------------------
    def test_hydrograph_date_range(self):
        """Test hydrograph retrieval with valid ISO 8601 date range."""
        res = self.client.get(
            "/api/stations/01646500/hydrograph?start_date=2022-01-01&end_date=2022-01-05"
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assert_no_nan_or_inf(data)

        self.assertEqual(data["station_id"], "01646500")
        self.assertEqual(data["total_points"], 5)
        self.assertEqual(data["start_date"], "2022-01-01")
        self.assertEqual(data["end_date"], "2022-01-05")

        # Verify point structure
        for pt in data["data"]:
            self.assertEqual(pt["station_id"], "01646500")
            self.assertIsNotNone(pt["actual_discharge_cfs"])
            self.assertIsNotNone(pt["predicted_discharge_cfs"])
            self.assertEqual(pt["prediction_model"], "LightGBM Log-Specific Discharge")
            self.assertEqual(pt["validation_type"], "LORSO_HOLDOUT")
            self.assertEqual(pt["data_status"], "OBSERVED_AND_VALIDATED")
            self.assertEqual(pt["data_source"], "USGS_NWIS_DAILY_MEAN_00060_00003")

    def test_hydrograph_pre_validation_period_null_prediction(self):
        """Test that dates prior to 2022 have null predicted discharge."""
        res = self.client.get(
            "/api/stations/01646500/hydrograph?start_date=2015-06-01&end_date=2015-06-03"
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_points"], 3)

        for pt in data["data"]:
            self.assertIsNotNone(pt["actual_discharge_cfs"])
            self.assertIsNone(pt["predicted_discharge_cfs"])
            self.assertIsNone(pt["prediction_model"])
            self.assertIsNone(pt["validation_type"])
            self.assertEqual(pt["data_status"], "OBSERVED_HISTORICAL")

    def test_hydrograph_model_selection(self):
        """Test selecting alternative model formulations ('raw', 'spec_q', 'log1p')."""
        # Test spec_q
        res_spec = self.client.get(
            "/api/stations/01646500/hydrograph?start_date=2022-01-01&end_date=2022-01-02&model_name=spec_q"
        )
        self.assertEqual(res_spec.status_code, 200)
        self.assertEqual(res_spec.json()["model_name"], "LightGBM Specific Discharge")
        self.assertEqual(res_spec.json()["target_formulation"], "spec_q")

        # Test log1p
        res_log1p = self.client.get(
            "/api/stations/01646500/hydrograph?start_date=2022-01-01&end_date=2022-01-02&model_name=log1p"
        )
        self.assertEqual(res_log1p.status_code, 200)
        self.assertEqual(res_log1p.json()["model_name"], "XGBoost Log1p")

    def test_hydrograph_invalid_date_range(self):
        """Test that start_date > end_date returns HTTP 400."""
        res = self.client.get(
            "/api/stations/01646500/hydrograph?start_date=2023-01-01&end_date=2022-01-01"
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("must be earlier than or equal to", res.json()["detail"])

    def test_hydrograph_malformed_date(self):
        """Test that an invalid date format returns HTTP 400."""
        res = self.client.get(
            "/api/stations/01646500/hydrograph?start_date=invalid-date"
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid date format", res.json()["detail"])

    def test_hydrograph_unknown_station(self):
        """Test hydrograph request for unknown station returns HTTP 404."""
        res = self.client.get("/api/stations/99999999/hydrograph")
        self.assertEqual(res.status_code, 404)

    def test_hydrograph_unknown_model(self):
        """Test hydrograph request with unknown model formulation returns HTTP 400."""
        res = self.client.get(
            "/api/stations/01646500/hydrograph?model_name=non_existent_neural_network"
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Unknown model identifier", res.json()["detail"])

    # -----------------------------------------------------------------------
    # 4. Validation Leaderboard Tests
    # -----------------------------------------------------------------------
    def test_validation_leaderboard(self):
        """Test GET /api/validation/leaderboard returns the 5 official models ranked by pooled R²."""
        res = self.client.get("/api/validation/leaderboard")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assert_no_nan_or_inf(data)

        self.assertEqual(data["total_models"], 5)
        self.assertEqual(data["total_validation_rows"], 24088)

        models = data["models"]
        # Top model must be LightGBM Log-Specific Discharge
        self.assertEqual(models[0]["model_name"], "LightGBM Log-Specific Discharge")
        self.assertEqual(models[0]["target_formulation"], "log_spec_q")
        self.assertAlmostEqual(models[0]["pooled_r2"], 0.4910, places=3)
        self.assertAlmostEqual(models[0]["overall_rmse_cfs"], 82871.13, places=1)
        self.assertAlmostEqual(models[0]["peak_rmse_cfs"], 156593.84, places=1)
        self.assertAlmostEqual(models[0]["overall_mae_cfs"], 24644.29, places=1)
        self.assertEqual(models[0]["validation_sample_count"], 24088)
        self.assertEqual(models[0]["peak_sample_count"], 2423)
        self.assertEqual(models[0]["rank_by_pooled_r2"], 1)

        # Check rankings are strictly monotonic descending by pooled_r2
        for i in range(len(models) - 1):
            self.assertGreaterEqual(models[i]["pooled_r2"], models[i + 1]["pooled_r2"])
            self.assertEqual(models[i]["rank_by_pooled_r2"], i + 1)

    # -----------------------------------------------------------------------
    # 5. River-System Analytics Tests
    # -----------------------------------------------------------------------
    def test_river_systems_analytics(self):
        """Test GET /api/validation/river-systems returns all 23 river systems."""
        res = self.client.get("/api/validation/river-systems")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assert_no_nan_or_inf(data)

        self.assertEqual(data["total_river_systems"], 23)
        self.assertEqual(len(data["river_systems"]), 23)

        # Check California Central Valley System (has 2 stations: 11447650 and 11303500)
        ccv = next(s for s in data["river_systems"] if s["river_system"] == "California Central Valley System")
        self.assertEqual(ccv["station_count"], 2)
        self.assertIn("11447650", ccv["held_out_station_ids"])
        self.assertIn("11303500", ccv["held_out_station_ids"])
        self.assertEqual(ccv["validation_sample_count"], 730)
        self.assertEqual(ccv["validation_status"], "EVALUATED_HOLDOUT")

    # -----------------------------------------------------------------------
    # 6. Catchment Profile Tests
    # -----------------------------------------------------------------------
    def test_catchment_profile_verified_station(self):
        """Test GET /api/stations/{station_id}/catchment-profile for a 100% verified GAGES-II station."""
        res = self.client.get("/api/stations/01646500/catchment-profile")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assert_no_nan_or_inf(data)

        self.assertEqual(data["station_id"], "01646500")
        self.assertEqual(data["overall_catchment_verification"], "VERIFIED_BENCHMARK_READY")

        # All 4 attributes verified
        da = data["drainage_area_sqmi"]
        self.assertEqual(da["verification_status"], "VERIFIED")
        self.assertAlmostEqual(da["value"], 11564.57, places=2)

        elev = data["mean_elevation_ft"]
        self.assertEqual(elev["verification_status"], "VERIFIED")
        self.assertAlmostEqual(elev["value"], 1269.03, places=2)

        slope = data["slope_pct"]
        self.assertEqual(slope["verification_status"], "VERIFIED")
        self.assertAlmostEqual(slope["value"], 11.70, places=2)

        forest = data["forest_cover_pct"]
        self.assertEqual(forest["verification_status"], "VERIFIED")
        self.assertAlmostEqual(forest["value"], 58.58, places=2)

        self.assertIn("Demonstrated spatial holdout skill", data["model_limitation_indicator"])

    def test_catchment_profile_unverified_attributes(self):
        """Test catchment profile for station with missing StreamStats elevation/slope/forest."""
        res = self.client.get("/api/stations/07010000/catchment-profile")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assert_no_nan_or_inf(data)

        self.assertEqual(data["station_id"], "07010000")
        self.assertEqual(data["overall_catchment_verification"], "VERIFIED_REQUIRES_STREAMSTATS")

        # Drainage area is verified
        self.assertEqual(data["drainage_area_sqmi"]["verification_status"], "VERIFIED")
        self.assertAlmostEqual(data["drainage_area_sqmi"]["value"], 697000.0, places=1)

        # Elevation is unverified
        self.assertEqual(data["mean_elevation_ft"]["verification_status"], "MISSING_OR_UNVERIFIED")
        self.assertIsNone(data["mean_elevation_ft"]["value"])
        self.assertIn("StreamStats lacks mean basin elevation", data["mean_elevation_ft"]["explanation"])

    def test_catchment_profile_regulated_limitation(self):
        """Test that regulated station 08158000 receives explicit reservoir regulation limitation notice."""
        res = self.client.get("/api/stations/08158000/catchment-profile")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("controlled by upstream reservoir releases", data["model_limitation_indicator"])

    def test_catchment_profile_truncated_record_limitation(self):
        """Test that station 11447650 receives zero 2022-2023 holdout sample limitation notice."""
        res = self.client.get("/api/stations/11447650/catchment-profile")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("ended on 2015-09-30", data["model_limitation_indicator"])
        self.assertIn("zero validation samples", data["model_limitation_indicator"])

    # -----------------------------------------------------------------------
    # 7. Ground Truth Data Authenticity Comparison Tests
    # -----------------------------------------------------------------------
    def test_hydrograph_matches_raw_csv_record(self):
        """Verify that hydrograph returned value matches exact value in PRAVAHA_TRAIN_LABELLED.csv."""
        res = self.client.get(
            "/api/stations/01646500/hydrograph?start_date=2010-01-01&end_date=2010-01-01"
        )
        self.assertEqual(res.status_code, 200)
        api_val = res.json()["data"][0]["actual_discharge_cfs"]

        # Read directly from raw CSV line 2
        df_raw = pd.read_csv(
            config.TRAIN_LABELLED_CSV,
            dtype={"station_id": str},
            nrows=2,
        )
        raw_val = float(df_raw.iloc[0]["discharge_cfs"])
        self.assertEqual(api_val, raw_val)
        self.assertEqual(api_val, 22100.0)

    def test_validation_leaderboard_matches_source_csv(self):
        """Verify leaderboard metrics match exact recorded values in lors_validation_results.csv."""
        res = self.client.get("/api/validation/leaderboard")
        self.assertEqual(res.status_code, 200)
        api_top = res.json()["models"][0]

        df_lvr = pd.read_csv(config.LORSO_VALIDATION_RESULTS_CSV)
        source_row = df_lvr[df_lvr["target_formulation"] == "log_spec_q"].iloc[0]

        self.assertEqual(api_top["model_name"], source_row["model_name"])
        self.assertAlmostEqual(api_top["overall_rmse_cfs"], float(source_row["pooled_rmse"]), places=2)
        self.assertAlmostEqual(api_top["peak_rmse_cfs"], float(source_row["pooled_rmse_top10"]), places=2)
        self.assertAlmostEqual(api_top["overall_mae_cfs"], float(source_row["pooled_mae"]), places=2)
        self.assertAlmostEqual(api_top["pooled_r2"], float(source_row["pooled_r2"]), places=5)

    def test_missing_artifact_diagnostic_reporting(self):
        """Verify health check accurately detects when an artifact is missing."""
        from unittest.mock import patch
        from pathlib import Path

        with patch("src.api.config.LORSO_PREDICTIONS_PARQUET", Path("non_existent_file.parquet")):
            res = self.client.get("/health")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertFalse(data["datasets"]["lorso_predictions"])
            self.assertEqual(data["status"], "degraded")


if __name__ == "__main__":
    unittest.main()
