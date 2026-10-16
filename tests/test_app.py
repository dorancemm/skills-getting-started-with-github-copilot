import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def api(monkeypatch):
    activity_data = {
        "Chess Club": {
            "description": "Learn chess",
            "schedule": "Fridays",
            "max_participants": 2,
            "participants": ["existing@example.com"],
        },
        "Art Club": {
            "description": "Make art",
            "schedule": "Wednesdays",
            "max_participants": 3,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", activity_data)
    return TestClient(app_module.app), activity_data


def test_get_activities_returns_all_activities(api):
    # Arrange
    client, activity_data = api

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activity_data


def test_signup_adds_participant(api):
    # Arrange
    client, activity_data = api
    email = "new@example.com"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activity_data["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(api):
    # Arrange
    client, activity_data = api
    participants_before = activity_data["Chess Club"]["participants"].copy()

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "existing@example.com"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activity_data["Chess Club"]["participants"] == participants_before


def test_signup_returns_404_for_unknown_activity(api):
    # Arrange
    client, _ = api

    # Act
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "new@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(api):
    # Arrange
    client, activity_data = api

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "existing@example.com"},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered existing@example.com from Chess Club"
    }
    assert activity_data["Chess Club"]["participants"] == []


def test_unregister_returns_404_for_unregistered_participant(api):
    # Arrange
    client, _ = api

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "missing@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_returns_404_for_unknown_activity(api):
    # Arrange
    client, _ = api

    # Act
    response = client.delete(
        "/activities/Unknown Club/participants",
        params={"email": "missing@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"