import json
from functools import lru_cache
from pathlib import Path

from app.models import CompileGraphRequest, NodeLibrary

ROOT = Path(__file__).resolve().parents[2]
NODE_LIBRARY_PATH = ROOT / "data" / "nodes" / "mvp_nodes.json"
EXAMPLES_PATH = ROOT / "data" / "examples"


@lru_cache
def get_node_library() -> NodeLibrary:
    return NodeLibrary.model_validate_json(NODE_LIBRARY_PATH.read_text(encoding="utf-8"))


def get_examples() -> list[CompileGraphRequest]:
    examples: list[CompileGraphRequest] = []
    for path in sorted(EXAMPLES_PATH.glob("*.json")):
        examples.append(CompileGraphRequest.model_validate(json.loads(path.read_text(encoding="utf-8"))))
    return examples
