import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from app.db import get_connection
from app.services.search_service import get_search


GENESIS_PAYLOAD = {"genesis": True}
GENESIS_PREVIOUS_HASH = "0"


class ChainServiceError(Exception):
    pass


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def data_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def block_hash(index: int, timestamp: str, payload_hash: str, previous_hash: str) -> str:
    raw = f"{index}|{timestamp}|{payload_hash}|{previous_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _row_to_block(row) -> dict[str, Any]:
    payload = json.loads(row["data_payload_json"])
    return {
        "index": row["index_id"],
        "timestamp": row["timestamp"],
        "data_hash": row["data_hash"],
        "data_payload": payload,
        "previous_hash": row["previous_hash"],
        "hash": row["hash"],
    }


def ensure_genesis_block() -> None:
    with get_connection() as conn:
        existing = conn.execute("SELECT COUNT(*) AS count FROM blocks").fetchone()["count"]
        if existing:
            return
        timestamp = datetime.now(timezone.utc).isoformat()
        payload_hash = data_hash(GENESIS_PAYLOAD)
        digest = block_hash(0, timestamp, payload_hash, GENESIS_PREVIOUS_HASH)
        conn.execute(
            """
            INSERT INTO blocks
                (index_id, timestamp, data_hash, data_payload_json, previous_hash, hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (0, timestamp, payload_hash, canonical_json(GENESIS_PAYLOAD), GENESIS_PREVIOUS_HASH, digest),
        )


def build_payload(search_id: str) -> dict[str, Any]:
    search = get_search(search_id)
    if search is None:
        raise ChainServiceError("Search result not found")
    return {
        "matched_url": search["matched_url"],
        "source_domain": search["source_domain"],
        "title": search["title"],
        "thumbnail_url": search["thumbnail_url"],
        "face_id": search["face_id"],
        "timestamp": search["created_at"],
    }


def add_block(search_id: str) -> dict[str, Any]:
    payload = build_payload(search_id)
    payload_hash = data_hash(payload)
    timestamp = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        previous = conn.execute(
            "SELECT * FROM blocks ORDER BY index_id DESC LIMIT 1"
        ).fetchone()
        if previous is None:
            raise ChainServiceError("Genesis block is missing")

        index = previous["index_id"] + 1
        previous_hash = previous["hash"]
        digest = block_hash(index, timestamp, payload_hash, previous_hash)
        conn.execute(
            """
            INSERT INTO blocks
                (index_id, timestamp, data_hash, data_payload_json, previous_hash, hash)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (index, timestamp, payload_hash, canonical_json(payload), previous_hash, digest),
        )

    return {
        "index": index,
        "timestamp": timestamp,
        "data_hash": payload_hash,
        "previous_hash": previous_hash,
        "hash": digest,
    }


def verify_block(block_index: int, data_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM blocks WHERE index_id = ?", (block_index,)).fetchone()
    if row is None:
        raise ChainServiceError("Block not found")

    payload = data_payload if data_payload is not None else json.loads(row["data_payload_json"])
    recomputed_data_hash = data_hash(payload)
    recomputed_hash = block_hash(
        row["index_id"],
        row["timestamp"],
        recomputed_data_hash,
        row["previous_hash"],
    )
    return {
        "valid": recomputed_data_hash == row["data_hash"] and recomputed_hash == row["hash"],
        "stored_hash": row["hash"],
        "recomputed_hash": recomputed_hash,
    }


def verify_chain() -> bool:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM blocks ORDER BY index_id ASC").fetchall()

    if not rows:
        return False

    previous_hash = GENESIS_PREVIOUS_HASH
    for expected_index, row in enumerate(rows):
        if row["index_id"] != expected_index:
            return False
        payload = json.loads(row["data_payload_json"])
        payload_hash = data_hash(payload)
        digest = block_hash(row["index_id"], row["timestamp"], payload_hash, row["previous_hash"])
        if payload_hash != row["data_hash"] or digest != row["hash"] or row["previous_hash"] != previous_hash:
            return False
        previous_hash = row["hash"]
    return True


def get_chain() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM blocks ORDER BY index_id ASC").fetchall()
    return [_row_to_block(row) for row in rows]
