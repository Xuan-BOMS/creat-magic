from dataclasses import dataclass

from app.models import CompileGraphRequest, NodeDefinition, StageBuild, StageId
from app.text_library import get_fixed_spell_text, get_system_name

STAGE_ORDER: tuple[StageId, ...] = ("model", "purify", "infuse", "release")

SYSTEM_NAMES = {
    "fire": "火系",
    "water": "水系",
    "wind": "风系",
    "earth": "土系",
    "chaos": "混沌系",
    "vector": "引力系",
}

SYSTEM_PURIFY_NODES = {
    "fire": "purify_fire",
    "water": "purify_water",
    "wind": "purify_wind",
    "earth": "purify_earth",
    "chaos": "purify_chaos",
    "vector": "purify_vector",
}


@dataclass(frozen=True)
class FixedSpellProfile:
    id: str
    system: str
    source_tier: int
    name: str
    summary: str
    nodes: dict[StageId, tuple[str, ...]]


def _profile(system: str, tier: int, name: str, summary: str, model: str, infuse: str, release: str) -> FixedSpellProfile:
    return FixedSpellProfile(
        id=f"fixed-{system}-{tier}",
        system=system,
        source_tier=tier,
        name=name,
        summary=summary,
        nodes={
            "model": (model,),
            "purify": (SYSTEM_PURIFY_NODES[system],),
            "infuse": (infuse,),
            "release": (release,),
        },
    )


def _with_external_text(profile: FixedSpellProfile) -> FixedSpellProfile:
    name, summary = get_fixed_spell_text(profile.id, profile.name, profile.summary)
    return FixedSpellProfile(
        id=profile.id,
        system=profile.system,
        source_tier=profile.source_tier,
        name=name,
        summary=summary,
        nodes=profile.nodes,
    )


