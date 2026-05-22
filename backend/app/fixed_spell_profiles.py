from app.models import CompileGraphRequest

SYSTEM_PURIFY_NODES = {
    "fire": "purify_fire",
    "water": "purify_water",
    "wind": "purify_wind",
    "earth": "purify_earth",
    "chaos": "purify_chaos",
    "vector": "purify_vector",
}

SYSTEM_NAMES = {
    "fire": "火系",
    "water": "水系",
    "wind": "风系",
    "earth": "土系",
    "chaos": "混沌系",
    "vector": "引力系",
}

FIXED_SPELL_NAMES = {
    "fire": {
        1: "火球术",
        2: "火环术",
        3: "火弹术",
        4: "火花术",
        5: "焚烧术",
        6: "御火术",
        7: "温控",
        8: "能量制造",
        9: "体内焚烧",
        10: "炎之灵域",
    },
    "water": {
        1: "水流术",
        2: "水牢术",
        3: "水壁术",
        4: "水蚀术",
        5: "水刃术",
        6: "御水术",
        7: "液体掌握",
        8: "湿度变动",
        9: "体内控液",
        10: "液之灵域",
    },
    "wind": {
        1: "吹风术",
        2: "风刃术",
        3: "暴风术",
        4: "极星术",
        5: "龙卷术",
        6: "御风术",
        7: "气体掌握",
        8: "动能制造",
        9: "体内操风",
        10: "风之灵域",
    },
    "earth": {
        1: "实弹术",
        2: "土墙术",
        3: "硬化术",
        4: "构造术",
        5: "石化术",
        6: "御土术",
        7: "固体生成",
        8: "物质制造",
        9: "体内构型",
        10: "地之灵域",
    },
    "chaos": {
        1: "魔弹术",
        2: "魔障壁",
        3: "魔沼泽",
        4: "模仿术",
        5: "魔侵入",
        6: "御魔术",
        7: "物质转化",
        8: "混沌融合",
        9: "体内转化",
        10: "混沌灵域",
    },
    "vector": {
        1: "动能术",
        2: "法师之眼",
        3: "扰乱术",
        4: "立场术",
        5: "破魔术",
        6: "御力术",
        7: "矢量引导",
        8: "精神引导",
        9: "体内引导",
        10: "引力灵域",
    },
}

TIER_RECIPES = {
    1: ("model_sphere", "infuse_standard", "release_projectile"),
    2: ("model_core_application", "infuse_maintain", "release_maintain"),
    3: ("model_focused", "infuse_compress", "release_activate"),
    4: ("model_adaptive", "infuse_adapt", "release_adaptive"),
    5: ("model_large_area", "infuse_high_efficiency", "release_wide"),
    6: ("model_existing_target", "infuse_existing_control", "release_direct_control"),
    7: ("model_essence", "infuse_essence_control", "release_essence_rewrite"),
    8: ("model_origin", "infuse_origin_formula", "release_origin_manufacture"),
    9: ("model_internal", "infuse_internal_bridge", "release_internal_cast"),
    10: ("model_domain", "infuse_domain_rule", "release_domain_control"),
}


def system_from_key(key: str | None) -> str | None:
    if key == "ether":
        return "vector"
    if key in FIXED_SPELL_NAMES:
        return key
    return None


def fixed_spell_name(system: str | None, tier: int) -> str | None:
    if not system:
        return None
    return FIXED_SPELL_NAMES.get(system, {}).get(tier)


def get_fixed_spell_examples() -> list[CompileGraphRequest]:
    examples: list[CompileGraphRequest] = []
    for system, purify_node in SYSTEM_PURIFY_NODES.items():
        for tier, (model_node, infuse_node, release_node) in TIER_RECIPES.items():
            examples.append(
                CompileGraphRequest(
                    id=f"fixed-{system}-{tier}",
                    intent=f"{SYSTEM_NAMES[system]}{tier}阶固定法术构建",
                    stages=[
                        {"stage": "model", "nodes": [{"instance_id": "model-1", "node_id": model_node}]},
                        {"stage": "purify", "nodes": [{"instance_id": "purify-1", "node_id": purify_node}]},
                        {"stage": "infuse", "nodes": [{"instance_id": "infuse-1", "node_id": infuse_node}]},
                        {"stage": "release", "nodes": [{"instance_id": "release-1", "node_id": release_node}]},
                    ],
                    context={
                        "system": system,
                        "expected_tier": tier,
                        "expected_spell_name": FIXED_SPELL_NAMES[system][tier],
                    },
                )
            )
    return examples
