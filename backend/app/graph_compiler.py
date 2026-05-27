from collections.abc import Iterable

from app.models import (
    CompileGraphRequest,
    CompileGraphResult,
    CompileIssue,
    CompoundRule,
    GraphSpellCard,
    NodeDefinition,
    NodeInstance,
    NodeLibrary,
    RadarScore,
    SpellModifier,
    SpellLevelAssessment,
    StageBuild,
    StageId,
    StageOutcome,
)
from app.fixed_spell_profiles import FixedSpellProfile, identify_fixed_spell, system_from_key
from app.node_library import get_node_library
from app.text_library import get_compiler_texts

STAGE_ORDER: list[StageId] = ["model", "purify", "infuse", "release"]
ELEMENT_KEYS = {"fire", "water", "wind", "earth", "ether", "chaos", "vector"}
STAGE_LABELS: dict[StageId, str] = {
    "model": "开模",
    "purify": "提纯",
    "infuse": "灌注",
    "release": "释放",
}
RADAR_LABELS: dict[str, str] = {
    "power": "威力",
    "stability": "稳定性",
    "learnability": "学习难度",
    "mana_efficiency": "魔力消耗",
    "versatility": "泛用性",
    "academic_value": "学术价值",
}
BASE_SCORE = {
    "power": 48,
    "stability": 62,
    "learnability": 60,
    "mana_efficiency": 58,
    "versatility": 55,
    "academic_value": 45,
}
DIFFICULTY_LIMITS = {
    0: 18,
    1: 44,
    2: 60,
    3: 90,
    4: 112,
    5: 140,
    6: 176,
    7: 218,
    8: 260,
    9: 320,
    10: 999,
}
DIFFICULTY_STEPS = {
    0: 18,
    1: 20,
    2: 24,
    3: 28,
    4: 32,
    5: 36,
    6: 42,
    7: 50,
    8: 60,
    9: 72,
    10: 999,
}
RISK_TEXT = {
    "thermal_spread": "热场外溢",
    "edge_control": "刃形边界散逸",
    "area_spill": "范围外溢",
    "block_path": "阻挡己方路径",
    "slip": "地面湿滑",
    "conductive_context": "环境导电",
    "drift": "路径偏移",
    "terrain_damage": "地形破坏",
    "cognitive_load": "认知负荷",
    "overpressure": "过压失控",
    "attention_parallel": "注意力并发不足",
    "miss": "投射落点偏移",
    "burst": "激发爆发",
    "governance_review": "治理审查",
    "high_voltage": "高压误伤",
    "internal_boundary": "体内边界突破",
    "domain_override": "领域统摄失控",
}


def _compiler_text_map(key: str, fallback: dict[str, str]) -> dict[str, str]:
    value = get_compiler_texts().get(key)
    return value if isinstance(value, dict) else fallback


def _stage_label(stage: StageId) -> str:
    return _compiler_text_map("stage_labels", STAGE_LABELS).get(stage, stage)


def _radar_label(key: str) -> str:
    return _compiler_text_map("radar_labels", RADAR_LABELS).get(key, key)


def _risk_text(tag: str) -> str:
    return _compiler_text_map("risk_text", RISK_TEXT).get(tag, tag)


