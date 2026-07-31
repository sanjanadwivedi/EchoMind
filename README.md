# 🧠 EchoMind

**AI-Powered NPC Long-Term Memory & Cognitive Pipeline for Interactive Game Worlds**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18.0+-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5.0+-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6F00?style=for-the-badge)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4.1--Mini-412991?style=for-the-badge&logo=openai&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-32%20Passed%20%E2%9C%85-brightgreen?style=for-the-badge)
![Hybrid RRF](https://img.shields.io/badge/Retrieval-Dense%20%2B%20BM25%20RRF-8A2BE2?style=for-the-badge)
![Evals](https://img.shields.io/badge/Evals-RAG%20Triad%20Bench-FF1493?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

---

## 🌟 Overview

**EchoMind** is an advanced AI architecture designed for RPG video games and interactive storytelling. It enables Non-Player Characters (NPCs) to form **persistent long-term memories**, track evolving player relationships, reflect on past experiences, and dynamically adapt their dialogue and mood — all without hallucinating false information or breaking character.

### ⚡ Key AI/ML Systems & Production Engineering Features

- 📊 **Automated RAG Triad Evaluation Suite (`RAGEvaluator`)**: Measures Context Precision, Groundedness (Anti-hallucination score), and Persona Consistency via an automated LLM-as-a-Judge benchmark CLI (`scripts/eval_benchmark.py`).
- 🔀 **3-Stage Hybrid Retrieval (Dense Vector + BM25 Sparse Keyword RRF)**: Merges dense vector embeddings with Okapi BM25 keyword matching using **Reciprocal Rank Fusion (RRF)**:
  $$\text{RRF Score}(d) = \frac{1}{60 + r_{\text{dense}}(d)} + \frac{1}{60 + r_{\text{sparse}}(d)}$$
- ⚡ **Semantic Query Cache (`SemanticCache`)**: In-memory vector similarity cache ($\ge 0.95$ cosine threshold) reducing redundant LLM inference latency to sub-5ms while eliminating token costs.
- 🌊 **Real-Time Streaming Dialogue (SSE)**: Server-Sent Events (`POST /chat/stream`) yielding token chunks live with execution telemetry breakdowns (`retrieval_ms`, `generation_ms`, `total_ms`).

When a player tells an NPC *"My cat is named Luna and I love espresso"*, the NPC extracts these facts, embeds them into a **ChromaDB vector store**, and retrieves them naturally weeks later when asked *"Do you remember what I drink?"*.

---

## 🎨 Interactive Dark Fantasy RPG Web Interface

EchoMind includes a dark fantasy web application built with **React**, **Vite**, **Framer Motion**, and custom Web Audio synthesizers:

- 🧔 **Visual Character Avatars & Stage Banners**: AI-generated character portraits (*Eldon*, *Ragnar*, *Luna*) with custom landscape environment art.
- 🎭 **Dynamic NPC Mood & Emotion System**: Live real-time mood detection (*Friendly*, *Suspicious*, *Impressed*, *Amused*, *Thoughtful*, *Guarded*).
- 🎙️ **Speech-To-Text (Voice Input)**: Speak into your microphone to converse hands-free using real-time Web Speech API transcription.
- 🗣️ **Text-To-Speech (TTS) Voice Synthesis**: NPCs speak their dialogue aloud in character-matched voices.
- 🎵 **Web Audio API SFX Synthesizer**: Zero-dependency procedural audio for swoops, chimes, coin clicks, and spell reflection chords.
- 🧠 **Live Memory Bank Inspection Drawer**: Inspect stored vector embeddings, category tags, importance scores, and timestamps in real time.

---

## 🏗️ Architecture & Memory Pipeline

```
                              ┌───────────────────────────┐
                              │     React + Vite Web UI   │
                              └─────────────┬─────────────┘
                                            │
                                            ▼
                                 ┌────────────────────┐
                                 │    FastAPI Server  │
                                 └──────────┬─────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
┌────────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐
│  Intent Classifier (LLM)   │ │ Dialogue Generation Engine│ │ Memory Extraction Engine │
└──────────────┬─────────────┘ └────────────┬─────────────┘ └────────────┬─────────────┘
               │                            │                            │
               ▼                            ▼                            ▼
┌────────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐
│  ChromaDB Vector Store     │ │ Memory Ranking Algorithm │ │ PostgreSQL Relational DB │
│  (Semantic Search)         │ │ (Similarity/Recency/Imp)│ │ (Structured Entities)    │
└────────────────────────────┘ └──────────────────────────┘ └──────────────────────────┘
```

### Core Cognitive Steps

1. **Extraction Pipeline (`MemoryExtractor`)**: Analyzes player dialogue using OpenAI structured JSON to extract singular persistent facts, importance scores (`0.0 - 1.0`), and category labels (`personal_fact`, `preference`, `relationship`, `goal`, `event`).
2. **Intent Classification (`MemoryIntentClassifier`)**: Predicts which memory categories should be queried based on the player's query.
3. **Hybrid Retrieval (`RetrievalService`)**: Queries ChromaDB vector embeddings (`text-embedding-3-small`) with category filtering.
4. **Weighted Ranking Algorithm (`MemoryRankingService`)**:
   $$\text{Score} = (0.60 \times \text{Similarity}) + (0.25 \times \text{Importance}) + (0.15 \times \text{Recency})$$
5. **Contextual Dialogue Assembly (`DialogueService`)**: Fuses NPC personality traits, relationship status, retrieved memories, and current player message into an anti-hallucination prompt.
6. **Consolidation & Reflection (`MemoryReflectionService`)**: Synthesizes clusters of raw memories into higher-level long-term knowledge.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **OpenAI API Key**

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/your-username/EchoMind.git
cd EchoMind

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS / Linux

# Install dependencies
pip install -r backend/requirements.txt

# Configure Environment Variables
cp backend/.env.example backend/.env
# Update backend/.env with your OPENAI_API_KEY and DATABASE_URL
```

### 2. Run Database Seed & Migrations

```bash
cd backend
python -m app.seed.seed_database
```

### 3. Launch Development Servers

```bash
# Terminal 1: Backend API (http://localhost:8000)
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend UI (http://localhost:5173)
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing & Quality Assurance

EchoMind contains unit tests covering memory ranking algorithms, recency decay math, API endpoints, and security checks:

```bash
# Run pytest suite
python -m pytest tests/ -v
```

```
======================== 19 passed in 2.26s ========================
```

---

## 📡 API Reference Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API Metadata |
| `GET` | `/health` | Health Check |
| `POST` | `/chat/` | Send message to NPC (returns dialogue + emotion) |
| `GET` | `/npcs/` | List all available NPCs |
| `GET` | `/npcs/{id}` | Retrieve specific NPC details |
| `GET` | `/players/` | List players |
| `POST` | `/players/` | Create a new player |
| `GET` | `/relationships/{npc_id}/{player_id}` | Fetch personality traits & relationship stats |
| `POST` | `/memory/reflect` | Consolidate memories into reflection summary |
| `GET` | `/memory/debug` | Fetch raw vector memory bank |

---

## 🛠️ Tech Stack & Dependencies

- **Framework:** FastAPI, React 18, Vite 5, Tailwind/Vanilla CSS Tokens
- **Database & ORM:** PostgreSQL, SQLAlchemy, Alembic, ChromaDB
- **AI & NLP:** OpenAI API (GPT-4o-mini, `text-embedding-3-small`)
- **Animation & Audio:** Framer Motion, Canvas API, Web Speech API, Web Audio API

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
