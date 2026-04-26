import os
import json

# Config (tune these if needed)
# -------------------------------
INPUT_DIR = "jsons"
OUTPUT_DIR = "newjsons"

MAX_GAP = 5         
MAX_WORDS = 120      


# Merge Function
# -------------------------------
def merge_chunks(chunks, max_gap=5, max_words=120):
    if not chunks:
        return []

    merged = []
    current = chunks[0].copy()

    for next_chunk in chunks[1:]:
        gap = next_chunk["start"] - current["end"]

        # condition to merge
        if gap <= max_gap and len(current["text"].split()) < max_words:
            current["end"] = next_chunk["end"]
            current["text"] += " " + next_chunk["text"]
        else:
            merged.append(current)
            current = next_chunk.copy()

    merged.append(current)
    return merged


# Process all JSON files
# -------------------------------
def process_files():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(INPUT_DIR, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks = data.get("chunks", [])

        chunks = sorted(chunks, key=lambda x: x["start"])

        new_chunks = merge_chunks(chunks, MAX_GAP, MAX_WORDS)

        output_path = os.path.join(OUTPUT_DIR, filename)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "chunks": new_chunks,
                    "text": data.get("text", "")
                },
                f,
                indent=4,
                ensure_ascii=False
            )

        print(f"Processed: {filename} → {len(chunks)} → {len(new_chunks)} chunks")


# Run script
# -------------------------------
if __name__ == "__main__":
    process_files()