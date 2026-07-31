from unittest.mock import MagicMock, patch
import pytest


@patch("app.services.dialogue.dialogue_service.DialogueService.generate_response_with_telemetry")
@patch("app.services.dialogue.conversation_service.ConversationService.process_conversation")
def test_chat_route_includes_telemetry(mock_process, mock_generate, client):
    mock_generate.return_value = (
        "I remember your favorite brew.",
        "Friendly",
        {"cache_hit": False, "intent_ms": 12.0, "retrieval_ms": 45.0, "generation_ms": 300.0, "total_ms": 357.0},
    )

    # 1. Create NPC
    npc_res = client.post(
        "/npcs/",
        json={
            "name": "Eldon",
            "role": "Alchemist",
            "location": "Lab",
            "personality": {
                "trust": 50, "respect": 50, "warmth": 50,
                "curiosity": 50, "fear": 10, "loyalty": 50, "aggression": 10
            },
        },
    )
    assert npc_res.status_code == 201
    npc_id = npc_res.json()["id"]

    # 2. Create Player
    player_res = client.post("/players/", json={"username": "test_hero"})
    assert player_res.status_code == 201
    player_id = player_res.json()["id"]

    # 3. Call Chat
    response = client.post(
        "/chat/",
        json={"npc_id": npc_id, "player_id": player_id, "message": "Do you remember me?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "I remember your favorite brew."
    assert data["emotion"] == "Friendly"
    assert data["telemetry"]["cache_hit"] is False
    assert data["telemetry"]["total_ms"] == 357.0


@patch("app.services.dialogue.dialogue_service.DialogueService.generate_response_with_telemetry")
@patch("app.services.dialogue.conversation_service.ConversationService.process_conversation")
def test_chat_stream_sse_endpoint(mock_process, mock_generate, client):
    mock_generate.return_value = (
        "Greetings adventurer!",
        "Amused",
        {"cache_hit": False, "retrieval_ms": 20.0, "generation_ms": 150.0, "total_ms": 170.0},
    )

    # 1. Create NPC
    npc_res = client.post(
        "/npcs/",
        json={
            "name": "Ragnar",
            "role": "Blacksmith",
            "location": "Forge",
            "personality": {
                "trust": 60, "respect": 70, "warmth": 40,
                "curiosity": 30, "fear": 5, "loyalty": 80, "aggression": 30
            },
        },
    )
    npc_id = npc_res.json()["id"]

    # 2. Create Player
    player_res = client.post("/players/", json={"username": "valkyrie"})
    player_id = player_res.json()["id"]

    # 3. Call Streaming Chat
    response = client.post(
        "/chat/stream",
        json={"npc_id": npc_id, "player_id": player_id, "message": "Hello there!"},
    )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    body = response.text
    assert "data:" in body
    assert "Greetings" in body
