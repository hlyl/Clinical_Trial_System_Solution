import pytest


@pytest.mark.asyncio
async def test_vendor_crud_flow(client, unique_code):
    vendor_code = f"TEST_VENDOR_{unique_code.upper()}"

    create_payload = {
        "vendor_code": vendor_code,
        "vendor_name": "Test Vendor",
        "vendor_type": "CRO",
        "contact_name": "QA Owner",
        "contact_email": "qa@example.com",
    }

    create_response = await client.post("/api/v1/vendors", json=create_payload)
    if create_response.status_code != 201:
        print(f"Response body: {create_response.text}")
    assert create_response.status_code == 201, f"Expected 201, got {create_response.status_code}: {create_response.text}"
    created = create_response.json()

    vendor_id = created["vendor_id"]
    assert created["vendor_code"] == vendor_code
    assert created["vendor_name"] == "Test Vendor"
    assert created["is_active"] is True

    detail_response = await client.get(f"/api/v1/vendors/{vendor_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["vendor_id"] == vendor_id
    assert detail["vendor_type"] == "CRO"

    update_response = await client.put(
        f"/api/v1/vendors/{vendor_id}",
        json={"vendor_name": "Updated Vendor", "is_active": False},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["vendor_name"] == "Updated Vendor"
    assert updated["is_active"] is False

    conflict_response = await client.post("/api/v1/vendors", json=create_payload)
    assert conflict_response.status_code == 409
    conflict_body = conflict_response.json()
    assert conflict_body["error"] == "CONFLICT"

    list_response = await client.get("/api/v1/vendors?limit=5&offset=0")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert "data" in listed and "meta" in listed
    assert listed["meta"]["limit"] == 5
