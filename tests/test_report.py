from fastapi.testclient import TestClient
from backend.main import app
import unittest
import os

class TestReport(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_generate_report(self):
        # Mock data for report
        payload = {
            "sensor_id": "TEST-REPORT-SENSOR",
            "health_score": 88.5,
            "status": "Green",
            "metrics": {
                "bias": 0.01,
                "slope": 0.0002,
                "noise_std": 0.15,
                "snr_db": 25.0,
                "hysteresis": 0.05,
                "hurst": 0.65,
                "hurst_r2": 0.95
            },
            "diagnosis": "System operating normally.",
            "flags": [],
            "recommendation": "No action needed.",
            "data": [10.0, 10.1, 10.2, 10.1, 10.0] * 10 # Dummy data for chart
        }
        
        response = self.client.post("/report", json=payload)
        
        # Check success
        if response.status_code != 200:
            print(f"Error Response: {response.json()}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        
        # Check if content looks like PDF header
        self.assertTrue(response.content.startswith(b"%PDF"))
        
        # Optional: Save to inspect manually
        # with open("test_report.pdf", "wb") as f:
        #     f.write(response.content)

if __name__ == '__main__':
    unittest.main()
