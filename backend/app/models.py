from typing import Literal

from pydantic import BaseModel, Field


class SpellLevel(BaseModel):
    tier: int = Field(ge=0, le=10)
    name: str
    focus: str
    description: str
    steps: list[str]
    costs: list[str]
    risks: list[str]
    tags: list[str]


class Branch(BaseModel):
    id: str
    name: str
    summary: str
    spells: list[SpellLevel]


class Element(BaseModel):
    id: str
    name: str
    color: str
    nature: str
    strength: str
    weakness: str
    build_hint: str
    branches: list[Branch]


class Catalog(BaseModel):
    version: str
    sources: list[str]
    elements: list[Element]


class CasterProfile(BaseModel):
    focus: int = Field(60, ge=0, le=100)
    control: int = Field(60, ge=0, le=100)
    knowledge: int = Field(2, ge=0, le=10)


class CompileRequest(BaseModel):
    element_id: str
    branch_id: str | None = None
    tier: int = Field(1, ge=0, le=10)
    intent: str = "验证并输出可执行法术"
    carrier: Literal["手势", "咏唱", "法杖", "魔法阵", "魔石", "卷轴"] = "法杖"
    technique: Literal["标准", "压缩", "扩散", "延迟", "多重", "序列"] = "标准"
    environment: Literal["训练场", "野外", "城镇", "战斗", "结界内"] = "训练场"
    caster: CasterProfile = Field(default_factory=CasterProfile)


class ScoreSet(BaseModel):
    executable: int
    stability: int
    cost: int
    governance: int


class SpellCard(BaseModel):
    title: str
    subtitle: str
    purpose: str
    chain: list[str]
    conditions: list[str]
    costs: list[str]
    risks: list[str]
    suggestions: list[str]
    source: str


class CompileResult(BaseModel):
    status: Literal["compiled", "partial", "failed", "unsafe"]
    selected_spell: SpellLevel
    element: Element
    branch: Branch
    scores: ScoreSet
    warnings: list[str]
    errors: list[str]
    spell_card: SpellCard


StageId = Literal["model", "purify", "infuse", "release"]


class StageDefinition(BaseModel):
    id: StageId
    name: str
    purpose: str


class NodeDefinition(BaseModel):
    id: str
    stage: StageId
    name: str
    category: str
    summary: str
    outputs: list[str]
    tags: list[str] = Field(default_factory=list)
    risk_tags: list[str] = Field(default_factory=list)
    score_bias: dict[str, int] = Field(default_factory=dict)


class CompoundRule(BaseModel):
    primary: str
    secondary: str
    catalyst: str | None = None
    result: str
    form: str
    risk_tags: list[str] = Field(default_factory=list)
    score_bias: dict[str, int] = Field(default_factory=dict)


class NodeLibrary(BaseModel):
    version: str
    stages: list[StageDefinition]
    nodes: list[NodeDefinition]
    compounds: list[CompoundRule]


class NodeInstance(BaseModel):
    instance_id: str
    node_id: str
    params: dict[str, str | int | float | bool] = Field(default_factory=dict)


class StageBuild(BaseModel):
    stage: StageId
    nodes: list[NodeInstance]


class CompileGraphRequest(BaseModel):
    id: str | None = None
    intent: str = "验证并输出可执行法术"
    stages: list[StageBuild]
    caster: CasterProfile = Field(default_factory=CasterProfile)
    context: dict[str, str | int | float | bool] = Field(default_factory=dict)


class StageOutcome(BaseModel):
    stage: StageId
    label: str
    result: str
    node_instance_ids: list[str]
    tags: list[str] = Field(default_factory=list)


class CompileIssue(BaseModel):
    rule_id: str
    severity: Literal["error", "warning", "unsafe"]
    stage: StageId | None = None
    node_instance_id: str | None = None
    message: str
    suggestion: str


class RadarScore(BaseModel):
    key: Literal["power", "stability", "learnability", "mana_efficiency", "versatility", "academic_value", "safety"]
    label: str
    value: int = Field(ge=0, le=100)
    direction: Literal["higher_better"] = "higher_better"
    reason: str


class GraphSpellCard(BaseModel):
    title: str
    summary: str
    chain: list[str]
    conditions: list[str]
    costs: list[str]
    risks: list[str]
    suggestions: list[str]


class CompileGraphResult(BaseModel):
    status: Literal["compiled", "partial", "failed", "unsafe"]
    spell_name: str
    summary: str
    stage_outcomes: list[StageOutcome]
    issues: list[CompileIssue]
    radar: list[RadarScore]
    spell_card: GraphSpellCard
