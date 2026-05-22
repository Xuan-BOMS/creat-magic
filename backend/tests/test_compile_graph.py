from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _example(example_id: str) -> dict:
    response = client.get("/api/examples")
    assert response.status_code == 200
    return next(item for item in response.json() if item["id"] == example_id)


def test_nodes_endpoint_exposes_mvp_stages() -> None:
    response = client.get("/api/nodes")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "mvp-0.1"
    assert [stage["id"] for stage in data["stages"]] == ["model", "purify", "infuse", "release"]
    assert {node["stage"] for node in data["nodes"]} == {"model", "purify", "infuse", "release"}
    assert all(isinstance(node["tier"], int) for node in data["nodes"])
    assert all(isinstance(node["difficulty"], int) for node in data["nodes"])


def test_compile_fireball_example() -> None:
    payload = _example("fireball")
    payload.pop("caster", None)
    response = client.post("/api/compile-graph", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "compiled"
    assert data["spell_name"] == "火球术"
    assert data["spell_level"]["tier"] == 1
    assert data["spell_level"]["base_tier"] == 1
    assert len(data["radar"]) == 6
    assert "safety" not in {score["key"] for score in data["radar"]}
    assert data["stage_outcomes"][0]["result"] == "球形弹体"


def test_compile_multi_wind_blade_example() -> None:
    response = client.post("/api/compile-graph", json=_example("multi_wind_blade"))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "compiled"
    assert data["spell_name"] == "多重风刃"
    assert any("多重" in item["result"] for item in data["stage_outcomes"])


def test_compile_mire_example() -> None:
    response = client.post("/api/compile-graph", json=_example("mire"))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "compiled"
    assert data["spell_name"] == "泥沼术"
    assert data["stage_outcomes"][1]["result"] == "泥沼系法术"


def test_compile_lightning_example_is_unsafe() -> None:
    response = client.post("/api/compile-graph", json=_example("lightning"))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unsafe"
    assert data["spell_name"] == "雷电术"
    assert len(data["radar"]) == 6
    assert any(issue["severity"] == "unsafe" for issue in data["issues"])


def test_difficulty_overflow_can_raise_above_highest_node_tier() -> None:
    payload = _example("fireball")
    payload.pop("caster", None)
    payload["stages"][2]["nodes"].extend(
        [
            {"instance_id": "infuse-extra-1", "node_id": "infuse_standard"},
            {"instance_id": "infuse-extra-2", "node_id": "infuse_standard"},
            {"instance_id": "infuse-extra-3", "node_id": "infuse_standard"},
        ]
    )
    response = client.post("/api/compile-graph", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["spell_level"]["base_tier"] == 1
    assert data["spell_level"]["tier"] > 1
    assert data["spell_level"]["difficulty_bonus"] > 0


def test_domain_node_locks_spell_to_tenth_tier() -> None:
    payload = {
        "id": "domain-fire",
        "intent": "领域统摄",
        "stages": [
            {"stage": "model", "nodes": [{"instance_id": "model-1", "node_id": "model_domain"}]},
            {"stage": "purify", "nodes": [{"instance_id": "purify-1", "node_id": "purify_fire"}]},
            {"stage": "infuse", "nodes": [{"instance_id": "infuse-1", "node_id": "infuse_domain_rule"}]},
            {"stage": "release", "nodes": [{"instance_id": "release-1", "node_id": "release_domain_control"}]},
        ],
        "context": {"environment": "训练场"},
    }
    response = client.post("/api/compile-graph", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["spell_name"] == "炎之灵域"
    assert data["spell_level"]["tier"] == 10
    assert data["status"] == "unsafe"


def test_fixed_spell_system_examples_cover_six_systems_and_tiers_1_to_10() -> None:
    response = client.get("/api/examples")
    assert response.status_code == 200
    fixed_examples = [item for item in response.json() if str(item["id"]).startswith("fixed-")]
    assert len(fixed_examples) == 60
    seen = {(item["context"]["system"], item["context"]["expected_tier"]) for item in fixed_examples}
    assert seen == {(system, tier) for system in {"fire", "water", "wind", "earth", "chaos", "vector"} for tier in range(1, 11)}

    for example in fixed_examples:
        compile_response = client.post("/api/compile-graph", json=example)
        assert compile_response.status_code == 200
        data = compile_response.json()
        assert data["status"] != "failed"
        assert data["spell_level"]["tier"] == example["context"]["expected_tier"]
        assert data["spell_name"] == example["context"]["expected_spell_name"]


def test_compile_graph_rejects_empty_stage() -> None:
    payload = _example("fireball")
    payload["stages"][1]["nodes"] = []
    response = client.post("/api/compile-graph", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert any(issue["rule_id"] == "stage.empty" and issue["stage"] == "purify" for issue in data["issues"])


def test_compile_graph_rejects_duplicate_stage() -> None:
    payload = _example("fireball")
    payload["stages"].insert(
        1,
        {"stage": "model", "nodes": [{"instance_id": "model-2", "node_id": "model_sphere"}]},
    )
    response = client.post("/api/compile-graph", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert any(issue["rule_id"] == "stage.duplicate" and issue["stage"] == "model" for issue in data["issues"])


def test_compile_graph_rejects_wrong_stage_node() -> None:
    payload = _example("fireball")
    payload["stages"][0]["nodes"][0]["node_id"] = "purify_fire"
    response = client.post("/api/compile-graph", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert any(issue["rule_id"] == "node.wrong_stage" for issue in data["issues"])


def test_compile_graph_rejects_unknown_node() -> None:
    payload = _example("fireball")
    payload["stages"][2]["nodes"][0]["node_id"] = "missing_node"
    response = client.post("/api/compile-graph", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert any(issue["rule_id"] == "node.unknown" for issue in data["issues"])