def compile_graph(request: CompileGraphRequest) -> CompileGraphResult:
    library = get_node_library()
    nodes_by_id = {node.id: node for node in library.nodes}
    stages = {stage.stage: stage for stage in request.stages}
    issues = _validate_request(request, library, nodes_by_id, stages)
    if not any(issue.severity == "error" for issue in issues):
        issues.extend(_selection_issues(stages, nodes_by_id))
    stage_outcomes: list[StageOutcome] = []
    score = dict(BASE_SCORE)
    risk_tags: list[str] = []
    compiled_nodes: list[NodeDefinition] = []
    context = _CompileContext()
    fixed_profile = identify_fixed_spell(request.stages, nodes_by_id) if not any(issue.severity == "error" for issue in issues) else None

    if not any(issue.severity == "error" for issue in issues):
        for stage_id in STAGE_ORDER:
            outcome = _compile_stage(stage_id, stages[stage_id], nodes_by_id, library, context)
            stage_outcomes.append(outcome)
            for instance in stages[stage_id].nodes:
                node = nodes_by_id[instance.node_id]
                compiled_nodes.append(node)
                _merge_score(score, node.score_bias)
                risk_tags.extend(node.risk_tags)
            if stage_id == "purify" and context.compound:
                _merge_score(score, context.compound.score_bias)
                risk_tags.extend(context.compound.risk_tags)
        issues.extend(_semantic_issues(context))

    assessment = _assess_spell_level(compiled_nodes, context.compound)
    if any(issue.severity == "error" for issue in issues):
        status = "failed"
    else:
        if risk_tags:
            issues.extend(_risk_issues(risk_tags))
        score = _clamp_score(score)
        if any(issue.severity == "unsafe" for issue in issues):
            status = "unsafe"
        elif min(score["stability"], score["mana_efficiency"]) < 45:
            status = "partial"
        else:
            status = "compiled"

    modifiers = _collect_modifiers(stages, nodes_by_id) if not any(issue.severity == "error" for issue in issues) else []
    spell_name = _name_spell(stage_outcomes, context, assessment, fixed_profile, modifiers)
    summary = _summarize(stage_outcomes, status, assessment)
    radar = _build_radar(score)
    card = _build_card(request, spell_name, summary, stage_outcomes, issues, risk_tags, assessment)
    return CompileGraphResult(
        status=status,
        spell_name=spell_name,
        summary=summary,
        spell_level=assessment,
        stage_outcomes=stage_outcomes,
        issues=issues,
        modifiers=modifiers,
        radar=radar,
        spell_card=card,
    )


class _CompileContext:
    mold: str | None = None
    mold_tags: list[str] = []
    element: str | None = None
    element_keys: list[str] = []
    system: str | None = None
    compound: CompoundRule | None = None
    infusion: str | None = None
    infusion_tags: list[str] = []


def _validate_request(
    request: CompileGraphRequest,
    library: NodeLibrary,
    nodes_by_id: dict[str, NodeDefinition],
    stages: dict[StageId, StageBuild],
) -> list[CompileIssue]:
    issues: list[CompileIssue] = []
    seen_stages: set[StageId] = set()
    for stage in request.stages:
        if stage.stage in seen_stages:
            issues.append(_issue("stage.duplicate", "error", stage.stage, None, f"{_stage_label(stage.stage)}阶段重复。", "每个固定阶段只能出现一次。"))
        seen_stages.add(stage.stage)

    for stage_id in STAGE_ORDER:
        stage = stages.get(stage_id)
        if not stage:
            issues.append(_issue("stage.missing", "error", stage_id, None, f"缺少{_stage_label(stage_id)}阶段。", "补齐四个固定阶段后再编译。"))
            continue
        if not stage.nodes:
            issues.append(_issue("stage.empty", "error", stage_id, None, f"{_stage_label(stage_id)}阶段没有节点。", "至少放入一个可产生阶段结果的节点。"))
            continue
        seen: set[str] = set()
        for instance in stage.nodes:
            if instance.instance_id in seen:
                issues.append(_issue("node.duplicate_instance", "error", stage_id, instance.instance_id, "节点实例 ID 重复。", "为同一节点的重复使用分配不同实例 ID。"))
            seen.add(instance.instance_id)
            node = nodes_by_id.get(instance.node_id)
            if not node:
                issues.append(_issue("node.unknown", "error", stage_id, instance.instance_id, f"未知节点 {instance.node_id}。", "从 /api/nodes 返回的节点库中选择节点。"))
                continue
            if node.stage != stage_id:
                issues.append(_issue("node.wrong_stage", "error", stage_id, instance.instance_id, f"节点「{node.name}」不能放在{_stage_label(stage_id)}阶段。", f"将它移动到{_stage_label(node.stage)}阶段。"))
    known_stages = {stage.id for stage in library.stages}
    for stage in request.stages:
        if stage.stage not in known_stages:
            issues.append(_issue("stage.unknown", "error", None, None, f"未知阶段 {stage.stage}。", "使用固定四阶段。"))
    return issues