SPELL_PROFILES: tuple[FixedSpellProfile, ...] = (
    _profile("fire", 1, "火球术", "球形火元素弹体，用投射完成引燃与灼烧。", "model_sphere", "infuse_standard", "release_projectile"),
    _profile("fire", 2, "火环术", "环状火焰持续维持，以热场阻止目标靠近。", "model_ring", "infuse_maintain", "release_maintain"),
    _profile("fire", 3, "火弹术", "微小聚焦模具压缩火元素，再以激发形成爆裂灼烧。", "model_focused", "infuse_compress", "release_activate"),
    _profile("fire", 4, "火花术", "分化火团在命中后连续延伸扩散，吞没目标范围。", "model_branching", "infuse_propagate", "release_chain_spread"),
    _profile("fire", 5, "焚烧术", "广域边界承载高效火焰灌注，覆盖并焚烧范围内对象。", "model_large_area", "infuse_high_efficiency", "release_wide"),
    _profile("fire", 6, "御火术", "直接接管既有火焰，使火焰按施法意图流动、收束或熄灭。", "model_existing_target", "infuse_existing_control", "release_direct_control"),
    _profile("fire", 7, "温控", "从火元素本质回落到温度升降，改写目标热状态。", "model_essence", "infuse_temperature_shift", "release_essence_rewrite"),
    _profile("fire", 8, "能量制造", "在底层原理模型中制造纯粹能量，作为燃烧与热变的根基。", "model_origin", "infuse_energy_seed", "release_origin_manufacture"),
    _profile("fire", 9, "体内焚烧", "突破体内边界后桥接目标火元素，由内而外引燃。", "model_internal", "infuse_internal_bridge", "release_internal_cast"),
    _profile("fire", 10, "炎之灵域", "以领域规则统摄范围内火元素，使其成为灵域内的执行规则。", "model_domain", "infuse_domain_rule", "release_domain_control"),
    _profile("water", 1, "水流术", "线形水流经标准灌注后流动释放，用于冲刷、降温或灭火。", "model_line", "infuse_standard", "release_flow"),
    _profile("water", 2, "水牢术", "囚笼模具持续维持水流边界，以流体限制行动和呼吸。", "model_cage", "infuse_maintain", "release_bind"),
    _profile("water", 3, "水壁术", "墙体模具承载流层灌注，以持续流动卸去冲击并隔绝属性。", "model_wall", "infuse_flow_layer", "release_maintain"),
    _profile("water", 4, "水蚀术", "团块水流强化渗透后侵入缝隙，使目标内部被水浸没。", "model_mass", "infuse_permeate", "release_infiltrate"),
    _profile("water", 5, "水刃术", "刃形模具配合高效灌注，将极致水流集中为狙击切线。", "model_blade", "infuse_high_efficiency", "release_projectile"),
    _profile("water", 6, "御水术", "接管既有水体并直接操纵，使其可形成波浪、束缚或冲击。", "model_existing_target", "infuse_existing_control", "release_direct_control"),
    _profile("water", 7, "液体掌握", "从水元素上升到液体构成，改写液体浓度与成分。", "model_essence", "infuse_liquid_composition", "release_essence_rewrite"),
    _profile("water", 8, "湿度变动", "在底层原理中制造湿度与状态变动，支配液体存在方式。", "model_origin", "infuse_humidity_state", "release_origin_manufacture"),
    _profile("water", 9, "体内控液", "突破体内边界后桥接目标液体，操纵体内流体状态。", "model_internal", "infuse_internal_bridge", "release_internal_cast"),
    _profile("water", 10, "液之灵域", "以领域规则统摄范围内液体，使液态变化成为灵域规则。", "model_domain", "infuse_domain_rule", "release_domain_control"),
    _profile("wind", 1, "吹风术", "线形气流经标准灌注后流动释放，干扰目标行动。", "model_line", "infuse_standard", "release_flow"),
    _profile("wind", 2, "风刃术", "刃形气流维持运动边界，以持续运动完成切割。", "model_blade", "infuse_standard", "release_flow"),
    _profile("wind", 3, "暴风术", "范围模具并行灌入风元素，形成乱流并搬动范围内对象。", "model_area", "infuse_multi", "release_flow"),
    _profile("wind", 4, "极星术", "导向模具强化气流加速，使目标沿气流方向高速运动。", "model_guidance", "infuse_accelerate", "release_accelerate"),
    _profile("wind", 5, "龙卷术", "漩涡模具维持运动气流，使龙卷在成立后自我延续。", "model_vortex", "infuse_maintain", "release_self_sustain"),
    _profile("wind", 6, "御风术", "接管既有风并直接操纵，将气流挤压成攻防一体的屏障。", "model_existing_target", "infuse_existing_control", "release_direct_control"),
    _profile("wind", 7, "气体掌握", "从风元素上升到气体构成，提取、分离或替换指定气体。", "model_essence", "infuse_gas_selection", "release_essence_rewrite"),
    _profile("wind", 8, "动能制造", "在底层原理中制造运动根基，理解事物为何而动。", "model_origin", "infuse_kinetic_seed", "release_origin_manufacture"),
    _profile("wind", 9, "体内操风", "突破体内边界后桥接目标气体，操纵体内气流。", "model_internal", "infuse_internal_bridge", "release_internal_cast"),
    _profile("wind", 10, "风之灵域", "以领域规则统摄范围内气体，使气体运动成为灵域规则。", "model_domain", "infuse_domain_rule", "release_domain_control"),
    _profile("earth", 1, "实弹术", "实体块状模具承载土元素，以投射形成直接打击。", "model_chunk", "infuse_standard", "release_projectile"),
    _profile("earth", 2, "土墙术", "墙体模具持续维持土石结构，以硬度抵御攻击。", "model_wall", "infuse_maintain", "release_maintain"),
    _profile("earth", 3, "硬化术", "强化模具灌入土石结构，使原有对象获得更高硬度。", "model_reinforcement", "infuse_reinforce", "release_maintain"),
    _profile("earth", 4, "构造术", "自适应结构灌入土石构型，按场合生成或改造形态。", "model_adaptive", "infuse_structure", "release_construct"),
    _profile("earth", 5, "石化术", "束缚外壳凝聚土石，将目标困入量身成型的硬质囚笼。", "model_binding_shell", "infuse_condense", "release_bind"),
    _profile("earth", 6, "御土术", "接管既有土石并直接操纵，改动地貌、震动或结构。", "model_existing_target", "infuse_existing_control", "release_direct_control"),
    _profile("earth", 7, "固体生成", "从土元素上升到固体构成，自由构筑或拆解固体。", "model_essence", "infuse_solid_generation", "release_essence_rewrite"),
    _profile("earth", 8, "物质制造", "在底层原理中制造物质凝聚与分离的根基。", "model_origin", "infuse_matter_seed", "release_origin_manufacture"),
    _profile("earth", 9, "体内构型", "突破体内边界后桥接目标固体结构，改写体内构型。", "model_internal", "infuse_internal_bridge", "release_internal_cast"),
    _profile("earth", 10, "地之灵域", "以领域规则统摄范围内固体，使地与物质成为灵域规则。", "model_domain", "infuse_domain_rule", "release_domain_control"),
    _profile("chaos", 1, "魔弹术", "球形无属性混合物投射命中，用湿热、粘附与刺激限制目标。", "model_sphere", "infuse_standard", "release_projectile"),
    _profile("chaos", 2, "魔障壁", "墙体模具维持无属性屏障，以性质变化削减攻击。", "model_wall", "infuse_maintain", "release_maintain"),
    _profile("chaos", 3, "魔沼泽", "范围模具注入粘附混合物，在侵蚀地面时束缚目标。", "model_area", "infuse_adhesion", "release_bind"),
    _profile("chaos", 4, "模仿术", "自适应结构读取对方法术，并用无属性比例进行对应模仿。", "model_adaptive", "infuse_mimic", "release_adaptive"),
    _profile("chaos", 5, "魔侵入", "目标锚定后强化侵入性，使无属性混合物沿弱点渗入体内。", "model_target", "infuse_intrusion", "release_infiltrate"),
    _profile("chaos", 6, "御魔术", "转化团块持续接触法术并将其转为无属性混合物。", "model_conversion_cube", "infuse_conversion", "release_direct_control"),
    _profile("chaos", 7, "物质转化", "从无属性本质上升到共同点识别，将一物转为另一物。", "model_essence", "infuse_matter_transmutation", "release_essence_rewrite"),
    _profile("chaos", 8, "混沌融合", "在底层原理中理解一与全，使不同功能表归于混沌。", "model_origin", "infuse_chaos_fusion", "release_origin_manufacture"),
    _profile("chaos", 9, "体内转化", "突破体内边界后桥接目标混沌变量，改写体内性质。", "model_internal", "infuse_internal_bridge", "release_internal_cast"),
    _profile("chaos", 10, "混沌灵域", "以领域规则统摄范围内无属性混沌，使转化成为灵域规则。", "model_domain", "infuse_domain_rule", "release_domain_control"),
    _profile("vector", 1, "动能术", "线形矢量经标准灌注后施加推力，完成直接动能干扰。", "model_line", "infuse_standard", "release_vector_push"),
    _profile("vector", 2, "法师之眼", "侦测模具维持矢量触探，以持续施力反馈目标行动。", "model_probe", "infuse_maintain", "release_sense"),
    _profile("vector", 3, "扰乱术", "目标锚定后并行施加多道矢量，使目标受力方向混乱。", "model_target", "infuse_vector_multi", "release_disrupt"),
    _profile("vector", 4, "立场术", "力场外壳灌入矢量场，使作用力转向、接近或反弹。", "model_field_shell", "infuse_vector_field", "release_reflect"),
    _profile("vector", 5, "破魔术", "锚定施法过程并注入反向矢量，使目标法术流程崩解。", "model_spell_process", "infuse_countermagic", "release_disrupt"),
    _profile("vector", 6, "御力术", "接管既有对象的受力状态，直接操纵行动与运动结果。", "model_existing_target", "infuse_existing_control", "release_direct_control"),
    _profile("vector", 7, "矢量引导", "从操作本质上升到力的流向，为不同事物赋予不同矢量。", "model_essence", "infuse_vector_guidance", "release_essence_rewrite"),
    _profile("vector", 8, "精神引导", "在底层原理中追索人的原动力，引导精神的运动方向。", "model_origin", "infuse_spirit_guidance", "release_origin_manufacture"),
    _profile("vector", 9, "体内引导", "突破体内边界后桥接目标矢量，操纵体内受力与行动。", "model_internal", "infuse_internal_bridge", "release_internal_cast"),
    _profile("vector", 10, "引力灵域", "以领域规则统摄范围内矢量，使力的方向成为灵域规则。", "model_domain", "infuse_domain_rule", "release_domain_control"),
)

