# 🔐 FaceVerify

### AI-Powered Face Discovery & Verifiable Evidence System

> **Scan a face → extract its identity representation → search the public web → discover potential matches → permanently record the result in a tamper-evident local blockchain.**

**FaceVerify** is an AI-powered computer-vision application designed to investigate whether an uploaded face appears elsewhere on the public internet.

The system combines **DeepFace face analysis**, **Google Lens reverse-image search through SerpApi**, **SQLite persistence**, and a **SHA-256 hash-linked blockchain** into a single local workflow.

It is designed especially for **hackathons, digital investigation prototypes, identity research, and demonstrable AI + blockchain workflows**.

---

## ✨ What FaceVerify Does

FaceVerify turns a single uploaded face image into a verifiable investigation trail.

```text
┌─────────────────┐
│   Upload Image  │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Face Detection │
│   + Embedding   │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Google Lens     │
│ Reverse Search  │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Potential Web / │
│ Social Match    │
└────────┬────────┘
         ↓
┌─────────────────┐
│ SHA-256 Hash    │
│ Linked Block    │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Verify Evidence │
│    On Chain     │
└─────────────────┘
```

The complete pipeline is exposed through a FastAPI endpoint:

```text
POST /api/pipeline/run
```

The backend processes the image, performs the reverse-image search, stores the result, and creates a blockchain record.

---

# 🚀 Key Features

## 🤖 AI Face Analysis

FaceVerify uses **DeepFace with FaceNet** to generate a numerical face embedding from the uploaded image.

The implementation attempts:

1. RetinaFace detection
2. OpenCV fallback
3. Face embedding extraction
4. Face validation
5. Persistent storage

The generated embedding is stored locally alongside the uploaded face record.

---

## 🔎 Reverse Image Search

The system uses **Google Lens through SerpApi** to search for visually similar images across the public web.

FaceVerify attempts to prioritize results from social platforms such as:

* Instagram
* Facebook
* X / Twitter
* LinkedIn
* Reddit

If a social result is unavailable, the system falls back to another usable visual match.

---

## ⛓️ Tamper-Evident Blockchain

Every discovered match is recorded in a **local, self-hosted blockchain**.

Each block contains:

* Block index
* Timestamp
* Data hash
* Previous block hash
* Current block hash
* Search metadata
* Face identifier

Hashes are generated using **SHA-256**, creating a chain where modifying previous data causes subsequent verification to fail.

> **Important:** this is a local hash-linked blockchain, not a cryptocurrency network or public blockchain.

---

## 🔐 Evidence Verification

FaceVerify can independently recompute the stored hashes and verify whether a block's contents have been modified.

The chain verification process checks:

* Block ordering
* Payload integrity
* Data hashes
* Block hashes
* Previous-hash relationships

This makes the system useful as a **tamper-evident evidence trail** for a prototype investigation workflow.

---

## 💾 Local Persistence

The project uses **SQLite** to store:

### Faces

```text
face_id
saved image path
face embedding
creation timestamp
```

### Search Results

```text
search_id
face_id
matched URL
source domain
title
thumbnail
creation timestamp
```

### Blockchain Blocks

```text
block index
timestamp
data hash
payload
previous hash
block hash
```

The database and face-storage directories are automatically initialized when the application starts.

---

# 🖥️ Web Interface

FaceVerify includes a lightweight browser-based frontend.

The interface provides:

* 📤 Image upload
* 👤 Face scanning
* 🔎 Match discovery
* 🌐 Matched URL
* 📌 Source domain
* 🖼️ Match thumbnail
* ⛓️ Blockchain record
* ✅ On-chain verification
* 🔗 Full blockchain viewer

The frontend is served directly by the FastAPI application, so no separate frontend server is required.

---

# 🧠 Technology Stack

| Layer           | Technology                 |
| --------------- | -------------------------- |
| Backend         | FastAPI                    |
| Server          | Uvicorn                    |
| Computer Vision | DeepFace                   |
| Face Model      | FaceNet                    |
| Face Detection  | RetinaFace / OpenCV        |
| Reverse Search  | Google Lens via SerpApi    |
| Database        | SQLite                     |
| Blockchain      | Custom SHA-256 hash chain  |
| Frontend        | HTML + CSS + JavaScript    |
| Configuration   | Pydantic Settings / dotenv |
| Language        | Python                     |

The current dependency set is defined in `requirements.txt`.

---

# 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │      Web Browser     │
                         │  HTML / CSS / JS     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │       Backend        │
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │ Face Service │  │Search Service│  │Chain Service │
          │              │  │              │  │              │
          │  DeepFace    │  │ Google Lens  │  │   SHA-256    │
          │  FaceNet     │  │  + SerpApi   │  │ Hash Chain   │
          └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
                 │                 │                 │
                 └─────────────────┼─────────────────┘
                                   ▼
                         ┌──────────────────────┐
                         │       SQLite         │
                         │      Database        │
                         └──────────────────────┘
