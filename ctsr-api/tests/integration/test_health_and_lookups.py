import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["database"] == "connected"
    assert "timestamp" in payload


@pytest.mark.asyncio
async def test_lookups_endpoint(client):
    response = await client.get("/api/v1/lookups")
    assert response.status_code == 200

    payload = response.json()
    categories = payload.get("system_categories", [])
    validation_statuses = payload.get("validation_statuses", [])

    assert categories, "Expected system categories in lookups response"
    assert any(cat["category_code"] == "EDC" for cat in categories)

    assert validation_statuses, "Expected validation statuses in lookups response"
    assert any(status["status_code"] == "VALIDATED" for status in validation_statuses)

    assert "CRO" in payload.get("vendor_types", [])
    assert payload.get("data_hosting_regions")
