"""
Automated Test Suite for Fault & Alarm Analytics Web Application.
"""

import unittest
from app.database.alarm_analytics_repo import get_alarm_logs, get_alarm_stats, export_alarm_csv
from app.web.server import app


class TestWebAnalytics(unittest.TestCase):
    """Test suite for analytics repository and Flask REST endpoints."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_01_repo_stats(self):
        """Verify analytics repository computes stats successfully."""
        stats = get_alarm_stats()
        self.assertIn("total_alarms", stats)
        self.assertIn("today_alarms", stats)
        self.assertIn("current_shift_alarms", stats)
        self.assertIn("station_distribution", stats)
        self.assertIn("top_alarms", stats)
        self.assertIn("timeline", stats)
        self.assertIsInstance(stats["station_distribution"], dict)
        self.assertIn("Press 1", stats["station_distribution"])

    def test_02_repo_logs_filter(self):
        """Verify filtering alarm logs by shift and limit."""
        logs, total = get_alarm_logs(limit=10, offset=0)
        self.assertIsInstance(logs, list)
        self.assertIsInstance(total, int)
        if logs:
            first = logs[0]
            self.assertIn("id", first)
            self.assertIn("timestamp", first)
            self.assertIn("alarm", first)
            self.assertIn("station", first)

    def test_03_flask_index_route(self):
        """Verify GET / returns 200 and contains analytics title."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        content = res.get_data(as_text=True)
        self.assertIn("FAULT &amp; ALARM ANALYTICS", content)
        self.assertIn("alarmsTable", content)

    def test_04_flask_api_alarms(self):
        """Verify GET /api/alarms returns JSON list."""
        res = self.client.get("/api/alarms?limit=5")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("records", data)
        self.assertIn("total", data)

    def test_05_flask_api_stats(self):
        """Verify GET /api/alarms/stats returns JSON analytics."""
        res = self.client.get("/api/alarms/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("stats", data)
        self.assertIn("total_alarms", data["stats"])

    def test_06_flask_api_export(self):
        """Verify GET /api/alarms/export returns CSV content."""
        res = self.client.get("/api/alarms/export")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.headers.get("Content-Type", ""))
        self.assertIn("attachment", res.headers.get("Content-Disposition", ""))
        csv_text = res.get_data(as_text=True)
        self.assertIn("ID,Timestamp,Station,Alarm", csv_text)

    def test_07_flask_api_health(self):
        """Verify GET /api/health reports SQL status."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("sql_connected", data)
        self.assertIn("sql_server", data)

    def test_08_flask_api_io_latest(self):
        """Verify GET /api/io/latest returns appropriate response."""
        res = self.client.get("/api/io/latest")
        self.assertIn(res.status_code, [200, 404])
        data = res.get_json()
        self.assertIn("success", data)

    def test_09_flask_api_config_get(self):
        """Verify GET /api/config returns active configuration dictionary."""
        res = self.client.get("/api/config")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("config", data)
        self.assertIn("plc_ip", data["config"])
        self.assertIn("sql_server", data["config"])
        self.assertIn("machine_id", data["config"])

    def test_10_flask_api_config_save(self):
        """Verify POST /api/config saves settings and returns updated config."""
        payload = {
            "plc_ip": "192.168.50.11",
            "sql_server": r"localhost\SQLEXPRESS",
            "sql_database": "HydraulicMachineDB"
        }
        res = self.client.post("/api/config", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["config"]["plc_ip"], "192.168.50.11")

    def test_11_flask_api_test_sql(self):
        """Verify POST /api/config/test-sql can validate connection."""
        payload = {
            "sql_server": r"localhost\SQLEXPRESS",
            "sql_database": "HydraulicMachineDB",
            "sql_trusted_connection": True
        }
        res = self.client.post("/api/config/test-sql", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("connected successfully", data["message"].lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)