```

---

# 📁 Project Structure

```text
FaceVerify/
│
├── app/
│   ├── routers/
│   │   ├── chain.py
│   │   ├── face.py
│   │   ├── pipeline.py
│   │   └── search.py
│   │
│   ├── services/
│   │   ├── chain_service.py
│   │   ├── face_service.py
│   │   └── search_service.py
│   │
│   ├── storage/
│   │   └── faces/
│   │
│   ├── config.py
│   ├── db.py
│   ├── main.py
│   └── models.py
│
├── web/
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── requirements.txt
├── README.md
└── .gitignore
```

The repository currently follows this separation between API routers, services, storage, and frontend assets.

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/APEX-BUILDERS/FaceVerify.git
cd FaceVerify
```

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

The project currently depends on FastAPI, Uvicorn, DeepFace, TensorFlow/Keras compatibility support, SerpApi, multipart handling, and environment configuration packages.

---

# 🔑 Configuration

Create a `.env` file in the project root.

```env
SERPAPI_API_KEY=your_serpapi_api_key
```

The application requires a SerpApi key for the Google Lens reverse-image-search stage.

> Never commit your real API key to GitHub.

---

# ▶️ Running FaceVerify

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://localhost:8000
```

Open the address in your browser to access the FaceVerify interface.

The FastAPI application automatically initializes the SQLite database and creates the blockchain genesis block during startup.

---

# 🧪 API Usage

## Run the Complete Pipeline

```bash
curl -X POST \
  "http://localhost:8000/api/pipeline/run" \
  -F "image=@/path/to/face.jpg"
```

The pipeline performs:

```text
Image Upload
     ↓
Face Detection
     ↓
Face Embedding
     ↓
Reverse Image Search
     ↓
Match Selection
     ↓
Database Storage
     ↓
Blockchain Commit
     ↓
JSON Response
```

The endpoint returns the generated face ID, search result, and blockchain block information.

---

# ⛓️ View the Blockchain

```bash
curl "http://localhost:8000/api/chain/full"
```

This returns the complete locally stored blockchain.

---

# 🔍 Blockchain Verification

The chain can be independently checked by recalculating the SHA-256 hashes of its blocks.

Conceptually:

```text
Block N
   │
   ├── Data Hash
   ├── Previous Hash
   └── Current Hash
           │
           ▼
        Block N+1
           │
           ├── Data Hash
           ├── Previous Hash = Hash(Block N)
           └── Current Hash
```

If any historical block is modified, the hash relationship becomes invalid.

---

# 🌐 How Reverse Search Works

Because Google Lens/SerpApi cannot directly access a `localhost` image URL, FaceVerify handles this situation by temporarily making the uploaded image publicly reachable before submitting it to the reverse-image-search service.

For a local deployment, the implementation attempts to upload the image to a public image host and then passes the resulting URL to SerpApi.

For a publicly reachable deployment, the application can construct a public `/storage/faces/<face_id>.jpg` URL instead.

> **Privacy warning:** uploaded images may therefore leave your local machine when reverse search is enabled. Do not use sensitive biometric images without appropriate authorization and consent.

---

# 🧩 Core Pipeline

### Step 1 — Upload

The user uploads an image containing a face.

### Step 2 — Face Processing

DeepFace generates a FaceNet embedding.

```text
Image
 ↓
Face Detection
 ↓
FaceNet
 ↓
