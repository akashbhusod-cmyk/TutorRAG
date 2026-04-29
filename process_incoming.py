import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import joblib
import requests

TOP_K = 1
SCORE_THRESHOLD = 0.3
MODEL = "llama3.2"

df = joblib.load('embeddings.joblib')

def format_time(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"

def create_embedding(text_list):
    r = requests.post("http://localhost:11434/api/embed", json={
        "model": "bge-m3",
        "input": text_list
    })
    return r.json()["embeddings"]

def infernce(prompt, model=MODEL):
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })
    return r.json()

def get_answer(incoming_query):
    question_embedding = create_embedding([incoming_query])[0]

    similarities = cosine_similarity(
        np.vstack(df['embedding']),
        [question_embedding]
    ).flatten()

    df['score'] = similarities

    query_lower = incoming_query.lower()

    def boost_score(row):
        text = row['text'].lower()
        title = row['title'].lower()
        boost = 0
        for word in query_lower.split():
            if word in text:
                boost += 0.05
            if word in title:
                boost += 0.15
        return row['score'] + boost

    df['score'] = df.apply(boost_score, axis=1)

    filtered_df = df[df['score'] > SCORE_THRESHOLD]

    if len(filtered_df) == 0:
        return "No strong match found."

    new_df = filtered_df.sort_values(by="score", ascending=False).head(TOP_K)

    context = "\n\n".join(
        f"""Video Title: {row['title']}
Video Number: {row['number']}
Timestamp: {format_time(row['start'])} - {format_time(row['end'])}
Content: {row['text']}"""
        for _, row in new_df.iterrows()
    )

    prompt = f"""
You are an assistant for a Python course.

Context:
{context}

Question:
{incoming_query}

Instructions:
- Use ONLY the context
- Identify the most relevant video
- Mention video title, number, and timestamp naturally in the first sentence
- Then explain briefly what the user will learn
- Do not use phrases like "we learn", "in this part", or "the assistant will guide"
- Write in direct, neutral tone (no narration)
- Keep sentences simple and professional
- Avoid phrases like "the user will learn"
- Do not start with "In video..."
- Write in direct, natural sentences

Rules:
- Keep it concise (2 sentences max)
- Do NOT use labels like "Video Title", "Video Number"
- Do NOT use bullet points or multiple lines
- Do NOT sound formal or robotic
- Do NOT add extra explanations or suggestions

Answer:
"""

    response = infernce(prompt)["response"]

    return response