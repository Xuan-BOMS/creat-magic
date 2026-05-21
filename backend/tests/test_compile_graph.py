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


def test_compile_fireball_example() -> None:
    response = client.post("/api/compile-graph", json=_example("fireball"))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "compiled"
    assert data["spell_name"] == "火球术"
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