Embedding Vector
```

### Step 3 — Reverse Search

The system sends the image to Google Lens through SerpApi.

### Step 4 — Match Selection

Potential visual matches are analyzed and social-domain results are prioritized.

### Step 5 — Persistence

The face and search result are stored in SQLite.

### Step 6 — Blockchain Anchoring

The discovered match is converted into a canonical payload and hashed with SHA-256.

### Step 7 — Verification

The blockchain record can later be recomputed and validated.

---

# 🎯 Use Cases

FaceVerify can serve as a prototype for:

* 🔎 Digital investigation
* 🕵️ Open-source intelligence research
* 📰 Image-source discovery
* 🚨 Fraud investigation prototypes
* 👤 Identity research
* 🧾 Evidence provenance
* 🔐 Tamper-evident investigation logs
* 🧪 AI + blockchain research
* 🏆 Hackathon demonstrations

**Important:** a reverse-image match is only a potential web match. It should not be treated as definitive proof that two images depict the same person.

---

# ⚠️ Limitations

FaceVerify is currently a **prototype / hackathon-oriented system**, not a production biometric identification platform.

### API limitations

SerpApi usage is subject to the limits of your account and plan.

### Search limitations

Google Lens can only discover images and pages that are publicly accessible and indexed.

### Recognition limitations

Face embeddings can be affected by:

* Image quality
* Lighting
* Pose
* Occlusion
* Resolution
* Facial appearance changes

### Privacy limitations

Reverse-image search may require sending an image to an external service or public image host.

### Blockchain limitations

The blockchain is:

* Local
* Self-hosted
* Not distributed
* Not consensus-based
* Not a public cryptocurrency blockchain

It provides **tamper evidence**, not decentralized trust.

### Model initialization

DeepFace may download model weights during its first execution, so initial setup can require internet access.

---

# 🔮 Future Roadmap

Potential improvements include:

* [ ] True liveness detection
* [ ] Anti-spoofing protection
* [ ] Multiple-face analysis
* [ ] Better match-ranking algorithms
* [ ] Confidence scoring
* [ ] Public blockchain / testnet integration
* [ ] IPFS evidence storage
* [ ] Encrypted biometric storage
* [ ] Authentication and role-based access
* [ ] Audit logs
* [ ] Docker deployment
* [ ] Cloud deployment
* [ ] Automated evaluation benchmarks
* [ ] Privacy-preserving image processing
* [ ] Model comparison and threshold calibration
* [ ] Automated evidence reports
* [ ] Stronger forensic provenance

---

# 🔐 Security & Privacy

FaceVerify deals with **biometric information**, so security should be treated as a first-class concern.

Before using the system with real people's images:

1. Obtain appropriate authorization.
2. Do not commit uploaded images to Git.
3. Keep API credentials in environment variables.
4. Restrict access to stored face images.
5. Avoid unnecessary retention of biometric data.
6. Understand where reverse-search images are transmitted.
7. Do not use search results as definitive identity proof.

This project should be considered a **technical prototype and research/hackathon implementation** unless additional security, privacy, compliance, and accuracy controls are implemented.

---

# 🏆 Hackathon Highlights

FaceVerify combines several technologies into one demonstrable pipeline:

```text
          COMPUTER VISION
                │
                ▼
          ┌───────────┐
          │ DeepFace  │
          │  FaceNet  │
          └─────┬─────┘
                │
                ▼
        REVERSE IMAGE SEARCH
                │
                ▼
          ┌───────────┐
          │ Google    │
          │   Lens    │
          └─────┬─────┘
                │
                ▼
           WEB MATCH
                │
                ▼
          ┌───────────┐
          │  SQLite   │
          └─────┬─────┘
                │
                ▼
          ┌───────────┐
          │ SHA-256   │
          │ Blockchain│
          └─────┬─────┘
                │
                ▼
          VERIFIABLE RECORD
```

The result is not simply **"face detected"**.

It creates an investigation trail:

> **Face → Search → Match → Evidence → Hash → Verification**

---

# 📊 Project Status

| Component                    | Status        |
| ---------------------------- | ------------- |
| FastAPI backend              | ✅ Implemented |
| Face detection               | ✅ Implemented |
| Face embeddings              | ✅ Implemented |
| Google Lens search           | ✅ Implemented |
| Social result prioritization | ✅ Implemented |
| SQLite persistence           | ✅ Implemented |
| Local blockchain             | ✅ Implemented |
| Blockchain verification      | ✅ Implemented |
| Web interface                | ✅ Implemented |
| Public blockchain            | 🔮 Future     |
| Liveness detection           | 🔮 Future     |
| Production security          | 🔮 Future     |

---

# 🤝 Contributing

Contributions are welcome.

```bash
git checkout -b feature/your-feature
```

Make your changes, test them locally, and open a pull request.

When contributing, please consider:

* Code quality
* Privacy implications
* Security
* API failure handling
* Reproducibility
* Documentation

---

# 📜 Disclaimer

FaceVerify is intended for **educational, research, and authorized investigative purposes**.

A reverse-image-search result does **not** establish a person's identity or prove that a person owns or controls a particular online account.

Users are responsible for complying with applicable privacy, biometric-data, copyright, and other laws when using this software.

---

# 👥 Built By

### **BuildOrBust**

Built with ❤️ for **HH GOA Hackathon / AI & Blockchain experimentation**.

---

## ⭐ Support the Project

If you find FaceVerify useful or interesting:

**⭐ Star the repository**
**🍴 Fork the project**
**🐛 Report issues**
**💡 Suggest improvements**

---

<p align="center">

### 🔐 FaceVerify

**Face Intelligence • Web Discovery • Verifiable Evidence**

</p>
