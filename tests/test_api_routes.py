import os
import sys

# Ensure backend directory is on sys.path for IDE module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestRootEndpoint:
    def test_root_returns_project_info(self, client):
        response = client.get("/")
        data = response.json()
        assert data["project"] == "EchoMind"
        assert data["version"] == "1.0.0"

    def test_root_does_not_expose_database_url(self, client):
        response = client.get("/")
        data = response.json()
        assert "database" not in data
        assert "DATABASE_URL" not in str(data)


class TestCORSHeaders:
    def test_cors_headers_present(self, client):
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" in response.headers


class TestNPCEndpoints:
    def test_create_and_get_npc(self, client):
        payload = {
            "name": "Zephyr",
            "role": "Alchemist",
            "location": "Apothecary",
            "personality": {
                "trust": 70,
                "respect": 80,
                "warmth": 60,
                "curiosity": 90,
                "fear": 15,
                "loyalty": 50,
                "aggression": 10,
            },
        }
        create_res = client.post("/npcs/", json=payload)
        assert create_res.status_code == 201
        data = create_res.json()
        assert data["name"] == "Zephyr"
        assert data["role"] == "Alchemist"
        assert data["location"] == "Apothecary"
        assert "id" in data

        get_res = client.get(f"/npcs/{data['id']}")
        assert get_res.status_code == 200
        assert get_res.json()["name"] == "Zephyr"


