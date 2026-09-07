# FaceVerify

FaceVerify is a FastAPI-based project that scans an uploaded face image, performs reverse image lookup with Google Lens (via SerpApi), and stores the resulting match in a locally verifiable SHA-256 blockchain.

It includes both:
- a backend API for the full face→search→chain workflow, and
- a lightweight web UI served from the same app.

## Features

- Face scan endpoint using DeepFace embeddings
- Reverse image lookup via SerpApi Google Lens
- Match persistence in SQLite
- Local blockchain with:
  - genesis block creation
  - append-only commits for search results
  - single-block and full-chain verification
- End-to-end pipeline endpoint (`scan -> search -> chain commit`)
- Browser UI for upload, pipeline execution, and chain inspection

## Tech Stack

- **Backend:** FastAPI, Uvicorn
- **AI / Vision:** DeepFace, OpenCV, NumPy, tf-keras
- **Storage:** SQLite
- **Search Integration:** SerpApi (`google-search-results`)
- **Config:** pydantic-settings, python-dotenv
- **Frontend:** HTML, CSS, vanilla JavaScript

## Installation

### 1) Clone and enter the project

```bash
git clone https://github.com/APEX-BUILDERS/FaceVerify.git
cd FaceVerify
```

### 2) Create a virtual environment

**Linux/macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the repository root:

```env
SERPAPI_API_KEY=your_serpapi_key
APP_BASE_URL=http://localhost:8000
```

Notes:
- `SERPAPI_API_KEY` is required for reverse image search.
- `APP_BASE_URL` defaults to `http://localhost:8000` if omitted.
- When running locally on localhost, the app uploads images to a temporary public host so SerpApi can access them.

## Usage

Start the server:

```bash
uvicorn app.main:app --reload
```

Then open:
- **Web UI:** `http://localhost:8000/`
- **API docs:** `http://localhost:8000/docs`

### Example API calls

Run full pipeline:

```bash
curl -X POST "http://localhost:8000/api/pipeline/run" -F "image=@/path/to/face.jpg"
```

Read full chain:

```bash
curl "http://localhost:8000/api/chain/full"
```

## Project Structure

```text
FaceVerify/
├── app/
│   ├── main.py                # FastAPI app + router registration + static mounts
│   ├── config.py              # settings, storage and DB paths
│   ├── db.py                  # SQLite initialization and connection helper
│   ├── routers/               # API routes (face, search, chain, pipeline)
│   ├── services/              # business logic for face scan, search, blockchain
│   └── storage/               # runtime-created DB and uploaded faces
├── web/                       # static frontend served by FastAPI
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Make focused changes
4. Open a pull request with a clear description

## License

No license file is currently included in this repository.
If you plan to open-source this project broadly, add a license (for example, MIT) in a `LICENSE` file.

## Contact / Support

- Open an issue in this repository for bugs, ideas, or support requests.
