# Lectica 📚
### _Turn any lecture into a study companion._

> A multimodal AI orchestration agent that routes video, audio, image, and PDF inputs through parallel async pipelines fusing transcripts, vision extractions, and semantic chunks into a unified vector store to generate flashcards, quizzes, summaries, and RAG-powered chat. Powered by Whisper, Groq, pgvector, and sentence-transformers.

<br/>

    $ upload "lecture.mp4"

      Processing video → extracting audio + keyframes...

      ✓ Transcribed 47 minutes of audio via Whisper
      ✓ Extracted 12 keyframes via Groq Vision
      ✓ Generated 15 flashcards · 5 quiz questions · summary

      Ask: "What are the key concepts?"
      → "The lecture covers three main topics: ..."

<br/>

## 🌐 Live Demo

| Service | URL |
|---|---|
| **Frontend** | `https://lectica.vercel.app` |
| **Backend API** | `https://lectica-api.onrender.com` |

<br/>

## ✨ Features

- 🎬 **Multimodal ingestion** — video, audio, images, PDFs, and text
- 📇 **Flashcards** — auto-generated with SM-2 spaced repetition scheduling
- 📝 **Quiz** — multiple choice questions with explanations
- 📋 **Summary** — key concepts + structured overview
- 💬 **RAG chat** — streaming answers grounded in your content
- ⚡ **Parallel pipelines** — all modalities processed concurrently via asyncio
- 🌙 **Modern dark UI** built with Next.js + Tailwind CSS

<br/>

## 🏗️ Architecture

**Ingestion Pipeline**

    Upload (video / audio / image / PDF / text)
                    ↓
          Modality Router (orchestrator.py)
                    ↓
    ┌─────────────────────────────────────────┐
    │           Parallel pipelines            │
    │  ├── Video  → ffmpeg → frames + audio   │
    │  ├── Audio  → Whisper → transcript      │
    │  ├── Image  → Groq Vision → text        │
    │  └── Text   → semantic chunker          │
    └─────────────────────────────────────────┘
                    ↓
       Embeddings (sentence-transformers)
                    ↓
            pgvector (Supabase)
                    ↓
       Groq llama-3.3-70b → Flashcards · Quiz · Summary

**Query Pipeline**

    User Question → Embed (sentence-transformers)
                          ↓
              pgvector Cosine Similarity Search
                    (top 8 chunks)
                          ↓
         Send Fused Context → Groq llama-3.3-70b
                          ↓
            Streaming SSE Response → Frontend

<br/>

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.11** | Runtime |
| **FastAPI** | Async REST API framework |
| **SQLAlchemy (async)** | ORM with pgvector support |
| **Whisper (local)** | Audio transcription |
| **ffmpeg** | Video frame + audio extraction |
| **Groq SDK** | LLM + vision inference |
| **sentence-transformers** | Local embeddings (all-MiniLM-L6-v2) |
| **PyMuPDF** | PDF text extraction |
| **SM-2 algorithm** | Spaced repetition scheduling |

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 14** | React framework with App Router |
| **TypeScript** | Type safety |
| **Tailwind CSS** | Utility-first styling |

### Infrastructure
| Service | Purpose |
|---|---|
| **Render** | Backend hosting |
| **Vercel** | Frontend hosting |
| **Supabase** | Postgres + pgvector |
| **Groq** | LLM + vision inference API |

<br/>

## 📁 Project Structure

    lectica/
    │
    ├── backend/
    │   ├── requirements.txt
    │   │
    │   └── app/
    │       ├── main.py
    │       ├── config.py
    │       ├── api/v1/
    │       │   ├── ingest.py
    │       │   ├── study.py
    │       │   └── chat.py
    │       ├── core/
    │       │   ├── orchestrator.py
    │       │   └── embedder.py
    │       ├── pipelines/
    │       │   ├── audio_pipeline.py
    │       │   ├── video_pipeline.py
    │       │   ├── vision_pipeline.py
    │       │   └── text_pipeline.py
    │       ├── services/
    │       │   ├── study_service.py
    │       │   ├── chat_service.py
    │       │   └── sm2_service.py
    │       ├── models/
    │       │   └── models.py
    │       ├── schemas/
    │       │   └── schemas.py
    │       └── db/
    │           └── database.py
    │
    └── frontend/
        └── src/app/
            ├── page.tsx
            ├── upload/
            │   └── page.tsx
            └── sessions/[id]/
                ├── page.tsx
                ├── flashcards/
                ├── quiz/
                ├── summary/
                └── chat/

