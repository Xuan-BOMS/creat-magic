from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_catalog_contains_full_element_systems() -> None:
    response = client.get("/api/catalog")
    assert response.status_code == 200
    data = response.json()
    assert {item["id"] for item in data["elements"]} == {"fire", "water", "wind", "earth", "ether"}
    for element in data["elements"]:
        for branch in element["branches"]:
            assert len(branch["spells"]) == 11
            assert branch["spells"][0]["tier"] == 0
            assert branch["spells"][-1]["tier"] == 10


def test_compile_fireball_with_staff() -> None:
    response = client.post(
        "/api/compile",
        json={
            "element_id": "fire",
            "tier": 1,
            "intent": "远程伤害",
            "carrier": "法杖",
            "technique": "标准",
            "environment": "训练场",
            "caster": {"focus": 65, "control": 60, "knowledge": 2},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "compiled"
    assert data["selected_spell"]["name"] == "火球术"
    assert "法杖" in data["spell_card"]["chain"]


def test_reject_spell_above_knowledge() -> None:
    response = client.post(
        "/api/compile",
        json={
            "element_id": "earth",
            "tier": 8,
            "carrier": "手势",
            "technique": "标准",
            "environment": "战斗",
            "caster": {"focus": 80, "control": 80, "knowledge": 3},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["errors"]


def test_high_tier_ether_is_unsafe_when_authority_missing() -> None:
    response = client.post(
        "/api/compile",
        json={
            "element_id": "ether",
            "branch_id": "ether-vector",
            "tier": 10,
            "carrier": "魔法阵",
            "technique": "序列",
            "environment": "城镇",
            "caster": {"focus": 95, "control": 95, "knowledge": 10},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unsafe"
    assert data["scores"]["governance"] < 40
