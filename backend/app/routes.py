from fastapi import APIRouter, HTTPException

from app.catalog import get_catalog
from app.compiler import compile_spell
from app.graph_compiler import compile_graph
from app.models import Catalog, CompileGraphRequest, CompileGraphResult, CompileRequest, CompileResult, NodeLibrary
from app.node_library import get_examples, get_node_library
from app.text_library import get_text_bundle

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/catalog", response_model=Catalog)
def catalog() -> Catalog:
    return get_catalog()


@router.get("/nodes", response_model=NodeLibrary)
def nodes() -> NodeLibrary:
    return get_node_library()


@router.get("/examples", response_model=list[CompileGraphRequest])
def examples() -> list[CompileGraphRequest]:
    return get_examples()


@router.get("/texts")
def texts() -> dict:
    return get_text_bundle()


@router.post("/compile", response_model=CompileResult)
def compile_endpoint(request: CompileRequest) -> CompileResult:
    try:
        return compile_spell(request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/compile-graph", response_model=CompileGraphResult)
def compile_graph_endpoint(request: CompileGraphRequest) -> CompileGraphResult:
    return compile_graph(request)
