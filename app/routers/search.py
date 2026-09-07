from fastapi import APIRouter

from app.main import app_error
from app.services.search_service import SearchServiceError, run_reverse_image_search

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/{face_id}")
def search(face_id: str):
    try:
        return run_reverse_image_search(face_id)
    except SearchServiceError as exc:
        message = str(exc)
        status = 404 if message == "Face not found" else 502
        raise app_error(status, message) from exc
    except Exception as exc:
        raise app_error(500, f"Reverse image search failed: {exc}") from exc
