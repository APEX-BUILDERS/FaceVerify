import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from fastapi import UploadFile

from app.config import FACES_DIR
from app.db import get_connection


class FaceDetectionError(Exception):
    pass


def _extract_embedding(img: np.ndarray) -> list[float]:
    from deepface import DeepFace

    result = None
    # Try retinaface as primary detector, fallback to opencv if it throws
    for backend in ("retinaface", "opencv"):
        try:
            # Set enforce_detection=False to prevent hard crashes on borderline detection
            result = DeepFace.represent(
                img_path=img,
                model_name="Facenet",
                detector_backend=backend,
                enforce_detection=False,
            )
            if result:
                break
        except Exception:
            continue

    # Manually check if face detection result is empty before raising 422
    if not result:
        raise FaceDetectionError("No face detected in uploaded image")

    face = result[0] if isinstance(result, list) else result
    # Check if a face was detected with non-zero confidence when enforce_detection=False
    if isinstance(face, dict) and face.get("face_confidence", 1.0) == 0.0:
        raise FaceDetectionError("No face detected in uploaded image")

    embedding = face.get("embedding") if isinstance(face, dict) else None
    # Ensure embedding list is present and non-empty
    if not embedding:
        raise FaceDetectionError("No face embedding produced")
    return [float(value) for value in embedding]


def scan_face(image: UploadFile) -> dict:
    face_id = str(uuid.uuid4())
    saved_path = FACES_DIR / f"{face_id}.jpg"

    # Read uploaded image bytes directly
    image_bytes = image.file.read()
    with saved_path.open("wb") as out:
        out.write(image_bytes)

    # Decode raw bytes into a numpy/OpenCV BGR array before passing to DeepFace
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    # Validate decoded image array
    if img is None:
        raise FaceDetectionError("Failed to decode uploaded image")

    embedding = _extract_embedding(img)
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO faces (id, saved_path, embedding_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (face_id, str(saved_path), json.dumps(embedding), created_at),
        )

    return {
        "face_id": face_id,
        "embedding_len": len(embedding),
        "saved_path": str(saved_path),
    }


def get_face(face_id: str):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM faces WHERE id = ?", (face_id,)).fetchone()
