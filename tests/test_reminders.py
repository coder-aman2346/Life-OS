from fastapi.testclient import TestClient


def test_create_and_list_reminders(client: TestClient) -> None:
    # Create a reminder
    response = client.post(
        "/api/v1/reminders",
        json={
            "user_id": "demo-user",
            "title": "Call dentist",
            "description": "Annual checkup",
            "priority": 2,
        },
    )
    assert response.status_code == 201
    reminder = response.json()
    assert reminder["title"] == "Call dentist"
    assert reminder["priority"] == 2
    assert reminder["completed"] is False
    reminder_id = reminder["id"]

    # List reminders
    response = client.get("/api/v1/reminders?user_id=demo-user")
    assert response.status_code == 200
    reminders = response.json()
    assert len(reminders) == 1

    # Update - mark complete
    response = client.patch(
        f"/api/v1/reminders/{reminder_id}",
        json={"completed": True},
    )
    assert response.status_code == 200
    assert response.json()["completed"] is True

    # Completed reminders hidden by default
    response = client.get("/api/v1/reminders?user_id=demo-user")
    assert len(response.json()) == 0

    # Show with completed
    response = client.get("/api/v1/reminders?user_id=demo-user&include_completed=true")
    assert len(response.json()) == 1

    # Delete
    response = client.delete(f"/api/v1/reminders/{reminder_id}")
    assert response.status_code == 204


def test_reminder_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/reminders/nonexistent-id")
    assert response.status_code == 404
