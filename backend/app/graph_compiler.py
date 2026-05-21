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
    StageBuild,
    StageId,
    StageOutcome,
)
from app.node_library import get_node_library

STAGE_ORDER: list[StageId] = ["model", "purify", "infuse", "release"]
STAGE_LABELS: dict[StageId, str] = {
    "model": "开模",
    "purify": "提纯",
    "infuse": "灌注",
    "release": "释放",
}
RADAR_LABELS: dict[str, str] = {
    "power": "威力",
    "stability": "稳定性",
    "learnability": "易学性",
    "mana_efficiency": "魔力效率",
    "versatility": "泛用性",
    "academic_value": "学术价值",
    "safety": "安全性",
}
BASE_SCORE = {
    "power": 48,
    "stability": 62,
    "learnability": 60,
    "mana_efficiency": 58,
    "versatility": 55,
    "academic_value": 45,
    "safety": 64,
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
}


def compile_graph(request: CompileGraphRequest) -> CompileGraphResult:
    library = get_node_library()
    nodes_by_id = {node.id: node for node in library.nodes}
    stages = {stage.stage: stage for stage in request.stages}
    issues = _validate_request(request, library, nodes_by_id, stages)
    stage_outcomes: list[StageOutcome] = []
    score = dict(BASE_SCORE)
    risk_tags: list[str] = []

    if not any(issue.severity == "error" for issue in issues):
        context = _CompileContext()
        for stage_id in STAGE_ORDER:
            outcome = _compile_stage(stage_id, stages[stage_id], nodes_by_id, library, context)
            stage_outcomes.append(outcome)
            for instance in stages[stage_id].nodes:
                node = nodes_by_id[instance.node_id]
                _merge_score(score, node.score_bias)
                risk_tags.extend(node.risk_tags)
            if stage_id == "purify" and context.compound:
                _merge_score(score, context.compound.score_bias)
                risk_tags.extend(context.compound.risk_tags)
        issues.extend(_semantic_issues(context))

    if any(issue.severity == "error" for issue in issues):
        status = "failed"
    else:
        if risk_tags:
            issues.extend(_risk_issues(risk_tags))
        score = _apply_caster(score, request)
        if score["safety"] < 45 or any(issue.severity == "unsafe" for issue in issues):
            status = "unsafe"
        elif min(score["stability"], score["mana_efficiency"]) < 45:
            status = "partial"
        else:
            status = "compiled"

    spell_name = _name_spell(stage_outcomes)
    summary = _summarize(stage_outcomes, status)
    radar = _build_radar(score)
    card = _build_card(request, spell_name, summary, stage_outcomes, issues, risk_tags)
    return CompileGraphResult(
        status=status,
        spell_name=spell_name,
        summary=summary,
        stage_outcomes=stage_outcomes,
        issues=issues,
        radar=radar,
        spell_card=card,
    )


class _CompileContext:
    mold: str | None = None
    mold_tags: list[str] = []
    element: str | None = None
    element_keys: list[str] = []
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
            issues.append(_issue("stage.duplicate", "error", stage.stage, None, f"{STAGE_LABELS[stage.stage]}阶段重复。", "每个固定阶段只能出现一次。"))
        seen_stages.add(stage.stage)

    for stage_id in STAGE_ORDER:
        stage = stages.get(stage_id)
        if not stage:
            issues.append(_issue("stage.missing", "error", stage_id, None, f"缺少{STAGE_LABELS[stage_id]}阶段。", "补齐四个固定阶段后再编译。"))
            continue
        if not stage.nodes:
            issues.append(_issue("stage.empty", "error", stage_id, None, f"{STAGE_LABELS[stage_id]}阶段没有节点。", "至少放入一个可产生阶段结果的节点。"))
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
                issues.append(_issue("node.wrong_stage", "error", stage_id, instance.instance_id, f"节点「{node.name}」不能放在{STAGE_LABELS[stage_id]}阶段。", f"将它移动到{STAGE_LABELS[node.stage]}阶段。"))
    known_stages = {stage.id for stage in library.stages}
    for stage in request.stages:
        if stage.stage not in known_stages:
            issues.append(_issue("stage.unknown", "error", None, None, f"未知阶段 {stage.stage}。", "使用固定四阶段。"))
    return issues


