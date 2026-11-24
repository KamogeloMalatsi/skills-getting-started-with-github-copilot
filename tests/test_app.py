import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activity_participants():
    original_participants = {
        name: activity["participants"][:]
        for name, activity in activities.items()
    }

    yield

    for name, participants in original_participants.items():
        activities[name]["participants"] = participants


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    expected_activity_names = set(activities)

    response = client.get("/activities")

    assert response.status_code == 200
    assert set(response.json()) == expected_activity_names


def test_signup_adds_participant_to_activity():
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    response = client.post(
        f"/activities/{activity_name.replace(' ', '%20')}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"


def test_signup_rejects_duplicate_registration():
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    client.post(
        f"/activities/{activity_name.replace(' ', '%20')}/signup",
        params={"email": email},
    )
    duplicate_response = client.post(
        f"/activities/{activity_name.replace(' ', '%20')}/signup",
        params={"email": email},
    )

    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_updates_activity_listing():
    activity_name = "Chess Club"
    email = "live.update@mergington.edu"

    client.post(
        f"/activities/{activity_name.replace(' ', '%20')}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")

    assert email in activities_response.json()[activity_name]["participants"]


def test_unregister_participant():
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    response = client.delete(
        f"/activities/{activity_name.replace(' ', '%20')}/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"


def test_unregister_rejects_unknown_activity():
    response = client.delete(
        "/activities/Unknown%20Activity/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unknown_participant():
    activity_name = "Chess Club"
    email = "not.signed.up@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name.replace(' ', '%20')}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
