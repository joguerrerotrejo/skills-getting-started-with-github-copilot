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


def test_root_redirect():
    # Arrange
    follow_redirects = False

    # Act
    response = client.get("/", follow_redirects=follow_redirects)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert expected_activity in activities
    assert activities[expected_activity]["description"] == "Learn strategies and compete in chess tournaments"
    assert activities[expected_activity]["max_participants"] == 12
    assert "michael@mergington.edu" in activities[expected_activity]["participants"]


def test_signup_participant_success():
    # Arrange
    activity_name = "Chess Club"
    email = "new_student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_participant_already_registered():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_activity_not_found():
    # Arrange
    activity_name = "Unknown Club"
    email = "new_student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_success():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_participant_not_found():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()


def test_unregister_activity_not_found():
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_via_post():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post("/activities/unregister", params={"activity_name": activity_name, "email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]
