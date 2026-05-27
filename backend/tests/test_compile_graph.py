from fastapi.testclient import TestClient

from app.main import app
from app.fixed_spell_profiles import SPELL_PROFILES

client = TestClient(app)


def _example(example_id: str) -> dict:
    response = client.get("/api/examples")
    assert response.status_code == 200
    return next(item for item in response.json() if item["id"] == example_id)


def test_nodes_endpoint_exposes_mvp_stages() -> None:
    response = client.get("/api/nodes")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "mvp-0.2"
    assert [stage["id"] for stage in data["stages"]] == ["model", "purify", "infuse", "release"]
    assert {node["stage"] for node in data["nodes"]} == {"model", "purify", "infuse", "release"}
    assert all(isinstance(node["tier"], int) for node in data["nodes"])
    assert all(isinstance(node["difficulty"], int) for node in data["nodes"])
    assert {node["selection_class"] for node in data["nodes"]} == {"core", "detail", "tuning"}
    assert {node["name_role"] for node in data["nodes"]} >= {"base", "variant", "buff"}


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
    payload["stages"][3]["nodes"].extend(
        [
            {"instance_id": f"release-speed-{index}", "node_id": "release_faster"}
            for index in range(6)
        ]
    )
    response = client.post("/api/compile-graph", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["spell_name"] == "火球术"
    assert data["spell_level"]["base_tier"] == 1
    assert data["spell_level"]["tier"] > 1
    assert data["spell_level"]["difficulty_bonus"] > 0
    assert next(item for item in data["modifiers"] if item["key"] == "release.speed.up")["count"] == 6


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
    signatures = {
        tuple((stage["stage"], tuple(node["node_id"] for node in stage["nodes"])) for stage in item["stages"])
        for item in fixed_examples
    }
    assert len(signatures) == 60
    assert len(SPELL_PROFILES) == 60

    for example in fixed_examples:
        compile_response = client.post("/api/compile-graph", json=example)
        assert compile_response.status_code == 200
        data = compile_response.json()
        assert data["status"] != "failed"
        assert data["spell_level"]["tier"] == example["context"]["expected_tier"]
        assert data["spell_name"] == example["context"]["expected_spell_name"]


def test_fixed_spell_name_comes_from_node_signature_not_context() -> None:
    payload = _example("fixed-fire-1")
    payload["context"]["system"] = "water"
    payload["context"]["expected_tier"] = 8
    payload["context"]["expected_spell_name"] = "湿度变动"
    response = client.post("/api/compile-graph", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["spell_name"] == "火球术"
    assert data["spell_level"]["tier"] == 1


def test_fixed_spell_identity_ignores_variant_and_buff_nodes() -> None:
    payload = _example("fixed-fire-1")
    payload["stages"][0]["nodes"].append({"instance_id": "model-detail-1", "node_id": "model_expanded"})
    payload["stages"][3]["nodes"].extend(
        [
            {"instance_id": "release-detail-1", "node_id": "release_curve_left"},
            {"instance_id": "release-buff-1", "node_id": "release_faster"},
            {"instance_id": "release-buff-2", "node_id": "release_faster"},
        ]
    )
    response = client.post("/api/compile-graph", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] != "failed"
    assert data["spell_name"] == "膨胀左弯火球术"
    assert any(item["label"] == "膨胀" and item["kind"] == "variant" for item in data["modifiers"])
    assert next(item for item in data["modifiers"] if item["key"] == "release.speed.up")["count"] == 2


def test_unregistered_base_signature_displays_placeholder_name() -> None:
    payload = _example("fireball")
    payload["stages"][3]["nodes"][0]["node_id"] = "release_flow"
    response = client.post("/api/compile-graph", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] != "failed"
    assert data["spell_name"] == "暂无"


def test_compile_graph_rejects_duplicate_detail_node() -> None:
    payload = _example("fireball")
    payload["stages"][0]["nodes"].extend(
        [
            {"instance_id": "model-detail-1", "node_id": "model_expanded"},
            {"instance_id": "model-detail-2", "node_id": "model_expanded"},
        ]
    )
    response = client.post("/api/compile-graph", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert any(issue["rule_id"] == "selection.detail_duplicate" for issue in data["issues"])


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
