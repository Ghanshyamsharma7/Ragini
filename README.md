# Ragini 🎓

An AI-powered study assistant for CBSE students (Classes 6–12), built with RAG (Retrieval-Augmented Generation). Tatvagyan answers curriculum-based questions using NCERT textbooks as its knowledge base.

---

## What it does

Students select their class and subject, then ask questions in Hindi or English. Tatvagyan retrieves relevant content from NCERT textbooks and generates accurate, curriculum-aligned answers using Gemini AI.

---

## Tech Stack

### Frontend
- React 19 + Vite
- Tailwind CSS
- React Router

### Backend
- FastAPI (Python)
- Google OAuth 2.0 — authentication
- PostgreSQL (Neon) — user sessions and chat history
- MongoDB Atlas — NCERT text chunks storage
- Pinecone — vector similarity search (namespace per class+subject)
- Redis — semantic cache for repeated questions
- Supabase Storage — NCERT PDF storage
- Google Gemini — embeddings + answer generation

### Ingestion Pipeline
- PyMuPDF — text extraction from digital PDFs (Class 6, 7, 8)
- Tesseract OCR — fallback for legacy-encoded PDFs (Class 9, 10)
- Fixed-size chunking (200 words, 50 word overlap)
- Gemini Embedding-001 — 3072-dimension vectors

---

## Architecture

```
Student asks question (Class + Subject selected)
        ↓
Redis semantic cache check
        ↓ miss
Gemini embeds question (3072d vector)
        ↓
Pinecone searches namespace "class_09__hindi kshitij"
        ↓
Top 5 chunk IDs returned
        ↓
MongoDB fetches chunk texts
        ↓
Gemini generates answer from context
        ↓
Answer stored in Redis cache + PostgreSQL history
```

---

## Project Structure

```
ragini/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Chat.jsx
│   │   │   ├── Login.jsx
│   │   │   └── AuthCallback.jsx
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── MessageInput.jsx
│   │   │   ├── SessionSelector.jsx
│   │   │   └── ProfileMenu.jsx
│   │   └── context/
│   │       └── AuthContext.jsx
│
└── backend/
    ├── app/
    │   ├── api/
    │   │   ├── auth.py
    │   │   ├── query.py
    │   │   ├── session.py
    │   │   ├── ingest.py
    │   │   ├── history.py
    │   │   └── config.py
    │   ├── services/
    │   │   ├── ocr_service.py
    │   │   ├── chunk_service.py
    │   │   ├── embedding_service.py
    │   │   ├── retrieval_service.py
    │   │   ├── context_service.py
    │   │   ├── llm_service.py
    │   │   ├── mongo_service.py
    │   │   ├── pinecone_service.py
    │   │   └── semantic_cache_service.py
    │   ├── db/
    │   │   ├── postgres.py
    │   │   └── mongo.py
    │   └── utils/
    │       ├── path_parser.py
    │       └── text_cleaner.py
    └── main.py
```

---

## Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Tesseract OCR — [Download]
- Poppler — for PDF to image conversion

### 1. Clone the repository
```bash
git clone https://github.com/ghanshyamsharma7/ragini.git
cd ragini
```

### 2. Backend setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Create `.env` in `/backend`:
```env
NEON_DATABASE_URL=your_neon_postgres_url
MONGO_URI=your_mongodb_atlas_uri
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=your_index_name
GEMINI_API_KEY=your_gemini_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_BUCKET=CBSE_BOOKS
REDIS_URL=your_redis_url
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SESSION_SECRET_KEY=your_random_secret
FRONTEND_URL=http://localhost:5173
CACHE_SIM_THRESHOLD=0.2
```

Start backend:
```bash
uvicorn app.main:app --reload
```

### 3. Frontend setup
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

---

## Ingestion Pipeline

> Run once locally to populate MongoDB and Pinecone. Not needed on deployment.

### Step 1 — Ingest PDFs into MongoDB
```bash
cd backend
python run_ingest.py
```

### Step 2 — Generate embeddings into Pinecone
```bash
python run_embed.py
```

Both scripts are resumable — safe to stop and restart anytime.

---

## Features

- 🔐 Google OAuth login
- 📚 Class and subject-based sessions (Classes 6–10, all NCERT subjects)
- 🌐 Hindi + English question support
- ⚡ Semantic caching via Redis — instant answers for repeated questions
- 💬 Chat history per session
- 🗑️ Session management — create, switch, delete
- 📱 Responsive UI — works on mobile and desktop




![Login Page](frontend/src/assets/tatva1.png)
![Chat](frontend/src/assets/tatva2.png)
![Short Answer](frontend/src/assets/tatva3.png)
![Analytical](frontend/src/assets/tatva4.png)