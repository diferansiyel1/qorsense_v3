"""
Analytics API Endpoint Tests

Tests for analysis endpoint functionality.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analyze_with_values(client: AsyncClient, sample_readings):
    """Test analysis with provided values."""
    analysis_request = {
        "sensor_id": "TEST001",
        "sensor_type": "Bio",
        "values": sample_readings[:50]  # Use first 50 points
    }
    
    response = await client.post("/analyze", json=analysis_request)
    assert response.status_code == 200
    
    data = response.json()
    assert data["sensor_id"] == "TEST001"
    assert "health_score" in data
    assert "status" in data
    assert "metrics" in data
    assert "diagnosis" in data
    assert "recommendation" in data
    
    # Check metrics
    metrics = data["metrics"]
    assert "bias" in metrics
    assert "slope" in metrics
    assert "snr_db" in metrics
    assert "hurst" in metrics


@pytest.mark.asyncio
async def test_analyze_insufficient_data(client: AsyncClient):
    """Test analysis with insufficient data."""
    analysis_request = {
        "sensor_id": "TEST001",
        "sensor_type": "Bio",
        "values": [1.0, 2.0, 3.0]  # Only 3 points
    }
    
    response = await client.post("/analyze", json=analysis_request)
    # Should still return 200 but with "No Data" status
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "No Data"


@pytest.mark.asyncio
async def test_synthetic_generation(client: AsyncClient):
    """Test synthetic data generation."""
    request = {
        "type": "Normal",
        "length": 100
    }
    
    response = await client.post("/synthetic/generate", json=request)
    assert response.status_code == 200
    
    data = response.json()
    assert "data" in data
    assert "timestamps" in data
    assert len(data["data"]) == 100
    assert len(data["timestamps"]) == 100


@pytest.mark.asyncio
async def test_synthetic_generation_types(client: AsyncClient):
    """Test different synthetic data types."""
    types = ["Normal", "Drifting", "Noisy", "Oscillation"]
    
    for signal_type in types:
        request = {
            "type": signal_type,
            "length": 50
        }
        
        response = await client.post("/synthetic/generate", json=request)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == signal_type
        assert len(data["data"]) == 50