SIGNATURE_INDEX = {tuple((stage, profile.nodes[stage]) for stage in STAGE_ORDER): profile for profile in SPELL_PROFILES}


def system_from_key(key: str | None) -> str | None:
    if key == "ether":
        return "vector"
    if key in SYSTEM_NAMES:
        return key
    return None


def identify_fixed_spell(stages: list[StageBuild], nodes_by_id: dict[str, NodeDefinition] | None = None) -> FixedSpellProfile | None:
    by_stage = {
        stage.stage: tuple(
            instance.node_id
            for instance in stage.nodes
            if not nodes_by_id or nodes_by_id[instance.node_id].name_role == "base"
        )
        for stage in stages
    }
    if set(by_stage) != set(STAGE_ORDER):
        return None
    profile = SIGNATURE_INDEX.get(tuple((stage, by_stage[stage]) for stage in STAGE_ORDER))
    return _with_external_text(profile) if profile else None


def get_fixed_spell_examples() -> list[CompileGraphRequest]:
    examples: list[CompileGraphRequest] = []
    for base_profile in SPELL_PROFILES:
        profile = _with_external_text(base_profile)
        examples.append(
            CompileGraphRequest(
                id=profile.id,
                intent=f"{get_system_name(profile.system, SYSTEM_NAMES[profile.system])}{profile.source_tier}阶固定法术构建",
                stages=[
                    {
                        "stage": stage,
                        "nodes": [
                            {"instance_id": f"{stage}-{index + 1}", "node_id": node_id}
                            for index, node_id in enumerate(profile.nodes[stage])
                        ],
                    }
                    for stage in STAGE_ORDER
                ],
                context={
                    "system": profile.system,
                    "profile_id": profile.id,
                    "expected_tier": profile.source_tier,
                    "expected_spell_name": profile.name,
                    "profile_summary": profile.summary,
                },
            )
        )
    return examples
