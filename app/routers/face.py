from fastapi import APIRouter, File, UploadFile

from app.main import app_error
from app.services.face_service import FaceDetectionError, scan_face

router = APIRouter(prefix="/api/face", tags=["face"])


@router.post("/scan")
def scan(image: UploadFile = File(...)):
    try:
        return scan_face(image)
    except FaceDetectionError as exc:
        raise app_error(422, str(exc)) from exc
    except Exception as exc:
        raise app_error(500, f"Face scan failed: {exc}") from exc