def _compile_stage(stage_id: StageId, stage: StageBuild, nodes_by_id: dict[str, NodeDefinition], library: NodeLibrary, context: _CompileContext) -> StageOutcome:
    definitions = [nodes_by_id[instance.node_id] for instance in stage.nodes]
    if stage_id == "model":
        context.mold_tags = list(dict.fromkeys(tag for node in definitions for tag in node.outputs))
        context.mold = _model_result(context.mold_tags)
        result = context.mold
    elif stage_id == "purify":
        context.element_keys = [node.outputs[0] for node in definitions if node.outputs]
        context.compound = _resolve_compound(context.element_keys, library.compounds)
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
        label=STAGE_LABELS[stage_id],
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
        issues.append(_issue(f"risk.{tag}", severity, None, None, RISK_TEXT.get(tag, tag), "编译可继续，但需要在结果中标记并处理该风险。"))
    return issues


def _issue(rule_id: str, severity: str, stage: StageId | None, node_instance_id: str | None, message: str, suggestion: str) -> CompileIssue:
    return CompileIssue(rule_id=rule_id, severity=severity, stage=stage, node_instance_id=node_instance_id, message=message, suggestion=suggestion)


def _model_result(tags: list[str]) -> str:
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
    names = {"fire": "火系法术", "water": "水系法术", "wind": "风系法术", "earth": "土系法术", "ether": "以太操作法术"}
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


def _apply_caster(score: dict[str, int], request: CompileGraphRequest) -> dict[str, int]:
    score["stability"] += request.caster.control // 10 - 5
    score["mana_efficiency"] += request.caster.focus // 12 - 5
    score["learnability"] += request.caster.knowledge * 2 - 6
    return {key: max(0, min(100, value)) for key, value in score.items()}


def _build_radar(score: dict[str, int]) -> list[RadarScore]:
    return [
        RadarScore(key=key, label=RADAR_LABELS[key], value=score[key], reason=_score_reason(key, score[key]))
        for key in RADAR_LABELS
    ]


def _score_reason(key: str, value: int) -> str:
    if key == "safety" and value < 45:
        return "该方案存在高危外溢或治理审查标签。"
    if value >= 70:
        return "节点组合对该维度有明显加成。"
    if value <= 40:
        return "节点组合在该维度存在明显负担。"
    return "该维度处于可用但仍需优化的区间。"


def _name_spell(outcomes: list[StageOutcome]) -> str:
    mold = _outcome(outcomes, "model")
    element = _outcome(outcomes, "purify")
    infusion = _outcome(outcomes, "infuse")
    if element == "火系法术" and mold == "球形弹体":
        return "火球术"
    if element == "风系法术" and "刃" in mold and "多重" in infusion:
        return "多重风刃"
    if element == "泥沼系法术":
        return "泥沼术"
    if element == "雷电系法术":
        return "雷电术"
    if element.endswith("法术"):
        return element
    return "未命名法术"


def _summarize(outcomes: list[StageOutcome], status: str) -> str:
    chain = " → ".join(outcome.result for outcome in outcomes)
    prefix = "该法术链路可执行" if status == "compiled" else "该法术链路需要审查"
    if status == "failed":
        prefix = "该法术链路无法执行"
    elif status == "unsafe":
        prefix = "该法术链路可形成结果，但高危"
    return f"{prefix}：{chain}。"


def _build_card(
    request: CompileGraphRequest,
    spell_name: str,
    summary: str,
    outcomes: list[StageOutcome],
    issues: list[CompileIssue],
    risk_tags: list[str],
) -> GraphSpellCard:
    return GraphSpellCard(
        title=spell_name,
        summary=summary,
        chain=[request.intent] + [outcome.result for outcome in outcomes] + ["代价与风险校验"],
        conditions=[
            "四阶段均需形成阶段结果。",
            "灌注必须同时消费开模结果和提纯结果。",
            "释放必须基于已完成的灌注结构。",
        ],
        costs=[
            f"精神力：{request.caster.focus}",
            f"控制力：{request.caster.control}",
            f"知识刻度：{request.caster.knowledge}",
        ],
        risks=[RISK_TEXT.get(tag, tag) for tag in sorted(set(risk_tags))],
        suggestions=_suggestions(issues),
    )


def _suggestions(issues: list[CompileIssue]) -> list[str]:
    if not issues:
        return ["当前方案可作为普通四阶段法术 MVP 示例。"]
    return list(dict.fromkeys(issue.suggestion for issue in issues))


def _outcome(outcomes: list[StageOutcome], stage: StageId) -> str:
    return next((outcome.result for outcome in outcomes if outcome.stage == stage), "")
