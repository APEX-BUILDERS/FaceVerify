from fastapi import APIRouter

from app.main import app_error
from app.services.chain_service import (
    ChainServiceError,
    add_block,
    get_chain,
    verify_block,
    verify_chain,
)

router = APIRouter(prefix="/api/chain", tags=["chain"])


@router.post("/commit/{search_id}")
def commit(search_id: str):
    try:
        return add_block(search_id)
    except ChainServiceError as exc:
        status = 404 if str(exc) == "Search result not found" else 500
        raise app_error(status, str(exc)) from exc
    except Exception as exc:
        raise app_error(500, f"Chain commit failed: {exc}") from exc


@router.get("/verify/{block_index}")
def verify(block_index: int):
    try:
        return verify_block(block_index)
    except ChainServiceError as exc:
        raise app_error(404, str(exc)) from exc
    except Exception as exc:
        raise app_error(500, f"Block verification failed: {exc}") from exc


@router.get("/full")
def full():
    try:
        return {"valid": verify_chain(), "chain": get_chain()}
    except Exception as exc:
        raise app_error(500, f"Chain read failed: {exc}") from exc
