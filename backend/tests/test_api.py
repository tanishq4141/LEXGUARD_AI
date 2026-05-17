import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint returns 200 OK and expected status."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_get_sample_contract():
    """Test the sample contract endpoint returns text."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/sample-contract")
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert len(data["text"]) > 100
    assert "INDEPENDENT CONTRACTOR AGREEMENT" in data["text"]
