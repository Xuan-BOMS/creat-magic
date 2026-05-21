from app.catalog import get_catalog
from app.models import Branch, CompileRequest, CompileResult, Element, ScoreSet, SpellCard, SpellLevel

TECHNIQUE_EFFECTS = {
    "标准": {"stability": 4, "cost": 4, "warning": None, "step": None},
    "压缩": {"stability": -8, "cost": -10, "warning": "压缩会提高密度与威力，但载体承压和失控风险上升。", "step": "压缩"},
    "扩散": {"stability": -10, "cost": -12, "warning": "扩散会扩大覆盖面，必须额外校验环境与误伤。", "step": "扩散"},
    "延迟": {"stability": -14, "cost": -16, "warning": "延迟需要维持方案，否则会持续扣除精神力并提高失控概率。", "step": "延迟维持"},
    "多重": {"stability": -18, "cost": -18, "warning": "多重是并行施法窗口，不等同于连续释放，注意力并发要求很高。", "step": "多重并发"},
    "序列": {"stability": -6, "cost": -8, "warning": "序列依赖条件触发与肌肉记忆，条件定义越模糊越容易误触发。", "step": "序列触发"},
}

CARRIER_EFFECTS = {
    "手势": {"stability": 0, "cost": 0, "condition": "手势承担精神力汇聚与方向控制。"},
    "咏唱": {"stability": 8, "cost": -4, "condition": "咏唱提高参数精度，但会暴露意图并延长施法窗口。"},
    "法杖": {"stability": 10, "cost": 6, "condition": "法杖负责汇聚与导流，提高一致性和容错率。"},
    "魔法阵": {"stability": 14, "cost": 8, "condition": "魔法阵把部分流程前置为公式，降低实时负担。"},
    "魔石": {"stability": 6, "cost": 12, "condition": "魔石节省提纯时间，但存在材料成本和爆裂风险。"},
    "卷轴": {"stability": 12, "cost": 10, "condition": "卷轴预置阵图与材料，适合稳定释放一次性结构。"},
}

ENVIRONMENT_RISKS = {
    "训练场": [],
    "野外": ["环境变量较多，落点和材料条件需复核。"],
    "城镇": ["城镇场景治理风险上升，火、风、以太高阶尤其需要授权。"],
    "战斗": ["战斗压力会增加被打断和步骤误差。"],
    "结界内": ["结界内规则可能改变施法优先级，需要确认主循环兼容。"],
}


def _find_element(element_id: str) -> Element | None:
    return next((item for item in get_catalog().elements if item.id == element_id), None)


def _find_branch(element: Element, branch_id: str | None) -> Branch:
    if branch_id:
        match = next((item for item in element.branches if item.id == branch_id), None)
        if match:
            return match
    return element.branches[0]


def _find_spell(branch: Branch, tier: int) -> SpellLevel:
    return next(item for item in branch.spells if item.tier == tier)


def _clamp(value: int) -> int:
    return max(0, min(100, value))


def compile_spell(request: CompileRequest) -> CompileResult:
    element = _find_element(request.element_id)
    if not element:
        raise ValueError(f"Unknown element: {request.element_id}")

    branch = _find_branch(element, request.branch_id)
    spell = _find_spell(branch, request.tier)
    technique = TECHNIQUE_EFFECTS[request.technique]
    carrier = CARRIER_EFFECTS[request.carrier]

    required_knowledge = spell.tier
    warnings: list[str] = []
    errors: list[str] = []
    if request.caster.knowledge < required_knowledge:
        errors.append(f"施法者知识刻度为 {request.caster.knowledge}，不足以稳定使用 {spell.tier} 阶的「{spell.name}」。")
    if request.caster.focus < 25:
        errors.append("精神力过低，无法完成开模、提纯、灌注、释放的连续流程。")
    if request.caster.control < 25:
        errors.append("控制力过低，法术结构无法稳定成型。")

    if technique["warning"]:
        warnings.append(str(technique["warning"]))
    warnings.extend(ENVIRONMENT_RISKS[request.environment])

    if request.environment == "城镇" and (element.id == "fire" or spell.tier >= 5):
        warnings.append("该组合在城镇中可能被判为非授权高危施法。")
    if spell.tier >= 9:
        warnings.append("九阶以上涉及体内边界或领域逻辑，默认需要授权与治理审查。")
    if element.id == "ether" and spell.tier >= 5:
        warnings.append("以太高阶存在魔中毒、现实错位或精神污染风险。")

    base = 78 + min(request.caster.knowledge - required_knowledge, 2) * 4
    executable = _clamp(base + request.caster.focus // 10 + request.caster.control // 12 - max(0, spell.tier - 4) * 5)
    stability = _clamp(70 + request.caster.control // 5 + int(carrier["stability"]) + int(technique["stability"]) - spell.tier * 5)
    cost = _clamp(82 + request.caster.focus // 8 + int(carrier["cost"]) + int(technique["cost"]) - spell.tier * 6)
    governance = _clamp(90 - spell.tier * 6 - len(warnings) * 3)

    if spell.tier >= 9:
        governance = min(governance, 36)
    if errors:
        status = "failed"
    elif governance < 40:
        status = "unsafe"
    elif min(executable, stability, cost) < 55:
        status = "partial"
    else:
        status = "compiled"

    chain = [request.intent, element.name, branch.name, spell.name]
    if technique["step"]:
        chain.append(str(technique["step"]))
    chain.extend(spell.steps)
    chain.append(request.carrier)
    chain.append("风险与代价校验")

    suggestions = _build_suggestions(request, spell, warnings, errors)
    card = SpellCard(
        title=f"{request.technique if request.technique != '标准' else ''}{spell.name}".strip(),
        subtitle=f"{element.name} / {branch.name} / {spell.tier}阶",
        purpose=request.intent,
        chain=chain,
        conditions=[
            f"施法者知识刻度至少达到 {spell.tier}。",
            carrier["condition"],
            f"当前环境：{request.environment}。",
            f"构建逻辑：{element.build_hint}",
        ],
        costs=spell.costs + [f"技巧代价：{request.technique}", f"载体：{request.carrier}"],
        risks=spell.risks + warnings,
        suggestions=suggestions,
        source="; ".join(get_catalog().sources),
    )

    return CompileResult(
        status=status,
        selected_spell=spell,
        element=element,
        branch=branch,
        scores=ScoreSet(executable=executable, stability=stability, cost=cost, governance=governance),
        warnings=warnings,
        errors=errors,
        spell_card=card,
    )


def _build_suggestions(request: CompileRequest, spell: SpellLevel, warnings: list[str], errors: list[str]) -> list[str]:
    suggestions: list[str] = []
    if errors:
        suggestions.append("先降低法术阶位，或提高施法者知识刻度后再尝试。")
    if request.carrier in {"手势", "咏唱"} and spell.tier >= 3:
        suggestions.append("改用法杖、魔法阵或卷轴承担部分流程，可提高稳定性。")
    if request.technique in {"多重", "延迟"}:
        suggestions.append("为技巧增加明确触发条件或维持结构，避免注意力被持续拉空。")
    if request.environment == "城镇":
        suggestions.append("切换到训练场或结界内测试，避免外溢风险影响编译结论。")
    if spell.tier >= 9:
        suggestions.append("九阶以上建议只作为资料预览，实际施法应标记为授权或禁用。")
    if not suggestions:
        suggestions.append("该构建可作为雏形输出，后续可加入目标、射程、持续时间和材料参数。")
    if warnings:
        suggestions.append("逐条处理警告后再次编译，优先解决治理与稳定性问题。")
    return suggestions
