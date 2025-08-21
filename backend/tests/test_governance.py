from fastapi.testclient import TestClient
from app.main import app


def test_governance_proposals_crud(client: TestClient):
    # list should return 200 and a list
    resp = client.get("/governance/proposals")
    assert resp.status_code == 200
    initial = resp.json()
    assert isinstance(initial, list)

    # create a proposal
    create_payload = {"title": "Test Proposal", "description": "desc"}
    resp = client.post("/governance/proposals", json=create_payload)
    assert resp.status_code == 201
    created = resp.json()
    assert created["title"] == "Test Proposal"
    proposal_id = created["id"]

    # list should now include the item
    resp = client.get("/governance/proposals")
    assert resp.status_code == 200
    items = resp.json()
    assert any(p["id"] == proposal_id for p in items)

    # close the proposal
    resp = client.post(f"/governance/proposals/{proposal_id}/close", params={"outcome": "passed"})
    assert resp.status_code == 200
    closed = resp.json()
    assert closed["status"] == "passed"
