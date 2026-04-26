import joblib
import numpy as np
import re
import requests
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity

TOP_K = 1
SCORE_THRESHOLD = 0.3
EMBED_MODEL = "bge-m3"
OLLAMA_URL = "http://localhost:11434"
DB_PATH = "tutorrag.db"

df = joblib.load("embeddings.joblib")


def init_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rag_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_query TEXT NOT NULL,
            prompt TEXT,
            response TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()
    connection.close()


def save_interaction(user_query, prompt, response, status):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO rag_history (user_query, prompt, response, status)
        VALUES (?, ?, ?, ?)
        """,
        (user_query, prompt, response, status),
    )
    connection.commit()
    connection.close()


def format_time(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


def create_embedding(text_list):
    response = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": text_list},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["embeddings"]


def clean_text(text):
    cleaned = re.sub(r"\s+", " ", str(text)).strip()
    cleaned = re.sub(r"^(welcome back[^.?!]*[.?!]\s*)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^(my name is[^.?!]*[.?!]\s*)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^(and in this video[^.?!]*[.?!]\s*)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^(so let's say[^.?!]*[.?!]\s*)", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def summarize_content(text):
    cleaned = clean_text(text)
    sentences = re.split(r"(?<=[.?!])\s+", cleaned)
    useful_sentences = []

    for sentence in sentences:
        compact = sentence.strip()
        if not compact:
            continue
        if len(compact) < 30:
            continue
        useful_sentences.append(compact)
        if len(useful_sentences) == 2:
            break

    if useful_sentences:
        return " ".join(useful_sentences)

    return cleaned[:240].strip()


def build_response(row):
    title = row["title"]
    number = row["number"]
    start_time = format_time(row["start"])
    end_time = format_time(row["end"])
    summary = summarize_content(row["text"])

    return (
        f"{title} is covered in video {number}, around {start_time} - {end_time}.\n\n"
        f"This lesson focuses on the topic directly and points you to the exact place in the course where it is explained.\n\n"
        f"{summary}"
    )


def get_answer(incoming_query):
    cleaned_query = incoming_query.strip()
    if not cleaned_query:
        return "Enter a question to search the course content."

    question_embedding = create_embedding([cleaned_query])[0]

    similarities = cosine_similarity(
        np.vstack(df["embedding"]),
        [question_embedding],
    ).flatten()

    ranked_df = df.copy()
    ranked_df["score"] = similarities
    query_lower = cleaned_query.lower()

    def boost_score(row):
        text = row["text"].lower()
        title = row["title"].lower()
        boost = 0
        for word in query_lower.split():
            if word in text:
                boost += 0.05
            if word in title:
                boost += 0.15
        return row["score"] + boost

    ranked_df["score"] = ranked_df.apply(boost_score, axis=1)
    filtered_df = ranked_df[ranked_df["score"] > SCORE_THRESHOLD]

    if len(filtered_df) == 0:
        response = "No strong match found for that question in the current course data."
        save_interaction(cleaned_query, "", response, "no_match")
        return response

    new_df = filtered_df.sort_values(by="score", ascending=False).head(TOP_K)
    best_row = new_df.iloc[0]

    context = "\n\n".join(
        f"""Video Title: {row['title']}
Video Number: {row['number']}
Timestamp: {format_time(row['start'])} - {format_time(row['end'])}
Content: {row['text']}"""
        for _, row in new_df.iterrows()
    )

    prompt = (
        f"Retrieved top lesson for query: {cleaned_query}\n\n"
        f"{context}\n\n"
        "Response style: always include the video number and exact timestamp, then give a concise explanation from the retrieved transcript."
    )
    response = build_response(best_row)

    with open("prompt.txt", "w", encoding="utf-8") as prompt_file:
        prompt_file.write(prompt)

    with open("response.txt", "w", encoding="utf-8") as response_file:
        response_file.write(response)

    save_interaction(cleaned_query, prompt, response, "success")
    return response


def main():
    incoming_query = input("Ask a Question: ")
    answer = get_answer(incoming_query)
    print("\nAnswer:\n", answer)


if __name__ == "__main__":
    init_database()
    main()
