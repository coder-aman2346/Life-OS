from fastapi.testclient import TestClient


def test_create_and_list_notes(client: TestClient) -> None:
    # Create a note
    response = client.post(
        "/api/v1/notes",
        json={"user_id": "demo-user", "title": "Test Note", "body": "Some content", "tags": "test"},
    )
    assert response.status_code == 201
    note = response.json()
    assert note["title"] == "Test Note"
    assert note["body"] == "Some content"
    assert note["tags"] == "test"
    note_id = note["id"]

    # List notes
    response = client.get("/api/v1/notes?user_id=demo-user")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["id"] == note_id

    # Get single note
    response = client.get(f"/api/v1/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Note"

    # Update note
    response = client.patch(
        f"/api/v1/notes/{note_id}",
        json={"title": "Updated Title", "pinned": True},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["pinned"] is True

    # Search
    response = client.get("/api/v1/notes?user_id=demo-user&q=Updated")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Delete
    response = client.delete(f"/api/v1/notes/{note_id}")
    assert response.status_code == 204

    response = client.get("/api/v1/notes?user_id=demo-user")
    assert response.json() == []


def test_note_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/notes/nonexistent-id")
    assert response.status_code == 404
