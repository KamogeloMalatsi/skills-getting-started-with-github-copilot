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