def _selection_issues(stages: dict[StageId, StageBuild], nodes_by_id: dict[str, NodeDefinition]) -> list[CompileIssue]:
    issues: list[CompileIssue] = []
    for stage_id in STAGE_ORDER:
        stage = stages[stage_id]
        core_instances = [instance for instance in stage.nodes if nodes_by_id[instance.node_id].selection_class == "core"]
        if stage_id != "purify" and len(core_instances) != 1:
            issues.append(
                _issue(
                    "selection.core_required",
                    "error",
                    stage_id,
                    None,
                    f"{_stage_label(stage_id)}阶段必须且只能有一个核心节点。",
                    "保留一个决定基础结构的核心节点，再把其他变化放入细节或调节节点。",
                )
            )
        elif len(core_instances) > 1:
            issues.append(
                _issue(
                    "selection.core_conflict",
                    "error",
                    stage_id,
                    core_instances[1].instance_id,
                    f"{_stage_label(stage_id)}阶段核心节点过多。",
                    "同一阶段只能选择一个不可叠加核心节点。",
                )
            )

        detail_seen: dict[str, NodeInstance] = {}
        exclusive_seen: dict[str, NodeInstance] = {}
        for instance in stage.nodes:
            node = nodes_by_id[instance.node_id]
            if node.selection_class != "detail":
                continue
            previous = detail_seen.get(node.id)
            if previous:
                issues.append(
                    _issue(
                        "selection.detail_duplicate",
                        "error",
                        stage_id,
                        instance.instance_id,
                        f"细节节点「{node.name}」不能重复选择。",
                        "第二类节点允许选择多种，但每种最多一个。",
                    )
                )
            detail_seen[node.id] = instance
            if not node.exclusive_group:
                continue
            previous_exclusive = exclusive_seen.get(node.exclusive_group)
            if previous_exclusive and previous_exclusive.node_id != node.id:
                previous_node = nodes_by_id[previous_exclusive.node_id]
                issues.append(
                    _issue(
                        "selection.detail_exclusive",
                        "error",
                        stage_id,
                        instance.instance_id,
                        f"细节节点「{previous_node.name}」与「{node.name}」互斥。",
                        "保留其中一个互斥细节。",
                    )
                )
            exclusive_seen[node.exclusive_group] = instance
    return issues


def _compile_stage(stage_id: StageId, stage: StageBuild, nodes_by_id: dict[str, NodeDefinition], library: NodeLibrary, context: _CompileContext) -> StageOutcome:
    definitions = [nodes_by_id[instance.node_id] for instance in stage.nodes]
    if stage_id == "model":
        context.mold_tags = list(dict.fromkeys(tag for node in definitions for tag in node.outputs))
        context.mold = _model_result(context.mold_tags)
        result = context.mold
    elif stage_id == "purify":
        context.element_keys = [output for node in definitions for output in node.outputs if output in ELEMENT_KEYS]
        context.compound = _resolve_compound(context.element_keys, library.compounds)
        context.system = system_from_key(context.element_keys[0]) if len(context.element_keys) == 1 else None
        context.element = context.compound.result if context.compound else _single_element_result(context.element_keys)
        result = context.element
    elif stage_id == "infuse":
        context.infusion_tags = list(dict.fromkeys(tag for node in definitions for tag in node.outputs))
        context.infusion = _infusion_result(context.mold, context.element, definitions)
        result = context.infusion
    else:
        release = "、".join(node.name for node in definitions)
        result = f"{release}完成"
    return StageOutcome(
        stage=stage_id,
        label=_stage_label(stage_id),
        result=result or "未形成结果",
        node_instance_ids=[instance.instance_id for instance in stage.nodes],
        tags=list(dict.fromkeys(tag for node in definitions for tag in node.tags)),
    )


