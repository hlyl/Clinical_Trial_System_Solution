import pytest
from datetime import date


@pytest.mark.asyncio
async def test_system_trial_confirmation_flow(client, unique_code):
    vendor_code = f"TEST_SYS_VENDOR_{unique_code.upper()}"
    system_code = f"SYS_{unique_code.upper()}"
    protocol_number = f"PROT-{unique_code}".upper()

    vendor_resp = await client.post(
        "/api/v1/vendors",
        json={
            "vendor_code": vendor_code,
            "vendor_name": "Systems Vendor",
            "vendor_type": "TECH_VENDOR",
            "contact_email": "sys@example.com",
        },
    )
    assert vendor_resp.status_code == 201
    vendor_id = vendor_resp.json()["vendor_id"]

    system_resp = await client.post(
        "/api/v1/systems",
        json={
            "instance_code": system_code,
            "platform_vendor_id": vendor_id,
            "category_code": "EDC",
            "platform_name": "Validation Platform",
            "platform_version": "1.0",
            "instance_name": "Test Instance",
            "instance_environment": "PRODUCTION",
            "validation_status_code": "VALIDATED",
            "hosting_model": "SAAS",
            "data_hosting_region": "US",
            "description": "Integration test system",
        },
    )
    assert system_resp.status_code == 201
    system_body = system_resp.json()
    instance_id = system_body["instance_id"]

    trial_resp = await client.post(
        "/api/v1/trials",
        json={
            "protocol_number": protocol_number,
            "trial_title": "Integration Trial",
            "trial_phase": "PHASE_2",
            "trial_status": "ACTIVE",
            "therapeutic_area": "ONCOLOGY",
            "trial_start_date": str(date.today()),
        },
    )
    assert trial_resp.status_code == 201
    trial_id = trial_resp.json()["trial_id"]

    link_resp = await client.post(
        f"/api/v1/trials/{trial_id}/systems",
        json={
            "instance_id": instance_id,
            "criticality_code": "CRIT",
            "usage_start_date": str(date.today()),
        },
    )
    assert link_resp.status_code == 201
    link_body = link_resp.json()
    assert link_body["trial_id"] == trial_id
    assert link_body["instance_id"] == instance_id

    detail_resp = await client.get(f"/api/v1/trials/{trial_id}")
    assert detail_resp.status_code == 200
    trial_detail = detail_resp.json()
    assert any(ls["instance_id"] == instance_id for ls in trial_detail.get("linked_systems", []))

    confirmation_resp = await client.post(
        "/api/v1/confirmations",
        json={
            "trial_id": trial_id,
            "confirmation_type": "PERIODIC",
            "due_date": str(date.today()),
        },
    )
    assert confirmation_resp.status_code == 201
    confirmation_id = confirmation_resp.json()["confirmation_id"]

    submit_resp = await client.post(
        f"/api/v1/confirmations/{confirmation_id}/submit",
        json={"capture_snapshots": True, "notes": "Submitted via test"},
    )
    assert submit_resp.status_code == 200
    submit_body = submit_resp.json()
    assert submit_body["confirmation_status"] == "COMPLETED"
    assert submit_body["validation_alerts_count"] == 0

    detail_conf_resp = await client.get(f"/api/v1/confirmations/{confirmation_id}")
    assert detail_conf_resp.status_code == 200
    detail_conf = detail_conf_resp.json()
    assert detail_conf["confirmation_status"] == "COMPLETED"
    snapshots = detail_conf.get("snapshots", [])
    assert snapshots, "Expected at least one snapshot after submission"
    assert snapshots[0]["instance_id"] == instance_id
