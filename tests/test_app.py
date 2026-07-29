from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_activities)


client = TestClient(app_module.app)


def test_unregister_participant_success():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_participant_not_found():
    response = client.delete("/activities/Chess Club/signup", params={"email": "missing@mergington.edu"})

    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()


def test_unregister_participant_via_post():
    response = client.post("/activities/unregister", params={"activity_name": "Chess Club", "email": "michael@mergington.edu"})

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