def _semantic_issues(context: _CompileContext) -> list[CompileIssue]:
    issues: list[CompileIssue] = []
    if not context.mold:
        issues.append(_issue("model.no_result", "error", "model", None, "开模阶段未形成模具。", "选择球形、刃形、范围、线形或墙体节点。"))
    if not context.element:
        issues.append(_issue("purify.no_result", "error", "purify", None, "提纯阶段未形成元素结果。", "至少选择一个元素提纯节点。"))
    if context.infusion and (not context.mold or not context.element):
        issues.append(_issue("infuse.missing_input", "error", "infuse", None, "灌注缺少模具或元素输入。", "先让开模和提纯阶段形成结果。"))
    if not context.infusion:
        issues.append(_issue("release.missing_infusion", "error", "release", None, "释放缺少灌注完成的法术结构。", "让灌注阶段消费模具和元素并形成灌注结果。"))
    return issues


def _risk_issues(risk_tags: Iterable[str]) -> list[CompileIssue]:
    issues: list[CompileIssue] = []
    for tag in sorted(set(risk_tags)):
        severity = "unsafe" if tag in {"high_voltage", "governance_review"} else "warning"
        issues.append(_issue(f"risk.{tag}", severity, None, None, _risk_text(tag), "编译可继续，但需要在结果中标记并处理该风险。"))
    return issues


def _issue(rule_id: str, severity: str, stage: StageId | None, node_instance_id: str | None, message: str, suggestion: str) -> CompileIssue:
    return CompileIssue(rule_id=rule_id, severity=severity, stage=stage, node_instance_id=node_instance_id, message=message, suggestion=suggestion)


def _model_result(tags: list[str]) -> str:
    if "domain" in tags:
        return "领域框架"
    if "internal" in tags:
        return "体内边界"
    if "origin" in tags:
        return "底层原理模型"
    if "essence" in tags:
        return "本质框架"
    if "spell_process" in tags:
        return "施法过程锚点"
    if "conversion" in tags:
        return "转化团块"
    if "binding" in tags:
        return "束缚外壳"
    if "vortex" in tags:
        return "漩涡模具"
    if "field" in tags:
        return "力场外壳"
    if "guidance" in tags:
        return "导向模具"
    if "reinforcement" in tags:
        return "强化模具"
    if "target" in tags:
        return "目标锚点"
    if "ring" in tags:
        return "环状模具"
    if "cage" in tags:
        return "囚笼模具"
    if "chunk" in tags and "projectile" in tags:
        return "实体弹体"
    if "probe" in tags:
        return "侦测模具"
    if "mass" in tags:
        return "团块模具"
    if "existing" in tags:
        return "既有对象"
    if "large_area" in tags:
        return "广域边界"
    if "adaptive" in tags:
        return "自适应结构"
    if "focused" in tags:
        return "聚焦模具"
    if "core" in tags:
        return "核心应用模具"
    if "sphere" in tags and "projectile" in tags:
        return "球形弹体"
    if "blade" in tags:
        return "刃形模具"
    if "area" in tags:
        return "范围场域"
    if "line" in tags:
        return "线形路径"
    if "wall" in tags:
        return "墙体模具"
    return "复合模具"


def _single_element_result(keys: list[str]) -> str:
    names = {
        "fire": "火系法术",
        "water": "水系法术",
        "wind": "风系法术",
        "earth": "土系法术",
        "ether": "以太操作法术",
        "chaos": "混沌系法术",
        "vector": "引力系法术",
    }
    if not keys:
        return ""
    if len(keys) == 1:
        return names.get(keys[0], keys[0])
    return "未登记复合属性"


def _resolve_compound(keys: list[str], compounds: list[CompoundRule]) -> CompoundRule | None:
    if len(keys) < 2:
        return None
    primary, secondary = keys[0], keys[1]
    catalyst = keys[2] if len(keys) > 2 else None
    return next((rule for rule in compounds if rule.primary == primary and rule.secondary == secondary and rule.catalyst == catalyst), None)


