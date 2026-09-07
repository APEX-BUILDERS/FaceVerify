import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

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
