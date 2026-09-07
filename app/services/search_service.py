import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

# Added requests and Path to support uploading local images to a public host for SerpApi.
from pathlib import Path
import requests

from app.config import get_settings
from app.db import get_connection
from app.services.face_service import get_face


SOCIAL_DOMAINS = (
    "facebook.com",
    "instagram.com",
    "x.com",
    "twitter.com",
    "linkedin.com",
    "reddit.com",
)


class SearchServiceError(Exception):
    pass


# SerpApi cannot access localhost URLs, so local face images must be hosted publicly before querying Google Lens.
def _upload_to_public_host(image_path: Path) -> str:
    try:
        with image_path.open("rb") as f:
            res = requests.post("https://uguu.se/upload", files={"files[]": f}, timeout=15)
            if res.status_code == 200 and res.json().get("success"):
                return res.json()["files"][0]["url"]
    except Exception:
        pass
    try:
        import base64

        data = base64.b64encode(image_path.read_bytes()).decode("utf-8")
        res = requests.post(
            "https://freeimage.host/api/1/upload",
            data={"key": "6d207e02198a847aa98d0a2a901485a5", "action": "upload", "source": data, "format": "json"},
            timeout=15,
        )
        if res.status_code == 200:
            url = res.json().get("image", {}).get("url")
            if url:
                return url
    except Exception:
        pass
    raise SearchServiceError("Failed to upload image to public host for SerpApi")


def _domain(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def _looks_social(url: str) -> bool:
    domain = _domain(url)
    return any(domain == social or domain.endswith(f".{social}") for social in SOCIAL_DOMAINS)


def _pick_match(results: dict) -> dict | None:
    matches = results.get("visual_matches") or []
    usable = [item for item in matches if item.get("link")]
    if not usable:
        return None
    social = next((item for item in usable if _looks_social(item["link"])), None)
    return social or usable[0]


def run_reverse_image_search(face_id: str) -> dict:
    settings = get_settings()
    if not settings.serpapi_api_key or settings.serpapi_api_key == "your_key_here":
        raise SearchServiceError("SERPAPI_API_KEY is not configured")

    face = get_face(face_id)
    if face is None:
        raise SearchServiceError("Face not found")

    saved_path = Path(face["saved_path"])
    # Passing a local/localhost URL to SerpApi fails because external Google Lens servers cannot reach it.
    if "localhost" in settings.app_base_url or "127.0.0.1" in settings.app_base_url:
        image_url = _upload_to_public_host(saved_path)
    else:
        image_url = f"{settings.app_base_url.rstrip('/')}/storage/faces/{face_id}.jpg"

    try:
        from serpapi import GoogleSearch

        search = GoogleSearch(
            {
                "engine": "google_lens",
                "url": image_url,
                "api_key": settings.serpapi_api_key,
            }
        )
        results = search.get_dict()
    except Exception as exc:
        raise SearchServiceError(f"SerpApi request failed: {exc}") from exc

    # SerpApi error/rate-limit responses were silently swallowed and misreported as no usable matches.
    if "error" in results:
        raise SearchServiceError(f"SerpApi error: {results['error']}")

    match = _pick_match(results)
    if match is None:
        raise SearchServiceError("SerpApi returned no usable visual matches")

    matched_url = match["link"]
    source_domain = _domain(matched_url)
    title = match.get("title") or match.get("source")
    thumbnail_url = match.get("thumbnail")
    search_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO searches
                (id, face_id, matched_url, source_domain, title, thumbnail_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (search_id, face_id, matched_url, source_domain, title, thumbnail_url, created_at),
        )

    return {
        "search_id": search_id,
        "matched_url": matched_url,
        "source_domain": source_domain,
        "title": title,
        "thumbnail_url": thumbnail_url,
    }


def get_search(search_id: str):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM searches WHERE id = ?", (search_id,)).fetchone()
