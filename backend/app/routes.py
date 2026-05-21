from fastapi import APIRouter, HTTPException

from app.catalog import get_catalog
from app.compiler import compile_spell
from app.models import Catalog, CompileRequest, CompileResult

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/catalog", response_model=Catalog)
def catalog() -> Catalog:
    return get_catalog()


@router.post("/compile", response_model=CompileResult)
def compile_endpoint(request: CompileRequest) -> CompileResult:
    try:
        return compile_spell(request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