def _infusion_result(mold: str | None, element: str | None, nodes: list[NodeDefinition]) -> str:
    if not mold or not element:
        return ""
    technique = "、".join(node.name for node in nodes)
    if any("多重" in node.tags for node in nodes):
        return f"多重{element}灌注至{mold}"
    return f"{element}经{technique}进入{mold}"


def _merge_score(score: dict[str, int], bias: dict[str, int]) -> None:
    for key, value in bias.items():
        if key in score:
            score[key] += value


def _clamp_score(score: dict[str, int]) -> dict[str, int]:
    return {key: max(0, min(100, value)) for key, value in score.items()}


def _assess_spell_level(nodes: list[NodeDefinition], compound: CompoundRule | None) -> SpellLevelAssessment:
    node_tiers = [node.tier for node in nodes]
    if compound:
        node_tiers.append(compound.tier)
    base_tier = max(node_tiers, default=0)
    difficulty = sum(node.difficulty for node in nodes) + (compound.difficulty if compound else 0)
    limit = DIFFICULTY_LIMITS[base_tier]
    raw_bonus = 0
    if difficulty > limit:
        raw_bonus = 1 + (difficulty - limit - 1) // DIFFICULTY_STEPS[base_tier]
    raw_tier = min(10, base_tier + raw_bonus)
    tier = _cap_tier_by_anchor(base_tier, raw_tier)
    difficulty_bonus = max(0, tier - base_tier)
    anchors = [node.name for node in nodes if node.tier == base_tier and base_tier > 0]
    if compound and compound.tier == base_tier:
        anchors.append(compound.result)
    reasons = [
        f"最高节点等阶为 {base_tier} 阶。",
        f"节点难度增幅合计 {difficulty}，当前阶容量为 {limit}。",
    ]
    if difficulty_bonus:
        reasons.append(f"难度溢出使法术上浮 {difficulty_bonus} 阶。")
    if raw_tier != tier:
        reasons.append("高阶需要本质、体内或领域锚点，已按最高锚点封顶。")
    if base_tier == 10:
        reasons.append("领域锚点直接锁定十阶法术尝试。")
    return SpellLevelAssessment(
        tier=tier,
        label=f"{tier}阶",
        base_tier=base_tier,
        difficulty=difficulty,
        difficulty_limit=limit,
        difficulty_bonus=difficulty_bonus,
        anchor_nodes=list(dict.fromkeys(anchors)),
        reasons=reasons,
    )


def _cap_tier_by_anchor(base_tier: int, raw_tier: int) -> int:
    if base_tier < 7:
        return min(raw_tier, 6)
    if base_tier < 9:
        return min(raw_tier, 8)
    if base_tier < 10:
        return min(raw_tier, 9)
    return raw_tier


def _build_radar(score: dict[str, int]) -> list[RadarScore]:
    radar: list[RadarScore] = []
    for key in RADAR_LABELS:
        value = 100 - score[key] if key in {"learnability", "mana_efficiency"} else score[key]
        direction = "higher_worse" if key in {"learnability", "mana_efficiency"} else "higher_better"
        radar.append(RadarScore(key=key, label=_radar_label(key), value=value, direction=direction, reason=_score_reason(key, value)))
    return radar


def _collect_modifiers(stages: dict[StageId, StageBuild], nodes_by_id: dict[str, NodeDefinition]) -> list[SpellModifier]:
    variant_modifiers: list[SpellModifier] = []
    buff_groups: dict[str, SpellModifier] = {}
    for stage_id in STAGE_ORDER:
        for instance in stages[stage_id].nodes:
            node = nodes_by_id[instance.node_id]
            if node.name_role == "variant":
                variant_modifiers.append(
                    SpellModifier(
                        key=node.stack_key or node.id,
                        label=node.name_affix or node.name,
                        kind="variant",
                        stage=stage_id,
                        count=1,
                        node_instance_ids=[instance.instance_id],
                    )
                )
            elif node.name_role == "buff":
                key = node.stack_key or node.id
                modifier = buff_groups.get(key)
                if modifier:
                    modifier.count += 1
                    modifier.node_instance_ids.append(instance.instance_id)
                else:
                    buff_groups[key] = SpellModifier(
                        key=key,
                        label=node.buff_label or node.name,
                        kind="buff",
                        stage=stage_id,
                        count=1,
                        node_instance_ids=[instance.instance_id],
                    )
    return variant_modifiers + list(buff_groups.values())


