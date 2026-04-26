# <h1>TutorRAG – RAG-Based AI Teaching Assistant</h1>

TutorRAG is a Retrieval-Augmented Generation (RAG) system designed to help users learn from structured course content. It enables users to search for specific topics within educational material and receive context-aware answers with precise timestamps.

The system combines semantic search using embeddings with a locally hosted language model to provide accurate and relevant responses.

# Features
Semantic search over course content using embeddings
Retrieval of relevant chunks with timestamps
Context-aware answer generation using a local LLM
End-to-end pipeline from video/audio to searchable knowledge
Lightweight and runs locally without external API dependency

# Tech Stack
Backend: Python
Embeddings: BGE-M3 model
LLM: Ollama (local inference)
Database: SQLite / local storage
Frontend: HTML (templates)
Tools: FFmpeg, Joblib

# How It Works

1. Videos → converted to audio
2. Audio → converted to JSON subtitles
3. JSON → chunked and merged
4. Embeddings generated using `bge-m3`
5. User query → embedding
6. Cosine similarity → best matching chunk
7. LLM generates final answer using context

---

# Project Structure

```bash
TutorRAG/
│
├── app.py                    # Flask web app
├── process_incoming.py       # RAG pipeline (retrieval + LLM)
├── preprocess_json.py        # Embedding generation
├── merge_chunks.py           # Chunk merging logic
├── mp3_to_json.py            # Audio → JSON conversion
├── video_to_mp3.py           # Video → audio conversion
│
├── embeddings.joblib         # Stored embeddings
├── tutorrag.db               # SQLite database
│
├── audios/                   # Extracted audio files
├── videos/                   # Source videos
├── jsons/                    # Raw JSON transcripts
├── newjsons/                 # Processed chunks
│
├── templates/
│   └── index.html            # Web UI
│
├── unused/                   # Experimental / unused files
├── __pycache__/              # Python cache (ignored)
│
├── prompt.txt                # Debug prompt
├── response.txt              # Debug response
├── README.md
├── .gitignore
```

---

# Installation

```bash
git clone https://github.com/akashbhusod-cmyk/TutorRAG.git
cd TutorRAG

```

---

# Run the Application

```bash
python app.py
```

Open in browser:

```
http://127.0.0.1:5000
```

---

# Data Processing Pipeline

Run these steps only when preparing data:

### 1. Convert video → audio

```bash
python video_to_mp3.py
```

### 2. Convert audio → JSON

```bash
python mp3_to_json.py
```

### 3. Merge chunks

```bash
python merge_chunks.py
```

### 4. Generate embeddings

```bash
python preprocess_json.py
```

---

# Database

* SQLite database: `tutorrag.db`
* Stores:

  * user queries
  * generated responses

---

# Example Query

> Where is swapping variables taught?

**Output:**

> Video 17: Swap 2 Variables in Python [0:00 – 0:35]
> Demonstrates swapping values using a temporary variable.

---

# Future Improvements

* Streaming responses (typing effect)
* Chat history sidebar
* Vector database (FAISS / Chroma)
* Multi-course support
* Deployment (Render / Railway)

---

---

# Author

## Akash Bhusod

---

# License

For educational and portfolio purposes.
