from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_signup_rejects_duplicate_registration():
    activity = activities["Chess Club"]
    original_participants = activity["participants"][:]

    try:
        email = "new.student@mergington.edu"
        activity["participants"] = original_participants[:]

        first_response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email},
        )
        duplicate_response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email},
        )

        assert first_response.status_code == 200
        assert duplicate_response.status_code == 400
        assert duplicate_response.json()["detail"] == "Student already signed up for this activity"
    finally:
        activity["participants"] = original_participants


def test_signup_updates_activity_participants():
    activity = activities["Chess Club"]
    original_participants = activity["participants"][:]

    try:
        email = "live.update@mergington.edu"
        activity["participants"] = original_participants[:]

        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email},
        )
        activities_response = client.get("/activities")

        assert response.status_code == 200
        assert email in activities_response.json()["Chess Club"]["participants"]
    finally:
        activity["participants"] = original_participants


def test_unregister_participant():
    activity = activities["Chess Club"]
    original_participants = activity["participants"][:]

    try:
        activity["participants"] = original_participants[:]
        email = activity["participants"][0]

        response = client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": email},
        )

        assert response.status_code == 200
        assert email not in activity["participants"]
        assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    finally:
        activity["participants"] = original_participants