<br/>

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- ffmpeg (`brew install ffmpeg`)
- Accounts on: [Supabase](https://supabase.com) · [Groq](https://console.groq.com)

### 1. Clone the repo

    git clone https://github.com/vedant1101/Lectica.git
    cd lectica

### 2. Backend setup

    cd backend
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Create `backend/.env`:

    APP_ENV=development
    DATABASE_URL=postgresql+asyncpg://...
    GROQ_API_KEY=your_groq_key
    GEMINI_API_KEY=your_gemini_key
    ALLOWED_ORIGINS=["http://localhost:3000"]

    uvicorn app.main:app --reload --port 8000

### 3. Frontend setup

    cd frontend
    npm install

Create `frontend/.env.local`:

    NEXT_PUBLIC_API_URL=http://localhost:8000

    npm run dev

Visit `http://localhost:3000` 🎉

<br/>

## 📡 API Reference

### `POST /api/v1/sessions`
Upload files and start a processing session.

**Request:** `multipart/form-data` with one or more files

**Response:**

    {
      "session_id": "uuid",
      "status": "processing",
      "message": "Processing 2 file(s)..."
    }

### `GET /api/v1/sessions/{session_id}`
Poll session status.

**Response:**

    {
      "id": "uuid",
      "status": "done",
      "created_at": "2026-03-19T..."
    }

### `GET /api/v1/sessions/{session_id}/flashcards`
Get generated flashcards with SM-2 scheduling data.

### `GET /api/v1/sessions/{session_id}/quiz?n=5`
Get N multiple choice quiz questions.

### `GET /api/v1/sessions/{session_id}/summary`
Get title, key concepts, and summary.

### `POST /api/v1/sessions/{session_id}/chat`
Stream a RAG-powered answer via Server-Sent Events.

**Request:**

    {
      "message": "What are the key concepts?",
      "history": []
    }

<br/>

## 🧠 How It Works

### 1. Modality Detection
The orchestrator detects file type and routes to the correct pipeline — video, audio, image, or text.

### 2. Parallel Processing
All pipelines run concurrently via `asyncio.gather`. A video triggers both the audio pipeline (Whisper) and vision pipeline (Groq Vision) simultaneously.

### 3. Embedding + Storage
Each chunk is embedded locally using sentence-transformers and stored in Supabase with pgvector for cosine similarity search.

### 4. Study Material Generation
Groq's llama-3.3-70b generates flashcards, quiz questions, and a summary from the combined chunk pool across all modalities.

### 5. RAG Chat
User questions are embedded and matched against all chunks via cosine similarity. The top 8 chunks — regardless of modality — are fused into a single context for Groq to answer from.

<br/>

## 🚢 Deployment

### Backend — Render
1. Push to GitHub
2. Create new Render web service → connect GitHub repo
3. Set Root Directory to `backend`
4. Set Build Command: `pip install -r requirements.txt`
5. Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables in Render dashboard

### Frontend — Vercel
1. Import repo on [vercel.com](https://vercel.com)
2. Set Root Directory to `frontend`
3. Set `NEXT_PUBLIC_API_URL` to your Render backend URL
4. Vercel auto-deploys on every push

<br/>

## 🔮 Future Improvements

- [ ] User authentication + session history
- [ ] Support for YouTube URL ingestion
- [ ] Re-upload and merge into existing session
- [ ] Export flashcards to Anki
- [ ] Mobile app
- [ ] Collaborative study rooms

<br/>

## 👨‍💻 Author

**Vedant Sahai**

Built from scratch as a portfolio project to demonstrate full-stack multimodal AI agent development.

- GitHub: [@vedant1101](https://github.com/vedant1101)

<br/>

## 📄 License

MIT © Vedant Sahai
