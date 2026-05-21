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
