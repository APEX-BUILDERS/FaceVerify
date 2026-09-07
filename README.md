<<<<<<< HEAD
# FaceVerify
=======
# FaceVerify

FaceVerify is a local FastAPI backend that scans an uploaded face image, performs a real Google Lens reverse-image search through SerpApi, and stores the discovered match in a verifiable local blockchain. It is built for hackathon demos where the whole pipeline can run in one local server process, with only the reverse-search step requiring internet access.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# edit .env and set SERPAPI_API_KEY
uvicorn app.main:app --reload
```

Linux/macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and set SERPAPI_API_KEY
uvicorn app.main:app --reload
```

## Blockchain

FaceVerify uses a local, self-hosted, SHA-256-linked block chain (not a public network) — chosen for offline reliability during the hackathon window; swapping in a public testnet via web3.py is a documented future step, not required by the task.

## Known Limitations

- SerpApi free tier call limit is 100 searches/month.
- Reverse-search quality depends on the input photo and whether matching public posts exist.
- DeepFace first run downloads model weights and needs internet once.

## Demo Curl

```bash
curl -X POST "http://localhost:8000/api/pipeline/run" -F "image=@/path/to/face.jpg"
```

Check the chain:

```bash
curl "http://localhost:8000/api/chain/full"
```
>>>>>>> master
