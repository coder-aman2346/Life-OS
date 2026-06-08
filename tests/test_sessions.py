from fastapi.testclient import TestClient


def test_session_chat_consolidation_and_memory_lookup(client: TestClient) -> None:
    session_response = client.post("/api/v1/sessions", json={"user_id": "demo-user"})
    assert session_response.status_code == 201
    session_id = session_response.json()["id"]

    chat_response = client.post(
        f"/api/v1/sessions/{session_id}/chat",
        json={
            "user_id": "demo-user",
            "message": "My name is Aman and I like quiet developer tools.",
        },
    )
    assert chat_response.status_code == 200
    assert "long-term memories" in chat_response.json()["response"]

    history_response = client.get(f"/api/v1/sessions/{session_id}/history")
    assert history_response.status_code == 200
    assert [message["role"] for message in history_response.json()] == ["user", "assistant"]

    end_response = client.delete(f"/api/v1/sessions/{session_id}?user_id=demo-user")
    assert end_response.status_code == 204

    memory_response = client.get("/api/v1/users/demo-user/memory")
    assert memory_response.status_code == 200
    memories = memory_response.json()
    assert len(memories) == 1
    assert "Aman" in memories[0]["content"]


def test_session_requires_matching_user(client: TestClient) -> None:
    session_response = client.post("/api/v1/sessions", json={"user_id": "owner"})
    session_id = session_response.json()["id"]

    response = client.post(
        f"/api/v1/sessions/{session_id}/chat",
        json={"user_id": "intruder", "message": "hello"},
    )

    assert response.status_code == 403