def _score_reason(key: str, value: int) -> str:
    if key in {"learnability", "mana_efficiency"}:
        if value >= 70:
            return "该维度负担较高，需要优化节点组合。"
        if value <= 40:
            return "该维度负担较低。"
        return "该维度处于可接受区间。"
    if value >= 70:
        return "节点组合对该维度有明显加成。"
    if value <= 40:
        return "节点组合在该维度存在明显负担。"
    return "该维度处于可用但仍需优化的区间。"


def _name_spell(
    outcomes: list[StageOutcome],
    context: _CompileContext,
    assessment: SpellLevelAssessment,
    fixed_profile: FixedSpellProfile | None,
    modifiers: list[SpellModifier],
) -> str:
    variant_prefix = "".join(modifier.label for modifier in modifiers if modifier.kind == "variant")
    if fixed_profile:
        return f"{variant_prefix}{fixed_profile.name}" if variant_prefix else fixed_profile.name
    mold = _outcome(outcomes, "model")
    element = _outcome(outcomes, "purify")
    infusion = _outcome(outcomes, "infuse")
    if element == "风系法术" and "刃" in mold and "多重" in infusion:
        return f"{variant_prefix}多重风刃" if variant_prefix else "多重风刃"
    if element == "泥沼系法术":
        return f"{variant_prefix}泥沼术" if variant_prefix else "泥沼术"
    if element == "雷电系法术":
        return f"{variant_prefix}雷电术" if variant_prefix else "雷电术"
    return "暂无"


def _summarize(outcomes: list[StageOutcome], status: str, assessment: SpellLevelAssessment) -> str:
    chain = " → ".join(outcome.result for outcome in outcomes)
    prefix = "该法术链路可执行" if status == "compiled" else "该法术链路需要审查"
    if status == "failed":
        prefix = "该法术链路无法执行"
    elif status == "unsafe":
        prefix = "该法术链路可形成结果，但高危"
    return f"{prefix}，判定为{assessment.label}：{chain}。"


def _build_card(
    request: CompileGraphRequest,
    spell_name: str,
    summary: str,
    outcomes: list[StageOutcome],
    issues: list[CompileIssue],
    risk_tags: list[str],
    assessment: SpellLevelAssessment,
) -> GraphSpellCard:
    return GraphSpellCard(
        title=spell_name,
        summary=summary,
        chain=[request.intent] + [outcome.result for outcome in outcomes] + ["代价与风险校验"],
        conditions=[
            "四阶段均需形成阶段结果。",
            "灌注必须同时消费开模结果和提纯结果。",
            "释放必须基于已完成的灌注结构。",
            "固定法术身份由完整节点签名识别，不能由元素和等阶反推。",
            "法术阶数由最高节点等阶与难度增幅共同评定。",
        ],
        costs=[
            f"法术等阶：{assessment.label}",
            f"基础锚点：{assessment.base_tier}阶",
            f"节点难度增幅：{assessment.difficulty}/{assessment.difficulty_limit}",
        ],
        risks=[_risk_text(tag) for tag in sorted(set(risk_tags))],
        suggestions=_suggestions(issues),
    )


def _suggestions(issues: list[CompileIssue]) -> list[str]:
    if not issues:
        return ["当前方案可作为普通四阶段法术 MVP 示例。"]
    return list(dict.fromkeys(issue.suggestion for issue in issues))


def _outcome(outcomes: list[StageOutcome], stage: StageId) -> str:
    return next((outcome.result for outcome in outcomes if outcome.stage == stage), "")
