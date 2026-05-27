import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TEXTS_PATH = ROOT / "data" / "texts" / "zh_cn.json"


def get_text_bundle() -> dict[str, Any]:
    return json.loads(TEXTS_PATH.read_text(encoding="utf-8"))


def get_app_texts() -> dict[str, Any]:
    return get_text_bundle().get("app", {})


def get_compiler_texts() -> dict[str, Any]:
    return get_text_bundle().get("compiler", {})


def get_fixed_spell_text(spell_id: str, fallback_name: str, fallback_summary: str) -> tuple[str, str]:
    spell = get_text_bundle().get("fixed_spells", {}).get(spell_id, {})
    return spell.get("name", fallback_name), spell.get("summary", fallback_summary)


def get_system_name(system: str, fallback: str) -> str:
    return get_compiler_texts().get("system_names", {}).get(system, fallback)
