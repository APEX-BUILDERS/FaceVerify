from fastapi import APIRouter, File, UploadFile

from app.main import app_error
from app.services.chain_service import ChainServiceError, add_block
from app.services.face_service import FaceDetectionError, scan_face
from app.services.search_service import SearchServiceError, run_reverse_image_search

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


@router.post("/run")
def run_pipeline(image: UploadFile = File(...)):
    try:
        face = scan_face(image)
        search_result = run_reverse_image_search(face["face_id"])
        block = add_block(search_result["search_id"])
        return {
            "face_id": face["face_id"],
            "search_result": search_result,
            "block": block,
        }
    except FaceDetectionError as exc:
        raise app_error(422, str(exc)) from exc
    except SearchServiceError as exc:
        raise app_error(502, str(exc)) from exc
    except ChainServiceError as exc:
        raise app_error(500, str(exc)) from exc
    except Exception as exc:
        raise app_error(500, f"Pipeline failed: {exc}") from exc
