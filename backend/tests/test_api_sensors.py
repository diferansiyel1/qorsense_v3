"""
Sensor API Endpoint Tests

Tests for sensor CRUD operations and data ingestion.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_sensor(client: AsyncClient):
    """Test creating a new sensor."""
    sensor_data = {
        "name": "Test Sensor",
        "location": "Lab A",
        "source_type": "CSV",
        "organization_id": 1
    }
    
    response = await client.post("/sensors", json=sensor_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sensor_data["name"]
    assert data["location"] == sensor_data["location"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_sensors_empty(client: AsyncClient):
    """Test getting sensors when none exist."""
    response = await client.get("/sensors")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_get_sensors(client: AsyncClient):
    """Test getting all sensors."""
    # Create a sensor first
    sensor_data = {
        "name": "Test Sensor",
        "location": "Lab A",
        "source_type": "CSV"
    }
    await client.post("/sensors", json=sensor_data)
    
    # Get all sensors
    response = await client.get("/sensors")
    assert response.status_code == 200
    data = response.json()
    sensors = data["items"]
    assert len(sensors) >= 1
    assert sensors[0]["name"] == sensor_data["name"]
    assert data["page"] == 1
    assert data["size"] == 20


@pytest.mark.asyncio
async def test_stream_data(client: AsyncClient):
    """Test streaming a single data point."""
    # Create a sensor first
    sensor_data = {
        "name": "Test Sensor",
        "location": "Lab A",
        "source_type": "IoT"
    }
    create_response = await client.post("/sensors", json=sensor_data)
    sensor_id = create_response.json()["id"]
    
    # Stream data point
    stream_data = {
        "sensor_id": sensor_id,
        "value": 42.5
    }
    
    response = await client.post("/sensors/stream-data", json=stream_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"
    assert data["sensor_id"] == sensor_id
