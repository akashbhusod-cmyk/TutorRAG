# TutorRAG

TutorRAG is a local RAG-based course assistant for Python learning content. It helps you ask questions like where a topic is taught, then returns the most relevant video, video number, and exact timestamp from your course data.

The project now runs as a Flask web app on `localhost`, includes a cleaner chat-style UI, and stores prompt/response history in SQLite.

## Features

- Local Flask web interface
- Course-topic search using embeddings
- Exact video and timestamp lookup
- Fast retrieval-based answer generation
- SQLite storage for prompts and responses
- Prompt and response logging to `prompt.txt` and `response.txt`

## Current Stack

- Python
- Flask
- Pandas
- NumPy
- Scikit-learn
- Joblib
- Requests
- SQLite3
- Ollama embeddings API

## Project Structure

```text
TutorRAG/
├── app.py
├── process_incoming.py
├── embeddings.joblib
├── prompt.txt
├── response.txt
├── Readme.md
├── templates/
│   └── index.html
├── audios/
├── jsons/
├── newjsons/
├── unused/
└── videos/
```

## How It Works

1. The user enters a course question in the web UI.
2. The query is converted into an embedding using Ollama.
3. Cosine similarity is used to find the best matching transcript chunk.
4. Title, video number, and timestamp are taken from the top match.
5. A clean answer is built from the retrieved lesson content.
6. The interaction is stored in SQLite.

## Setup

### 1. Install Python packages

```bash
pip install flask pandas numpy scikit-learn joblib requests
```

### 2. Install Ollama

Download Ollama from [ollama.com](https://ollama.com)

Then pull the embedding model used by this project:

```bash
ollama pull bge-m3
```

### 3. Start Ollama

```bash
ollama serve
```

Ollama should be available at:

```text
http://localhost:11434
```

## Run The App

Start the Flask app:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Example Questions

- Where is tuple explained in the course?
- Which video covers swapping two variables?
- Where is list taught in Python?
- Which lesson explains user input?

## Database

TutorRAG stores interactions in a SQLite database file:

```text
tutorrag.db
```

The database is created automatically when the app starts.

### Stored Table

```text
rag_history
```

### Stored Fields

- `user_query`
- `prompt`
- `response`
- `status`
- `created_at`

## Files Updated During Runtime

- `prompt.txt` stores the latest constructed prompt/context
- `response.txt` stores the latest generated answer
- `tutorrag.db` stores interaction history

## Notes

- The app depends on `embeddings.joblib` being present in the project root.
- If Ollama is not running, the app will show a connection-related error.
- The current response flow is optimized for fast and accurate course lookup rather than long-form generated answers.

## Author

Akki
