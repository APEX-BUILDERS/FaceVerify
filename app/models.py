from typing import Any

from pydantic import BaseModel


class FaceScanResponse(BaseModel):
    face_id: str
    embedding_len: int
    saved_path: str


class SearchResponse(BaseModel):
    search_id: str
    matched_url: str
    source_domain: str
    title: str | None = None
    thumbnail_url: str | None = None


class BlockResponse(BaseModel):
    index: int
    timestamp: str
    data_hash: str
    previous_hash: str
    hash: str


class VerifyResponse(BaseModel):
    valid: bool
    stored_hash: str
    recomputed_hash: str


class ChainFullResponse(BaseModel):
    valid: bool
    chain: list[dict[str, Any]]
