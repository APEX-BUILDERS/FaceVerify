import sqlite3

from app.config import DB_PATH, FACES_DIR, STORAGE_DIR


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    FACES_DIR.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS faces (
                id TEXT PRIMARY KEY,
                saved_path TEXT NOT NULL,
                embedding_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS searches (
                id TEXT PRIMARY KEY,
                face_id TEXT NOT NULL,
                matched_url TEXT NOT NULL,
                source_domain TEXT NOT NULL,
                title TEXT,
                thumbnail_url TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(face_id) REFERENCES faces(id)
            );

            CREATE TABLE IF NOT EXISTS blocks (
                index_id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                data_hash TEXT NOT NULL,
                data_payload_json TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                hash TEXT NOT NULL
            );
            """
        )
